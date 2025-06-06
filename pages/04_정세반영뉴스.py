import streamlit as st
import openai
import requests

# OpenAI 및 NewsData API 키 불러오기 (secrets.toml에 저장되어 있어야 함)
openai.api_key = st.secrets["openai_api_key"]
NEWS_API_KEY = st.secrets["newsdata_api_key"]

# 뉴스 불러오기 함수
def get_news(query="stock", language="en", country="us"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={query}&language={language}&country={country}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            st.error(f"뉴스 API 오류: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"뉴스를 불러오는 중 오류 발생: {e}")
        return []

# GPT 분석 함수 (OpenAI >= 1.0.0 방식)
def gpt_analysis(title, content):
    prompt = f"""
    다음은 주식 관련 뉴스입니다.

    제목: {title}
    내용: {content}

    위 뉴스가 주식 시장에 미칠 영향과 추천 종목이 있다면 예측 및 근거를 300자 이상으로 설명해주세요.
    """
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 주식 분석가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 분석 실패: {e}"

# Streamlit UI
st.title("📰 뉴스 기반 주식 분석 및 종목 추천")
query = st.text_input("🔍 분석할 키워드를 입력하세요", "반도체")

if query:
    with st.spinner("뉴스를 불러오는 중..."):
        news_list = get_news(query=query)

    if news_list:
        for i, article in enumerate(news_list[:3]):
            st.subheader(f"🗞️ {article['title']}")
            st.write(article["description"] or "내용 없음")
            st.caption(f"🕒 {article['pubDate']}")
            with st.spinner("GPT가 분석 중입니다..."):
                analysis = gpt_analysis(article["title"], article["description"])
            st.success(analysis)
            st.markdown("---")
    else:
        st.warning("뉴스를 찾을 수 없습니다.")
