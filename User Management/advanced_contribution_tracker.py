#!/usr/bin/env python3
"""
Advanced GitHub Contribution Tracker with Gamification

This script provides comprehensive tracking of GitHub contributions with enhanced features:

1. **Data Sources:**
   - GitHub GraphQL API for detailed contribution data
   - REST API fallback for repository-level analysis
   - Smart caching system with 24-hour expiry

2. **Time Range Support:**
   - Last N days tracking (default: 30 days)
   - Quarterly tracking (Q1, Q2, Q3, Q4) for any year
   - Custom date range support

3. **Gamification System:**
   - Commits: 2 points each (capped at 100)
   - Pull Requests: 5 points + merge rate bonus
   - Code Reviews: 3 points + comment engagement
   - Collaboration score based on helping others
   - Consistency bonus for regular activity

4. **Features:**
   - Real-time progress bar with user feedback
   - File-based caching for improved performance
   - Comprehensive error handling with status meanings
   - Dynamic leaderboard (top 100 or all users)
   - CSV export with detailed metrics
   - Full name support from user configuration

5. **Configuration:**
   - Set GITHUB_TOKEN environment variable for authentication
   - Set GITHUB_ORG environment variable for organization (default: statisticsnorway)
   - Users and their full names are configured in config.json

Usage Examples:
    export GITHUB_TOKEN=your_token_here
    export GITHUB_ORG=your_org_name  # Optional, defaults to statisticsnorway
    
    python advanced_contribution_tracker.py                    # Last 30 days
    python advanced_contribution_tracker.py --days 90          # Last 90 days
    python advanced_contribution_tracker.py --quarter Q1-2025  # Q1 2025
    python advanced_contribution_tracker.py --clear-cache      # Clear cache
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import csv
from dataclasses import dataclass, asdict
from joblib import Memory
import time
import sys
import hashlib
import pickle

# Configuration Constants
ORG_NAME = os.getenv('GITHUB_ORG', 'statisticsnorway')  # GitHub organization name from env variable
CACHE_DIR = "CACHE"            # Directory for file-based cache storage
CACHE_EXPIRY_HOURS = 24        # Cache expiry time in hours
memory = Memory(CACHE_DIR, verbose=0)  # Legacy joblib memory (kept for compatibility)

@dataclass
class ContributionMetrics:
    """Data class for storing comprehensive contribution metrics and gamification scores.
    
    This class encapsulates all metrics tracked for a user including:
    - Basic contribution counts (commits, PRs, reviews)
    - Calculated gamification scores for each category
    - Overall ranking and collaboration metrics
    """
    username: str      # GitHub username
    full_name: str     # User's full name from configuration
    
    # Commit metrics
    commits_count: int = 0        # Total commits in time period
    commits_score: float = 0.0    # Gamification points for commits
    
    # Pull Request metrics
    prs_opened: int = 0           # Total PRs opened
    prs_merged: int = 0           # Total PRs merged
    pr_merge_rate: float = 0.0    # Percentage of PRs that were merged
    pr_score: float = 0.0         # Gamification points for PRs
    
    # Code Review metrics
    reviews_given: int = 0        # Number of code reviews provided
    review_comments: int = 0      # Comments made during reviews
    reviews_score: float = 0.0    # Gamification points for reviews
    
    # Collaboration metrics
    collaboration_score: float = 0.0  # Score for helping others
    consistency_score: float = 0.0    # Score for regular activity
    
    # Overall gamification score and ranking
    total_score: float = 0.0      # Sum of all gamification scores
    rank: int = 0                 # Position in leaderboard

class AdvancedContributionTracker:
    """Main class for tracking GitHub contributions with caching and gamification.
    
    This class handles:
    - GitHub API interactions (GraphQL and REST)
    - File-based caching system
    - User contribution analysis
    - Gamification scoring
    - Progress tracking and error handling
    """
    
    def __init__(self, token: str):
        """Initialize tracker with GitHub token and set up API headers.
        
        Args:
            token: GitHub personal access token with repo permissions
        """
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.graphql_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.github.com'
        self.graphql_url = 'https://api.github.com/graphql'
        
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    def get_quarter_dates(self, year: int, quarter: int) -> Tuple[datetime, datetime]:
        """Calculate start and end dates for a specific quarter.
        
        Args:
            year: The year (e.g., 2025)
            quarter: Quarter number (1, 2, 3, or 4)
            
        Returns:
            Tuple of (start_date, end_date) as datetime objects
            
        Raises:
            ValueError: If quarter is not 1, 2, 3, or 4
        """
        if quarter == 1:  # Q1: January - March
            start = datetime(year, 1, 1)
            end = datetime(year, 3, 31, 23, 59, 59)
        elif quarter == 2:  # Q2: April - June
            start = datetime(year, 4, 1)
            end = datetime(year, 6, 30, 23, 59, 59)
        elif quarter == 3:  # Q3: July - September
            start = datetime(year, 7, 1)
            end = datetime(year, 9, 30, 23, 59, 59)
        elif quarter == 4:  # Q4: October - December
            start = datetime(year, 10, 1)
            end = datetime(year, 12, 31, 23, 59, 59)
        else:
            raise ValueError("Quarter must be 1, 2, 3, or 4")
        
        return start, end
    
    def get_cache_key(self, *args) -> str:
        """Generate a cache key from arguments"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cache_file_path(self, cache_key: str) -> str:
        """Get the file path for a cache key"""
        return os.path.join(CACHE_DIR, f"{cache_key}.pkl")
    
    def is_cache_valid(self, cache_file: str) -> bool:
        """Check if cache file exists and is not expired"""
        if not os.path.exists(cache_file):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        return file_time > expiry_time
    
    def load_from_cache(self, cache_key: str):
        """Load data from cache file"""
        cache_file = self.get_cache_file_path(cache_key)
        if self.is_cache_valid(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                # If cache is corrupted, remove it
                os.remove(cache_file)
        return None
    
    def save_to_cache(self, cache_key: str, data):
        """Save data to cache file"""
        cache_file = self.get_cache_file_path(cache_key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save to cache: {e}")
    
    def get_status_code_meaning(self, status_code: int) -> str:
        """Get human-readable meaning of HTTP status codes"""
        status_meanings = {
            400: "Bad Request",
            401: "Unauthorized", 
            403: "Forbidden/Rate Limited",
            404: "Not Found",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }
        return status_meanings.get(status_code, "Unknown Error")
    
    def print_progress_bar(self, current: int, total: int, username: str, full_name: str):
        """Print a progress bar for user tracking"""
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Truncate name if too long to fit on one line
        display_name = full_name[:25] + "..." if len(full_name) > 25 else full_name
        
        # Clear line and print progress
        sys.stdout.write(f'\r[{bar}] {percentage:5.1f}% ({current:3d}/{total}) {display_name} ({username})')
        sys.stdout.flush()
        
    def load_users_config(self) -> Dict[str, str]:
        """Load user configuration from config.json"""
        try:
            # Get the parent directory (root of the project)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(script_dir)
            config_path = os.path.join(root_dir, 'config.json')
            
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('users', {})
        except FileNotFoundError:
            print("Warning: config.json not found. Using empty user list.")
            return {}
    
    def make_graphql_request(self, query: str, variables: Dict = None) -> Dict:
        """Make a GraphQL request with file-based caching"""
        # Create cache key from query and variables
        cache_key = self.get_cache_key("graphql", query, str(variables) if variables else "none")
        
        # Try to load from cache first
        cached_data = self.load_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
            
        response = requests.post(
            self.graphql_url,
            headers=self.graphql_headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            # Save to cache
            self.save_to_cache(cache_key, data)
            return data
        else:
            error_meaning = self.get_status_code_meaning(response.status_code)
            print(f"GraphQL request failed: {response.status_code} ({error_meaning})")
            return {}
    
    def make_rest_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a REST API request with file-based caching"""
        # Create cache key from endpoint and params
        cache_key = self.get_cache_key("rest", endpoint, str(params) if params else "none")
        
        # Try to load from cache first
        cached_data = self.load_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Save to cache
            self.save_to_cache(cache_key, data)
            return data
        elif response.status_code == 403:
            print("Rate limit exceeded, waiting...")
            time.sleep(60)
            return self.make_rest_request(endpoint, params)
        else:
            error_meaning = self.get_status_code_meaning(response.status_code)
            print(f"REST request failed: {response.status_code} ({error_meaning})")
            return {}
    
    def get_user_contributions_graphql(self, username: str, start_date: str) -> Dict:
        """Get comprehensive user contributions using GraphQL"""
        query = """
        query($username: String!, $from: DateTime!) {
          user(login: $username) {
            contributionsCollection(from: $from) {
              totalCommitContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              commitContributionsByRepository {
                repository {
                  name
                  owner {
                    login
                  }
                }
                contributions {
                  totalCount
                }
              }
              pullRequestContributionsByRepository {
                repository {
                  name
                  owner {
                    login
                  }
                }
                contributions {
                  totalCount
                }
              }
            }
            pullRequests(first: 100, states: [MERGED, OPEN, CLOSED], orderBy: {field: CREATED_AT, direction: DESC}) {
              edges {
                node {
                  title
                  state
                  createdAt
                  mergedAt
                  additions
                  deletions
                  reviews {
                    totalCount
                  }
                  comments {
                    totalCount
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {
            'username': username,
            'from': start_date
        }
        
        return self.make_graphql_request(query, variables)
    
    def get_user_reviews_rest(self, username: str, start_date: str) -> List[Dict]:
        """Get detailed review information using REST API"""
        # Search for reviews by user in the organization
        search_query = f"reviewed-by:{username} org:{ORG_NAME} created:>={start_date}"
        
        response = self.make_rest_request(
            'search/issues',
            {'q': search_query, 'sort': 'created', 'order': 'desc'}
        )
        
        reviews = []
        for item in response.get('items', []):
            if item.get('pull_request'):
                reviews.append({
                    'title': item['title'],
                    'number': item['number'],
                    'repository': item['repository_url'].split('/')[-1],
                    'created_at': item['created_at']
                })
        
        return reviews
    
    def get_repository_contributions(self, username: str, start_date: datetime) -> Dict:
        """Fallback method: iterate through repositories to get contributions"""
        # Get organization repositories
        repos_response = self.make_rest_request(f'orgs/{ORG_NAME}/repos', {'per_page': 100})
        
        total_commits = 0
        total_prs = 0
        repositories_contributed = set()
        
        for repo in repos_response:
            if repo.get('archived') or repo.get('fork'):
                continue
                
            repo_name = repo['name']
            
            # Get commits by user in this repository
            commits_response = self.make_rest_request(
                f'repos/{ORG_NAME}/{repo_name}/commits',
                {
                    'author': username,
                    'since': start_date.isoformat(),
                    'per_page': 100
                }
            )
            
            if commits_response:
                repo_commits = len(commits_response)
                if repo_commits > 0:
                    total_commits += repo_commits
                    repositories_contributed.add(repo_name)
            
            # Get pull requests by user in this repository
            prs_response = self.make_rest_request(
                f'repos/{ORG_NAME}/{repo_name}/pulls',
                {
                    'creator': username,
                    'state': 'all',
                    'sort': 'created',
                    'direction': 'desc',
                    'per_page': 100
                }
            )
            
            if prs_response:
                # Filter PRs by date
                recent_prs = []
                for pr in prs_response:
                    pr_date = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                    if pr_date >= start_date:
                        recent_prs.append(pr)
                total_prs += len(recent_prs)
        
        return {
            'total_commits': total_commits,
            'total_prs': total_prs,
            'repositories_count': len(repositories_contributed),
            'repositories': list(repositories_contributed)
        }
    
    def calculate_gamification_scores(self, metrics: ContributionMetrics) -> ContributionMetrics:
        """Calculate gamification scores for different contribution types"""
        
        # Commit scoring (quality over quantity)
        metrics.commits_score = min(metrics.commits_count * 2, 100)  # Cap at 100 points
        
        # PR scoring (merge rate matters)
        if metrics.prs_opened > 0:
            metrics.pr_merge_rate = metrics.prs_merged / metrics.prs_opened
            metrics.pr_score = (metrics.prs_opened * 5) + (metrics.pr_merge_rate * 20)
        
        # Review scoring (helping others is valuable)
        metrics.reviews_score = (metrics.reviews_given * 3) + (metrics.review_comments * 1)
        
        # Collaboration score (reviews + comments + helping others)
        metrics.collaboration_score = metrics.reviews_score
        
        # Consistency score (regular activity vs bursts)
        # This would need historical data to calculate properly
        metrics.consistency_score = min(metrics.commits_count * 0.5, 25)  # Simplified version
        
        # Total gamification score
        metrics.total_score = (
            metrics.commits_score +
            metrics.pr_score +
            metrics.reviews_score +
            metrics.collaboration_score +
            metrics.consistency_score
        )
        
        return metrics
    
    def track_user_contributions(self, username: str, full_name: str, start_date: datetime = None, end_date: datetime = None, days_back: int = 30) -> ContributionMetrics:
        """Track comprehensive contributions for a single user"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days_back)
        if end_date is None:
            end_date = datetime.now()
        
        start_date_str = start_date.isoformat()
        
        metrics = ContributionMetrics(username=username, full_name=full_name)
        
        # Try GraphQL first
        graphql_data = self.get_user_contributions_graphql(username, start_date_str)
        
        if graphql_data.get('data', {}).get('user'):
            user_data = graphql_data['data']['user']
            contributions = user_data.get('contributionsCollection', {})
            
            # Extract basic metrics
            metrics.commits_count = contributions.get('totalCommitContributions', 0)
            metrics.prs_opened = contributions.get('totalPullRequestContributions', 0)
            metrics.reviews_given = contributions.get('totalPullRequestReviewContributions', 0)
            
            # Extract detailed PR information
            prs = user_data.get('pullRequests', {}).get('edges', [])
            recent_prs = []
            for pr in prs:
                pr_date = datetime.fromisoformat(pr['node']['createdAt'].replace('Z', '+00:00')).replace(tzinfo=None)
                if pr_date >= start_date:
                    recent_prs.append(pr['node'])
            
            metrics.prs_merged = len([pr for pr in recent_prs if pr['state'] == 'MERGED'])
            metrics.review_comments = sum(pr.get('comments', {}).get('totalCount', 0) for pr in recent_prs)
        
        else:
            # Fallback to REST API repository iteration
            rest_data = self.get_repository_contributions(username, start_date)
            metrics.commits_count = rest_data.get('total_commits', 0)
            metrics.prs_opened = rest_data.get('total_prs', 0)
        
        # Get additional review data from REST API
        reviews = self.get_user_reviews_rest(username, start_date_str.split('T')[0])
        if not metrics.reviews_given:  # If GraphQL didn't provide this
            metrics.reviews_given = len(reviews)
        
        # Calculate gamification scores
        metrics = self.calculate_gamification_scores(metrics)
        
        return metrics
    
    def track_all_users(self, start_date: datetime = None, end_date: datetime = None, days_back: int = 30) -> List[ContributionMetrics]:
        """Track contributions for all users in config"""
        users = self.load_users_config()
        all_metrics = []
        total_users = len(users)
        current_user = 0
        
        # Determine date range for display
        if start_date and end_date:
            date_info = f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            date_info = f"last {days_back} days"
        
        print(f"\n🚀 Starting to track {total_users} users ({date_info})...")
        
        for username, full_name in users.items():
            current_user += 1
            
            try:
                self.print_progress_bar(current_user, total_users, username, full_name)
                metrics = self.track_user_contributions(username, full_name, start_date, end_date, days_back)
                all_metrics.append(metrics)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                # Clear progress line before printing error, then restore it
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()
                error_msg = f"❌ Error tracking {full_name} ({username}): {e}"
                print(error_msg)
                continue
        
        # Clear progress bar and add completion message
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()
        print(f"✅ Completed tracking {len(all_metrics)} users\n")
        
        # Sort by total score and assign ranks
        all_metrics.sort(key=lambda x: x.total_score, reverse=True)
        for i, metrics in enumerate(all_metrics):
            metrics.rank = i + 1
        
        return all_metrics
    
    def save_results(self, metrics_list: List[ContributionMetrics], filename: str = None):
        """Save results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advanced_contributions_{timestamp}.csv"
        
        fieldnames = [
            'rank', 'username', 'full_name', 'total_score',
            'commits_count', 'commits_score',
            'prs_opened', 'prs_merged', 'pr_merge_rate', 'pr_score',
            'reviews_given', 'review_comments', 'reviews_score',
            'collaboration_score', 'consistency_score'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for metrics in metrics_list:
                row = asdict(metrics)
                writer.writerow(row)
        
        print(f"Results saved to {filename}")
        return filename
    
    def print_leaderboard(self, metrics_list: List[ContributionMetrics]):
        """Print a formatted leaderboard"""
        total_users = len(metrics_list)
        top_n = min(100, total_users)  # Show max 100 or all users if less than 100
        
        print(f"\n🏆 GitHub Contribution Leaderboard (Top {top_n} of {total_users})")
        print("=" * 100)
        print(f"{'Rank':<4} {'Name':<30} {'Score':<8} {'Commits':<8} {'PRs':<6} {'Reviews':<8}")
        print("-" * 100)
        
        for metrics in metrics_list[:top_n]:
            # Truncate long names for display
            display_name = metrics.full_name[:29] if len(metrics.full_name) > 29 else metrics.full_name
            print(f"{metrics.rank:<4} {display_name:<30} {metrics.total_score:<8.1f} "
                  f"{metrics.commits_count:<8} {metrics.prs_opened:<6} {metrics.reviews_given:<8}")
        
        print("\n📊 Scoring Breakdown:")
        print("• Commits: 2 points each (max 100)")
        print("• PRs: 5 points + 20 bonus for high merge rate")
        print("• Reviews: 3 points each + 1 per comment")
        print("• Collaboration: Reviews + comments")
        print("• Consistency: Regular activity bonus")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced GitHub Contribution Tracker')
    parser.add_argument('--days', type=int, default=30, help='Number of days to track (default: 30)')
    parser.add_argument('--quarter', type=str, help='Track by quarter (format: Q1-2025, Q2-2024, etc.)')
    parser.add_argument('--year', type=int, help='Year for quarter tracking (default: current year)')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before running')
    
    args = parser.parse_args()
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return
    
    tracker = AdvancedContributionTracker(token)
    
    # Clear cache if requested
    if args.clear_cache:
        import shutil
        if os.path.exists(CACHE_DIR):
            shutil.rmtree(CACHE_DIR)
            print("🗑️ Cache cleared")
        os.makedirs(CACHE_DIR, exist_ok=True)
    
    print("🚀 Starting Advanced GitHub Contribution Tracking...")
    print(f"Organization: {ORG_NAME}")
    
    start_date = None
    end_date = None
    
    # Handle quarter tracking
    if args.quarter:
        try:
            if '-' in args.quarter:
                quarter_str, year_str = args.quarter.split('-')
                quarter = int(quarter_str[1])  # Extract number from Q1, Q2, etc.
                year = int(year_str)
            else:
                quarter = int(args.quarter[1])  # Extract number from Q1, Q2, etc.
                year = args.year if args.year else datetime.now().year
            
            start_date, end_date = tracker.get_quarter_dates(year, quarter)
            print(f"Tracking period: Q{quarter} {year} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})\n")
            
            # Track all users for the quarter
            metrics_list = tracker.track_all_users(start_date=start_date, end_date=end_date)
            filename_suffix = f"Q{quarter}_{year}"
            
        except (ValueError, IndexError):
            print("Error: Invalid quarter format. Use Q1-2025, Q2-2024, etc.")
            return
    else:
        print(f"Tracking period: Last {args.days} days\n")
        # Track all users for specified days
        metrics_list = tracker.track_all_users(days_back=args.days)
        filename_suffix = f"{args.days}days"
    
    if metrics_list:
        # Print leaderboard
        tracker.print_leaderboard(metrics_list)
        
        # Save results with appropriate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"advanced_contributions_{filename_suffix}_{timestamp}.csv"
        tracker.save_results(metrics_list, filename)
        print(f"\n✅ Tracking complete! Results saved to {filename}")
        
        # Show cache info
        cache_files = len([f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]) if os.path.exists(CACHE_DIR) else 0
        print(f"🗄 Cache: {cache_files} files (expires after {CACHE_EXPIRY_HOURS}h)")
    else:
        print("❌ No contribution data found. Check your configuration and token permissions.")

if __name__ == "__main__":
    main()