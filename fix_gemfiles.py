import os

REPO_DIR = "planningalerts_monorepo"

def patch_gemfiles():
    print(f"🔧 Patching Gemfiles in {REPO_DIR}...")
    count = 0
    
    # Walk through all folders
    for root, dirs, files in os.walk(REPO_DIR):
        if "Gemfile" in files:
            file_path = os.path.join(root, "Gemfile")
            
            # Read the file
            with open(file_path, "r") as f:
                lines = f.readlines()
            
            # Filter out the specific 'ruby' version line
            new_lines = [line for line in lines if not line.strip().startswith("ruby ")]
            
            # If we changed something, write it back
            if len(lines) != len(new_lines):
                with open(file_path, "w") as f:
                    f.writelines(new_lines)
                count += 1
                print(f"   Fixed: {os.path.basename(root)}")

    print(f"\n✅ Successfully removed strict Ruby versions from {count} Gemfiles.")

if __name__ == "__main__":
    patch_gemfiles()