import streamlit as st
from services.github_entitlements import fetch_entitlements, find_user, is_entitled

def require_login():
    if "auth" not in st.session_state:
        st.warning("로그인이 필요합니다.")
        st.stop()

def download_page():
    require_login()
    st.title("⬇️ KFITER 다운로드")

    email = st.session_state["auth"]["email"]

    owner = st.secrets["GITHUB_OWNER"]
    repo = st.secrets["GITHUB_REPO"]
    path = st.secrets["GITHUB_ENTITLEMENTS_PATH"]
    token = st.secrets["GITHUB_TOKEN"]

    gf = fetch_entitlements(owner, repo, path, token)
    u = find_user(gf.content_json, email)

    if not u or not is_entitled(u):
        st.error("구독이 비활성/만료 상태입니다. 결제 또는 관리자 승인 후 이용 가능합니다.")
        st.stop()

    st.success(f"구독 유효: {u.get('plan','')}, 만료일: {u.get('expires_at','')}")
    d_owner = st.secrets["DOWNLOAD_OWNER"]
    d_repo = st.secrets["DOWNLOAD_REPO"]
    asset = st.secrets["DOWNLOAD_ASSET_NAME"]

    url = f"https://github.com/{d_owner}/{d_repo}/releases/latest/download/{asset}"
    st.link_button("✅ 최신 버전 EXE 다운로드", url)

download_page()
