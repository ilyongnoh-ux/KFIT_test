# services/github_entitlements.py
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import requests


@dataclass
class GithubFile:
    content_json: Dict[str, Any]
    sha: str


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_entitlements(owner: str, repo: str, path: str, token: str, ref: Optional[str] = None) -> GithubFile:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    if ref:
        url += f"?ref={ref}"

    r = requests.get(url, headers=_headers(token), timeout=15)
    if r.status_code == 404:
        raise RuntimeError("GitHub contents 404: OWNER/REPO/PATH 또는 토큰 권한을 확인하세요.")
    r.raise_for_status()

    data = r.json()
    raw = base64.b64decode(data["content"]).decode("utf-8")
    return GithubFile(content_json=json.loads(raw), sha=data["sha"])


def update_entitlements(owner: str, repo: str, path: str, token: str, new_json: Dict[str, Any], sha: str) -> str:
    """
    GitHub 파일 업데이트: sha 기반이라 동시 저장 충돌(409)이 날 수 있음.
    409이면 fetch 다시 하고 sha 최신으로 재시도해야 함.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    body = {
        "message": f"update entitlements {datetime.now().isoformat(timespec='seconds')}",
        "content": base64.b64encode(json.dumps(new_json, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8"),
        "sha": sha,
    }

    r = requests.put(url, headers=_headers(token), json=body, timeout=20)
    if r.status_code == 409:
        raise RuntimeError("GitHub 409 Conflict: 누군가 먼저 수정했거나 sha가 최신이 아닙니다. 다시 불러와서 저장하세요.")
    r.raise_for_status()
    return r.json()["content"]["sha"]


def find_user(entitlements: Dict[str, Any], email: str) -> Optional[Dict[str, Any]]:
    email_l = (email or "").strip().lower()
    for u in entitlements.get("users", []):
        if (u.get("email") or "").strip().lower() == email_l:
            return u
    return None


def is_entitled(user: Dict[str, Any]) -> bool:
    if not user:
        return False
    if not user.get("active", False):
        return False
    expires_at = user.get("expires_at")
    if expires_at:
        try:
            exp = date.fromisoformat(expires_at)
            if date.today() > exp:
                return False
        except ValueError:
            # 날짜 형식이 깨졌으면 보수적으로 차단
            return False
    return True
