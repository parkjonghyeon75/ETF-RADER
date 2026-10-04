# -*- coding: utf-8 -*-
"""ETF RADAR V7 청산 엔진 단위 테스트

목적:
- C/D 선정 로직은 건드리지 않고 V7 청산 엔진만 검증한다.
- 1R 50% -> 2R 추가 25% -> 잔여 25% 20일선 추적손절 구조가 실제로 체결되는지 확인한다.
- 테스트는 실제 시장 데이터가 아닌 결정론적 OHLC 시나리오를 사용한다.

실행:
    python ETF_RADAR_EXIT_ENGINE_UNIT_TEST.py

현재 FINAL 파일의 simulate_cd_trade_v7()를 AST로 추출해 직접 테스트하므로,
실전 코드와 테스트 코드의 청산 로직이 달라지는 문제를 피한다.
"""
import ast
import sys
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE = Path(__file__).with_name("ETF_RADAR_STRATEGY_BACKTEST_FINAL.py")


def load_engine():
    src = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    wanted = {"_trade_levels_v6", "simulate_cd_trade_v7"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    found = {n.name for n in nodes}
    missing = wanted - found
    if missing:
        raise RuntimeError(f"청산 엔진 함수가 없습니다: {sorted(missing)}")
    ns = {"np": np, "pd": pd}
    # _trade_levels_v6가 먼저 오도록 정렬
    nodes.sort(key=lambda n: 0 if n.name == "_trade_levels_v6" else 1)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), ns)
    return ns["simulate_cd_trade_v7"]


def make_case(bars, entry_open=100.0, signal_close=100.0,
              ma20_signal=100.0, ma60_signal=100.0, low20_signal=100.0):
    """첫 행=신호일, 둘째 행부터 실제 거래일."""
    dates = pd.date_range("2026-01-01", periods=len(bars) + 1, freq="B")
    signal = pd.DataFrame([{
        "날짜": dates[0], "ETF": "TEST", "테마": "UNIT", "테마점수": 80.0,
        "선행점수": 80, "D_미래테마선행가격": True,
    }])
    rows = []
    # signal row: _trade_levels_v6가 읽는 값
    rows.append({
        "Open": signal_close, "High": signal_close, "Low": signal_close,
        "Close": signal_close, "MA20": ma20_signal, "MA60": ma60_signal,
        "LOW20": low20_signal,
    })
    for k, b in enumerate(bars, start=1):
        rows.append({
            "Open": b.get("Open", entry_open if k == 1 else b.get("Close", entry_open)),
            "High": b.get("High", b.get("Close", entry_open)),
            "Low": b.get("Low", b.get("Close", entry_open)),
            "Close": b.get("Close", entry_open),
            "MA20": b.get("MA20", entry_open),
            "MA60": b.get("MA60", entry_open),
            "LOW20": b.get("LOW20", low20_signal),
        })
    d = pd.DataFrame(rows, index=dates)
    return signal, {"TEST": d}


def run_one(sim, name, bars, expected, **case_kwargs):
    r, data = make_case(bars, **case_kwargs)
    trades, metrics = sim(
        r, data, initial_cash=1_000_000,
        fee_per_side=0.0, slippage_per_side=0.0,
        max_hold_days=250,
    )
    if trades.empty:
        raise AssertionError("거래가 생성되지 않았습니다.")
    t = trades.iloc[0].to_dict()
    checks = []
    for key, exp in expected.items():
        got = t.get(key)
        if isinstance(exp, (int, float)) and isinstance(got, (int, float)):
            ok = abs(float(got) - float(exp)) <= 1e-6
        else:
            ok = got == exp
        if not ok:
            checks.append(f"{key}: expected={exp!r}, got={got!r}")
    if checks:
        raise AssertionError("; ".join(checks))
    return t


def main():
    sim = load_engine()
    tests = []

    # entry=100, signal MA20=100, MA60=100, LOW20=100
    # stop1=97, stop2=97, risk=3, TP1=103, TP2=106.
    tests.append((
        "1R 50% 익절",
        [{"Open":100,"High":103,"Low":100,"Close":102,"MA20":100}],
        {"1R도달": True, "2R도달": False, "청산사유": "1R 후 기간만료"},
    ))

    tests.append((
        "2R 추가 25% 익절",
        [{"Open":100,"High":106,"Low":100,"Close":105,"MA20":100},
         {"Open":105,"High":105,"Low":104,"Close":105,"MA20":100}],
        {"1R도달": True, "2R도달": True, "청산사유": "추적손절·기간만료", "순수익률": 4.25},
    ))

    # 2R 다음 봉에 MA20 추적손절 99.0 도달
    tests.append((
        "2R 후 20일선 추적손절",
        [{"Open":100,"High":106,"Low":100,"Close":105,"MA20":100},
         {"Open":105,"High":106,"Low":98.9,"Close":100,"MA20":100}],
        {"1R도달": True, "2R도달": True, "20일선추적손절": True, "청산사유": "20일선 추적손절", "순수익률": 2.75},
    ))

    # 1R 이전 stop1만 터지도록 low=97, stop2=97이라 현재 엔진에서는 2차손절로 잡힐 수 있음.
    # 이 테스트는 '1차 손절 이벤트가 실제로 존재하는지' 확인하기 위해 별도 기대값을 둔다.
    tests.append((
        "1R 이전 1차 손절",
        [{"Open":100,"High":102,"Low":95.3,"Close":98,"MA20":100}],
        {"1R도달": False, "2R도달": False, "1차손절도달": True, "청산사유": "1차 손절·기간만료"},
        {"low20_signal":97.0},
    ))

    tests.append((
        "1R 후 2R 전 2차 손절",
        [{"Open":100,"High":103,"Low":100,"Close":102,"MA20":100},
         {"Open":102,"High":103,"Low":94.5,"Close":98,"MA20":100}],
        {"1R도달": True, "2R도달": False, "2차손절도달": True, "청산사유": "2차 손절"},
    ))

    tests.append((
        "250일 기간만료",
        [{"Open":100,"High":101,"Low":99,"Close":100,"MA20":100}],
        {"1R도달": False, "2R도달": False, "청산사유": "기간만료"},
    ))

    passed = 0
    failed = 0
    for item in tests:
        name, bars, expected = item[:3]
        case_kwargs = item[3] if len(item) > 3 else {}
        try:
            t = run_one(sim, name, bars, expected, **case_kwargs)
            print(f"PASS | {name} | {t['청산사유']} | return={t['순수익률'] if '순수익률' in t else 'n/a'}")
            passed += 1
        except Exception as e:
            print(f"FAIL | {name} | {e}")
            failed += 1

    print("-" * 72)
    print(f"결과: PASS {passed} / FAIL {failed} / TOTAL {len(tests)}")
    if failed:
        print("청산 엔진 수정 후 다시 테스트해야 합니다.")
        return 1
    print("청산 엔진 단위 테스트 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
