# A.C.E.S Setup Guide

This guide will walk you through setting up the A.C.E.S (Admin Control and Efficiency Suite) on your local machine.

## 📋 Prerequisites

- **Python 3.7+** (Python 3.9+ recommended)
- **Git** for version control
- **GitHub Personal Access Token** with repository permissions
- **Command line access** (Terminal/PowerShell/Command Prompt)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/A.C.E.S.git
cd A.C.E.S
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your GitHub token
# GITHUB_TOKEN=your_actual_github_token_here
```

### 4. Set Up Configuration Files
```bash
# Copy configuration templates
cp "User Management/config.json.template" "User Management/config.json"
cp "User Management/all-users.txt.template" "User Management/all-users.txt"

# Edit config.json with your organization and users
# Edit all-users.txt with your user mappings
```

### 5. Test the Setup
```bash
# Test the advanced contribution tracker
python "User Management/advanced_contribution_tracker.py" --help

# Test with a small sample (last 7 days)
python "User Management/advanced_contribution_tracker.py" --days 7
```

## 🔧 Detailed Configuration

### GitHub Personal Access Token

1. **Go to GitHub Settings:**
   - Visit: https://github.com/settings/personal-access-tokens
   - Click "Generate new token"

2. **Configure Token:**
   - **Name**: "A.C.E.S Contribution Tracker"
   - **Expiration**: Choose appropriate duration
   - **Scopes**: Select `repo` permissions

3. **Save Token:**
   - Copy the generated token
   - Add to your `.env` file: `GITHUB_TOKEN=your_token_here`

### User Configuration

#### config.json Structure:
```json
{
  "org_name": "your-github-organization",
  "users": {
    "github-username": "Display Name"
  }
}
```

#### all-users.txt Format:
```
Full Name:github-username
John Doe:johndoe
Jane Smith:jsmith
```

### Organization Setup

1. **Update Organization Name:**
   - Edit `config.json` 
   - Set `org_name` to your GitHub organization

2. **Add Users:**
   - List all users you want to track
   - Use actual GitHub usernames
   - Provide display names for reports

## 🎯 Usage Examples

### Basic Usage
```bash
# Track last 30 days (default)
python "User Management/advanced_contribution_tracker.py"

# Track last 90 days
python "User Management/advanced_contribution_tracker.py" --days 90
```

### Quarterly Reports
```bash
# Q1 2025 (January - March)
python "User Management/advanced_contribution_tracker.py" --quarter Q1-2025

# Q4 2024 (October - December)  
python "User Management/advanced_contribution_tracker.py" --quarter Q4-2024

# Current year quarter (specify year if different)
python "User Management/advanced_contribution_tracker.py" --quarter Q2 --year 2024
```

### Cache Management
```bash
# Clear cache and run fresh
python "User Management/advanced_contribution_tracker.py" --clear-cache

# Run with fresh data for last 60 days
python "User Management/advanced_contribution_tracker.py" --clear-cache --days 60
```

## 📊 Understanding Output

### Console Output
- **Progress Bar**: Shows real-time tracking progress
- **Leaderboard**: Top contributors with scores
- **Error Messages**: Any issues with specific users

### CSV Reports
Generated files: `advanced_contributions_[period]_[timestamp].csv`

**Columns include:**
- User rank and identification
- Commit counts and scores
- Pull request metrics
- Code review participation
- Collaboration scores

## 🛠️ Troubleshooting

### Common Issues

#### "GITHUB_TOKEN not set"
```bash
# Check if token is in environment
echo $GITHUB_TOKEN

# If empty, check your .env file
cat .env

# Make sure .env is in project root directory
```

#### "config.json not found"
```bash
# Verify file exists
ls "User Management/config.json"

# If missing, copy from template
cp "User Management/config.json.template" "User Management/config.json"
```

#### "403 Forbidden" Errors
- **Token expired**: Generate new GitHub token
- **Rate limited**: Wait or use smaller user groups
- **Wrong permissions**: Ensure token has `repo` scope

#### "No contribution data found"
- **Check organization name**: Verify in config.json
- **Check usernames**: Ensure they exist in the organization
- **Check time period**: Try different date ranges

### Performance Issues

#### Slow Initial Runs
- **Normal behavior**: First runs fetch all data
- **Large organizations**: Consider processing in batches
- **Use caching**: Subsequent runs will be much faster

#### API Rate Limits
- **Built-in handling**: Script waits automatically
- **Reduce scope**: Process fewer users at once
- **Use cache**: Avoid repeated API calls

## 🔒 Security Considerations

### Local Development
- **Never commit** real configuration files
- **Use .env** for sensitive environment variables
- **Test with sample data** before production use

### Production Usage
- **Rotate tokens** regularly
- **Monitor API usage** to stay within limits
- **Backup configurations** securely offline

## 📁 File Structure

```
A.C.E.S/
├── .env                          # Your environment variables (not committed)
├── .env.template                 # Template for environment setup
├── config.json                   # Your configuration (not committed)
├── requirements.txt              # Python dependencies
├── User Management/
│   ├── config.json               # User configuration (not committed)
│   ├── config.json.template      # Template for user config
│   ├── all-users.txt             # User mappings (not committed)
│   ├── all-users.txt.template    # Template for user mappings
│   └── advanced_contribution_tracker.py
├── Security/
│   └── vulnerability_tracker.py
└── [other directories...]
```

## 🆘 Getting Help

### Documentation
- **README.md**: Project overview and features
- **CONTRIBUTING.md**: Development guidelines
- **SECURITY.md**: Security policies and best practices

### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community help
- **Documentation**: In-code comments and docstrings

## 🎉 You're Ready!

Once setup is complete, you should be able to:
- ✅ Track GitHub contributions for your organization
- ✅ Generate quarterly and custom date range reports
- ✅ View gamification scores and leaderboards
- ✅ Export detailed CSV reports for analysis

**Happy tracking! 🚀**