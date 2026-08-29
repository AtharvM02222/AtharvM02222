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
