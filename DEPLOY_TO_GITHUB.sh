#!/bin/bash
# ============================================================================
# Deploy UBEM MCP to GitHub - Automated Script (Linux/Mac)
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if username provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: GitHub username required${NC}"
    echo "Usage: ./DEPLOY_TO_GITHUB.sh <github_username> [repo_name]"
    echo "Example: ./DEPLOY_TO_GITHUB.sh myusername ubem-mcp"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME=${2:-ubem-mcp}

echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}  UBEM Analysis MCP - GitHub Deployment Script${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}[ERROR] Git is not installed${NC}"
    echo "Please install Git first: https://git-scm.com/downloads"
    exit 1
fi

echo -e "${GREEN}[OK] Git found: $(git --version)${NC}"

# Update README
echo ""
echo -e "${YELLOW}[Step 1/6] Updating README.md...${NC}"
if [ -f "README.md" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" README.md
    sed -i.bak "s/ubem-mcp/$REPO_NAME/g" README.md
    rm README.md.bak 2>/dev/null
    echo -e "${GREEN}  [OK] README.md updated${NC}"
fi

# Update CHANGELOG
if [ -f "CHANGELOG.md" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" CHANGELOG.md
    sed -i.bak "s/ubem-mcp/$REPO_NAME/g" CHANGELOG.md
    rm CHANGELOG.md.bak 2>/dev/null
    echo -e "${GREEN}  [OK] CHANGELOG.md updated${NC}"
fi

# Update pyproject.toml
if [ -f "pyproject.toml" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" pyproject.toml
    sed -i.bak "s/ubem-mcp/$REPO_NAME/g" pyproject.toml
    rm pyproject.toml.bak 2>/dev/null
    echo -e "${GREEN}  [OK] pyproject.toml updated${NC}"
fi

# Update CONTRIBUTING.md
if [ -f "CONTRIBUTING.md" ]; then
    sed -i.bak "s/YOUR_USERNAME/$GITHUB_USERNAME/g" CONTRIBUTING.md
    sed -i.bak "s/ubem-mcp/$REPO_NAME/g" CONTRIBUTING.md
    rm CONTRIBUTING.md.bak 2>/dev/null
    echo -e "${GREEN}  [OK] CONTRIBUTING.md updated${NC}"
fi

# Initialize git
echo ""
echo -e "${YELLOW}[Step 2/6] Initializing Git repository...${NC}"
if [ -d ".git" ]; then
    echo -e "${CYAN}  [INFO] Git repository already initialized${NC}"
else
    git init
    echo -e "${GREEN}  [OK] Git repository initialized${NC}"
fi

# Add files
echo ""
echo -e "${YELLOW}[Step 3/6] Adding files to Git...${NC}"
git add .
echo -e "${GREEN}  [OK] Files added${NC}"

# Create commit
echo ""
echo -e "${YELLOW}[Step 4/6] Creating initial commit...${NC}"
git commit -m "Initial commit: UBEM Analysis MCP Server v1.0.0

- Complete MCP server with 6 tools
- Weather analysis, simulation, and data analysis tools
- Full documentation (English + Chinese)
- MIT License
- Ready for production use"

echo -e "${GREEN}  [OK] Commit created${NC}"

# Set main branch
echo ""
echo -e "${YELLOW}[Step 5/6] Setting up main branch...${NC}"
git branch -M main
echo -e "${GREEN}  [OK] Branch renamed to main${NC}"

# Add remote
echo ""
echo -e "${YELLOW}[Step 6/6] Adding GitHub remote...${NC}"
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git remote add origin $REMOTE_URL 2>/dev/null || git remote set-url origin $REMOTE_URL
echo -e "${GREEN}  [OK] Remote added: $REMOTE_URL${NC}"

# Final instructions
echo ""
echo -e "${CYAN}============================================================================${NC}"
echo -e "${GREEN}  READY TO PUSH!${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "${NC}1. Create a new repository on GitHub:${NC}"
echo -e "${CYAN}   - Go to: https://github.com/new${NC}"
echo -e "${CYAN}   - Repository name: $REPO_NAME${NC}"
echo -e "${CYAN}   - Description: Urban Building Energy Model Analysis MCP Server${NC}"
echo -e "${CYAN}   - Visibility: Public${NC}"
echo -e "${YELLOW}   - DO NOT initialize with README${NC}"
echo ""
echo -e "${NC}2. Then push your code:${NC}"
echo -e "${GREEN}   git push -u origin main${NC}"
echo ""
echo -e "${NC}3. (Optional) Create a release:${NC}"
echo -e "${CYAN}   - Go to: https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new${NC}"
echo -e "${CYAN}   - Tag: v1.0.0${NC}"
echo ""
echo -e "${YELLOW}Your repository URL will be:${NC}"
echo -e "${GREEN}  https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
echo ""
echo -e "${CYAN}============================================================================${NC}"

