import os
import shutil
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
ORG_NAME = "planningalerts-scrapers"
OUTPUT_DIR = "planningalerts_monorepo"
GITHUB_TOKEN = None  # Optional: Add your token if you hit rate limits (e.g., "ghp_...")
MAX_WORKERS = 8      # Number of concurrent clones

def get_all_repos(org_name):
    """Fetches the list of all repos in the organization via GitHub API."""
    repos = []
    page = 1
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    print(f"🔍 Fetching repository list for {org_name}...")
    
    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error fetching API: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        if not data:
            break
            
        for repo in data:
            repos.append({
                "name": repo["name"],
                "clone_url": repo["clone_url"]
            })
        
        print(f"   Found {len(data)} repos on page {page}...")
        page += 1
        
    print(f"✅ Total repositories found: {len(repos)}\n")
    return repos

def process_repo(repo_info):
    """Clones a single repo and removes its .git folder."""
    name = repo_info["name"]
    url = repo_info["clone_url"]
    target_path = os.path.join(OUTPUT_DIR, name)
    
    # Skip if already exists
    if os.path.exists(target_path):
        return f"⏭️  Skipped {name} (already exists)"

    try:
        # Clone shallow copy (depth 1) to save bandwidth
        subprocess.run(
            ["git", "clone", "--depth", "1", url, target_path],
            check=True,
            stdout=subprocess.DEVNULL, # Silence standard output
            stderr=subprocess.DEVNULL
        )
        
        # Remove the internal .git directory to decouple history
        git_dir = os.path.join(target_path, ".git")
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
            
        return f"📥 Downloaded {name}"
        
    except subprocess.CalledProcessError:
        return f"❌ Failed to clone {name}"
    except Exception as e:
        return f"⚠️  Error processing {name}: {e}"

def main():
    # 1. Create Output Directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📂 Created directory: {OUTPUT_DIR}")

    # 2. Get list of repos
    repos = get_all_repos(ORG_NAME)
    if not repos:
        print("No repositories found. Exiting.")
        return

    # 3. Clone in parallel
    print(f"🚀 Starting download with {MAX_WORKERS} parallel workers...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(process_repo, repos)
        
        # Print results as they complete
        for result in results:
            print(result)

    # 4. Initialize new Monorepo
    print("\n📦 Initializing combined git repository...")
    os.chdir(OUTPUT_DIR)
    
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit: Combined all planningalerts scrapers"], check=True)
        print(f"\n✨ Success! All code combined in: {os.path.abspath('.')}")
    except Exception as e:
        print(f"⚠️  Could not finalize git repo: {e}")

if __name__ == "__main__":
    main() """Script to clone all repositories from a GitHub organization into a single monorepo."""