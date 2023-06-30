import requests
from datetime import datetime, timedelta
import os

ORG_NAME = "statisticsnorway"  
TOKEN = os.getenv('GITHUB_TOKEN')

HEADERS = {
    'Authorization': 'token ' + TOKEN,
    'Accept': 'application/vnd.github+json',
}

# Get the date 30 days ago
date_30_days_ago = datetime.now() - timedelta(days=30)

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


def get_contributions(username):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, headers=HEADERS)
    events = response.json()

    contribution_events = ['PushEvent', 'PullRequestEvent', 'IssuesEvent', 
                           'IssueCommentEvent', 'PullRequestReviewEvent', 
                           'PullRequestReviewCommentEvent']

    contributions = 0
    repos_contributed_to = set()
    
    for event in events:
        # Convert event's 'created_at' date to datetime object
        event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")

        # Only count the event if it is a contribution and happened in the last 30 days
        if event['type'] in contribution_events and event_date >= date_30_days_ago:
            contributions += 1
            repos_contributed_to.add(event['repo']['name'])

    return contributions, list(repos_contributed_to)


# Calculate contributions and rank
print("Fetching and calculating contributions for users from the last 30 days...")
contributions = {name: get_contributions(username) for username, name in users.items()}
print("Done fetching contributions. Ranking users...\n")
rankings = sorted(contributions.items(), key=lambda item: item[1][0], reverse=True)

# Print rankings
print(f"The rankings are based on the number of contributions a user has made from {date_30_days_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}. \
\nContributions include commits, pull requests, issues reported, comments on issues, \
code reviews, and comments on code reviews. \nThe ranking also lists the repositories \
to which the user has made contributions. Here are the rankings:\n")

for i, (name, contribution_data) in enumerate(rankings, 1):
    contributions_count, repos = contribution_data
    repos_str = ', '.join(repos)
    print(f"{i}. {name}: {contributions_count} contributions on these repos: {repos_str}")
    if contributions_count > 250:
        print(f"WARNING: {name} has over 250 events. Not all events in the past 30 days may be included.")