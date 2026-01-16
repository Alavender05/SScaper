import os

REPO_DIR = "planningalerts_monorepo"

# Libraries removed in Ruby 3.4 that old scrapers likely need
MISSING_GEMS = ["nkf", "csv", "base64", "mutex_m", "bigdecimal"]

def modernize_gemfiles():
    print(f"🚑 Injecting Ruby 3.4 compatibility gems into {REPO_DIR}...")
    count = 0
    
    for root, dirs, files in os.walk(REPO_DIR):
        if "Gemfile" in files:
            file_path = os.path.join(root, "Gemfile")
            
            with open(file_path, "r") as f:
                content = f.read()
            
            updates = []
            for gem in MISSING_GEMS:
                # Only add if not already present
                if f"gem '{gem}'" not in content and f'gem "{gem}"' not in content:
                    updates.append(f"\ngem '{gem}'")
            
            if updates:
                with open(file_path, "a") as f:
                    f.writelines(updates)
                count += 1
                # print(f"   Updated: {os.path.basename(root)}")

    print(f"\n✅ Modernized {count} Gemfiles with Ruby 3.4 support.")

if __name__ == "__main__":
    modernize_gemfiles()