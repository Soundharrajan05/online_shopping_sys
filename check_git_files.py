#!/usr/bin/env python3
"""
Check which files will be uploaded to GitHub
Shows what git will track and what will be ignored
"""

import os
import subprocess

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def main():
    print("=" * 70)
    print("GitHub Upload File Checker")
    print("=" * 70)
    print()
    
    # Check if git is initialized
    print("1. Checking if git is initialized...")
    output, code = run_command("git status")
    
    if code != 0:
        print("   ✗ Git is NOT initialized")
        print()
        print("   To initialize git, run:")
        print("   git init")
        print()
        return
    else:
        print("   ✓ Git is initialized")
        print()
    
    # Check tracked files
    print("2. Files that WILL be uploaded to GitHub:")
    print("-" * 70)
    
    # Get list of files that will be committed
    output, code = run_command("git ls-files")
    
    if output:
        files = output.split('\n')
        print(f"   Total: {len(files)} files")
        print()
        
        # Group by directory
        root_files = []
        app_files = []
        other_files = []
        
        for f in files:
            if '/' not in f:
                root_files.append(f)
            elif f.startswith('app/'):
                app_files.append(f)
            else:
                other_files.append(f)
        
        print("   Root level files:")
        for f in sorted(root_files):
            print(f"   ✓ {f}")
        
        print()
        print(f"   app/ directory: {len(app_files)} files")
        print("   (showing first 20)")
        for f in sorted(app_files)[:20]:
            print(f"   ✓ {f}")
        if len(app_files) > 20:
            print(f"   ... and {len(app_files) - 20} more files")
        
        if other_files:
            print()
            print("   Other files:")
            for f in sorted(other_files)[:10]:
                print(f"   ✓ {f}")
    else:
        print("   No files tracked yet. Run: git add .")
    
    print()
    print("-" * 70)
    
    # Check ignored files
    print()
    print("3. Files that will be IGNORED (not uploaded):")
    print("-" * 70)
    
    output, code = run_command("git status --ignored --short")
    
    if output:
        ignored = [line for line in output.split('\n') if line.startswith('!!')]
        if ignored:
            print(f"   Total: {len(ignored)} files/folders")
            print()
            for line in ignored[:20]:
                filename = line.replace('!! ', '')
                print(f"   ✗ {filename}")
            if len(ignored) > 20:
                print(f"   ... and {len(ignored) - 20} more")
        else:
            print("   No ignored files")
    else:
        print("   No ignored files")
    
    print()
    print("-" * 70)
    
    # Check for sensitive files
    print()
    print("4. Security check - Looking for sensitive files...")
    print("-" * 70)
    
    sensitive_files = ['.env', 'app_errors.log', '*.pyc', '__pycache__']
    found_sensitive = False
    
    output, code = run_command("git ls-files")
    if output:
        tracked = output.split('\n')
        for pattern in sensitive_files:
            for f in tracked:
                if pattern in f or f == pattern:
                    print(f"   ⚠️  WARNING: {f} is tracked (should be ignored!)")
                    found_sensitive = True
    
    if not found_sensitive:
        print("   ✓ No sensitive files found in tracked files")
    
    print()
    print("-" * 70)
    
    # Check required files
    print()
    print("5. Checking required files for Render deployment...")
    print("-" * 70)
    
    required_files = [
        'run.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'build.sh',
        'render.yaml',
        'config.py',
        'schema_postgresql.sql',
        'render_init.py',
        'seed_data.py',
        'app/__init__.py'
    ]
    
    all_present = True
    for f in required_files:
        if os.path.exists(f):
            print(f"   ✓ {f}")
        else:
            print(f"   ✗ MISSING: {f}")
            all_present = False
    
    print()
    print("=" * 70)
    
    if all_present:
        print("✓ All required files present!")
        print()
        print("Next steps:")
        print("1. Run: git add .")
        print("2. Run: git commit -m 'Initial commit'")
        print("3. Create GitHub repository")
        print("4. Run: git remote add origin YOUR_GITHUB_URL")
        print("5. Run: git push -u origin main")
    else:
        print("✗ Some required files are missing")
        print("Please create the missing files before uploading")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
