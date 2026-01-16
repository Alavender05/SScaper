import os
import pandas as pd
from datetime import datetime

# CONFIGURATION
REPO_DIR = "planningalerts_monorepo"
OUTPUT_FILE = "planning_scrapers_report.xlsx"

def scan_repositories():
    data = []
    
    # 1. Check if the directory exists
    if not os.path.exists(REPO_DIR):
        print(f"❌ Could not find directory: {REPO_DIR}")
        print("   Make sure you have run clone.py first!")
        return

    print(f"Scanning {REPO_DIR}...")

    # 2. Iterate through every folder (each folder is a scraper)
    for folder_name in sorted(os.listdir(REPO_DIR)):
        folder_path = os.path.join(REPO_DIR, folder_name)
        
        if os.path.isdir(folder_path):
            # Basic Info
            scraper_info = {
                "Scraper Name": folder_name,
                "Path": folder_path,
                "Has Ruby File": os.path.exists(os.path.join(folder_path, "scraper.rb")),
                "Has Python File": os.path.exists(os.path.join(folder_path, "scraper.py")),
                "File Count": len(os.listdir(folder_path))
            }
            
            # Attempt to read 'morph.yaml' if it exists (often contains description)
            morph_path = os.path.join(folder_path, "morph.yaml")
            if os.path.exists(morph_path):
                try:
                    with open(morph_path, "r") as f:
                        # Grab first few lines as a rough description
                        scraper_info["Config Found"] = "Yes"
                except:
                    scraper_info["Config Found"] = "Error reading"
            else:
                scraper_info["Config Found"] = "No"

            data.append(scraper_info)

    # 3. Save to Excel
    if data:
        df = pd.DataFrame(data)
        
        # Reorder columns for neatness
        cols = ["Scraper Name", "Has Ruby File", "Has Python File", "File Count", "Config Found", "Path"]
        df = df[cols]
        
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\n✅ Success! Report generated: {OUTPUT_FILE}")
        print(f"   Found {len(df)} scrapers.")
    else:
        print("⚠️  No subfolders found. Is the directory empty?")

if __name__ == "__main__":
    scan_repositories()