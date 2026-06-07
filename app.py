import streamlit as st
import pandas as pd
import requests
import datetime

# ----------------------------------------
# ⚠️ 설정 구역 (본인의 URL로 변경하세요)
# ----------------------------------------
# 1. 생성된 구글 시트 ID가 반영된 주소입니다.
SHEET_ID = "1KLbqBdtN5i7P30OlDrajPPwUkn8ux0uYkZH3gsQfq-M"
DATA_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# 2. 1단계에서 복사한 구글 앱스 스크립트 웹 앱 URL을 따옴표 안에 붙여넣으세요
API_URL = "https://script.google.com/macros/s/AKfycbzRe3aLLXofX8d8UZgKM2MD4HH7P0xe-FR68aUNYHT0gSLfef_p0QWgYay1YVLY904YLA/exec"
# ----------------------------------------

st.set_page_config(page_title="모바일 장부 시스템", layout="centered")
st.title("📊 나의 모바일 장부")

try:
    df = pd.read_csv(f"{DATA_URL}&clear_cache={datetime.datetime.now().timestamp()}")
    df['금액'] = pd.to_numeric(df['금액'], errors='coerce').fillna(0)
except Exception as e:
    st.error("구글 시트 데이터를 불러오지 못했습니다.")
    df = pd.DataFrame(columns=["날짜", "구분", "상세분류", "금액", "메모"])

sales_total = df[df['구분'] == '매출']['금액'].sum()
expense_total = df[df['구분'] == '매입']['금액'].sum()
net_profit = sales_total - expense_total

st.subheader("💰 이번 달 현황")
col1, col2, col3 = st.columns(3)
col1.metric("총매출", f"{int(sales_total):,}원")
col2.metric("총매입", f"{int(expense_total):,}원")
col3.metric("순이익 추정", f"{int(net_profit):,}원")

st.divider()

st.subheader("📝 새 내역 기록하기")

date = st.date_input("날짜", datetime.date.today())
type_choice = st.selectbox("구분", ["매출", "매입"])

if type_choice == "매출":
    category = st.selectbox("상세분류", ["현장매출", "배달(배민)", "배달(쿠팡이츠)", "단체예약매출", "기타 매출"])
else:
    category = st.selectbox("상세분류", ["재료비", "월세", "제세공과금", "기타 매입"])
    
amount = st.number_input("금액 (원)", min_value=0, step=1000)
memo = st.text_input("메모", "")

if st.button("장부에 기록하기"):
    if "여기에" in API_URL:
        st.warning("구글 앱스 스크립트 URL을 먼저 설정해주세요.")
    else:
        payload = {
            "date": str(date),
            "type": type_choice,
            "category": category,
            "amount": int(amount),
            "memo": memo
        }
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                st.success("성공적으로 기록되었습니다. 화면을 위에서 아래로 당겨 새로고침하면 아래 표에 반영됩니다.")
            else:
                st.error("기록에 실패했습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")

st.divider()

st.subheader("📋 최근 기록된 내역")
if not df.empty:
    st.dataframe(df.tail(10), use_container_width=True)
else:
    st.text("기록된 데이터가 없습니다.")
