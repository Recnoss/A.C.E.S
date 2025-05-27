# User Management

This folder contains advanced scripts and tools for GitHub organization management, user analytics, and contribution tracking. These scripts are designed to provide comprehensive insights into team productivity and collaboration patterns.

## 🚀 Featured Scripts

### 🔥 Advanced GitHub Contribution Tracker
**File:** `advanced_contribution_tracker.py`

A comprehensive individual GitHub contribution tracking system with gamification, caching, and advanced analytics.

### ⭐ NEW: Team Contribution Tracker
**File:** `team_contribution_tracker.py`

A team-based GitHub contribution tracking system that aggregates individual scores into team leaderboards with configurable team filtering.

#### **🌟 Team Tracker Key Features:**
- **Configurable Teams**: Only tracks teams specified in `config.json`
- **Multi-Organization Support**: Searches teams across multiple GitHub organizations
- **Team Aggregation**: Combines individual contribution scores by team
- **Team Analytics**: Total scores, averages, and detailed member breakdowns
- **Dual CSV Export**: Separate files for team summaries and individual members by team
- **Smart Team Discovery**: Automatically finds configured teams in specified organizations
- **Error Handling**: Graceful handling of private teams or missing teams

#### **Team Configuration:**
Add teams to your `config.json`:
```json
{
  "teams": {
    "ssbno-developers": "Team SSB.no",
    "microdata-developers": "Team Microdata",
    "statbank-developers": "Team Statistikkbanken",
    "statbank-utviklere": "Legacy Statbank"
  }
}
```

#### **Multi-Organization Setup:**
```bash
# Set environment variables for multiple organizations
export GITHUB_ORG=statisticsnorway      # Primary organization  
export GITHUB_ORG_2=PxTools              # Secondary organization
```

#### **Team Tracker Usage Examples:**
```bash
# Track team contributions for last 30 days
python team_contribution_tracker.py

# Track team contributions for last 90 days
python team_contribution_tracker.py --days 90

# Track Q1 2025 with top 3 team details
python team_contribution_tracker.py --quarter Q1-2025 --top-teams 3

# Clear cache and run fresh
python team_contribution_tracker.py --clear-cache
```

#### **Team Output Files:**
- `team_contributions_[period]_[timestamp]_teams.csv`: Team summary with rankings
- `team_contributions_[period]_[timestamp]_members_by_team.csv`: Individual members organized by team

#### **Individual Tracker Key Features:**
- **Multi-source Data Collection**: GraphQL API + REST API fallback
- **Smart Caching**: 24-hour file-based cache for optimal performance
- **Flexible Time Ranges**: Last N days or quarterly tracking (Q1, Q2, Q3, Q4)
- **Real-time Progress Tracking**: Visual progress bar with user feedback
- **Gamification System**: Points-based scoring for various contribution types
- **Dynamic Leaderboards**: Top 100 users with full name support
- **Comprehensive Error Handling**: Detailed error messages with HTTP status meanings

#### **🏆 Improved Gamification Scoring System:**

Our scoring system provides a balanced assessment of individual productivity and team collaboration. **Recent improvements eliminated double-counting issues** for fair and accurate rankings:

| Contribution Type | Scoring Rules | Data Source & Calculation Method |
|------------------|---------------|----------------------------------|
| **Commits** | 2 points each (capped at 100 points) | **Data:** GitHub GraphQL `totalCommitContributions` + multi-org REST fallback<br>**Method:** Direct count of commits authored across all configured organizations<br>**Cap Reasoning:** Prevents volume over quality; encourages meaningful commits |
| **Pull Requests** | 5 base points + up to 20 merge rate bonus | **Data:** GitHub GraphQL `totalPullRequestContributions` + PR state analysis<br>**Calculation:** `(PRs_opened × 5) + (merge_rate × 20)`<br>**Merge Rate:** `PRs_merged / PRs_opened`<br>**Quality Focus:** Rewards PRs that get accepted by the team |
| **Code Reviews** | 3 points per review + 1 point per review comment | **Data:** GitHub GraphQL `totalPullRequestReviewContributions` + comment analysis<br>**Method:** Counts reviews submitted + comments made during reviews<br>**Team Value:** Recognizes time spent helping others improve their code |
| **Collaboration** | 10-35 bonus points for active reviewing (**NEW**) | **Data:** Review activity patterns and engagement quality<br>**Calculation:** Bonus points for active reviewers (>5 reviews: +10, >20 comments: +15, well-rounded contributor: +10)<br>**Purpose:** **No longer duplicates review scores** - rewards exceptional collaboration |
| **Consistency** | 8 points per contribution type (max 24) (**IMPROVED**) | **Data:** Activity diversity across contribution types<br>**Calculation:** 8 points each for commits, PRs, and reviews (independent scoring)<br>**Philosophy:** **Eliminates double-counting** - rewards balanced contribution patterns |

#### **Data Collection Methodology:**

**🔍 Primary Data Sources:**
- **GitHub GraphQL API:** Comprehensive contribution data with precise metrics
- **GitHub REST API:** Fallback for detailed repository-level analysis across multiple organizations
- **Multi-Organization Support:** Searches contributions across all configured organizations  
- **Time-based Filtering:** All data is filtered to the specified time period (days/quarters)

**📊 Specific Data Points Tracked:**

1. **Commit Analysis:**
   - Total commits authored in time period
   - Commits per repository (organization-scoped only)
   - Excludes forks and archived repositories for accuracy

2. **Pull Request Metrics:**
   - PRs opened, merged, closed, and still open
   - Merge success rate calculation
   - Comments received on user's PRs (engagement indicator)
   - Lines added/deleted (complexity indicator)

3. **Code Review Participation:**
   - Reviews submitted on others' PRs
   - Comments made during review process
   - Review quality through engagement metrics
   - Cross-team collaboration patterns

4. **Collaboration Tracking:**
   - Comments on team members' PRs
   - Participation in code discussions
   - Mentoring indicators through review feedback
   - Knowledge sharing through detailed comments

**🛡️ Data Integrity & Privacy:**
- **API Permissions:** Read-only access to public organization data
- **Rate Limiting:** Built-in GitHub API rate limit handling
- **Caching:** 24-hour local cache to minimize API calls
- **Error Handling:** Comprehensive fallbacks for missing or incomplete data
- **Transparency:** All calculations are logged and auditable

**⚖️ Scoring Philosophy:**

**Quality Over Quantity:** The capped scoring system prevents gaming through volume and emphasizes meaningful contributions.

**Team-First Approach:** Heavy weighting on reviews and collaboration reflects that great developers make their entire team better.

**Sustainable Practices:** Consistency bonuses encourage healthy work-life balance over crunch periods.

**Fair Assessment:** Multiple data sources ensure no single metric dominates, providing a holistic view of contribution value.

**Recognition of "Invisible" Work:** Code reviews and mentoring finally get the recognition they deserve in team productivity.

#### **Individual Tracker Usage Examples:**
```bash
# Track last 30 days (default) across multiple orgs
python advanced_contribution_tracker.py

# Track last 90 days
python advanced_contribution_tracker.py --days 90

# Track Q1 2025
python advanced_contribution_tracker.py --quarter Q1-2025

# Clear cache and run fresh
python advanced_contribution_tracker.py --clear-cache
```

#### **Combined Usage Workflow:**
```bash
# 1. Set up multiple organizations
export GITHUB_ORG=statisticsnorway
export GITHUB_ORG_2=PxTools

# 2. Run individual tracking first
python advanced_contribution_tracker.py --days 30

# 3. Then run team analysis on the same period
python team_contribution_tracker.py --days 30 --top-teams 5

# 4. Compare individual vs team performance
# Individual CSV: advanced_contributions_30days_[timestamp].csv
# Team CSV: team_contributions_30days_[timestamp]_teams.csv
```

#### **Requirements:**
- Python 3.7+
- GitHub Personal Access Token with repo permissions
- Required packages: `requests`, `pandas`, `matplotlib`, `numpy`, `joblib`, `tabulate`

#### **Setup:**
1. **Set environment variables:**
   ```bash
   export GITHUB_TOKEN=your_token_here
   export GITHUB_ORG=your_primary_org
   export GITHUB_ORG_2=your_secondary_org  # Optional
   ```

2. **Configure `config.json`:**
   ```json
   {
     "users": {
       "github-username": "Display Name"
     },
     "teams": {
       "team-slug": "Team Display Name"
     }
   }
   ```

3. **Run the trackers:**
   - Individual: `python advanced_contribution_tracker.py`
   - Teams: `python team_contribution_tracker.py`

### Script History

The User Management folder previously contained legacy scripts (`org_total_commits.py` and `user_contributions.py`) that have been replaced by the comprehensive `advanced_contribution_tracker.py`. The new tracker provides all functionality of the legacy scripts plus enhanced features like caching, gamification, and flexible time periods.

## Configuration Files

- **`config.json`**: Contains organization settings and user mappings
- **`all-users.txt`**: Full name to username mappings for display purposes

## Output Files

### Individual Tracker Output:
- `advanced_contributions_[period]_[timestamp].csv`: Comprehensive individual contribution data with gamification scores

### Team Tracker Output:
- `team_contributions_[period]_[timestamp]_teams.csv`: Team summary with rankings, totals, and averages
- `team_contributions_[period]_[timestamp]_members_by_team.csv`: Individual members organized by team affiliation

## Cache Management

The advanced tracker uses intelligent file-based caching:
- **Location**: `CACHE/` directory
- **Expiry**: 24 hours
- **Benefits**: Significantly faster re-runs and reduced API calls
- **Management**: Use `--clear-cache` flag to reset

## Performance Notes

- **Initial runs**: May take several minutes depending on organization size
- **Cached runs**: Complete in seconds for repeated time periods
- **Rate limiting**: Built-in handling for GitHub API limits
- **Progress tracking**: Real-time feedback for long-running operations

Feel free to explore the scripts and customize them according to your specific organizational needs. Each script includes comprehensive error handling and detailed logging for troubleshooting.

