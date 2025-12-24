import streamlit as st
from datetime import datetime
from services.github_entitlements import fetch_entitlements, update_entitlements, find_user

def require_admin():
    a = st.session_state.get("auth")
    if not a:
        st.warning("로그인이 필요합니다.")
        st.stop()
    if a.get("role") != "admin":
        st.error("관리자만 접근 가능합니다.")
        st.stop()

def admin_page():
    require_admin()
    st.title("🛠️ 관리자: 사용자 권한/구독 관리")

    owner = st.secrets["GITHUB_OWNER"]
    repo = st.secrets["GITHUB_REPO"]
    path = st.secrets["GITHUB_ENTITLEMENTS_PATH"]
    token = st.secrets["GITHUB_TOKEN"]

    gf = fetch_entitlements(owner, repo, path, token)
    ent = gf.content_json

    users = ent.get("users", [])
    st.caption(f"현재 사용자 수: {len(users)}명")

    emails = [u.get("email","") for u in users]
    sel = st.selectbox("사용자 선택", ["(신규 추가)"] + emails)

    if sel == "(신규 추가)":
        email = st.text_input("이메일(신규)", placeholder="new@example.com")
        role = st.selectbox("role", ["user", "admin"], index=0)
        plan = st.selectbox("plan", ["basic", "pro"], index=1)
        active = st.checkbox("active", value=True)
        expires_at = st.date_input("expires_at")
        if st.button("➕ 추가 저장"):
            if not email.strip():
                st.error("이메일이 필요합니다.")
                st.stop()
            if find_user(ent, email):
                st.error("이미 존재하는 이메일입니다.")
                st.stop()
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            ent["users"].append({
                "id": f"u-{len(users)+1:04d}",
                "email": email.strip(),
                "role": role,
                "plan": plan,
                "active": bool(active),
                "expires_at": expires_at.isoformat(),
                "created_at": now,
                "updated_at": now,
            })
            new_sha = update_entitlements(owner, repo, path, token, ent, gf.sha)
            st.success(f"저장 완료 (sha: {new_sha[:7]}...)")
            st.rerun()
    else:
        u = find_user(ent, sel)
        st.subheader(sel)
        role = st.selectbox("role", ["user", "admin"], index=0 if u.get("role","user")=="user" else 1)
        plan = st.selectbox("plan", ["basic", "pro"], index=0 if u.get("plan","basic")=="basic" else 1)
        active = st.checkbox("active", value=bool(u.get("active", False)))
        expires_at = st.text_input("expires_at(YYYY-MM-DD)", value=u.get("expires_at",""))

        if st.button("💾 변경 저장"):
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            u["role"] = role
            u["plan"] = plan
            u["active"] = bool(active)
            u["expires_at"] = expires_at.strip()
            u["updated_at"] = now

            new_sha = update_entitlements(owner, repo, path, token, ent, gf.sha)
            st.success(f"저장 완료 (sha: {new_sha[:7]}...)")
            st.rerun()

admin_page()
