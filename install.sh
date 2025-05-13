#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Folder Icon Annotation System Installer for Colab ===${NC}"

# Create installation directory
INSTALL_DIR="/content/folder-icon-annotation"
echo -e "${CYAN}Installing to: ${YELLOW}$INSTALL_DIR${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Installation directory already exists. Updating...${NC}"
    cd "$INSTALL_DIR"
    if [ -d ".git" ]; then
        git pull
    else
        echo -e "${RED}Existing directory is not a git repository. Removing and reinstalling...${NC}"
        cd /content
        rm -rf "$INSTALL_DIR"
        git clone https://github.com/tigerai-tech/folder-icon-annotation.git "$INSTALL_DIR"
    fi
else
    echo -e "${CYAN}Cloning repository...${NC}"
    git clone https://github.com/tigerai-tech/folder-icon-annotation.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Install dependencies directly (no venv needed in Colab)
echo -e "${CYAN}Installing dependencies...${NC}"
if [ -f "$INSTALL_DIR/requirements-colab.txt" ]; then
    pip install -r requirements-colab.txt
else
    pip install -r requirements.txt
fi

# Create a simple Python wrapper for non-interactive usage
cat > "$INSTALL_DIR/run_colab.py" << 'EOF'
#!/usr/bin/env python
import os
import sys
import argparse
from main import setup_environment, full_process_flow, classification_flow, tagging_flow

def main():
    """Non-interactive runner for Colab environment"""
    parser = argparse.ArgumentParser(description='Folder Icon Annotation Tool for Colab')
    parser.add_argument('--env', type=str, default='dev', help='Environment (dev, prod)')
    parser.add_argument('--url', type=str, help='URL to crawl')
    parser.add_argument('--classify', action='store_true', help='Run classification only')
    parser.add_argument('--tag', action='store_true', help='Run tagging only')
    parser.add_argument('--config', type=str, help='Override a config value in format space.key=value')
    
    args = parser.parse_args()
    
    # Setup environment
    config_holder = setup_environment(args.env)
    
    # Handle config override if provided
    if args.config and '=' in args.config:
        key_path, value = args.config.split('=', 1)
        if '.' in key_path:
            space, key = key_path.split('.', 1)
            
            # Try to convert value to appropriate type
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                value = float(value)
                
            # Update config
            try:
                config = config_holder.get_config(space)
                if '.' in key:
                    # Handle nested keys
                    parts = key.split('.')
                    current = config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    config[key] = value
                print(f"Updated config: {space}.{key} = {value}")
            except Exception as e:
                print(f"Error updating config: {e}")
    
    # Print current configuration
    print("\n=== Current Configuration ===")
    try:
        app_config = config_holder.get_config('application')
        print("\nApplication Config:")
        for key, value in app_config.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error loading application config: {e}")
        
    try:
        tagger_config = config_holder.get_config('tagger')
        print("\nTagger Config:")
        for key, value in tagger_config.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error loading tagger config: {e}")
    
    # Run the requested flow
    if args.url:
        print("\nRunning full process flow...")
        full_process_flow(args.url)
    elif args.classify:
        print("\nRunning classification flow...")
        classification_flow()
    elif args.tag:
        print("\nRunning tagging flow...")
        tagging_flow()
    else:
        print("\nNo action specified. Please use --url, --classify, or --tag")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x "$INSTALL_DIR/run_colab.py"

# Create a simple notebook for Colab usage
cat > "$INSTALL_DIR/colab_demo.ipynb" << 'EOF'
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github"
      },
      "source": [
        "# Folder Icon Annotation System - Colab Demo\n",
        "\n",
        "This notebook demonstrates how to use the Folder Icon Annotation System in Google Colab."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "source": [
        "# Install the package\n",
        "!curl -fsSL https://raw.githubusercontent.com/tigerai-tech/folder-icon-annotation/main/install-colab.sh -o install-colab.sh && chmod +x install-colab.sh && ./install-colab.sh"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## View Configuration\n",
        "\n",
        "Let's first check the current configuration:"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "source": [
        "# View the current configuration\n",
        "!python /content/folder-icon-annotation/run_colab.py --tag"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Upload Images\n",
        "\n",
        "You can upload images to be annotated:"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "source": [
        "from google.colab import files\n",
        "import os\n",
        "\n",
        "# Create input directory if it doesn't exist\n",
        "input_dir = \"/content/folder-icon-annotation/data/input\"\n",
        "os.makedirs(input_dir, exist_ok=True)\n",
        "\n",
        "# Upload files\n",
        "uploaded = files.upload()\n",
        "\n",
        "# Move uploaded files to input directory\n",
        "for filename in uploaded.keys():\n",
        "    with open(f\"{input_dir}/{filename}\", 'wb') as f:\n",
        "        f.write(uploaded[filename])\n",
        "    print(f\"Uploaded {filename} to {input_dir}\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Run Tag Flow\n",
        "\n",
        "Now let's run the tagging flow to annotate the uploaded images:"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "source": [
        "# Run the tagging flow\n",
        "!python /content/folder-icon-annotation/run_colab.py --tag"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## Change Configuration\n",
        "\n",
        "You can also change configuration values:"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "source": [
        "# Example: Change the tagger provider\n",
        "!python /content/folder-icon-annotation/run_colab.py --config application.tagger.use_provider=blip"
      ]
    }
  ],
  "metadata": {
    "colab": {
      "collapsed_sections": [],
      "name": "Folder Icon Annotation Demo",
      "provenance": []
    },
    "kernelspec": {
      "display_name": "Python 3",
      "name": "python3"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 0
}
EOF

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${CYAN}You can now run the tool with:${NC}"
echo -e "${YELLOW}python /content/folder-icon-annotation/run_colab.py --tag${NC}"
echo -e "${YELLOW}python /content/folder-icon-annotation/run_colab.py --classify${NC}"
echo -e "${YELLOW}python /content/folder-icon-annotation/run_colab.py --url https://example.com${NC}"
echo -e "${YELLOW}python /content/folder-icon-annotation/run_colab.py --config application.tagger.use_provider=blip${NC}"
echo -e "${CYAN}or open the demo notebook:${NC} ${YELLOW}/content/folder-icon-annotation/colab_demo.ipynb${NC}" 