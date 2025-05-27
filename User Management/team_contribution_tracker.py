#!/usr/bin/env python3
"""
GitHub Team Contribution Tracker

This script extends the individual contribution tracker to provide team-based rankings:

1. **Team Discovery:**
   - Fetches all teams in the organization via GitHub API
   - Maps users to their team memberships
   - Handles users with multiple team memberships

2. **Team Scoring:**
   - Aggregates individual contribution scores by team
   - Calculates team averages and totals
   - Provides team-level metrics and rankings

3. **Features:**
   - Team leaderboard with combined scores
   - Individual contributor rankings within teams
   - CSV export with team-organized data
   - Support for same time ranges as individual tracker

Usage Examples:
    export GITHUB_TOKEN=your_token_here
    export GITHUB_ORG=your_org_name
    
    python team_contribution_tracker.py                    # Last 30 days
    python team_contribution_tracker.py --days 90          # Last 90 days
    python team_contribution_tracker.py --quarter Q1-2025  # Q1 2025
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import csv
from dataclasses import dataclass, asdict
import sys

from advanced_contribution_tracker import AdvancedContributionTracker, ContributionMetrics

# Configuration Constants
ORG_NAME = os.getenv('GITHUB_ORG', 'statisticsnorway')
ORG_NAME_2 = os.getenv('GITHUB_ORG_2')  # Optional second organization

@dataclass
class TeamMetrics:
    """Data class for storing team-level contribution metrics."""
    team_name: str
    team_slug: str
    team_description: str
    member_count: int
    
    # Aggregated scores
    total_team_score: float = 0.0
    average_team_score: float = 0.0
    
    # Individual contribution totals
    total_commits: int = 0
    total_prs_opened: int = 0
    total_prs_merged: int = 0
    total_reviews_given: int = 0
    total_review_comments: int = 0
    
    # Team ranking
    team_rank: int = 0
    
    # Team members and their individual metrics
    members: List[ContributionMetrics] = None
    
    def __post_init__(self):
        if self.members is None:
            self.members = []

class TeamContributionTracker(AdvancedContributionTracker):
    """Extension of AdvancedContributionTracker with team-based functionality."""
    
    def __init__(self, token: str):
        super().__init__(token)
        self.teams_cache = {}
        self.user_teams_cache = {}
        self.organizations = [ORG_NAME]
        if ORG_NAME_2:
            self.organizations.append(ORG_NAME_2)
    
    def load_teams_config(self) -> Dict[str, str]:
        """Load team configuration from config.json"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(script_dir)
            config_path = os.path.join(root_dir, 'config.json')
            
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('teams', {})
        except FileNotFoundError:
            print("Warning: config.json not found. No team filter will be applied.")
            return {}
        except KeyError:
            print("Warning: No 'teams' section in config.json. No team filter will be applied.")
            return {}
    
    def get_configured_teams(self) -> List[Dict]:
        """Get teams specified in config.json from all configured organizations"""
        configured_teams = self.load_teams_config()
        
        if not configured_teams:
            print("No teams configured in config.json. Please add a 'teams' section.")
            return []
        
        found_teams = []
        
        for org_name in self.organizations:
            print(f"Searching for teams in organization: {org_name}")
            
            for team_slug, display_name in configured_teams.items():
                cache_key = self.get_cache_key("team_info", org_name, team_slug)
                cached_team = self.load_from_cache(cache_key)
                
                if cached_team is not None:
                    if cached_team:  # Not None and not empty dict
                        cached_team['display_name'] = display_name
                        cached_team['org_name'] = org_name
                        found_teams.append(cached_team)
                    continue
                
                # Try to get team info from this organization
                team_response = self.make_rest_request(f'orgs/{org_name}/teams/{team_slug}')
                
                if team_response and 'slug' in team_response:
                    team_response['display_name'] = display_name
                    team_response['org_name'] = org_name
                    found_teams.append(team_response)
                    self.save_to_cache(cache_key, team_response)
                    print(f"  ✅ Found team '{display_name}' ({team_slug}) in {org_name}")
                else:
                    # Cache empty result to avoid repeated API calls
                    self.save_to_cache(cache_key, {})
                    print(f"  ❌ Team '{team_slug}' not found in {org_name}")
        
        return found_teams
    
    def get_team_members(self, org_name: str, team_slug: str) -> List[str]:
        """Get members of a specific team in a specific organization"""
        cache_key = self.get_cache_key("team_members", org_name, team_slug)
        cached_members = self.load_from_cache(cache_key)
        
        if cached_members is not None:
            return cached_members
        
        members = []
        page = 1
        per_page = 100
        
        while True:
            response = self.make_rest_request(
                f'orgs/{org_name}/teams/{team_slug}/members',
                {'page': page, 'per_page': per_page}
            )
            
            if not response or len(response) == 0:
                break
            
            # Extract usernames
            for member in response:
                members.append(member['login'])
            
            if len(response) < per_page:
                break
                
            page += 1
        
        # Save to cache
        self.save_to_cache(cache_key, members)
        return members
    
    def map_users_to_teams(self, users: Dict[str, str]) -> Dict[str, List[Dict]]:
        """Map each user to their configured team memberships"""
        print(f"\n🔍 Discovering team memberships for {len(users)} users...")
        
        user_teams = {}
        teams = self.get_configured_teams()
        
        if not teams:
            print("❌ No configured teams found!")
            return {}
        
        print(f"Found {len(teams)} configured teams across {len(self.organizations)} organizations")
        
        # Build reverse mapping: user -> teams
        for i, team in enumerate(teams):
            team_slug = team['slug']
            team_name = team.get('display_name', team['name'])
            org_name = team['org_name']
            
            # Progress indicator
            sys.stdout.write(f'\rAnalyzing team {i+1}/{len(teams)}: {team_name} ({org_name})')
            sys.stdout.flush()
            
            try:
                members = self.get_team_members(org_name, team_slug)
                
                for username in members:
                    if username in users:  # Only track configured users
                        if username not in user_teams:
                            user_teams[username] = []
                        
                        user_teams[username].append({
                            'name': team_name,
                            'slug': team_slug,
                            'description': team.get('description', ''),
                            'org_name': org_name
                        })
            except Exception as e:
                print(f"\n⚠️  Warning: Could not get members for team {team_name}: {e}")
                continue
        
        # Clear progress line
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()
        
        print(f"✅ Team mapping complete")
        return user_teams
    
    def create_team_metrics(self, teams: List[Dict], user_teams: Dict[str, List[Dict]], 
                           user_metrics: List[ContributionMetrics]) -> List[TeamMetrics]:
        """Create team metrics by aggregating individual contributions"""
        
        # Create mapping from username to metrics
        metrics_by_user = {m.username: m for m in user_metrics}
        
        team_metrics_list = []
        
        for team in teams:
            team_slug = team['slug']
            team_name = team.get('display_name', team['name'])  # Use display name from config
            org_name = team['org_name']
            
            # Find all users in this team
            team_members = []
            for username, user_team_list in user_teams.items():
                for user_team in user_team_list:
                    if (user_team['slug'] == team_slug and 
                        user_team.get('org_name') == org_name and 
                        username in metrics_by_user):
                        team_members.append(metrics_by_user[username])
                        break
            
            if not team_members:
                continue  # Skip teams with no configured members
            
            # Create team metrics
            team_metrics = TeamMetrics(
                team_name=team_name,
                team_slug=team_slug,
                team_description=team.get('description', ''),
                member_count=len(team_members),
                members=team_members
            )
            
            # Aggregate team statistics
            for member in team_members:
                team_metrics.total_team_score += member.total_score
                team_metrics.total_commits += member.commits_count
                team_metrics.total_prs_opened += member.prs_opened
                team_metrics.total_prs_merged += member.prs_merged
                team_metrics.total_reviews_given += member.reviews_given
                team_metrics.total_review_comments += member.review_comments
            
            # Calculate average
            if team_metrics.member_count > 0:
                team_metrics.average_team_score = team_metrics.total_team_score / team_metrics.member_count
            
            team_metrics_list.append(team_metrics)
        
        # Sort by total team score and assign ranks
        team_metrics_list.sort(key=lambda x: x.total_team_score, reverse=True)
        for i, team_metrics in enumerate(team_metrics_list):
            team_metrics.team_rank = i + 1
        
        return team_metrics_list
    
    def print_team_leaderboard(self, team_metrics: List[TeamMetrics]):
        """Print a formatted team leaderboard"""
        print(f"\n🏆 GitHub Team Contribution Leaderboard ({len(team_metrics)} teams)")
        print("=" * 120)
        print(f"{'Rank':<4} {'Team Name':<25} {'Members':<8} {'Total Score':<12} {'Avg Score':<10} {'Commits':<8} {'PRs':<6}")
        print("-" * 120)
        
        for team in team_metrics:
            team_name = team.team_name[:24] if len(team.team_name) > 24 else team.team_name
            print(f"{team.team_rank:<4} {team_name:<25} {team.member_count:<8} "
                  f"{team.total_team_score:<12.1f} {team.average_team_score:<10.1f} "
                  f"{team.total_commits:<8} {team.total_prs_opened:<6}")
    
    def print_team_details(self, team_metrics: List[TeamMetrics], top_teams: int = 5):
        """Print detailed breakdown for top teams"""
        print(f"\n📋 Top {min(top_teams, len(team_metrics))} Team Details")
        print("=" * 100)
        
        for team in team_metrics[:top_teams]:
            print(f"\n🏅 #{team.team_rank} {team.team_name}")
            if team.team_description:
                print(f"   Description: {team.team_description}")
            print(f"   Total Score: {team.total_team_score:.1f} | Average: {team.average_team_score:.1f} | Members: {team.member_count}")
            print("   " + "-" * 80)
            
            # Sort team members by individual score
            sorted_members = sorted(team.members, key=lambda x: x.total_score, reverse=True)
            
            for member in sorted_members:
                print(f"   {member.full_name:<30} {member.total_score:<8.1f} "
                      f"(C:{member.commits_count} P:{member.prs_opened} R:{member.reviews_given})")
    
    def save_team_results(self, team_metrics: List[TeamMetrics], filename: str = None):
        """Save team results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"team_contributions_{timestamp}.csv"
        
        # Team summary CSV
        team_fieldnames = [
            'team_rank', 'team_name', 'team_slug', 'team_description', 'member_count',
            'total_team_score', 'average_team_score', 'total_commits', 'total_prs_opened',
            'total_prs_merged', 'total_reviews_given', 'total_review_comments'
        ]
        
        team_filename = filename.replace('.csv', '_teams.csv')
        
        with open(team_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=team_fieldnames)
            writer.writeheader()
            
            for team in team_metrics:
                row = asdict(team)
                # Remove the members list for the team summary
                row.pop('members', None)
                writer.writerow(row)
        
        # Individual members by team CSV
        member_filename = filename.replace('.csv', '_members_by_team.csv')
        member_fieldnames = [
            'team_name', 'team_rank', 'username', 'full_name', 'individual_rank',
            'total_score', 'commits_count', 'commits_score', 'prs_opened', 'prs_merged',
            'pr_merge_rate', 'pr_score', 'reviews_given', 'review_comments', 'reviews_score',
            'collaboration_score', 'consistency_score'
        ]
        
        with open(member_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=member_fieldnames)
            writer.writeheader()
            
            for team in team_metrics:
                for member in team.members:
                    row = {
                        'team_name': team.team_name,
                        'team_rank': team.team_rank,
                        'username': member.username,
                        'full_name': member.full_name,
                        'individual_rank': member.rank,
                        'total_score': member.total_score,
                        'commits_count': member.commits_count,
                        'commits_score': member.commits_score,
                        'prs_opened': member.prs_opened,
                        'prs_merged': member.prs_merged,
                        'pr_merge_rate': member.pr_merge_rate,
                        'pr_score': member.pr_score,
                        'reviews_given': member.reviews_given,
                        'review_comments': member.review_comments,
                        'reviews_score': member.reviews_score,
                        'collaboration_score': member.collaboration_score,
                        'consistency_score': member.consistency_score
                    }
                    writer.writerow(row)
        
        print(f"\nResults saved to:")
        print(f"  Teams: {team_filename}")
        print(f"  Members: {member_filename}")
        return team_filename, member_filename

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Team Contribution Tracker')
    parser.add_argument('--days', type=int, default=30, help='Number of days to track (default: 30)')
    parser.add_argument('--quarter', type=str, help='Track by quarter (format: Q1-2025, Q2-2024, etc.)')
    parser.add_argument('--year', type=int, help='Year for quarter tracking (default: current year)')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before running')
    parser.add_argument('--top-teams', type=int, default=5, help='Number of top teams to show details (default: 5)')
    
    args = parser.parse_args()
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return
    
    tracker = TeamContributionTracker(token)
    
    # Clear cache if requested
    if args.clear_cache:
        import shutil
        if os.path.exists("CACHE"):
            shutil.rmtree("CACHE")
            print("🗑️ Cache cleared")
        os.makedirs("CACHE", exist_ok=True)
    
    print("🚀 Starting Team-Based GitHub Contribution Tracking...")
    organizations_str = ', '.join(tracker.organizations)
    print(f"Organizations: {organizations_str}")
    
    # Handle time range (same as individual tracker)
    start_date = None
    end_date = None
    
    if args.quarter:
        try:
            if '-' in args.quarter:
                quarter_str, year_str = args.quarter.split('-')
                quarter = int(quarter_str[1])
                year = int(year_str)
            else:
                quarter = int(args.quarter[1])
                year = args.year if args.year else datetime.now().year
            
            start_date, end_date = tracker.get_quarter_dates(year, quarter)
            period_desc = f"Q{quarter} {year}"
            filename_suffix = f"Q{quarter}_{year}"
            
        except (ValueError, IndexError):
            print("Error: Invalid quarter format. Use Q1-2025, Q2-2024, etc.")
            return
    else:
        period_desc = f"Last {args.days} days"
        filename_suffix = f"{args.days}days"
    
    print(f"Tracking period: {period_desc}\n")
    
    # Step 1: Get individual user contributions (reuse existing tracker)
    print("📊 Getting individual contribution data...")
    individual_metrics = tracker.track_all_users(start_date=start_date, end_date=end_date, 
                                               days_back=args.days)
    
    if not individual_metrics:
        print("❌ No individual contribution data found. Check configuration and token permissions.")
        return
    
    # Step 2: Discover team memberships
    users = tracker.load_users_config()
    user_teams = tracker.map_users_to_teams(users)
    
    # Step 3: Create team metrics
    print(f"\n📈 Aggregating team contributions...")
    teams = tracker.get_configured_teams()
    team_metrics = tracker.create_team_metrics(teams, user_teams, individual_metrics)
    
    if not team_metrics:
        print("❌ No team data found. Users may not be in any teams or teams may be private.")
        return
    
    # Step 4: Display results
    tracker.print_team_leaderboard(team_metrics)
    tracker.print_team_details(team_metrics, args.top_teams)
    
    # Step 5: Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"team_contributions_{filename_suffix}_{timestamp}.csv"
    tracker.save_team_results(team_metrics, filename)
    
    print(f"\n✅ Team tracking complete!")
    
    # Show cache info
    cache_files = len([f for f in os.listdir("CACHE") if f.endswith('.pkl')]) if os.path.exists("CACHE") else 0
    print(f"🗄 Cache: {cache_files} files")

if __name__ == "__main__":
    main()