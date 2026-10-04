# -*- coding: utf-8 -*-
"""ETF RADAR 청산 엔진 단위 테스트 - 독립 실행형
FINAL 백테스트 파일을 별도로 읽지 않습니다. 현재 FINAL의 청산 함수 코드를 테스트 파일에 포함합니다.
"""
import numpy as np
import pandas as pd

def _trade_levels_v6(d, signal_i, entry_price):
    """신호일의 정보만 사용해 다음 거래일 진입 기준을 계산한다."""
    r = d.iloc[signal_i]
    c = float(r['Close'])
    ma20 = float(r['MA20'])
    ma60 = float(r['MA60'])
    low20 = float(r['LOW20'])
    support = max(low20, ma20 * 0.985)
    stop1 = min(ma60 * 0.97, support * 0.97)
    stop2 = min(stop1, low20 * 0.98)
    if not np.isfinite(stop1) or stop1 <= 0:
        stop1 = entry_price * 0.95
    if not np.isfinite(stop2) or stop2 <= 0:
        stop2 = stop1
    risk = max(entry_price - stop1, entry_price * 0.02)
    tp1 = entry_price + risk
    tp2 = entry_price + risk * 2.0
    return {'entry': entry_price, 'support': support, 'stop1': stop1, 'stop2': stop2, 'risk': risk, 'tp1': tp1, 'tp2': tp2, 'signal_close': c}

def simulate_cd_trade_v7(r, data, initial_cash=1000000, fee_per_side=0.001, slippage_per_side=0.0005, max_hold_days=250):
    """V7 실전형 C/D 체결 시뮬레이션.

    C/D 선정 로직은 변경하지 않고 청산 구조만 개선한다.
    1) D 신호 다음 거래일 시가 진입.
    2) 1R에서 50% 익절.
    3) 2R에서 남은 물량의 50%(전체의 25%) 익절.
    4) 2R 도달 이후 남은 25%는 20일선 추적손절.
    5) 1차 손절은 보유물량의 50%, 2차 손절은 잔여물량 전량.
    6) 같은 봉에서 손절과 익절이 충돌하면 보수적으로 손절 우선.
    7) 최대 보유기간 종료 시 잔여물량 종가 청산.
    8) 보유 중 새 D 신호는 무시.
    """
    if r is None or r.empty:
        return (pd.DataFrame(), {'거래수': 0})
    signals = r.loc[r['D_미래테마선행가격'] == True].copy()
    if signals.empty:
        return (pd.DataFrame(), {'거래수': 0})
    signals['날짜'] = pd.to_datetime(signals['날짜'])
    signals = signals.sort_values('날짜').reset_index(drop=True)
    cash = float(initial_cash)
    trades = []
    next_available = pd.Timestamp.min

    def px(v, fallback):
        try:
            v = float(v)
            return v if np.isfinite(v) and v > 0 else fallback
        except Exception:
            return fallback
    for _, sig in signals.iterrows():
        signal_date = pd.Timestamp(sig['날짜'])
        if signal_date < next_available:
            continue
        ticker = sig['ETF']
        d = data.get(ticker)
        if d is None or d.empty:
            continue
        idx = d.index.searchsorted(signal_date)
        if idx >= len(d) or d.index[idx] != signal_date:
            continue
        entry_i = idx + 1
        if entry_i >= len(d):
            continue
        entry_row = d.iloc[entry_i]
        raw_entry = px(entry_row.get('Open', np.nan), px(entry_row.get('Close', np.nan), np.nan))
        if not np.isfinite(raw_entry) or raw_entry <= 0:
            continue
        entry_fill = raw_entry * (1 + slippage_per_side)
        lv = _trade_levels_v6(d, idx, entry_fill)
        stop1 = float(lv['stop1'])
        stop2 = float(lv['stop2'])
        tp1 = float(lv['tp1'])
        tp2 = float(lv['tp2'])
        remaining = 1.0
        realized = 0.0
        tp1_hit = False
        tp2_hit = False
        stop1_hit = False
        stop2_hit = False
        trail_hit = False
        trail_active = False
        exit_reason = ''
        last_i = min(len(d) - 1, entry_i + int(max_hold_days) - 1)
        exit_i = last_i

        def net_return(fill, weight):
            return weight * (fill / entry_fill - 1 - fee_per_side * 2)
        for j in range(entry_i, last_i + 1):
            bar = d.iloc[j]
            close_j = px(bar.get('Close', np.nan), np.nan)
            high_j = px(bar.get('High', np.nan), close_j)
            low_j = px(bar.get('Low', np.nan), close_j)
            ma20_j = px(bar.get('MA20', np.nan), np.nan)
            if not np.isfinite(close_j):
                continue
            if trail_active and remaining > 0 and np.isfinite(ma20_j) and (ma20_j > 0):
                trail_stop = ma20_j * 0.99
                if low_j <= trail_stop:
                    fill = trail_stop * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    trail_hit = True
                    exit_reason = '20일선 추적손절'
                    remaining = 0.0
                    exit_i = j
                    break
            if not trail_active and remaining > 0 and (low_j <= stop2):
                fill = stop2 * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                stop2_hit = True
                exit_reason = '2차 손절'
                remaining = 0.0
                exit_i = j
                break
            if not trail_active and remaining > 0 and (not stop1_hit) and (low_j <= stop1):
                fill = stop1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                stop1_hit = True
                if j == last_i and remaining > 0:
                    fill = close_j * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    remaining = 0.0
                    exit_reason = '1차 손절·기간만료'
                    exit_i = j
                    break
                continue
            if remaining > 0 and (not tp1_hit) and (high_j >= tp1):
                fill = tp1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp1_hit = True
            if remaining > 0 and tp1_hit and (not tp2_hit) and (high_j >= tp2):
                fill = tp2 * (1 - slippage_per_side)
                cut = min(0.25, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp2_hit = True
                trail_active = remaining > 0
                continue
            if remaining <= 0:
                exit_reason = '2R 익절' if tp2_hit else '1R 익절'
                exit_i = j
                break
            if j == last_i and remaining > 0:
                fill = close_j * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                remaining = 0.0
                if trail_active:
                    exit_reason = '추적손절·기간만료'
                elif tp2_hit:
                    exit_reason = '2R 후 기간만료'
                elif tp1_hit:
                    exit_reason = '1R 후 기간만료'
                else:
                    exit_reason = '기간만료'
                exit_i = j
                break
        cash *= 1 + realized
        exit_date = d.index[exit_i]
        next_available = exit_date + pd.Timedelta(days=1)
        trades.append({'신호일': signal_date.date(), '진입일': d.index[entry_i].date(), '청산일': exit_date.date(), 'ETF': ticker, '테마': sig['테마'], '테마점수': float(sig['테마점수']), '선행점수': int(sig['선행점수']), '진입가': entry_fill, '1차익절': tp1, '2차익절': tp2, '1차손절': stop1, '2차손절': stop2, 'R': lv['risk'], '1R도달': tp1_hit, '2R도달': tp2_hit, '1차손절도달': stop1_hit, '2차손절도달': stop2_hit, '20일선추적손절': trail_hit, '청산사유': exit_reason, '보유거래일': int(exit_i - entry_i + 1), '순수익률': realized * 100, '거래후자산': cash})
    td = pd.DataFrame(trades)
    if td.empty:
        return (td, {'초기자산': initial_cash, '최종자산': initial_cash, '총수익률': 0.0, '거래수': 0, '승률': np.nan, '최대낙폭': 0.0, '연환산': np.nan})
    curve = td[['청산일', '거래후자산']].copy()
    curve['청산일'] = pd.to_datetime(curve['청산일'])
    curve['고점'] = curve['거래후자산'].cummax()
    curve['낙폭'] = (curve['거래후자산'] / curve['고점'] - 1) * 100
    final_cash = float(td.iloc[-1]['거래후자산'])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (curve['청산일'].iloc[-1] - curve['청산일'].iloc[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100
    wins = int((td['순수익률'] > 0).sum())
    avg_win = td.loc[td['순수익률'] > 0, '순수익률'].mean()
    avg_loss = td.loc[td['순수익률'] <= 0, '순수익률'].mean()
    gross_profit = td.loc[td['순수익률'] > 0, '순수익률'].sum()
    gross_loss = -td.loc[td['순수익률'] < 0, '순수익률'].sum()
    metrics = {'초기자산': initial_cash, '최종자산': final_cash, '총수익률': total_ret, '연환산': annualized, '거래수': len(td), '승률': wins / len(td) * 100, '평균승리': avg_win, '평균손실': avg_loss, '손익비': abs(avg_win / avg_loss) if pd.notna(avg_win) and pd.notna(avg_loss) and (avg_loss != 0) else np.nan, 'ProfitFactor': gross_profit / gross_loss if gross_loss > 0 else np.inf, '기대값': td['순수익률'].mean(), '최대낙폭': float(curve['낙폭'].min()), '1R도달률': td['1R도달'].mean() * 100, '2R도달률': td['2R도달'].mean() * 100, '1차손절률': td['1차손절도달'].mean() * 100, '2차손절률': td['2차손절도달'].mean() * 100, '추적손절률': td['20일선추적손절'].mean() * 100, '평균보유일': td['보유거래일'].mean()}
    return (td, metrics)

def make_case(bars, ma20=100.0, ma60=100.0, low20=100.0):
    dates=pd.date_range("2026-01-01",periods=len(bars)+1,freq="B")
    sig=pd.DataFrame([{"날짜":dates[0],"ETF":"TEST","테마":"UNIT","테마점수":80.0,"선행점수":80,"D_미래테마선행가격":True}])
    rows=[{"Open":100,"High":100,"Low":100,"Close":100,"MA20":ma20,"MA60":ma60,"LOW20":low20}]
    for b in bars:
        rows.append({"Open":b.get("Open",100),"High":b.get("High",b.get("Close",100)),"Low":b.get("Low",b.get("Close",100)),"Close":b.get("Close",100),"MA20":b.get("MA20",100),"MA60":b.get("MA60",100),"LOW20":b.get("LOW20",low20)})
    return sig,{"TEST":pd.DataFrame(rows,index=dates)}

def run(name,bars,checks,**kw):
    r,data=make_case(bars,**kw); td,m=simulate_cd_trade_v7(r,data,initial_cash=1_000_000,fee_per_side=0,slippage_per_side=0,max_hold_days=250)
    assert not td.empty, '거래가 생성되지 않음'
    t=td.iloc[0]
    for k,v in checks.items(): assert t[k]==v, f"{k}: expected {v!r}, got {t[k]!r}"
    print('PASS',name)

def main():
    # stop1=97, stop2=min(97,98)=97, risk=3, TP1=103, TP2=106
    run('1R 50% + 기간만료',[{"Open":100,"High":103,"Low":100,"Close":102}],{"1R도달":True,"2R도달":False,"청산사유":"1R 후 기간만료"})
    run('2R 추가 25%',[{"Open":100,"High":106,"Low":100,"Close":105},{"Open":105,"High":105,"Low":98.9,"Close":100}],{"1R도달":True,"2R도달":True,"20일선추적손절":True,"청산사유":"20일선 추적손절"})
    run('2R 후 추적손절',[{"Open":100,"High":106,"Low":100,"Close":105},{"Open":105,"High":106,"Low":98.9,"Close":100,"MA20":100}],{"1R도달":True,"2R도달":True,"20일선추적손절":True,"청산사유":"20일선 추적손절"})
    run('1R 이전 2차손절',[{"Open":100,"High":102,"Low":96,"Close":98}],{"1R도달":False,"2R도달":False,"2차손절도달":True,"청산사유":"2차 손절"})
    run('1R 후 2R 전 2차손절',[{"Open":100,"High":103,"Low":100,"Close":102},{"Open":102,"High":103,"Low":96,"Close":98}],{"1R도달":True,"2R도달":False,"2차손절도달":True,"청산사유":"2차 손절"})
    run('기간만료',[{"Open":100,"High":101,"Low":99,"Close":100}],{"1R도달":False,"2R도달":False,"청산사유":"기간만료"})
    print('ALL PASS: 6/6')

if __name__=='__main__': main()
