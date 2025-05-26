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

### 🚀 **New: Advanced GitHub Contribution Tracker**

The latest addition to A.C.E.S is a comprehensive GitHub contribution tracking system with:

#### **Key Features:**
- **Multi-source Data**: GraphQL API + REST API fallback for comprehensive data
- **Smart Caching**: 24-hour file-based cache for improved performance
- **Flexible Time Ranges**: Last N days or quarterly tracking (Q1, Q2, Q3, Q4)
- **Real-time Progress**: Visual progress bar with user feedback
- **Gamification System**: Points-based scoring for commits, PRs, reviews, and collaboration
- **Dynamic Leaderboards**: Top 100 users with full name support
- **Error Handling**: Comprehensive error reporting with HTTP status meanings

#### **Gamification Scoring:**
- **Commits**: 2 points each (capped at 100)
- **Pull Requests**: 5 points + merge rate bonus (up to 20 points)
- **Code Reviews**: 3 points each + 1 point per review comment
- **Collaboration**: Bonus points for helping team members
- **Consistency**: Regular activity bonuses

#### **Usage Examples:**
```bash
# Track last 30 days (default)
python "User Management/advanced_contribution_tracker.py"

# Track last 90 days
python "User Management/advanced_contribution_tracker.py" --days 90

# Track Q1 2025
python "User Management/advanced_contribution_tracker.py" --quarter Q1-2025

# Clear cache and run fresh
python "User Management/advanced_contribution_tracker.py" --clear-cache
```

## Installation

1. Clone the repository to your local machine using the following command:

   ```shell
   git clone https://github.com/your-username/aces.git
   ```

2. Set up Python virtual environment and install dependencies:

   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install required packages
   pip install -r requirements.txt
   ```

3. Set up environment variables (for GitHub tracking):

   ```bash
   # Set GitHub token for API access
   export GITHUB_TOKEN=your_github_token_here
   
   # Or create a .env file in the project root
   echo "GITHUB_TOKEN=your_github_token_here" > .env
   ```

4. Customize the scripts and configuration files to match your specific needs.

## Usage
Navigate to the desired category or specific task folder in the repository.

Review the documentation and README files associated with the script or code snippet you wish to use.

Modify the script parameters or code as required to suit your environment.

Execute the script or incorporate the code snippet into your existing workflow.

## Contributing
Contributions to A.C.E.S are welcome! If you have any ideas, improvements, or new scripts/snippets to add, please follow these steps:

1. Fork the repository.
2. Create a new branch with a descriptive name for your feature or improvement.
3. Make your changes and ensure they adhere to the repository's coding guidelines.
4. Test your changes thoroughly.
5. Commit your changes and push them to your forked repository.
6. Open a pull request, providing a clear and concise description of your changes.
7. Discuss and address any feedback or suggestions provided.

Your contributions will be reviewed, and once approved, they will be merged into the main repository.

## License
The A.C.E.S repository is licensed under the MIT License. You are free to use, modify, and distribute the code in this repository for personal and commercial purposes. However, please review the license file for complete details and limitations.

With A.C.E.S, take control of your administrative tasks, improve efficiency, and streamline your workflow. Feel free to explore the repository, utilize the scripts, and contribute to make it an even more powerful suite of tools. If you encounter any issues or have suggestions, don't hesitate to reach out. Happy automating!
