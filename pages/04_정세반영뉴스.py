import streamlit as st
import openai
import requests

# OpenAI 키 설정
client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

# NewsData API로 뉴스 불러오기
def get_news(query="stock", language="en", country="us"):
    api_key = st.secrets["newsdata_api_key"]
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={query}&language={language}&country={country}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error("뉴스 로딩 실패")
        return []

# GPT 분석 함수 (최신 방식)
def analyze_news_with_gpt(news_title, news_content):
    full_text = f"뉴스 제목: {news_title}\n내용: {news_content}\n\n이 뉴스가 주식 시장에 어떤 영향을 줄 수 있을지 분석해줘."
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 경제 전문가입니다."},
            {"role": "user", "content": full_text}
        ],
        temperature=0.7,
    )
    return completion.choices[0].message.content

# Streamlit UI
st.title("📈 정세 반영 뉴스 기반 주식 분석")

query = st.text_input("뉴스 키워드를 입력하세요", "삼성전자")
if query:
    articles = get_news(query=query)
    for article in articles[:3]:
        st.subheader(article["title"])
        st.write(article["description"])
        st.write(f"🕒 {article['pubDate']}")
        with st.spinner("GPT 분석 중..."):
            analysis = analyze_news_with_gpt(article["title"], article["description"])
        st.success(analysis)
        st.markdown("---")
