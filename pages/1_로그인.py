import streamlit as st
import requests

def gh_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def debug_github():
    st.warning("🛠️ GitHub 연결 진단 모드")
    owner = st.secrets.get("GITHUB_OWNER", "")
    repo  = st.secrets.get("GITHUB_REPO", "")
    path  = st.secrets.get("GITHUB_ENTITLEMENTS_PATH", "")
    token = st.secrets.get("GITHUB_TOKEN", "")

    st.write({"GITHUB_OWNER": owner, "GITHUB_REPO": repo, "PATH": path, "TOKEN_LEN": len(token)})

    # 1) 토큰 자체 유효성 (/user)
    r1 = requests.get("https://api.github.com/user", headers=gh_headers(token), timeout=15)
    st.write("1) /user status:", r1.status_code)
    if r1.status_code != 200:
        st.write(r1.json() if "application/json" in r1.headers.get("content-type","") else r1.text[:300])
        st.stop()

    # 2) repo 접근 (/repos/OWNER/REPO)
    r2 = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=gh_headers(token), timeout=15)
    st.write("2) /repos/<owner>/<repo> status:", r2.status_code)
    if r2.status_code != 200:
        st.write(r2.json() if "application/json" in r2.headers.get("content-type","") else r2.text[:300])
        st.stop()

    # 3) contents 접근 (/contents/PATH)
    r3 = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), timeout=15)
    st.write("3) /contents/<path> status:", r3.status_code)
    st.write(r3.json() if "application/json" in r3.headers.get("content-type","") else r3.text[:300])
    st.stop()

# ✅ 진단 버튼 (누르면 바로 원인 출력)
if st.button("🔎 GitHub 연결 진단 실행"):
    debug_github()

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
import requests

if st.button("🔎 GitHub repo 연결 테스트"):
    owner = st.secrets["GITHUB_OWNER"]
    repo = st.secrets["GITHUB_REPO"]
    token = st.secrets["GITHUB_TOKEN"]

    url = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }, timeout=15)

    st.write("status:", r.status_code)
    try:
        st.write(r.json())
    except Exception:
        st.write(r.text[:300])
    st.stop()

login_page()
