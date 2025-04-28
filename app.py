import streamlit as st
import openai
import os
import requests

# OpenAI API Key 설정
os.environ["OPENAI_API_KEY"] = "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"
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# OpenWeatherMap API Key
weather_api_key = "여기에_네_API_KEY_넣어"

# 실제 날씨 가져오기 함수
def get_weather(region_kor):
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    korean_to_english = {
        "서울": "Seoul",
        "경기": "Suwon",
        "인천": "Incheon",
        "부산": "Busan",
        "대구": "Daegu",
        "광주": "Gwangju",
        "대전": "Daejeon",
        "울산": "Ulsan",
        "기타": "Seoul"
    }

    city = korean_to_english.get(region_kor, "Seoul")

    params = {
        "q": city,
        "appid": weather_api_key,
        "units": "metric",
        "lang": "kr"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather_description}, {temp:.1f}°C"
    else:
        return "날씨 정보를 가져올 수 없습니다."

# Streamlit 앱 타이틀
st.title("G코디")
st.markdown("""
<div style='padding: 24px; background: linear-gradient(135deg, #D7E5FF, #E0CCFF); border-radius: 12px;'>
매일 아침 '오늘 뭐 입지?' 고민 끝!<br>  
G코디가 당신의 기분과 스케줄, 날씨까지 고려해서<br>  
오늘 가장 어울리는 출근룩을 추천해드릴게요.
</div>
""", unsafe_allow_html=True)

# --- 입력 파트 ---
st.header("기본 정보를 입력해주세요.")

st.subheader("나의 정보")
st.selectbox("성별을 선택하세요", ["남성", "여성"], key="gender")
st.selectbox("나이대를 선택하세요", ["20대", "30대", "40대", "50대 이상"], key="age_group")
st.selectbox("지역을 선택하세요", ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산", "기타"], key="region")

st.subheader("오늘의 상황")
st.selectbox("회사 분위기는 어떤가요?", ["비즈니스 포멀", "비즈니스 캐주얼", "세미 캐주얼", "완전 프리한 분위기"], key="company_style")
st.selectbox("오늘 스케줄은 어떤가요?", ["외부 미팅", "사무실 근무만", "근무 이후 친구와 약속", "회식 예정"], key="today_schedule")
st.selectbox("오늘 기분은 어떤가요?", ["편하고 싶다", "자신감 넘치게 보이고 싶다", "깔끔하고 단정하게", "발랄하고 상큼하게"], key="today_mood")
st.selectbox("좋아하는 스타일은?", ["심플/미니멀", "스트릿/캐주얼", "러블리/로맨틱", "포멀/클래식"], key="favorite_style")

# 하루 기온 예시 데이터
temp_values = {
    "서울": [15, 18, 20, 21, 19, 17],
    "경기": [14, 17, 19, 20, 18, 16],
    "인천": [13, 16, 18, 19, 17, 15],
    "부산": [17, 20, 22, 23, 22, 20],
    "대구": [16, 19, 23, 24, 22, 20],
    "광주": [15, 17, 19, 20, 18, 16],
    "대전": [14, 17, 19, 20, 18, 16],
    "울산": [16, 19, 21, 22, 21, 19],
    "기타": [15, 18, 20, 21, 19, 17]
}

# --- 함수 정의 ---
def generate_codi():
    prompt = f"""
    당신은 뛰어난 패션 스타일리스트입니다.

    사용자의 오늘 정보를 참고하여 출근 코디를 추천해주세요:
    - 성별: {st.session_state.gender}
    - 나이대: {st.session_state.age_group}
    - 지역: {st.session_state.region}
    - 현재 날씨: {st.session_state.today_weather}
    - 회사 분위기: {st.session_state.company_style}
    - 오늘 스케줄: {st.session_state.today_schedule}
    - 오늘 기분: {st.session_state.today_mood}
    - 좋아하는 스타일: {st.session_state.favorite_style}

    상의, 하의, 아우터(필요시), 신발, 액세서리까지 포함하여 구체적으로 작성해주세요.
    """
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": "당신은 출근룩 스타일링 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.output_text

def generate_image(codi_description):
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Office outfit realistic, {codi_description}",
        n=1,
    )
    return response.data[0].url

def generate_message():
    prompt = f"{st.session_state.tone}의 말투로, 사용자의 오늘 스케줄({st.session_state.today_schedule})과 기분({st.session_state.today_mood})을 고려하여 1~2줄의 짧은 응원의 한마디를 작성해줘. 자연스럽고 따뜻하고 위로가 되는 톤으로 작성해줘."
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": "당신은 사용자에게 응원의 한마디를 따뜻하게 전달하는 역할입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.output_text

# --- 코디 추천 버튼 ---
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #2C12EF;
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-size: 18px;
    }
    div.stButton > button:first-child:hover,
    div.stButton > button:first-child:focus,
    div.stButton > button:first-child:active {
        background-color: #3437FF;
        color: #FFFFFF !important;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("👗 오늘의 코디 추천받기"):
    today_weather = get_weather(st.session_state.region)
    st.session_state.today_weather = today_weather

    st.session_state.codi = generate_codi()
    st.session_state.today_temp = temp_values.get(st.session_state.region, [15, 18, 20, 21, 19, 17])
    st.session_state.image_url = generate_image(st.session_state.codi)

# --- 추천 결과 표시 ---
if "codi" in st.session_state:
    st.subheader("🌡️ 오늘의 기온 정보")
    min_temp = min(st.session_state.today_temp)
    max_temp = max(st.session_state.today_temp)
    st.markdown(f"**최저 기온**: {min_temp}°C  ")
    st.markdown(f"**최고 기온**: {max_temp}°C")
    
    st.subheader("👔 추천받은 출근룩")
    codi_text = st.session_state.codi
    if "#" in codi_text:
        codi_main, codi_tags = codi_text.rsplit("#", 1)
        st.write(codi_main.strip())
        st.subheader("🔖 오늘의 키워드")
        st.write("#" + codi_tags.strip())
    else:
        st.write(codi_text)

    st.subheader("🎨 코디 이미지 미리보기")
    st.image(st.session_state.image_url)

# --- 응원 메시지 파트 ---
st.subheader("💬 응원의 한마디 받기")
st.selectbox("응원의 톤을 선택하세요", ["엄마", "애인", "로봇", "친구"], key="tone")

if st.button("💌 응원 한마디 추천받기"):
    st.session_state.message = generate_message()

if "message" in st.session_state:
    st.markdown(f"_{st.session_state.message}_")

# --- 다른 코디 추천 버튼 ---
if st.button("🔄 다른 코디 추천받기"):
    st.session_state.codi = generate_codi()
    st.session_state.image_url = generate_image(st.session_state.codi)
    st.experimental_rerun()
