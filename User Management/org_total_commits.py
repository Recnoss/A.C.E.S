import csv
import os
import time
from collections import defaultdict
from datetime import datetime

import requests
from joblib import Memory

# Constants
ORG_NAME = "statisticsnorway"
TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
}

# Create a memory object for caching
cachedir = 'CACHE'
memory = Memory(cachedir, verbose=0)

if TOKEN is None:
    raise ValueError("Please set the 'GITHUB_TOKEN' environment variable.")

def handle_rate_limit(response):
    """Handle GitHub's rate limit by sleeping when the limit is exceeded."""
    if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
        reset_time = int(response.headers['X-RateLimit-Reset'])
        sleep_time = max(0, reset_time - int(time.time()))
        print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)

@memory.cache
def get_repos(org_name):
    """Fetch all non-fork, non-archived repositories of the organization."""
    page = 1
    repos = []
    while True:
        print(f"Fetching page {page} of repositories...")
        url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch repos: {response.text}")
            break
        handle_rate_limit(response)
        current_page_repos = response.json()
        if not current_page_repos:
            break
        repos += [repo['name'] for repo in current_page_repos if repo['full_name'].startswith(org_name + "/") and not repo['fork'] and not repo['archived']]
        page += 1
    return repos

@memory.cache
def get_contributors(org_name, repo_name):
    """Fetch all contributors of the specific repository."""
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contributors"
    all_contributors = []
    repos = get_repos(org_name)
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch contributors for {repo_name}: {response.text}")
            break
        handle_rate_limit(response)
        contributors = response.json()
        for contributor in contributors:
            if contributor['contributions'] > 0 and contributor['login'] not in repos:
                all_contributors.append(contributor)
        url = response.links.get('next', {}).get('url')

    return all_contributors

@memory.cache
def get_user_real_name(username):
    """Fetch the real name of the user. If not available, return the username."""
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch user information for {username}: {response.text}")
        return username
    user = response.json()
    return user['name'] if user.get('name') else username

def save_contributions_to_file(org_name, contributions, most_contributed_repos, repos):
    """Save the contributions data to a CSV file."""
    filename = f"{org_name} - Github Contributions - {datetime.now().strftime('%Y-%m')}.csv"
    with open(filename, 'w', newline='', encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Rank", "Name", "Commits", "Most Contributed Repo"])
        for rank, (contributor, contribution) in enumerate(contributions, start=1):
            if contributor not in repos:
                writer.writerow([
                    rank,
                    get_user_real_name(contributor),
                    contribution,
                    most_contributed_repos[contributor],
                ])
    print(f"Contribution data saved to {filename}")

def rank_contributors(org_name):
    """Rank contributors based on their contributions."""
    repos = get_repos(org_name)
    contributions = defaultdict(int)
    most_contributed_repos = defaultdict(str)

    for repo in repos:
        print(f"Fetching contributors for repository: {repo}")
        contributors = get_contributors(org_name, repo)
        for contributor in contributors:
            username = contributor['login']
            contributions_count = contributor['contributions']
            contributions[username] += contributions_count
            if (
                most_contributed_repos[username] == ''
                or contributions_count > contributions[most_contributed_repos[username]]
            ):
                most_contributed_repos[username] = repo

    contributions = sorted(contributions.items(), key=lambda item: item[1], reverse=True)
    save_contributions_to_file(org_name, contributions, most_contributed_repos, repos)

if __name__ == "__main__":
    rank_contributors(ORG_NAME)
