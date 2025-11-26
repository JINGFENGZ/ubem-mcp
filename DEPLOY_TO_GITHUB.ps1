# ============================================================================
# Deploy UBEM MCP to GitHub - Automated Script
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$GithubUsername,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "ubem-mcp"
)

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  UBEM Analysis MCP - GitHub Deployment Script" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "[OK] Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# Update README with username
Write-Host ""
Write-Host "[Step 1/6] Updating README.md with your GitHub username..." -ForegroundColor Yellow

$readmePath = "README.md"
if (Test-Path $readmePath) {
    $content = Get-Content $readmePath -Raw
    $content = $content -replace "YOUR_USERNAME", $GithubUsername
    $content = $content -replace "https://github.com/YOUR_USERNAME/ubem-mcp", "https://github.com/$GithubUsername/$RepoName"
    Set-Content $readmePath -Value $content -NoNewline
    Write-Host "  [OK] README.md updated" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] README.md not found" -ForegroundColor Yellow
}

# Update CHANGELOG
$changelogPath = "CHANGELOG.md"
if (Test-Path $changelogPath) {
    $content = Get-Content $changelogPath -Raw
    $content = $content -replace "YOUR_USERNAME", $GithubUsername
    $content = $content -replace "ubem-mcp", $RepoName
    Set-Content $changelogPath -Value $content -NoNewline
    Write-Host "  [OK] CHANGELOG.md updated" -ForegroundColor Green
}

# Update pyproject.toml
$pyprojectPath = "pyproject.toml"
if (Test-Path $pyprojectPath) {
    $content = Get-Content $pyprojectPath -Raw
    $content = $content -replace "YOUR_USERNAME", $GithubUsername
    $content = $content -replace "ubem-mcp", $RepoName
    Set-Content $pyprojectPath -Value $content -NoNewline
    Write-Host "  [OK] pyproject.toml updated" -ForegroundColor Green
}

# Update CONTRIBUTING.md
$contributingPath = "CONTRIBUTING.md"
if (Test-Path $contributingPath) {
    $content = Get-Content $contributingPath -Raw
    $content = $content -replace "YOUR_USERNAME", $GithubUsername
    $content = $content -replace "ubem-mcp", $RepoName
    Set-Content $contributingPath -Value $content -NoNewline
    Write-Host "  [OK] CONTRIBUTING.md updated" -ForegroundColor Green
}

# Initialize git repository
Write-Host ""
Write-Host "[Step 2/6] Initializing Git repository..." -ForegroundColor Yellow

if (Test-Path ".git") {
    Write-Host "  [INFO] Git repository already initialized" -ForegroundColor Cyan
} else {
    git init
    Write-Host "  [OK] Git repository initialized" -ForegroundColor Green
}

# Add all files
Write-Host ""
Write-Host "[Step 3/6] Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "  [OK] Files added" -ForegroundColor Green

# Create initial commit
Write-Host ""
Write-Host "[Step 4/6] Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: UBEM Analysis MCP Server v1.0.0

- Complete MCP server with 6 tools
- Weather analysis, simulation, and data analysis tools
- Full documentation (English + Chinese)
- MIT License
- Ready for production use"

Write-Host "  [OK] Commit created" -ForegroundColor Green

# Set main branch
Write-Host ""
Write-Host "[Step 5/6] Setting up main branch..." -ForegroundColor Yellow
git branch -M main
Write-Host "  [OK] Branch renamed to main" -ForegroundColor Green

# Add remote
Write-Host ""
Write-Host "[Step 6/6] Adding GitHub remote..." -ForegroundColor Yellow
$remoteUrl = "https://github.com/$GithubUsername/$RepoName.git"
git remote add origin $remoteUrl 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [INFO] Remote already exists, updating..." -ForegroundColor Cyan
    git remote set-url origin $remoteUrl
}

Write-Host "  [OK] Remote added: $remoteUrl" -ForegroundColor Green

# Display final instructions
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  READY TO PUSH!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create a new repository on GitHub:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "   - Repository name: $RepoName" -ForegroundColor Cyan
Write-Host "   - Description: Urban Building Energy Model Analysis MCP Server" -ForegroundColor Cyan
Write-Host "   - Visibility: Public" -ForegroundColor Cyan
Write-Host "   - DO NOT initialize with README (we already have one)" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Then push your code:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Green
Write-Host ""
Write-Host "   If you have 2FA enabled, use a Personal Access Token:" -ForegroundColor Yellow
Write-Host "   - Create token at: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host "   - Scopes needed: repo" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. (Optional) Create a release:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/$GithubUsername/$RepoName/releases/new" -ForegroundColor Cyan
Write-Host "   - Tag: v1.0.0" -ForegroundColor Cyan
Write-Host "   - Title: UBEM Analysis MCP Server v1.0.0" -ForegroundColor Cyan
Write-Host "   - Description: See CHANGELOG.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your repository URL will be:" -ForegroundColor Yellow
Write-Host "  https://github.com/$GithubUsername/$RepoName" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan

