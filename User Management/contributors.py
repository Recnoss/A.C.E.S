import requests
import base64
import os

ORG_NAME = "statisticsnorway"  
TOKEN = os.getenv('GITHUB_TOKEN')


# def get_contributors(repo_name):
#     url = f"https://api.github.com/repos/{ORG_NAME}/{repo_name}/contributors?anon=false"
#     response = requests.get(url, headers=HEADERS)
#     contributors = response.json()
#     print(contributors)  # Add this line for debugging
#     return [(contributor['login'], contributor['contributions']) for contributor in contributors]


HEADERS = {
    'Authorization': 'token ' + TOKEN,
    'Accept': 'application/vnd.github+json',
}


# List of users
users = {
    'johnnadeluy': 'Johnnadel',
    'ssb-cgn': 'Carina',
    'Glenruben': 'Glenruben',
    'omsaggau': 'Ole',
    'oyessb': 'Oyvind',
    'JohannesFinsveen': 'Johannes',
    'PerIngeVaaje': 'Per Inge',
    'vaskalan': 'Vassilios',
    'pawbu': 'Pawel',
    'DanielElisenberg': 'Daniel',
    'JoachimH99': 'Joachim'
}

# Function that feteches the default first 30 repos
def get_repos(org_name):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    response = requests.get(url, headers=HEADERS)
    repos = response.json()
    return [repo['name'] for repo in repos]

# Function to get all repos in the organization
def get_all_repos(org_name):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    all_repos = []
    page = 1
    while True:
        response = requests.get(url, headers=HEADERS, params={'page': page, 'per_page': 100})
        if response.status_code == 200:
            repos = response.json()
            if repos:
                all_repos.extend([repo['name'] for repo in repos])
                page += 1
            else:
                break
        else: 
            print(f"Error {response.status_code}: {response.text}")
            break
    return all_repos



def get_contributors(repo_name):
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo_name}/contributors"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        contributors = response.json()
        return [(contributor['login'], contributor['contributions']) for contributor in contributors]
    else:
        print(f"Error: Received response {response.status_code} from GitHub API")
        return []




def get_user_contributions(username):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url)
    events = response.json()

    contribution_events = ['PushEvent', 'PullRequestEvent', 'IssuesEvent', 
                           'IssueCommentEvent', 'PullRequestReviewEvent', 
                           'PullRequestReviewCommentEvent']

    contributions = sum(event['type'] in contribution_events for event in events)
    return contributions







def main():
    repos = get_all_repos(ORG_NAME)
    print(f"Number of repositories fetched: {len(repos)}")  
    all_contributors = {}
    for repo in repos:
        contributors = get_contributors(repo)
        for contributor, contributions in contributors:
            if contributor in all_contributors:
                all_contributors[contributor] += contributions
            else:
                all_contributors[contributor] = contributions

    sorted_contributors = sorted(all_contributors.items(), key=lambda item: item[1], reverse=True)
    for i, (contributor, contributions) in enumerate(sorted_contributors[:100], start=1):
        print(f"{i}. {contributor}: {contributions} contributions")

if __name__ == "__main__":
    main()