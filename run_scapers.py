import os
import subprocess
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
REPO_DIR = "planningalerts_monorepo"
OUTPUT_FILE = "combined_planning_data.xlsx"
LIMIT = 0  # Try 10 first, then set to None for all

def run_command(command, cwd):
    try:
        # TIMEOUT added to prevent one council hanging forever (30 seconds install, 60s run)
        subprocess.run(command, cwd=cwd, shell=True, check=True, capture_output=True, text=True, timeout=120)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Failed: {e.stderr.strip().splitlines()[-1] if e.stderr else 'Unknown error'}")
        return False
    except subprocess.TimeoutExpired:
        print("    ⏳ Timed out!")
        return False

def extract_data_from_sqlite(db_path, scraper_name):
    if not os.path.exists(db_path): return None
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM swdata", conn)
        conn.close()
        df["source_scraper"] = scraper_name
        return df
    except: return None

def main():
    all_data = []
    processed_count = 0
    
    if not os.path.exists(REPO_DIR):
        print(f"❌ Directory '{REPO_DIR}' not found.")
        return

    scrapers = sorted([f for f in os.listdir(REPO_DIR) if os.path.isdir(os.path.join(REPO_DIR, f))])
    print(f"🚀 Found {len(scrapers)} scrapers. Starting execution (Limit: {LIMIT})...")

    for scraper_name in scrapers:
        if LIMIT and processed_count >= LIMIT: break
            
        scraper_path = os.path.abspath(os.path.join(REPO_DIR, scraper_name))
        has_gemfile = os.path.exists(os.path.join(scraper_path, "Gemfile"))
        has_ruby = os.path.exists(os.path.join(scraper_path, "scraper.rb"))
        
        if not has_ruby: continue
            
        print(f"\nProcessing: {scraper_name}...")
        processed_count += 1
        
        success = False
        if has_gemfile:
            # Use UPDATE to fix git dependencies
            print("    Updating gems...")
            if run_command("bundle update", scraper_path):
                print("    Running scraper...")
                success = run_command("bundle exec ruby scraper.rb", scraper_path)
        else:
            # Fallback for no Gemfile
            print("    Running scraper (no Gemfile)...")
            success = run_command("ruby scraper.rb", scraper_path)

        # Harvest Data
        db_file = os.path.join(scraper_path, "data.sqlite")
        df = extract_data_from_sqlite(db_file, scraper_name)
        if df is not None and not df.empty:
            print(f"    ✅ Captured {len(df)} records!")
            all_data.append(df)
        else:
            print("    ⚠️  No data found.")

    if all_data:
        print(f"\n📦 Merging {len(all_data)} datasets...")
        try:
            final_df = pd.concat(all_data, ignore_index=True)
            final_df.to_excel(OUTPUT_FILE, index=False)
            print(f"✨ Done! Saved to {OUTPUT_FILE}")
        except Exception as e:
            print(f"❌ Error saving Excel: {e}")
            # Fallback to CSV if Excel fails
            final_df.to_csv("combined_planning_data.csv", index=False)
            print("Saved as CSV instead.")

if __name__ == "__main__":
    main()