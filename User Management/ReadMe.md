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

#### **Gamification Scoring System:**
| Contribution Type | Scoring Rules |
|------------------|---------------|
| **Commits** | 2 points each (capped at 100 points) |
| **Pull Requests** | 5 points + merge rate bonus (up to 20 points) |
| **Code Reviews** | 3 points each + 1 point per review comment |
| **Collaboration** | Bonus points for helping team members |
| **Consistency** | Regular activity bonuses |

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

### Legacy Scripts

#### **org_total_commits.py**
Generates organization-wide contribution rankings with caching support for historical analysis.

#### **user_contributions.py** 
Tracks individual user contributions for the previous month with lines of code delta calculations.

## Configuration Files

- **`config.json`**: Contains organization settings and user mappings
- **`all-users.txt`**: Full name to username mappings for display purposes

## Output Files

All scripts generate timestamped CSV files with detailed metrics:
- `advanced_contributions_[period]_[timestamp].csv`: Comprehensive contribution data
- `org_total_commits_[timestamp].csv`: Organization-wide commit statistics
- `user_contributions_[timestamp].csv`: Monthly user contribution reports

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

