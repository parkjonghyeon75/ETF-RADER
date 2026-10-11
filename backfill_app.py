import os
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ETF RADAR Backfill Validator", layout="wide")

st.title("📊 ETF RADAR 상장폐지 및 생존편향 검증 앱")
st.markdown("기존 데이터를 덮어쓰지 않으며, 저장소의 마스터 파일과 일별 시세를 기반으로 안전하게 검증을 수행합니다.")

# 1. 저장소 파일 자동 로드 함수
@st.cache_data
def load_local_data():
    data_dir = "data"
    
    # 경로 설정 (루트 또는 data/ 폴더 모두 대응)
    delisted_path = "KRX_DELISTED_ALL.csv" if os.path.exists("KRX_DELISTED_ALL.csv") else os.path.join(data_dir, "KRX_DELISTED_ALL.csv")
    master_path = "KRX_ETF_MASTER.csv" if os.path.exists("KRX_ETF_MASTER.csv") else os.path.join(data_dir, "KRX_ETF_MASTER.csv")
    daily_path = "KRX_ETF_DAILY_RAW.csv" if os.path.exists("KRX_ETF_DAILY_RAW.csv") else os.path.join(data_dir, "KRX_ETF_DAILY_RAW.csv")
    
    delisted_df = pd.read_csv(delisted_path, dtype=str) if os.path.exists(delisted_path) else pd.DataFrame()
    master_df = pd.read_csv(master_path, dtype=str) if os.path.exists(master_path) else pd.DataFrame()
    daily_df = pd.read_csv(daily_path, dtype=str) if os.path.exists(daily_path) else pd.DataFrame()
    
    return delisted_df, master_df, daily_df

delisted_df, master_df, daily_df = load_local_data()

st.sidebar.header("📁 데이터 파일 상태")
st.sidebar.write(f"- 상장폐지 종목: **{len(delisted_df):,}건**")
st.sidebar.write(f"- ETF 기준정보: **{len(master_df):,}건**")
st.sidebar.write(f"- 일별 시세: **{len(daily_df):,}행**")

# 2. 메인 검증 로직 및 안전 장치
st.subheader("🔍 상장폐지 ETF 생존편향 검증 (테스트 모드)")

if not master_df.empty and not delisted_df.empty:
    # 정확한 식별자(단축코드 / ISU_CD) 매칭 검증
    # ETF 기준정보의 단축코드와 상장폐지 목록의 종목코드 교차 확인
    master_codes = set(master_df['단축코드'].dropna()) if '단축코드' in master_df.columns else set()
    delist_codes = set(delisted_df['종목코드'].dropna()) if '종목코드' in delisted_df.columns else set()
    
    matched_codes = master_codes.intersection(delist_codes)
    
    st.info(f"기준정보 ETF 총 {len(master_codes)}개 중 상장폐지 목록과 일치하는 종목 코드 수: {len(matched_codes)}개")
    
    # 샘플 테스트를 위한 5개 종목 추출 (안전 장치: 전체 일괄 실행 방지)
    sample_size = min(5, len(master_codes))
    sample_codes = list(master_codes)[:sample_size]
    
    st.write(f"👉 **최소 5개 종목 샘플 테스트 대상 코드:** {sample_codes}")
    
    if st.button("샘플 종목 매칭 및 데이터 무결성 검증 실행"):
        results = []
        for code in sample_codes:
            # 기준정보 매칭 행 추출
            m_row = master_df[master_df['단축코드'] == code]
            name = m_row['한글종목명'].values[0] if not m_row.empty and '한글종목명' in m_row.columns else "알 수 없음"
            
            # 일별 시세 확인
            d_rows = daily_df[daily_df['ISU_CD'] == code] if 'ISU_CD' in daily_df.columns else pd.DataFrame()
            
            results.append({
                "종목코드": code,
                "종목명": name,
                "기준정보확인": "성공" if not m_row.empty else "미확인",
                "시세데이터행수": len(d_rows),
                "결과": f"데이터 {len(d_rows)}건 확인됨"
            })
            
        res_df = pd.DataFrame(results)
        
        # PyArrow ArrowInvalid 오류 방지를 위해 '결과' 및 모든 컬럼을 확실한 문자열 타입으로 변환
        for col in res_df.columns:
            res_df[col] = res_df[col].astype(str)
            
        st.dataframe(res_df, use_container_width=True)
        st.success("샘플 검증이 안전하게 완료되었습니다. 기존 데이터는 덮어쓰이지 않았습니다.")
else:
    st.warning("데이터 파일을 찾을 수 없습니다. 저장소의 `data/` 경로를 확인해주세요.")

# 3. 문법 오류 수정 확인용 스캔 날짜 로직 예시
if 'BAS_DD' in daily_df.columns and not daily_df['BAS_DD'].empty:
    min_date = daily_df['BAS_DD'].min()
    max_date = daily_df['BAS_DD'].max()
    st.sidebar.markdown(f"📅 **시세 수집 기간**: `{min_date} ~ {max_date}`")
