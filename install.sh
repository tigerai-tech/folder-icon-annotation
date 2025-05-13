#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Folder Icon Annotation System Installer ===${NC}"
echo -e "${CYAN}This script will install the Folder Icon Annotation System and all its dependencies.${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/folder-icon-annotation"
echo -e "${CYAN}Installing to: ${YELLOW}$INSTALL_DIR${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Installation directory already exists. Updating...${NC}"
    cd "$INSTALL_DIR"
    if [ -d ".git" ]; then
        git pull
    else
        echo -e "${RED}Existing directory is not a git repository. Please backup and remove it first.${NC}"
        exit 1
    fi
else
    echo -e "${CYAN}Cloning repository...${NC}"
    git clone https://github.com/YOUR_USERNAME/folder-icon-annotation.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${CYAN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo -e "${CYAN}Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create shortcut script
SHORTCUT="$HOME/.local/bin/folder-icon-annotate"
mkdir -p "$(dirname "$SHORTCUT")"

cat > "$SHORTCUT" << 'EOF'
#!/bin/bash
cd "$HOME/folder-icon-annotation"
source venv/bin/activate
python main.py "$@"
EOF

chmod +x "$SHORTCUT"

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${CYAN}You can now run the tool with:${NC} ${YELLOW}folder-icon-annotate --interactive${NC}"
echo -e "${CYAN}Make sure ${YELLOW}$HOME/.local/bin${CYAN} is in your PATH.${NC}"

# Add PATH advice if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Consider adding the following to your shell profile (${HOME}/.bashrc or ${HOME}/.zshrc):${NC}"
    echo -e "${YELLOW}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
fi 