# A.C.E.S - Admin Control and Efficiency Suite

A.C.E.S (Admin Control and Efficiency Suite) is a personal collection of scripts and code snippets designed to enhance training and administrative tasks. This repository serves as a centralized location for storing and organizing various tools that can streamline your workflow, increase productivity, and simplify administrative tasks.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

As an administrator or someone involved in training activities, you often encounter repetitive tasks that can be time-consuming and error-prone. A.C.E.S aims to address these challenges by providing a comprehensive suite of scripts and code snippets that automate common administrative tasks, improve efficiency, and promote control.

The repository is organized into different categories based on the nature of the tasks they help with. Whether you need to automate user management, generate reports, or perform data analysis, A.C.E.S has you covered.

## Features

- **User Management**: Advanced GitHub contribution tracking with gamification, user analytics, and organizational metrics
- **Security**: Vulnerability tracking and visualization tools with comprehensive reporting
- **Data Analysis**: Tools for analyzing data sets and generating insights for decision-making
- **Report Generation**: Custom report generation tools with CSV export capabilities
- **Task Automation**: Scripts to automate repetitive tasks, reducing manual effort and increasing efficiency

### 🚀 **New: Advanced GitHub Contribution & Team Tracking**

The latest addition to A.C.E.S includes both individual and team-based GitHub contribution tracking systems with:

#### **🔥 Individual Contribution Tracker**
- **Multi-source Data**: GraphQL API + REST API fallback for comprehensive data
- **Multi-Organization Support**: Track contributions across multiple GitHub organizations
- **Smart Caching**: 24-hour file-based cache for improved performance
- **Flexible Time Ranges**: Last N days or quarterly tracking (Q1, Q2, Q3, Q4)
- **Real-time Progress**: Visual progress bar with user feedback
- **Gamification System**: Points-based scoring for commits, PRs, reviews, and collaboration
- **Dynamic Leaderboards**: Top 100 users with full name support
- **Error Handling**: Comprehensive error reporting with HTTP status meanings

#### **⭐ NEW: Team Contribution Tracker**
- **Team-Based Rankings**: Aggregate individual scores into team leaderboards
- **Configurable Teams**: Only track teams specified in your configuration
- **Cross-Organization Teams**: Support teams from multiple GitHub organizations
- **Team Analytics**: Total scores, averages, and member breakdowns
- **Dual CSV Export**: Separate files for team summaries and member details

#### **Improved Scoring System:**
- **Commits**: 2 points each (capped at 100)
- **Pull Requests**: 5 points + up to 20 merge rate bonus
- **Code Reviews**: 3 points each + 1 per comment
- **Collaboration**: 10-35 bonus points for active reviewing (no longer double-counted)
- **Consistency**: 8 points per contribution type (max 24)

#### **Multi-Organization Support:**
```bash
# Set up multiple organizations
export GITHUB_ORG=my_primary_org
export GITHUB_ORG_2=my_secondary_org

# Individual tracking across both orgs
python "User Management/advanced_contribution_tracker.py" --days 30

# Team tracking across both orgs
python "User Management/team_contribution_tracker.py" --days 30
```


#### **Usage Examples:**
```bash
# Individual tracking (last 30 days, multiple orgs)
python "User Management/advanced_contribution_tracker.py"

# Team tracking with top 3 team details
python "User Management/team_contribution_tracker.py" --top-teams 3

# Track Q1 2025 for teams
python "User Management/team_contribution_tracker.py" --quarter Q1-2025

# Clear cache and run fresh
python "User Management/advanced_contribution_tracker.py" --clear-cache
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ (Python 3.9+ recommended)
- Git
- GitHub Personal Access Token

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/A.C.E.S.git
   cd A.C.E.S
   ```

2. **Set up Python environment:**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install required packages
   pip install -r requirements.txt
   ```

3. **Configure environment and settings:**
   ```bash
   # Set up environment variables
   export GITHUB_TOKEN=your_token_here
   export GITHUB_ORG=your_primary_org
   export GITHUB_ORG_2=your_secondary_org  # Optional
   
   ```

4. **Configure teams and users in config.json:**
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

5. **Test the setup:**
   ```bash
   # Test individual tracking
   python "User Management/advanced_contribution_tracker.py" --days 7
   
   # Test team tracking
   python "User Management/team_contribution_tracker.py" --days 7
   ```

## 🔒 Security & Privacy

**⚠️ This repository is PUBLIC** - strict security measures are in place:

- **PII Protection**: All personal data is excluded via .gitignore
- **Template System**: Example configurations use fictional data
- **Environment Variables**: Sensitive tokens stored locally only


## 📄 License

The A.C.E.S repository is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute the code in this repository for personal and commercial purposes. Please review the license file for complete details and limitations.

## 🎯 Project Goals

A.C.E.S aims to:
- **Automate** repetitive administrative tasks
- **Enhance** team productivity through data-driven insights  
- **Streamline** organizational workflows
- **Provide** actionable analytics for decision-making
- **Maintain** security and privacy standards

---

**With A.C.E.S, take control of your administrative tasks, improve efficiency, and streamline your workflow. Happy automating! 🎉**