import requests

def get_contributions(username):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url)
    events = response.json()

    contribution_events = ['PushEvent', 'PullRequestEvent', 'IssuesEvent', 
                           'IssueCommentEvent', 'PullRequestReviewEvent', 
                           'PullRequestReviewCommentEvent']

    contributions = sum(event['type'] in contribution_events for event in events)
    return contributions

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

# Calculate contributions and rank
contributions = {name: get_contributions(username) for username, name in users.items()}
rankings = sorted(contributions.items(), key=lambda item: item[1], reverse=True)

# Print rankings
for i, (name, contributions) in enumerate(rankings, 1):
    print(f"{i}. {name}: {contributions} contributions")
