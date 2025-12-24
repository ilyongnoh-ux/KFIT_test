import streamlit as st
from services.github_entitlements import fetch_entitlements, find_user

def login_page():
    st.title("🔐 로그인")
    st.caption("테스트(MVP): 이메일만으로 권한DB에 등록된 사용자 확인")

    email = st.text_input("이메일", placeholder="user@example.com")

    if st.button("로그인"):
        owner = st.secrets["GITHUB_OWNER"]
        repo = st.secrets["GITHUB_REPO"]
        path = st.secrets["GITHUB_ENTITLEMENTS_PATH"]
        token = st.secrets["GITHUB_TOKEN"]

        gf = fetch_entitlements(owner, repo, path, token)
        u = find_user(gf.content_json, email)

        if not u:
            st.error("등록되지 않은 사용자입니다. 관리자에게 문의하세요.")
            return

        st.session_state["auth"] = {
            "email": u["email"],
            "role": u.get("role", "user"),
        }
        st.success("로그인 완료")
        st.rerun()

login_page()
