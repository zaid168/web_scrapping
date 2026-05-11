from github import Github

# 🔐 Step 1: Authenticate (use YOUR token, not the leaked one)
TOKEN = "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"
g = Github(TOKEN)

# 📦 Step 2: Specify repository (owner/repo)
repo_name = "Muslim-Coders-Organisation/Sheikh-Bot"
repo = g.get_repo(repo_name)

# 📊 Step 3: Basic repository info
print("=== Repository Info ===")
print(f"Name: {repo.name}")
print(f"Full Name: {repo.full_name}")
print(f"Description: {repo.description}")
print(f"Stars: {repo.stargazers_count}")
print(f"Forks: {repo.forks_count}")
print(f"Open Issues: {repo.open_issues_count}")

# 👥 Step 4: Contributors
print("\n=== Contributors ===")
for contributor in repo.get_contributors():
    print(f"{contributor.login} ({contributor.contributions} contributions)")

# 📁 Step 5: List files in root directory
print("\n=== Files in Repo ===")
contents = repo.get_contents("")
for content in contents:
    print(content.name)

# 📝 Step 6: Recent commits
print("\n=== Recent Commits ===")
commits = repo.get_commits()[:5]  # latest 5 commits
for commit in commits:
    print(f"{commit.commit.author.name} - {commit.commit.message}")