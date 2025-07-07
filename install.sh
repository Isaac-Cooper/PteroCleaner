#!/bin/bash

set -e

echo "🔧 Installing PteroCleaner..."

# Prompt for API key (required)
read -p "Enter your Pterodactyl API key: " api_key
while [[ -z "$api_key" ]]; do
    echo "❗ API key is required!"
    read -p "Enter your Pterodactyl API key: " api_key
done

# Prompt for panel base URL (required, no default)
read -p "Enter your panel base URL (e.g. https://panel.example.com): " panel_url
while [[ -z "$panel_url" ]]; do
    echo "❗ Panel base URL is required!"
    read -p "Enter your panel base URL (e.g. https://panel.example.com): " panel_url
done

# Optional: backups folder with default
read -p "Enter path to the backups folder [/var/lib/pterodactyl/backups]: " backup_folder
backup_folder=${backup_folder:-/var/lib/pterodactyl/backups}

# Optional: scan interval
read -p "Enter scan interval in seconds [300]: " sleep_interval
sleep_interval=${sleep_interval:-300}

# Create config directory and write config.yml
sudo mkdir -p /etc/pterocleaner
sudo tee /etc/pterocleaner/config.yml > /dev/null <<EOF
api_key: "${api_key}"
panel_base_url: "${panel_url}"
backup_folder: "${backup_folder}"
sleep_interval: ${sleep_interval}
EOF

# Download main Python script
echo "📥 Downloading PteroCleaner..."
sudo curl -sL https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/pterocleaner.py -o /etc/pterocleaner/pterocleaner.py
sudo chmod +x /etc/pterocleaner/pterocleaner.py

# Install Python and dependencies
echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip
sudo pip3 install requests pyyaml

# Download systemd unit
echo "⚙️  Setting up systemd service..."
sudo curl -sL https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/pterocleaner.service -o /etc/systemd/system/pterocleaner.service

# Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable pterocleaner
sudo systemctl start pterocleaner

echo ""
echo "✅ PteroCleaner has been installed and is now running!"
echo "▶️ You can control it with:"
echo "   sudo systemctl start pterocleaner"
echo "   sudo systemctl stop pterocleaner"
echo "   sudo systemctl status pterocleaner"
echo ""
