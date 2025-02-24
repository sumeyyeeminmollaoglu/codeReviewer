import os
import requests
import yaml
from mistralai import Mistral
import logging

# Load GitHub & Mistral API Keys
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-1]
OWNER = os.getenv("GITHUB_REPOSITORY_OWNER")

client = Mistral(api_key=MISTRAL_API_KEY)
model = "mistral-small-latest"


# Load YAML code review rules
def load_code_review_rules(file_path="rules.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


# Format YAML rules for Mistral AI
def format_rules_for_prompt(rules):
    formatted_rules = "### AI Code Review Rules:\n\n"
    for category, subrules in rules.items():
        formatted_rules += f"**{category.replace('_', ' ').capitalize()} Rules:**\n"
        for rule in subrules:
            formatted_rules += f"- {rule}\n"
        formatted_rules += "\n"
    return formatted_rules


# Get changed files in the PR
def get_pr_files():
    url = f"https://api.github.com/repos/sumeyyeeminmollaoglu/{REPO}/pulls/{PR_NUMBER}/files"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    try:
        files = response.json()
        if isinstance(files, list):  # ✅ Ensure it's a list before processing
            return files
        else:
            print("❌ Unexpected API response:", files)
            return []
    except Exception as e:
        print("❌ Error parsing GitHub API response:", str(e))
        return []


# Extract code from PR
def extract_code_from_pr():
    files = get_pr_files()
    code_snippets = []
    for file_info in files:
        if isinstance(file_info, dict) and "filename" in file_info and "patch" in file_info:
            if file_info["filename"].endswith(".py"):  # ✅ Ensure correct file format
                patch = file_info["patch"]  # ✅ Get changed code
                code_snippets.append(f"### File: {file_info['filename']}\n```python\n{patch}\n```\n")
        else:
            print("⚠️ Skipping invalid file entry:", file_info)

    return "\n".join(code_snippets) if code_snippets else "No Python files detected in PR."


# Post AI feedback as a GitHub comment
def post_github_comment(feedback):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"body": feedback}
    requests.post(url, json=data, headers=headers)


def main():
    # Load and format rules
    rules = load_code_review_rules()
    formatted_rules = format_rules_for_prompt(rules["code_review_rules"])

    # Extract code from PR
    code_to_review = extract_code_from_pr()
    if not code_to_review:
        post_github_comment("⚠️ No Python code detected in this PR.")
        return

    # Create AI prompt
    prompt = f"""
    You are an AI Code Reviewer. Follow these rules while reviewing the code:

    {formatted_rules}

    Now, review the following code:

    {code_to_review}
    """

    # Send request to Mistral AI
    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        ai_feedback = response.get("choices", [{}])[0].get("text", "").strip()
        post_github_comment(f"### 🧐 AI Code Review Feedback:\n{ai_feedback}")

    except Exception as e:
        post_github_comment(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
