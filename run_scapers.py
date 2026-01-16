import os
import subprocess
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
REPO_DIR = "planningalerts_monorepo"   # Where your scrapers are
OUTPUT_FILE = "combined_planning_data.xlsx"
LIMIT = 5  # Set to None to run ALL scrapers.

def run_command(command, cwd):
    """Runs a shell command in a specific directory."""
    try:
        subprocess.run(command, cwd=cwd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Command failed: {e.cmd}")
        # print(e.stderr) # Uncomment to see full error logs
        return False

def extract_data_from_sqlite(db_path, scraper_name):
    """Reads the 'swdata' table from the generated SQLite file."""
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        # Most scrapers save data to the 'swdata' table
        df = pd.read_sql_query("SELECT * FROM swdata", conn)
        conn.close()
        
        # Add a column so we know which scraper this came from
        df["source_scraper"] = scraper_name
        return df
    except Exception as e:
        print(f"    ⚠️  Could not read database: {e}")
        return None

def main():
    all_data = []
    processed_count = 0
    
    if not os.path.exists(REPO_DIR):
        print(f"❌ Directory '{REPO_DIR}' not found. Did you run clone.py?")
        return

    # Get list of folders
    scrapers = sorted([f for f in os.listdir(REPO_DIR) if os.path.isdir(os.path.join(REPO_DIR, f))])
    
    print(f"🚀 Found {len(scrapers)} scrapers. Starting execution (Limit: {LIMIT})...")

    for scraper_name in scrapers:
        if LIMIT and processed_count >= LIMIT:
            break
            
        scraper_path = os.path.abspath(os.path.join(REPO_DIR, scraper_name))
        
        # Detect Language
        is_ruby = os.path.exists(os.path.join(scraper_path, "scraper.rb"))
        is_python = os.path.exists(os.path.join(scraper_path, "scraper.py"))
        
        if not (is_ruby or is_python):
            continue # Skip non-scraper folders
            
        print(f"\nProcessing: {scraper_name}...")
        processed_count += 1
        
        # --- STEP 1: INSTALL DEPENDENCIES & RUN ---
        success = False
        if is_ruby:
            # Ruby: install gems then run
            if os.path.exists(os.path.join(scraper_path, "Gemfile")):
                print("    Installing Ruby gems...")
                run_command("bundle install", scraper_path)
            
            print("    Running scraper.rb (this may take time)...")
            success = run_command("bundle exec ruby scraper.rb", scraper_path)
            
        elif is_python:
            # Python: install requirements then run
            if os.path.exists(os.path.join(scraper_path, "requirements.txt")):
                print("    Installing Python requirements...")
                run_command("pip install -r requirements.txt", scraper_path)
                
            print("    Running scraper.py...")
            success = run_command("python scraper.py", scraper_path)

        # --- STEP 2: HARVEST DATA ---
        if success:
            db_file = os.path.join(scraper_path, "data.sqlite")
            df = extract_data_from_sqlite(db_file, scraper_name)
            
            if df is not None and not df.empty:
                print(f"    ✅ Captured {len(df)} records!")
                all_data.append(df)
            else:
                print("    ⚠️  Scraper ran but produced no data (or no data.sqlite found).")
        else:
            print("    ❌ Scraper execution failed.")

    # --- STEP 3: COMBINE & SAVE ---
    if all_data:
        print(f"\n📦 Merging {len(all_data)} datasets...")
        final_df = pd.concat(all_data, ignore_index=True)
        
        print(f"💾 Saving to {OUTPUT_FILE}...")
        final_df.to_excel(OUTPUT_FILE, index=False)
        print(f"✨ Done! Total records collected: {len(final_df)}")
    else:
        print("\n❌ No data collected. Check the error logs above.")

if __name__ == "__main__":
    main()