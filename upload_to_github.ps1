# PowerShell script to upload project to GitHub
# Run this in PowerShell: .\upload_to_github.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "GitHub Upload Script - Online Shopping System" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if git is installed
Write-Host "Step 1: Checking if git is installed..." -ForegroundColor Yellow
$gitVersion = git --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Check if git is initialized
Write-Host "Step 2: Checking if git is initialized..." -ForegroundColor Yellow
$gitStatus = git status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Git is not initialized. Initializing now..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git is already initialized" -ForegroundColor Green
}
Write-Host ""

# Step 3: Check for required files
Write-Host "Step 3: Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "run.py",
    "requirements.txt",
    "Procfile",
    "runtime.txt",
    "build.sh",
    "render.yaml",
    "config.py",
    "app/__init__.py"
)

$allPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ MISSING: $file" -ForegroundColor Red
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Host ""
    Write-Host "✗ Some required files are missing. Please create them first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ All required files present" -ForegroundColor Green
Write-Host ""

# Step 4: Add files to git
Write-Host "Step 4: Adding files to git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Files added to git" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to add files" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: Show what will be committed
Write-Host "Step 5: Files to be committed:" -ForegroundColor Yellow
$filesToCommit = git diff --cached --name-only
$fileCount = ($filesToCommit | Measure-Object -Line).Lines
Write-Host "  Total files: $fileCount" -ForegroundColor Cyan
Write-Host ""

# Step 6: Commit
Write-Host "Step 6: Committing files..." -ForegroundColor Yellow
$commitMessage = "Initial commit - Online Shopping System for Render deployment"
git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Files committed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Commit failed or no changes to commit" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Check if remote exists
Write-Host "Step 7: Checking GitHub remote..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Remote already configured: $remoteUrl" -ForegroundColor Green
    Write-Host ""
    
    # Ask if user wants to push
    Write-Host "Do you want to push to GitHub now? (Y/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host ""
        Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
        
        # Check current branch
        $currentBranch = git branch --show-current
        Write-Host "Current branch: $currentBranch" -ForegroundColor Cyan
        
        # Push
        git push -u origin $currentBranch
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=" -NoNewline -ForegroundColor Green
            Write-Host ("=" * 69) -ForegroundColor Green
            Write-Host "✓ SUCCESS! Your code is now on GitHub!" -ForegroundColor Green
            Write-Host "=" -NoNewline -ForegroundColor Green
            Write-Host ("=" * 69) -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "1. Go to https://dashboard.render.com/" -ForegroundColor White
            Write-Host "2. Follow the guide in QUICK_START_RENDER.md" -ForegroundColor White
            Write-Host "3. Deploy your app!" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "✗ Push failed. Check your credentials and try again." -ForegroundColor Red
        }
    } else {
        Write-Host ""
        Write-Host "Skipped push. Run 'git push' manually when ready." -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ No remote configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please configure your GitHub repository:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Create a new repository on GitHub" -ForegroundColor White
    Write-Host "2. Copy the repository URL" -ForegroundColor White
    Write-Host "3. Run this command:" -ForegroundColor White
    Write-Host "   git remote add origin YOUR_GITHUB_URL" -ForegroundColor Yellow
    Write-Host "4. Run this command:" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or use GitHub Desktop for easier setup!" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
