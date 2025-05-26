# User Management

This folder contains advanced scripts and tools for GitHub organization management, user analytics, and contribution tracking. These scripts are designed to provide comprehensive insights into team productivity and collaboration patterns.

## 🚀 Featured Scripts

### Advanced GitHub Contribution Tracker
**File:** `advanced_contribution_tracker.py`

A comprehensive GitHub contribution tracking system with gamification, caching, and advanced analytics.

#### **Key Features:**
- **Multi-source Data Collection**: GraphQL API + REST API fallback
- **Smart Caching**: 24-hour file-based cache for optimal performance
- **Flexible Time Ranges**: Last N days or quarterly tracking (Q1, Q2, Q3, Q4)
- **Real-time Progress Tracking**: Visual progress bar with user feedback
- **Gamification System**: Points-based scoring for various contribution types
- **Dynamic Leaderboards**: Top 100 users with full name support
- **Comprehensive Error Handling**: Detailed error messages with HTTP status meanings

#### **Comprehensive Gamification Scoring System:**

Our scoring system is designed to provide a balanced assessment of both individual productivity and team collaboration. Here's how each metric is calculated and why it matters:

| Contribution Type | Scoring Rules | Data Source & Calculation Method |
|------------------|---------------|----------------------------------|
| **Commits** | 2 points each (capped at 100 points) | **Data:** GitHub GraphQL `totalCommitContributions`<br>**Method:** Direct count of commits authored in time period<br>**Cap Reasoning:** Prevents volume over quality; encourages meaningful commits |
| **Pull Requests** | 5 base points + merge rate bonus (up to 20 points) | **Data:** GitHub GraphQL `totalPullRequestContributions` + PR state analysis<br>**Calculation:** `(PRs_opened × 5) + (merge_rate × 20)`<br>**Merge Rate:** `PRs_merged / PRs_opened`<br>**Quality Focus:** Rewards PRs that get accepted by the team |
| **Code Reviews** | 3 points per review + 1 point per review comment | **Data:** GitHub GraphQL `totalPullRequestReviewContributions` + comment analysis<br>**Method:** Counts reviews submitted + comments made during reviews<br>**Team Value:** Recognizes time spent helping others improve their code |
| **Collaboration** | Combined review engagement score | **Data:** Review comments + issue discussions + PR feedback<br>**Calculation:** `(reviews_given × 3) + (review_comments × 1)`<br>**Purpose:** Measures investment in team success and knowledge sharing |
| **Consistency** | Regular activity bonus | **Data:** Distribution of commits over time period<br>**Calculation:** `min(commits_count × 0.5, 25)`<br>**Philosophy:** Steady contribution is more valuable than sporadic bursts |

#### **Data Collection Methodology:**

**🔍 Primary Data Sources:**
- **GitHub GraphQL API:** Comprehensive contribution data with precise metrics
- **GitHub REST API:** Fallback for detailed repository-level analysis
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

#### **Usage Examples:**
```bash
# Track last 30 days (default)
python advanced_contribution_tracker.py

# Track last 90 days
python advanced_contribution_tracker.py --days 90

# Track Q1 2025
python advanced_contribution_tracker.py --quarter Q1-2025

# Track Q4 2024
python advanced_contribution_tracker.py --quarter Q4-2024

# Clear cache and run fresh
python advanced_contribution_tracker.py --clear-cache
```

#### **Requirements:**
- Python 3.7+
- GitHub Personal Access Token with repo permissions
- Required packages: `requests`, `pandas`, `matplotlib`, `numpy`, `joblib`, `tabulate`

#### **Setup:**
1. Set environment variable: `export GITHUB_TOKEN=your_token_here`
2. Configure users in `config.json`
3. Ensure `all-users.txt` contains full name mappings
4. Run the script with desired parameters

### Script History

The User Management folder previously contained legacy scripts (`org_total_commits.py` and `user_contributions.py`) that have been replaced by the comprehensive `advanced_contribution_tracker.py`. The new tracker provides all functionality of the legacy scripts plus enhanced features like caching, gamification, and flexible time periods.

## Configuration Files

- **`config.json`**: Contains organization settings and user mappings
- **`all-users.txt`**: Full name to username mappings for display purposes

## Output Files

The tracker generates timestamped CSV files with detailed metrics:
- `advanced_contributions_[period]_[timestamp].csv`: Comprehensive contribution data with gamification scores

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

