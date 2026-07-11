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
    """Get all GitHub stats"""
    # Main stats query
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
        }
    }'''
    
    data = query_github(query, {'login': USER_NAME})
    user = data['data']['user']
    
    # Calculate total stars
    stars = sum(repo['stargazers']['totalCount'] for repo in user['ownedRepos']['nodes'])
    
    # Get total commits using the search API (more accurate for all-time)
    # Note: This only counts commits to default branches
    try:
        search_response = requests.get(
            f'https://api.github.com/search/commits?q=author:{USER_NAME}',
            headers={**HEADERS, 'Accept': 'application/vnd.github.cloak-preview'}
        )
        if search_response.status_code == 200:
            total_commits = search_response.json()['total_count']
        else:
            # Fallback: Use contribution calendar (last year only)
            contrib_query = '''
            query($login: String!) {
                user(login: $login) {
                    contributionsCollection {
                        contributionCalendar {
                            totalContributions
                        }
                    }
                }
            }'''
            contrib_data = query_github(contrib_query, {'login': USER_NAME})
            total_commits = contrib_data['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions']
    except:
        total_commits = 0
    
    return {
        'commits': total_commits,
        'stars': stars,
        'repos': user['repositories']['totalCount'],
        'contrib_repos': user['contributedRepos']['totalCount'],
        'followers': user['followers']['totalCount']
    }

def get_loc_from_readme():
    """Extract LOC stats from README badges"""
    try:
        with open('README.md', 'r') as f:
            readme = f.read()
        
        import re
        # Extract from badges like: Total_Lines-365017-00d9ff
        total_match = re.search(r'Total_Lines-(\d+)-', readme)
        added_match = re.search(r'Lines_Added-(\d+)-', readme)
        changed_match = re.search(r'Lines_Changed-(\d+)-', readme)
        
        if total_match and added_match and changed_match:
            total = int(total_match.group(1))
            added = int(added_match.group(1))
            changed = int(changed_match.group(1))
            deleted = changed - added
            return {
                'total': total,
                'added': added,
                'deleted': deleted
            }
    except:
        pass
    
    return {'total': 0, 'added': 0, 'deleted': 0}

def update_svg(filename, stats, loc_stats):
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
    
    # Update LOC from count-lines workflow
    update_element('loc_data', loc_stats['total'], 13)
    update_element('loc_add', loc_stats['added'], 12)
    update_element('loc_del', loc_stats['deleted'], 11)
    
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
    
    print('Extracting LOC from README...')
    loc_stats = get_loc_from_readme()
    print(f"""
LOC Stats:
  Total: {loc_stats['total']:,}
  Added: {loc_stats['added']:,}
  Deleted: {loc_stats['deleted']:,}
""")
    
    update_svg('dark_mode.svg', stats, loc_stats)
    update_svg('light_mode.svg', stats, loc_stats)
    
    print('✅ All done!')
