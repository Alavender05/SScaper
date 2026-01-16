import os
import re

REPO_DIR = "planningalerts_monorepo"

def fix_git_deps():
    print(f"🔧 Relaxing git dependencies in {REPO_DIR}...")
    count = 0
    
    for root, dirs, files in os.walk(REPO_DIR):
        if "Gemfile" in files:
            path = os.path.join(root, "Gemfile")
            with open(path, "r") as f:
                lines = f.readlines()
            
            new_lines = []
            changed = False
            
            for line in lines:
                # Target lines defining git sources: gem 'name', ... git: 'url' ...
                if "gem '" in line and "git:" in line:
                    # Regex to extract just the gem name and the git URL
                    match = re.search(r"gem ['\"]([^'\"]+)['\"].*git: ['\"]([^'\"]+)['\"]", line)
                    if match:
                        gem_name, git_url = match.groups()
                        # Replace the complex line with a simple one (fetches latest HEAD)
                        new_line = f"gem '{gem_name}', git: '{git_url}'\n"
                        
                        # Only apply if it actually simplifies the line
                        if new_line.strip() != line.strip():
                            new_lines.append(new_line)
                            changed = True
                            continue
                
                new_lines.append(line)
            
            if changed:
                with open(path, "w") as f:
                    f.writelines(new_lines)
                count += 1
                print(f"   Fixed: {os.path.basename(root)}")

    print(f"\n✅ Updated {count} Gemfiles to use latest library versions.")

if __name__ == "__main__":
    fix_git_deps()