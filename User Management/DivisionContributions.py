"""
This module fetches and calculates contributions and Lines of Code (LoC) delta 
for a list of GitHub users over the last 30 days, and stores the results in a CSV file.

The contribution count includes events like commits, pull requests, issues reported,
comments on issues, code reviews, and comments on code reviews. The LoC delta is 
calculated as the total number of lines added minus the total number of lines removed.

This script uses the GitHub REST API v3 and requires a personal access token 
stored in an environment variable 'GITHUB_TOKEN'.

List of users to be analysed needs to be provided in the 'users' dictionary in the format:
users = {'github_username': 'user_real_name', ...}

Usage:
    python3 script_name.py
"""
import csv
import os
from datetime import datetime, timedelta
import requests

ORG_NAME = "statisticsnorway"
TOKEN = os.getenv('GITHUB_TOKEN')

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


def get_contributions_and_loc(username):
    """
    Fetches and calculates the contributions and Lines of Code (LoC) delta 
    for a given GitHub user over the past 30 days.

    A contribution is counted if it's a 'PushEvent', 'PullRequestEvent', 'IssuesEvent', 
    'IssueCommentEvent', 'PullRequestReviewEvent', or 'PullRequestReviewCommentEvent'.
    The LoC delta is calculated as the total number of lines added minus the 
    total number of lines removed in 'PushEvent's.

    Parameters:
        username (str): The GitHub username of the user.

    Returns:
        tuple: A tuple containing:
            - contributions (int): The total number of contributions made by the user.
            - loc_delta (int): The total LoC delta for the user.
            - repos_contributed_to (list): A list of repository names the user has contributed to.

    Note: This function may exceed GitHub's API rate limits if the user has a 
    high number of contributions. Consider implementing a delay or pagination if needed.
    """

    date_30_days_ago = datetime.now() - timedelta(days=30)

    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, headers=HEADERS, timeout=10)
    events = response.json()

    contribution_events = ['PushEvent', 'PullRequestEvent', 'IssuesEvent',
                           'IssueCommentEvent', 'PullRequestReviewEvent', 
                           'PullRequestReviewCommentEvent']

    contributions = 0
    loc_delta = 0
    repos_contributed_to = set()
    for event in events:
        # Convert event's 'created_at' date to datetime object
        event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")

        # Only count the event if it is a contribution and happened in the last 30 days
        if event['type'] in contribution_events and event_date >= date_30_days_ago:
            contributions += 1
            repos_contributed_to.add(event['repo']['name'])
            # Only calculate LoC delta for PushEvents
            if event['type'] == 'PushEvent':
                for commit in event['payload']['commits']:
                    commit_url = commit['url']
                    commit_response = requests.get(commit_url, headers=HEADERS, timeout=10)
                    commit_data = commit_response.json()
                    loc_delta += commit_data['stats']['additions']
                    loc_delta -= commit_data['stats']['deletions']

    return contributions, loc_delta, list(repos_contributed_to)

# Calculate contributions and rank
print("Fetching and calculating contributions and LoC delta for users from the last 30 days...")
contributions = {name: get_contributions_and_loc(username) for username, name in users.items()}
print("Done fetching contributions. Ranking users...\n")
rankings = sorted(contributions.items(), key=lambda item: item[1][0], reverse=True)

# Define csv filename
current_month = datetime.now().strftime('%Y-%m')
filename = f"S723 - GitHub Contributions - {current_month}.csv"

# Write rankings to csv file
with open(filename, 'w', newline='', encoding="None") as file:
    writer = csv.writer(file)
    writer.writerow(["Ranking", "Username", "Contributions", "LoC Delta", "Repos"])
    for i, (name, contribution_data) in enumerate(rankings, 1):
        contributions_count, loc_delta, repos = contribution_data
        writer.writerow([i, name, contributions_count, loc_delta, ', '.join(repos)])
        if contributions_count > 250:
            print(f"WARNING: {name} has over 250 events. Not all events may be included.")
print(f"Rankings successfully written to {filename}")
