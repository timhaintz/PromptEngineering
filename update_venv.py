'''
Update all packages in the virtual environment

This script:
1. Captures all installed packages to requirements.txt
2. Updates all packages to their latest versions
3. Shows what was updated

Usage:
python update_venv.py [filter_option]

Examples:
python update_venv.py          # Update all packages
python update_venv.py a        # Update packages starting with 'a'
python update_venv.py abc      # Update packages starting with 'a', 'b', or 'c'
python update_venv.py d-o      # Update packages starting with any letter from 'd' through 'o'
python update_venv.py a,d-g    # Update packages starting with 'a' or any letter from 'd' through 'g'
'''

import os
import subprocess
import sys
import re

def parse_filter_option(filter_option):
    """Parse a filter option into a set of letters."""
    if not filter_option:
        return None
    
    letters = set()
    # Split by comma to handle multiple filters
    for part in filter_option.split(','):
        if '-' in part:  # Handle ranges like 'd-o'
            match = re.match(r'([a-z])-([a-z])', part.lower())
            if match:
                start, end = match.groups()
                # Add all letters in the range
                for char_code in range(ord(start), ord(end) + 1):
                    letters.add(chr(char_code))
        else:  # Handle individual letters
            for letter in part:
                letters.add(letter.lower())
    
    return letters if letters else None

def update_venv(filter_option=None):
    # Parse the filter option to get the set of letters
    filter_letters = parse_filter_option(filter_option)
    
    print("Capturing current packages to requirements.txt...")
    subprocess.run([sys.executable, "-m", "pip", "freeze", ">", "requirements.txt"], shell=True)
    
    print("Updating packages...")
    with open("requirements.txt", "r") as f:
        packages = f.readlines()
    
    updated = []
    skipped = []
    for pkg in packages:
        # Skip comments and empty lines
        if not pkg.strip() or pkg.strip().startswith('#'):
            continue
        
        # Remove version specifiers for full upgrade
        package_name = pkg.split('==')[0].strip()
        
        # Apply letter filter if specified
        if filter_letters and package_name and not any(package_name.lower().startswith(letter) for letter in filter_letters):
            skipped.append(package_name)
            continue
            
        if package_name:
            print(f"Updating {package_name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", package_name], 
                capture_output=True,
                text=True
            )
            if "Successfully installed" in result.stdout:
                updated.append(package_name)
    
    print(f"\nUpdated {len(updated)} packages:")
    for pkg in updated:
        print(f"  - {pkg}")
    
    if filter_letters:
        filter_display = filter_option if filter_option else ""
        print(f"\nSkipped {len(skipped)} packages not matching filter: {filter_display}")
    
    print("\nGenerating new requirements.txt with updated versions...")
    subprocess.run([sys.executable, "-m", "pip", "freeze", ">", "requirements_updated.txt"], shell=True)
    print("Done! Updated requirements saved to requirements_updated.txt")

if __name__ == "__main__":
    # Get filter option from command line arguments
    filter_option = None
    if len(sys.argv) > 1:
        filter_option = sys.argv[1]
    
    update_venv(filter_option)