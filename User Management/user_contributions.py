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
    python3 user_contributions.py
"""

import csv
import os
from datetime import datetime, timedelta
import requests
from requests.exceptions import HTTPError

# Constants
ORG_NAME = "statisticsnorway"
TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github+json',
}
USERS = {
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

CONTRIBUTION_EVENTS = ['PushEvent', 'PullRequestEvent', 'IssuesEvent',
                       'IssueCommentEvent', 'PullRequestReviewEvent',
                       'PullRequestReviewCommentEvent']

# Check if the Github token is present
if TOKEN is None:
    raise ValueError("Please set the 'GITHUB_TOKEN' environment variable.")


def fetch_data_from_url(url):
    """
    Fetch JSON data from a specified URL.

    This function sends a GET request to the provided URL and returns the 
    response as a JSON object. If the request is unsuccessful (either due 
    to an HTTP error or another exception), an appropriate error message is printed 
    and the function returns None.

    Args:
        url (str): The URL from which to fetch data.

    Returns:
        dict: The JSON response from the URL if the request is successful, 
              None otherwise.

    Raises:
        HTTPError: If an HTTP error occurs.
        Exception: If an error occurs for a different reason.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as err:
        print(f"Other error occurred: {err}")
        return None


def get_contributions_and_loc(username):
    """
Fetch and calculate contributions and Lines of Code (LoC) delta for a specific GitHub user.

This function sends multiple GET requests to the GitHub REST API to fetch all events 
related to the user within the last 30 days. It then calculates the number of contributions
(including commits, pull requests, issues reported, comments on issues, code reviews, 
and comments on code reviews) and the LoC delta (total lines added minus total lines removed).

Args:
    username (str): The GitHub username of the user.

Returns:
    tuple: A tuple containing:
        contributions (int): The total number of contributions.
        loc_delta (int): The LoC delta.
        repos_contributed_to (list): The list of repos the user contributed to.

Raises:
    HTTPError: If an HTTP error occurs during any of the requests.
    Exception: If an error occurs for a different reason during any of the requests.
"""
    date_30_days_ago = datetime.now() - timedelta(days=30)
    contributions = 0
    lines_of_code_delta = 0
    repos_contributed_to = set()
    page = 1

    while True:
        url = f"https://api.github.com/users/{username}/events?page={page}"
        events = fetch_data_from_url(url)

        if not events:
            break  # No more events

        for event in events:
            event_date = datetime.strptime(
                event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            if event['type'] in CONTRIBUTION_EVENTS and event_date >= date_30_days_ago:
                contributions += 1
                repos_contributed_to.add(event['repo']['name'])
                if event['type'] == 'PushEvent':
                    for commit in event['payload']['commits']:
                        commit_url = commit['url']
                        commit_data = fetch_data_from_url(commit_url)
                        if commit_data:
                            lines_of_code_delta += commit_data['stats']['additions']
                            lines_of_code_delta -= commit_data['stats']['deletions']

        page += 1  # Go to next page

    return contributions, lines_of_code_delta, list(repos_contributed_to)



def main():
    """
    Fetch, calculate and store contributions and Lines of Code delta for a list of GitHub users.

    This function gets contributions and LoC delta for a list of GitHub users over the 
    last 30 days using the GitHub REST API. Results are sorted in descending order of contributions, 
    and then written to a CSV file named "S723 - GitHub Contributions - {current_month}.csv".

    If a user has more than 250 events, a warning message will be printed, as GitHub's APIs have 
    some limitations on the number of events returned.

    Note: This function requires a 'GITHUB_TOKEN' environment variable set localy.
    It also uses a predefined USERS dictionary that maps GitHub usernames to their 
    corresponding real names.

    Raises:
        ValueError: If 'GITHUB_TOKEN' environment variable is not set.
    """

    # Calculate contributions and rank
    print("Fetching and calculating contributions and LoC delta for users from the last 30 days...")

    contributions = {name: get_contributions_and_loc(
        username) for username, name in USERS.items()}

    print("Done fetching contributions. Ranking users...\n")
    rankings = sorted(contributions.items(),
                      key=lambda item: item[1][0], reverse=True)

    # Define csv filename
    current_month = datetime.now().strftime('%Y-%m')
    filename = f"S723 - GitHub Contributions - {current_month}.csv"

    # Write rankings to csv file
    with open(filename, 'w', newline='', encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Ranking", "Username", "Contributions", "LoC Delta", "Repos"])
        for i, (name, contribution_data) in enumerate(rankings, 1):
            contributions_count, loc_delta, repos = contribution_data
            writer.writerow([i, name, contributions_count,
                            loc_delta, ', '.join(repos)])
            if contributions_count > 250:
                print(
                    f"WARNING: {name} has over 250 events. Not all events may be included.")
    print(f"Rankings successfully written to {filename}")


if __name__ == "__main__":
    main()
