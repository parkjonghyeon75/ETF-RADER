import os
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ETF RADAR Backfill Validator", layout="wide")

APP_TITLE = "ETF RADAR — 상장폐지 ETF 식별자 진단"
st.title(APP_TITLE)
st.caption(
    "저장소 CSV를 읽어 컬럼·식별자·시세 연결 상태를 진단합니다. "
    "이 도구는 확인되지 않은 종목을 ETF로 추정하지 않으며, 원본 파일을 수정하지 않습니다."
)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def find_csv(filename: str):
    """Find a repository CSV in root or data/ without guessing other filenames."""
    for candidate in (ROOT / filename, DATA_DIR / filename):
        if candidate.is_file():
            return candidate
    return None


@st.cache_data(show_spinner=False)
def read_csv_safe(path_text: str):
    """Read text identifiers without losing leading zeroes; return a user-facing error."""
    try:
        frame = pd.read_csv(path_text, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        frame.columns = [str(c).strip().replace("\ufeff", "") for c in frame.columns]
        for col in frame.columns:
            frame[col] = frame[col].astype(str).str.strip()
        return frame, ""
    except UnicodeDecodeError:
        try:
            frame = pd.read_csv(path_text, dtype=str, keep_default_na=False, encoding="cp949")
            frame.columns = [str(c).strip().replace("\ufeff", "") for c in frame.columns]
            for col in frame.columns:
                frame[col] = frame[col].astype(str).str.strip()
            return frame, ""
        except Exception as exc:
            return pd.DataFrame(), f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        return pd.DataFrame(), f"{type(exc).__name__}: {exc}"


def clean_code(value):
    """Only trim and uppercase. Never truncate, pad, or infer a match."""
    if value is None:
        return ""
    return str(value).strip().upper()


def choose_column(df, preferred, label):
    options = list(df.columns)
    if not options:
        return None
    default_index = options.index(preferred) if preferred in options else 0
    return st.selectbox(label, options, index=default_index, key=f"col_{label}")


def summarize_frame(label, path, df, error):
    with st.container(border=True):
        st.markdown(f"**{label}**")
        st.write(f"경로: `{path}`" if path else "경로: 파일을 찾지 못함")
        if error:
            st.error(f"읽기 실패: {error}")
        elif path and not df.empty:
            st.success(f"로드됨: {len(df):,}행 × {len(df.columns)}열")
            st.caption("컬럼: " + ", ".join(df.columns))
        elif path:
            st.warning("파일은 있지만 데이터 행이 0개입니다.")
        else:
            st.warning("저장소 루트 또는 data/ 폴더에서 파일을 찾지 못했습니다.")


files = {
    "delisted": find_csv("KRX_DELISTED_ALL.csv"),
    "master": find_csv("KRX_ETF_MASTER.csv"),
    "daily": find_csv("KRX_ETF_DAILY_RAW.csv"),
}
frames = {}
errors = {}
for key, path in files.items():
    if path:
        frames[key], errors[key] = read_csv_safe(str(path))
    else:
        frames[key], errors[key] = pd.DataFrame(), ""

delisted = frames["delisted"]
master = frames["master"]
daily = frames["daily"]

st.subheader("1. 저장소 파일 자동 탐색 결과")
c1, c2, c3 = st.columns(3)
with c1:
    summarize_frame("상장폐지 목록", files["delisted"], delisted, errors["delisted"])
with c2:
    summarize_frame("ETF 기준정보", files["master"], master, errors["master"])
with c3:
    summarize_frame("ETF 일별 시세", files["daily"], daily, errors["daily"])

if master.empty or daily.empty:
    st.error(
        "ETF 기준정보 또는 일별 시세 파일을 읽지 못했습니다. "
        "GitHub 저장소의 파일명과 위치를 확인하세요. 파일 업로드는 필수가 아닙니다."
    )
    st.stop()

st.subheader("2. ETF 기준정보 ↔ 일별 시세 정확 일치 검사")
required_master = {"단축코드", "표준코드", "한글종목명"}
required_daily = {"BAS_DD", "ISU_CD", "ISU_NM"}
missing_master = sorted(required_master - set(master.columns))
missing_daily = sorted(required_daily - set(daily.columns))

if missing_master:
    st.error(f"ETF 기준정보 필수 컬럼 누락: {missing_master}")
if missing_daily:
    st.error(f"ETF 일별 시세 필수 컬럼 누락: {missing_daily}")

if not missing_master and not missing_daily:
    master_codes = set(master["단축코드"].map(clean_code)) - {""}
    daily_codes = set(daily["ISU_CD"].map(clean_code)) - {""}
    exact_codes = master_codes & daily_codes
    master_only = master_codes - daily_codes
    daily_only = daily_codes - master_codes

    a, b, c, d = st.columns(4)
    a.metric("기준정보 고유 단축코드", f"{len(master_codes):,}")
    b.metric("시세 고유 ISU_CD", f"{len(daily_codes):,}")
    c.metric("정확 일치 코드", f"{len(exact_codes):,}")
    d.metric("기준정보에만 존재", f"{len(master_only):,}")

    st.write(f"시세 파일에만 존재하는 코드: **{len(daily_only):,}개**")
    st.caption(
        "비교는 앞뒤 공백 제거 및 대문자 통일 후 전체 문자열 완전 일치로만 수행했습니다. "
        "코드 자르기, 숫자 변환, 앞자리/뒷자리 부분 일치는 하지 않았습니다."
    )

    # Per-code daily range, with stable and repeatable sample selection.
    daily_dates = daily[["ISU_CD", "BAS_DD"]].copy()
    daily_dates["ISU_CD"] = daily_dates["ISU_CD"].map(clean_code)
    daily_dates["BAS_DD"] = daily_dates["BAS_DD"].astype(str).str.strip()
    daily_dates = daily_dates[daily_dates["ISU_CD"] != ""]
    date_summary = (
        daily_dates.groupby("ISU_CD", as_index=False)
        .agg(시세행수=("BAS_DD", "size"), 최초거래일=("BAS_DD", "min"), 최종거래일=("BAS_DD", "max"))
    )

    master_view = master[["단축코드", "표준코드", "한글종목명"]].copy()
    master_view["단축코드"] = master_view["단축코드"].map(clean_code)
    master_view = master_view.merge(date_summary, left_on="단축코드", right_on="ISU_CD", how="left")
    master_view["시세행수"] = master_view["시세행수"].fillna(0).astype(int)
    master_view["시세연결상태"] = master_view["시세행수"].map(
        lambda n: "정확 일치·시세 있음" if n > 0 else "정확 일치 시세 없음"
    )
    st.markdown("**기준정보별 시세 연결 현황 (앞 20행)**")
    st.dataframe(master_view.drop(columns=["ISU_CD"], errors="ignore").head(20), use_container_width=True)

    with st.expander("정확 일치하지 않는 코드 예시"):
        st.write("기준정보에만 있는 코드 (최대 30개)")
        st.code("\n".join(sorted(master_only)[:30]) or "(없음)")
        st.write("시세에만 있는 코드 (최대 30개)")
        st.code("\n".join(sorted(daily_only)[:30]) or "(없음)")

st.subheader("3. 상장폐지 목록의 식별자 구조 확인")
if delisted.empty:
    st.warning(
        "상장폐지 목록을 읽지 못해 상장폐지 ETF 매칭은 수행할 수 없습니다. "
        "현재 결과로 상장폐지 ETF가 없다고 결론 내리지 마세요."
    )
else:
    st.write("상장폐지 파일의 실제 컬럼을 확인하고, 식별자 컬럼을 직접 지정하세요.")
    st.caption(
        "상장폐지 파일의 코드가 6자리 단축코드가 아닐 수 있으므로 자동으로 잘라서 연결하지 않습니다. "
        "코드 컬럼을 선택해도 전체 문자열 완전 일치만 계산합니다."
    )
    delisted_code_col = choose_column(delisted, "종목코드" if "종목코드" in delisted.columns else "", "상장폐지 목록의 코드 컬럼")
    name_options = ["(선택 안 함)"] + list(delisted.columns)
    name_default = (list(delisted.columns).index("종목명") + 1) if "종목명" in delisted.columns else 0
    delisted_name_col = st.selectbox("상장폐지 목록의 종목명 컬럼(선택)", name_options, index=name_default)
    date_options = ["(선택 안 함)"] + list(delisted.columns)
    date_default = (list(delisted.columns).index("폐지일") + 1) if "폐지일" in delisted.columns else 0
    delisted_date_col = st.selectbox("상장폐지 목록의 폐지일 컬럼(선택)", date_options, index=date_default)

    if delisted_code_col:
        delisted_codes = delisted[delisted_code_col].map(clean_code)
        code_lengths = delisted_codes[delisted_codes != ""].map(len).value_counts().sort_index()
        length_table = pd.DataFrame({"코드 길이": code_lengths.index.astype(str), "행 수": code_lengths.values})
        st.markdown("**상장폐지 코드 길이 분포**")
        st.dataframe(length_table, use_container_width=True, hide_index=True)

        master_short_codes = set(master["단축코드"].map(clean_code)) - {""} if "단축코드" in master.columns else set()
        master_isins = set(master["표준코드"].map(clean_code)) - {""} if "표준코드" in master.columns else set()
        delisted_code_set = set(delisted_codes) - {""}
        exact_short = delisted_code_set & master_short_codes
        exact_isin = delisted_code_set & master_isins

        x, y, z = st.columns(3)
        x.metric("폐지 코드 고유값", f"{len(delisted_code_set):,}")
        y.metric("단축코드 완전 일치", f"{len(exact_short):,}")
        z.metric("표준코드 완전 일치", f"{len(exact_isin):,}")

        st.warning(
            "완전 일치가 0건이어도 자동으로 다른 코드 형식으로 변환하지 않습니다. "
            "이는 식별자 체계가 다르거나 기준정보가 과거 종목을 포함하지 않을 가능성을 뜻할 뿐, "
            "상장폐지 ETF가 0개라는 뜻은 아닙니다."
        )

        # Sample includes both exact matches and unmatched codes, reproducibly.
        matched_sample = sorted(exact_short)[:5]
        unmatched_sample = sorted(delisted_code_set - master_short_codes)[:5]
        sample_codes = matched_sample + unmatched_sample
        sample_codes = list(dict.fromkeys(sample_codes))

        if sample_codes:
            rows = []
            for code in sample_codes:
                subset = delisted[delisted_code_col].map(clean_code).eq(code)
                raw_rows = delisted.loc[subset]
                row = {
                    "상장폐지 코드": code,
                    "폐지목록 행 수": int(subset.sum()),
                    "단축코드 완전일치": code in master_short_codes,
                    "표준코드 완전일치": code in master_isins,
                    "판정": "정확 식별자 일치" if code in exact_short or code in exact_isin else "미확인 — 추가 기준정보 필요",
                }
                if delisted_name_col != "(선택 안 함)":
                    row["폐지목록 종목명"] = raw_rows.iloc[0][delisted_name_col] if not raw_rows.empty else ""
                if delisted_date_col != "(선택 안 함)":
                    row["폐지일"] = raw_rows.iloc[0][delisted_date_col] if not raw_rows.empty else ""
                rows.append(row)
            st.markdown("**상장폐지 코드 샘플 진단**")
            st.dataframe(pd.DataFrame(rows).astype(str), use_container_width=True, hide_index=True)

st.subheader("4. 진단 결론")
st.info(
    "이 앱은 식별자와 로컬 시세 연결 상태를 진단합니다. "
    "현재 기준정보와 상장폐지 목록의 정확한 연결만으로 ETF의 과거 상장 상태를 모두 복원할 수는 없습니다."
)
st.markdown(
    """
**이 앱이 아직 수행하지 않는 작업**
- KRX API를 통한 상장폐지 ETF 과거 가격 수집
- 과거 상장일·폐지일을 이용한 거래 신호 유효성 검증
- ETF RADAR 백테스트 재계산
- 생존편향 보정 전후 수익률·MDD·승률 비교

위 작업은 상장폐지 ETF를 정확히 식별할 수 있는 공식 과거 종목 기준정보와 과거 시세가 확보된 뒤 별도 단계로 수행해야 합니다.
"""
)
