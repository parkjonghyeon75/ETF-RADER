
# krx_etf_type_verify.py
# KRX ETF 공식 데이터 기반 상장폐지 ETF 분류 검증
# 기존 app.py 및 백필 스크립트는 수정하지 않습니다.

import os
import re
import json
import time
import argparse
from pathlib import Path

import pandas as pd
import requests

API_URL = (
    "https://data-dbg.krx.co.kr/"
    "svc/apis/etp/etf_bydd_trd"
)


def clean(value):
    """종목명 비교용 정규화. 분류의 최종 근거로 사용하지 않음."""
    if pd.isna(value):
        return ""
    return re.sub(r"[\s\W_]+", "", str(value)).upper()


def fetch_etf_day(session, api_key, date):
    """KRX ETF 일별매매정보 조회."""
    response = session.get(
        API_URL,
        params={"basDd": date},
        headers={"AUTH_KEY": api_key},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    # KRX 응답 구조 확인
    rows = data.get("OutBlock_1", [])
    if isinstance(rows, dict):
        rows = [rows]

    if not isinstance(rows, list):
        raise ValueError(
            f"예상하지 못한 KRX 응답 구조: {str(data)[:500]}"
        )

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="KRX_DELISTED_ALL.csv",
    )
    parser.add_argument(
        "--out",
        default="KRX_ETF_TYPE_REVIEW",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="시험 실행 건수. 0이면 전체",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.3,
    )
    args = parser.parse_args()

    api_key = os.getenv("KRX_API_KEY")
    if not api_key:
        raise SystemExit(
            "KRX_API_KEY 환경변수가 없습니다. "
            "KRX Open API 인증키를 등록해 주세요."
        )

    source = Path(args.input)
    if not source.exists():
        raise SystemExit(
            f"입력 파일을 찾을 수 없습니다: {source}"
        )

    df = pd.read_csv(source, dtype=str).fillna("")

    required = {"종목명", "폐지일"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(
            f"필수 컬럼 누락: {sorted(missing)}"
        )

    # ETF라고 추측하지 않고 공식 ETF 데이터와 대조할 대상만 준비
    df["폐지일_정규화"] = (
        df["폐지일"].str.replace("/", "", regex=False)
    )
    df["이름비교키"] = df["종목명"].map(clean)

    targets = df[
        df["폐지일_정규화"].str.fullmatch(r"\d{8}")
        & df["이름비교키"].ne("")
    ].copy()

    if args.limit > 0:
        targets = targets.head(args.limit)

    # 폐지일 직전 거래일 후보 날짜를 최대 10일 전까지 조회
    dates = set()
    for date in targets["폐지일_정규화"]:
        end = pd.to_datetime(date, format="%Y%m%d")
        for offset in range(1, 11):
            d = (end - pd.Timedelta(days=offset))
            if d.weekday() < 5:
                dates.add(d.strftime("%Y%m%d"))

    session = requests.Session()
    day_frames = []
    errors = []

    for i, date in enumerate(sorted(dates), start=1):
        try:
            daily = fetch_etf_day(session, api_key, date)

            if not daily.empty:
                daily["조회기준일"] = date
                day_frames.append(daily)

            print(
                f"[{i}/{len(dates)}] {date}: "
                f"{len(daily)} rows"
            )

        except Exception as exc:
            errors.append({
                "date": date,
                "error": f"{type(exc).__name__}: {exc}",
            })
            print(f"[ERROR] {date}: {exc}")

        time.sleep(max(0, args.pause))

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    all_etf = (
        pd.concat(day_frames, ignore_index=True)
        if day_frames else pd.DataFrame()
    )

    all_etf.to_csv(
        outdir / "KRX_ETF_DAILY_REFERENCE.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # KRX 응답 컬럼을 확인해 이름 비교
    if not all_etf.empty and "ISU_NM" in all_etf.columns:
        all_etf["이름비교키"] = all_etf["ISU_NM"].map(clean)
    else:
        all_etf["이름비교키"] = ""

    records = []

    for _, target in targets.iterrows():
        key = target["이름비교키"]

        matches = all_etf[
            all_etf["이름비교키"].eq(key)
        ]

        records.append({
            "종목코드": target.get("종목코드", ""),
            "종목명": target["종목명"],
            "폐지일": target["폐지일"],
            "공식ETF데이터명일치": not matches.empty,
            "확인된ETF데이터날짜": (
                ";".join(
                    sorted(matches["조회기준일"].unique())
                )
                if not matches.empty else ""
            ),
            "판정": (
                "공식 ETF 데이터 일치 - 코드 추가 대조 필요"
                if not matches.empty
                else "미확인 - ETF 아님으로 단정 금지"
            ),
        })

    result = pd.DataFrame(records)
    result.to_csv(
        outdir / "KRX_ETF_TYPE_REVIEW.csv",
        index=False,
        encoding="utf-8-sig",
    )

    pd.DataFrame(errors).to_csv(
        outdir / "KRX_ETF_API_ERRORS.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = {
        "input_rows": len(df),
        "tested_rows": len(targets),
        "queried_dates": len(dates),
        "official_etf_reference_rows": len(all_etf),
        "name_matched_rows": (
            int(result["공식ETF데이터명일치"].sum())
            if not result.empty else 0
        ),
        "api_error_count": len(errors),
        "status": (
            "REVIEW_REQUIRED"
            if errors or all_etf.empty
            else "NAME_MATCH_REVIEW_REQUIRED"
        ),
        "warning": (
            "종목명 일치는 1차 검증일 뿐입니다. "
            "종목코드/ISIN 연결과 폐지일을 추가 대조하기 전에는 "
            "백테스트에 확정 반영하지 마십시오."
        ),
    }

    (outdir / "RUN_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n=== 검증 결과 ===")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"\n결과 폴더: {outdir.resolve()}")


if __name__ == "__main__":
    main()
