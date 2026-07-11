#!/usr/bin/env python3
"""
Simple SVG updater for GitHub profile
Updates commit count, stars, repos, followers (LOC from count-lines workflow)
"""
import requests
import os
from lxml import etree

HEADERS = {'authorization': 'token ' + os.environ['ACCESS_TOKEN']}
USER_NAME = os.environ['USER_NAME']

def query_github(query, variables):
    """Execute GraphQL query"""
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': variables},
        headers=HEADERS
    )
    if response.status_code == 200:
        return response.json()
    raise Exception(f'Query failed: {response.status_code} {response.text}')

def get_stats():
    """Get all GitHub stats in one query"""
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
                    stargazers {
                        totalCount
                    }
                }
            }
            followers {
                totalCount
            }
            contributionsCollection {
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }'''
    
    data = query_github(query, {'login': USER_NAME})
    user = data['data']['user']
    
    # Calculate total stars
    stars = sum(repo['stargazers']['totalCount'] for repo in user['ownedRepos']['nodes'])
    
    return {
        'commits': user['contributionsCollection']['contributionCalendar']['totalContributions'],
        'stars': stars,
        'repos': user['repositories']['totalCount'],
        'contrib_repos': user['contributedRepos']['totalCount'],
        'followers': user['followers']['totalCount']
    }

def update_svg(filename, stats):
    """Update SVG file with stats"""
    tree = etree.parse(filename)
    root = tree.getroot()
    
    def update_element(element_id, value, dots_len):
        """Update text and dots for justification"""
        # Update value
        element = root.find(f".//*[@id='{element_id}']")
        if element is not None:
            value_str = f"{value:,}"
            element.text = value_str
            
            # Update dots
            dots_element = root.find(f".//*[@id='{element_id}_dots']")
            if dots_element is not None:
                just_len = max(0, dots_len - len(value_str))
                if just_len <= 2:
                    dot_map = {0: '', 1: ' ', 2: '. '}
                    dots_element.text = dot_map[just_len]
                else:
                    dots_element.text = ' ' + ('.' * just_len) + ' '
    
    update_element('commit_data', stats['commits'], 7)
    update_element('star_data', stats['stars'], 11)
    update_element('repo_data', stats['repos'], 9)
    update_element('contrib_data', stats['contrib_repos'], 10)
    update_element('follower_data', stats['followers'], 12)
    
    # LOC remains 0 (updated by count-lines workflow via README badges)
    update_element('loc_data', 0, 13)
    update_element('loc_add', 0, 12)
    update_element('loc_del', 0, 11)
    
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f'✅ Updated {filename}')

if __name__ == '__main__':
    print('Fetching GitHub stats...')
    stats = get_stats()
    
    print(f"""
Stats fetched:
  Commits: {stats['commits']:,}
  Stars: {stats['stars']:,}
  Repos: {stats['repos']:,}
  Contributed Repos: {stats['contrib_repos']:,}
  Followers: {stats['followers']:,}
""")
    
    update_svg('dark_mode.svg', stats)
    update_svg('light_mode.svg', stats)
    
    print('✅ All done!')
