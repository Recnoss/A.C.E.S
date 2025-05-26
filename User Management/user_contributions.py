"""
GitHub User Contributions Tracker

This module fetches and calculates contributions and Lines of Code (LoC) delta 
for a list of GitHub users over the previous month, and stores the results in a CSV file.

The contribution count includes events like commits, pull requests, issues reported,
comments on issues, code reviews, and comments on code reviews. The LoC delta is 
calculated as the total number of lines added minus the total number of lines removed.

This script uses the GitHub REST API v3 and requires a personal access token 
stored in an environment variable 'GITHUB_TOKEN'.

Usage:
    python3 user_contributions.py [--config config.json]
"""

import csv
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import requests
from requests.exceptions import HTTPError, RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_contributions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GitHubContributionsTracker:
    """Tracks GitHub user contributions and generates reports."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        "org_name": "statisticsnorway",
        "users": {
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
            'JoachimH99': 'Joachim',
            'Recnoss': 'Erik'
        },
        "contribution_events": [
            'PushEvent', 'PullRequestEvent', 'PullRequestReviewEvent',
            'PullRequestReviewCommentEvent'
        ],
        "max_pages": 10,
        "rate_limit_sleep": 60
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the contributions tracker.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config = self._load_config(config_file)
        self.token = self._get_github_token()
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github+json',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading config file {config_file}: {e}")
                logger.info("Using default configuration")
        return self.DEFAULT_CONFIG.copy()
    
    def _get_github_token(self) -> str:
        """Get GitHub token from environment variable."""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("Please set the 'GITHUB_TOKEN' environment variable.")
        return token


    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle GitHub rate limiting."""
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            reset_time = response.headers.get('X-RateLimit-Reset')
            if reset_time:
                wait_time = int(reset_time) - int(time.time()) + 10
                logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds.")
                time.sleep(max(wait_time, self.config['rate_limit_sleep']))
            else:
                logger.warning(f"Rate limit exceeded. Waiting {self.config['rate_limit_sleep']} seconds.")
                time.sleep(self.config['rate_limit_sleep'])
    
    def _fetch_data_from_url(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Fetch JSON data from a specified URL with retry logic.

        Args:
            url: The URL from which to fetch data
            max_retries: Maximum number of retry attempts

        Returns:
            JSON response as dictionary if successful, None otherwise
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 403:
                    self._handle_rate_limit(response)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except HTTPError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except (RequestException, json.JSONDecodeError) as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)
                
        return None


    def _get_date_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for the previous month."""
        today = datetime.now()
        first_day_of_current_month = datetime(today.year, today.month, 1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = datetime(
            last_day_of_previous_month.year, 
            last_day_of_previous_month.month, 
            1
        )
        return first_day_of_previous_month, first_day_of_current_month
    
    def get_user_contributions(self, username: str) -> Tuple[int, int, List[str]]:
        """Fetch and calculate contributions and LoC delta for a GitHub user.

        Args:
            username: The GitHub username

        Returns:
            Tuple containing:
                - contributions count
                - lines of code delta 
                - list of repositories contributed to
        """
        logger.info(f"Fetching contributions for user: {username}")
        
        start_date, end_date = self._get_date_range()
        contributions = 0
        lines_of_code_delta = 0
        repos_contributed_to = set()
        page = 1
        
        while page <= self.config['max_pages']:
            url = f"https://api.github.com/users/{username}/events?page={page}&per_page=100"
            events = self._fetch_data_from_url(url)

            if not events:
                break

            # Check if we've gone beyond our date range
            if events and len(events) > 0:
                last_event_date = datetime.strptime(events[-1]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                if last_event_date < start_date:
                    break

            for event in events:
                event_date = datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                
                # Skip events outside our date range
                if not (start_date <= event_date < end_date):
                    continue
                    
                if event['type'] in self.config['contribution_events']:
                    contributions += 1
                    repos_contributed_to.add(event['repo']['name'])
                    
                    if event['type'] == 'PushEvent':
                        self._process_push_event(event, username)
                        lines_of_code_delta += self._calculate_loc_delta(event)

            page += 1

        logger.info(f"User {username}: {contributions} contributions, {lines_of_code_delta} LoC delta")
        return contributions, lines_of_code_delta, list(repos_contributed_to)
    
    def _process_push_event(self, event: Dict[str, Any], username: str) -> None:
        """Process push event for additional metrics if needed."""
        # This method can be extended for additional push event processing
        pass
    
    def _calculate_loc_delta(self, event: Dict[str, Any]) -> int:
        """Calculate lines of code delta for a push event."""
        loc_delta = 0
        if event['type'] == 'PushEvent':
            for commit in event.get('payload', {}).get('commits', []):
                commit_url = commit.get('url')
                if commit_url:
                    commit_data = self._fetch_data_from_url(commit_url)
                    if commit_data and 'stats' in commit_data:
                        loc_delta += commit_data['stats'].get('additions', 0)
                        loc_delta -= commit_data['stats'].get('deletions', 0)
        return loc_delta



    def generate_report(self) -> str:
        """Generate contributions report for all configured users."""
        logger.info("Starting contributions analysis...")
        
        contributions = {}
        for username, display_name in self.config['users'].items():
            try:
                contrib_data = self.get_user_contributions(username)
                contributions[display_name] = contrib_data
            except Exception as e:
                logger.error(f"Failed to get contributions for {username}: {e}")
                contributions[display_name] = (0, 0, [])
        
        # Sort by contribution count
        rankings = sorted(
            contributions.items(),
            key=lambda item: item[1][0], 
            reverse=True
        )
        
        # Generate filename
        previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        filename = f"{self.config['org_name']} - GitHub Contributions - {previous_month}.csv"
        
        # Write CSV report
        self._write_csv_report(filename, rankings)
        
        logger.info(f"Report generated successfully: {filename}")
        return filename
    
    def _write_csv_report(self, filename: str, rankings: List[Tuple[str, Tuple[int, int, List[str]]]]) -> None:
        """Write the contributions report to CSV file."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Ranking", "Username", "Contributions", "LoC Delta", "Repos"])
                
                for i, (name, contribution_data) in enumerate(rankings, 1):
                    contributions_count, loc_delta, repos = contribution_data
                    writer.writerow([
                        i, 
                        name, 
                        contributions_count,
                        loc_delta, 
                        ', '.join(repos[:10])  # Limit repo list length
                    ])
                    
                    if contributions_count > 250:
                        logger.warning(
                            f"{name} has over 250 events. Some events may not be included."
                        )
        except IOError as e:
            logger.error(f"Failed to write CSV file {filename}: {e}")
            raise

def main():
    """Main function to run the contributions tracker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track GitHub user contributions')
    parser.add_argument(
        '--config', 
        type=str, 
        help='Path to configuration file'
    )
    args = parser.parse_args()
    
    try:
        tracker = GitHubContributionsTracker(args.config)
        filename = tracker.generate_report()
        print(f"Report generated: {filename}")
        
    except Exception as e:
        logger.error(f"Error running contributions tracker: {e}")
        raise

if __name__ == "__main__":
    main()
