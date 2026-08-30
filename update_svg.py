#!/usr/bin/env python3
"""
SVG updater for GitHub profile — updates GitHub stats (commits, stars, repos, followers)
LOC, streak, and language rows are handled by count-lines.yml workflow.
"""
import requests
import os
from lxml import etree

HEADERS = {'authorization': 'token ' + os.environ['ACCESS_TOKEN']}
USER_NAME = os.environ['USER_NAME']
DISCORD_USER_ID = '1147221423815938179'
LANYARD_KV_KEY = os.environ.get('DC', '')  # KV API key stored as repo secret


STATUS_COLORS = {
    'online':  '#23d18b',
    'idle':    '#f0b232',
    'dnd':     '#f04747',
    'offline': '#747f8d',
}
STATUS_LABELS = {
    'online':  'Online',
    'idle':    'Idle',
    'dnd':     'Do Not Disturb',
    'offline': 'Offline',
}


def get_discord_presence():
    """Fetch live Discord presence via Lanyard REST API."""
    headers = {}
    if LANYARD_KV_KEY:
        headers['Authorization'] = LANYARD_KV_KEY
    try:
        resp = requests.get(
            f'https://api.lanyard.rest/v1/users/{DISCORD_USER_ID}',
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            raise Exception(f'Lanyard returned {resp.status_code}')
        payload = resp.json()
        if not payload.get('success'):
            raise Exception('Lanyard success=false')
        data = payload['data']
    except Exception as e:
        print(f'⚠️  Lanyard fetch failed: {e}')
        return {
            'status':       'offline',
            'status_color': STATUS_COLORS['offline'],
            'status_label': STATUS_LABELS['offline'],
            'activity':     '—',
            'spotify':      '—',
        }

    raw_status = data.get('discord_status', 'offline')
    status_color = STATUS_COLORS.get(raw_status, STATUS_COLORS['offline'])
    status_label = STATUS_LABELS.get(raw_status, raw_status.capitalize())

    # ── Spotify ──────────────────────────────────────────────────────────────
    spotify_text = '—'
    if data.get('listening_to_spotify') and data.get('spotify'):
        sp = data['spotify']
        song   = sp.get('song', '')
        artist = sp.get('artist', '')
        if song and artist:
            spotify_text = f'{song} — {artist}'
        elif song:
            spotify_text = song

    # ── Activity ─────────────────────────────────────────────────────────────
    # Priority: non-custom activities first, then custom status emoji+text
    activity_text = '—'
    activities = data.get('activities', [])
    for act in activities:
        act_type = act.get('type', -1)
        if act_type == 4:  # Custom Status
            emoji = (act.get('emoji') or {}).get('name', '')
            state = act.get('state', '')
            parts = [p for p in [emoji, state] if p]
            if parts:
                activity_text = ' '.join(parts)
        elif act_type in (0, 1, 2, 3):  # Playing / Streaming / Listening / Watching
            act_name = act.get('name', '')
            details  = act.get('details', '')
            if act_name and details:
                activity_text = f'{act_name}: {details}'
            elif act_name:
                activity_text = act_name
            break  # prefer the first non-custom activity

    return {
        'status':       raw_status,
        'status_color': status_color,
        'status_label': status_label,
        'activity':     activity_text,
        'spotify':      spotify_text,
    }


def query_github(query, variables):
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': variables},
        headers=HEADERS
    )
    if response.status_code == 200:
        return response.json()
    raise Exception(f'Query failed: {response.status_code} {response.text}')


def get_stats():
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 1, ownerAffiliations: OWNER) {
                totalCount
            }
            contributedRepos: repositories(first: 1, ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]) {
                totalCount
            }
            ownedRepos: repositories(first: 100, ownerAffiliations: OWNER) {
                nodes {
                    stargazers { totalCount }
                }
            }
            followers { totalCount }
        }
    }'''
    data = query_github(query, {'login': USER_NAME})
    user = data['data']['user']
    stars = sum(repo['stargazers']['totalCount'] for repo in user['ownedRepos']['nodes'])

    try:
        search_response = requests.get(
            f'https://api.github.com/search/commits?q=author:{USER_NAME}',
            headers={**HEADERS, 'Accept': 'application/vnd.github.cloak-preview'}
        )
        if search_response.status_code == 200:
            total_commits = search_response.json()['total_count']
        else:
            raise Exception('search fallback')
    except Exception:
        contrib_query = '''
        query($login: String!) {
            user(login: $login) {
                contributionsCollection {
                    contributionCalendar { totalContributions }
                }
            }
        }'''
        contrib_data = query_github(contrib_query, {'login': USER_NAME})
        total_commits = contrib_data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']

    return {
        'commits':       total_commits,
        'stars':         stars,
        'repos':         user['repositories']['totalCount'],
        'contrib_repos': user['contributedRepos']['totalCount'],
        'followers':     user['followers']['totalCount'],
    }


def _truncate(text, max_len):
    """Truncate long strings so they don't overflow the SVG width."""
    return text if len(text) <= max_len else text[:max_len - 1] + '…'


def find_and_set(root, element_id, text):
    el = root.find(f".//*[@id='{element_id}']")
    if el is not None:
        el.text = str(text)


def update_svg(filename, stats):
    tree = etree.parse(filename)
    root = tree.getroot()

    def justified(element_id, value, dots_len):
        value_str = f"{value:,}" if isinstance(value, int) else str(value)
        find_and_set(root, element_id, value_str)
        just_len = max(0, dots_len - len(value_str))
        dot_map = {0: '', 1: ' ', 2: '. '}
        dot_str = dot_map[just_len] if just_len <= 2 else ' ' + ('.' * just_len) + ' '
        find_and_set(root, f"{element_id}_dots", dot_str)

    justified('commit_data',   stats['commits'],       7)
    justified('star_data',     stats['stars'],          11)
    justified('repo_data',     stats['repos'],          9)
    justified('contrib_data',  stats['contrib_repos'],  10)
    justified('follower_data', stats['followers'],      12)

    # LOC, streak, languages are written by count-lines.yml — skip here
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f'✅ Updated {filename}')


if __name__ == '__main__':
    print('Fetching GitHub stats...')
    stats = get_stats()
    print(f"""
  Commits:         {stats['commits']:,}
  Stars:           {stats['stars']:,}
  Repos:           {stats['repos']:,}
  Contributed:     {stats['contrib_repos']:,}
  Followers:       {stats['followers']:,}
""")

    update_svg('dark_mode.svg', stats)
    update_svg('light_mode.svg', stats)
    print('✅ All done!')
