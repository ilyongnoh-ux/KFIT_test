import streamlit as st
from utils import show_footer, hide_header
from apps import Wannabe_Golf, Wannabe_Tax, Wannabe_Life_Plan

st.set_page_config(page_title="Services - Kfit", page_icon="🚀", layout="wide")

hide_header()

# [CSS] 사이드바 숨김 & 스타일링 (기존 유지)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }

    [data-testid="stPageLink-NavLink"] { 
        border: none !important; 
        background: transparent !important; 
        padding: 0px !important; 
    }

    /* 기본 상태: 약간 작게 + 여유 패딩 + 부드러운 전환 */
    [data-testid="stPageLink-NavLink"] p { 
        font-size: 1.2rem;            /* 기본 크기 */
        font-weight: 600; 
        color: #444; 
        padding: 4px 6px;             /* 박스를 조금 크게 */
        margin: 0; 
        transition: all 0.15s ease-in-out;  /* 부드럽게 커지도록 */
    }

    /* 호버 상태: 글자 크기만 키우기 (scale 대신) */
    [data-testid="stPageLink-NavLink"]:hover p { 
        color: #1E3A8A; 
        font-weight: 900; 
        /*font-size: 1.3rem;             여기서 살짝만 키움 */
        /* transform: scale(1.05);  ← 이 줄은 제거 */
    }

    .block-container { padding-top: 1rem !important; }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# [NEW] URL 꼬리표(Query Params) 감지 로직
# ==============================================================================
# 1. URL에서 '?tool=xxx' 값을 가져옵니다.
query_params = st.query_params
target_tool = query_params.get("tool", "life")  # 없으면 기본값 'life'

# 2. 꼬리표와 셀렉트박스 순서 매핑
tool_options = ["Wannabe Golf", "Wannabe Tax", "Wannabe Life Plan"]
tool_map = {
    "golf": 0,  # Wannabe Golf
    "tax": 1,   # Wannabe Tax
    "life": 2   # Wannabe Life Plan
}

# 3. 선택해야 할 인덱스 찾기 (오타나 엉뚱한 값이면 0번 골프)
default_idx = tool_map.get(str(target_tool).lower(), 0)

# ==============================================================================
# 화면 분할 및 실행
# ==============================================================================
left_col, right_col = st.columns([3, 7], gap="medium")

with left_col:
    st.write("") 
    c1, c2 = st.columns(2)
    with c1: st.page_link("Home.py", label="Home", use_container_width=True)
    with c2: st.page_link("pages/Company.py", label="Company", use_container_width=True)
    
    st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin: 0 0 10px 0; font-size: 1.2rem;'>Solution Menu</h3>", unsafe_allow_html=True)
    
    # [수정] index 파라미터에 위에서 계산한 default_idx를 넣어줍니다.
    selected_app = st.selectbox(
        "솔루션 선택", 
        tool_options, 
        index=default_idx,  # 여기가 핵심! URL에 따라 기본 선택이 바뀜
        label_visibility="collapsed"
    )
    st.markdown("---")

with right_col:
    # 선택된 앱 실행 (왼쪽 컬럼 넘겨주기)
    if selected_app == "Wannabe Golf":
        Wannabe_Golf.app(left_col)
    elif selected_app == "Wannabe Tax":
        Wannabe_Tax.app(left_col)
    elif selected_app == "Wannabe Life Plan":
        Wannabe_Life_Plan.app(left_col)

show_footer()






