#!/usr/bin/env python3
"""
Auto-updates the Organizations section in README.md.

- Fetches the authenticated user's public org memberships via GitHub API.
- Falls back to a hard-coded list if an org isn't returned by the API
  (e.g. private membership or the token lacks org:read scope).
- Each org is displayed as its real avatar linked to its GitHub page.
"""

import os
import re
import requests

HEADERS = {
    "Authorization": f"token {os.environ['ACCESS_TOKEN']}",
    "Accept": "application/vnd.github+json",
}
USER_NAME = os.environ["USER_NAME"]

# Hard-coded avatar URLs for known orgs (avoids extra API calls)
# Key: org login lowercase, Value: avatar URL
ORG_AVATARS: dict[str, str] = {
    "hackclub":      "https://avatars.githubusercontent.com/u/5633654?s=64&v=4",
    "techsyndicate": "https://avatars.githubusercontent.com/u/50449253?s=64&v=4",
    "robonexxus":    "https://avatars.githubusercontent.com/u/260877624?s=64&v=4",
    "1st-commit":    "https://avatars.githubusercontent.com/u/295718725?s=64&v=4",
}

# Orgs that must always appear even if the API doesn't return them
FALLBACK_ORGS = ["hackclub", "techsyndicate", "RoboNexxus", "1st-Commit"]


def get_user_orgs() -> list[dict]:
    """Return list of org dicts (login + avatar_url) the user belongs to."""
    url = f"https://api.github.com/users/{USER_NAME}/orgs"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        return resp.json()  # each item has 'login' and 'avatar_url'
    print(f"⚠️  Could not fetch orgs ({resp.status_code}), using fallback list.")
    return []


def get_avatar_url(login: str, api_avatar: str | None = None) -> str:
    """Return avatar URL: prefer cached map, then API value, then generic."""
    cached = ORG_AVATARS.get(login.lower())
    if cached:
        return cached
    if api_avatar:
        return api_avatar
    # Last resort: GitHub's avatar endpoint by org name
    return f"https://github.com/{login}.png?size=64"


def badge_html(login: str, avatar_url: str) -> str:
    """Build the HTML anchor + img for one org."""
    return (
        f'<a href="https://github.com/{login}" title="{login}">\n'
        f'  <img src="{avatar_url}" width="48" height="48" '
        f'style="border-radius:50%" alt="{login}" />\n'
        f'</a>'
    )


def build_badge_block(orgs: list[dict]) -> str:
    parts = []
    for org in orgs:
        login = org["login"]
        avatar = get_avatar_url(login, org.get("avatar_url"))
        parts.append(badge_html(login, avatar))
    badges = "\n&nbsp;&nbsp;\n".join(parts)
    return (
        "<!-- ORG_BADGES_START -->\n"
        + badges
        + "\n<!-- ORG_BADGES_END -->"
    )


def update_readme(new_block: str) -> None:
    with open("README.md", "r") as f:
        content = f.read()

    pattern = r"<!-- ORG_BADGES_START -->.*?<!-- ORG_BADGES_END -->"
    updated = re.sub(pattern, new_block, content, flags=re.DOTALL)

    if updated == content:
        print("ℹ️  No changes to README.")
        return

    with open("README.md", "w") as f:
        f.write(updated)
    print("✅ README updated with fresh org avatars.")


if __name__ == "__main__":
    api_orgs = get_user_orgs()

    # Build a map of login -> full org dict from API results
    seen: dict[str, dict] = {o["login"].lower(): o for o in api_orgs}

    # Append fallbacks not already present (using cached avatar URLs)
    for login in FALLBACK_ORGS:
        key = login.lower()
        if key not in seen:
            seen[key] = {"login": login, "avatar_url": get_avatar_url(login)}

    merged = list(seen.values())
    print(f"🏢 Orgs to display: {[o['login'] for o in merged]}")

    block = build_badge_block(merged)
    update_readme(block)
