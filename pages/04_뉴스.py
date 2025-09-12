import streamlit as st
import openai
import requests
import datetime

# ✅ API 키 설정 (secrets.toml에 저장되어 있어야 함)
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# ✅ 기본 설정
st.set_page_config(page_title="📊 뉴스 + GPT 분석", layout="centered")
st.title("📰 뉴스 기반 종목 분석 (주가 제외)")

# ✅ 종목 선택
stocks = ["Apple", "Tesla", "Amazon", "Google", "Microsoft"]
stock_name = st.selectbox("🔎 분석할 종목을 선택하세요", stocks)

# ✅ 뉴스 불러오기 함수
def get_news(query="Apple", language="en", country="us"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}&country={country}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error(f"❌ 뉴스 API 오류: {res.status_code} - {res.text}")
            return []
        return res.json().get("results", [])
    except Exception as e:
        st.error(f"⚠️ 뉴스 요청 오류: {e}")
        return []

# ✅ GPT 분석 함수
def gpt_analysis(title, content):
    prompt = f"""
    다음은 {stock_name}에 대한 뉴스 기사입니다.

    제목: {title}
    내용: {content}

    이 뉴스가 {stock_name} 주식에 미칠 영향과 향후 투자 전략을 최소 300자 이상으로 분석해 주세요.
    """
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 금융 전문 애널리스트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 분석 실패: {e}"

# ✅ 뉴스 섹션
st.subheader(f"📰 {stock_name} 관련 뉴스 및 GPT 분석")

news_items = get_news(query=f"{stock_name} stock")
if not news_items:
    st.info("📭 관련 뉴스가 없습니다.")
else:
    seen_titles = set()
    for article in news_items:
        title = article.get("title", "제목 없음")
        if title in seen_titles:
            continue
        seen_titles.add(title)

        st.markdown(f"### {title}")
        st.write(article.get("description", "설명 없음"))
        st.caption(f"🕒 {article.get('pubDate', '날짜 없음')}")
        st.markdown(f"[🔗 원문 보기]({article.get('link', '#')})")

        with st.spinner("🤖 GPT 분석 중..."):
            analysis = gpt_analysis(title, article.get("description", ""))
        st.success(analysis)
        st.markdown("---")
