import streamlit as st
from utils import set_bg_hack, show_footer, hide_header

st.set_page_config(
    page_title="한국금융투자기술",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

hide_header()
set_bg_hack("background.jpg")

# 사이드바 강제 숨김
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# 네비게이션 스타일 (흰색 글씨)
st.markdown(
    """
    <style>
    [data-testid="stPageLink-NavLink"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px 10px !important;
        margin: 0 !important;
        text-decoration: none !important;
    }
    [data-testid="stPageLink-NavLink"] p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        padding: 5px 10px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    [data-testid="stPageLink-NavLink"]:hover p {
        color: #FFD700 !important;
        font-weight: 900 !important;
        transform: scale(1.05);
        text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.6);
        transition: all 0.2s ease-in-out;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 상단 네비게이션
col_nav1, col_nav2, col_empty = st.columns([0.2, 0.2, 0.6])
with col_nav1:
    st.page_link("pages/Company.py", label="Company", use_container_width=True)
with col_nav2:
    st.page_link("pages/Service.py", label="Service", use_container_width=True)

# 메인 타이틀 영역
st.markdown(
    """
    <div style="text-align: center; margin-top: 150px; margin-bottom: 30px;">
        <!-- 메인 슬로건 -->
        <h1 style="
            color: white;
            font-size: 5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            font-weight: 800;
            margin-bottom: 10px;
        ">
            Bridge the Gap
        </h1>
        <!-- 영문 서브 슬로건 -->
        <h2 style="
            color: #f5f5f5;
            font-size: 2.6rem;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
            font-weight: 500;
            margin-top: 0;
            margin-bottom: 16px;
        ">
            between possibility and reality
        </h2>
        <!-- 한글 메시지 -->
        <h3 style="
            color: #eeeeee;
            font-size: 1.9rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 4px;
        ">
            가능성과 현실의 간극을 메우는,
        </h3>
        <h3 style="
            color: #ffffff;
            font-size: 1.9rem;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
            font-weight: 700;
            margin-top: 0;
        ">
            당신의 평생 금융파트너, 한국금융투자기술
        </h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# 페이지 하단으로 footer를 내리기 위한 여유 공간(스페이서)
st.markdown(
    "<div style='height: 40vh;'></div>",
    unsafe_allow_html=True,
)

# 항상 맨 마지막에 호출
show_footer()









