#!/bin/bash

set -e

echo "🔧 Installing PteroCleaner..."

# === Step 1: Prompt for config values ===
read -p "Enter your Pterodactyl API key: " api_key
while [[ -z "$api_key" ]]; do
    echo "❗ API key is required!"
    read -p "Enter your Pterodactyl API key: " api_key
done

read -p "Enter your panel base URL (e.g. https://panel.example.com): " panel_url
while [[ -z "$panel_url" ]]; do
    echo "❗ Panel base URL is required!"
    read -p "Enter your panel base URL (e.g. https://panel.example.com): " panel_url
done

read -p "Enter path to the backups folder [/var/lib/pterodactyl/backups]: " backup_folder
backup_folder=${backup_folder:-/var/lib/pterodactyl/backups}

read -p "Enter scan interval in seconds [300]: " sleep_interval
sleep_interval=${sleep_interval:-300}

# === Step 2: Create config directory and config.yml ===
sudo mkdir -p /etc/pterocleaner
sudo tee /etc/pterocleaner/config.yml > /dev/null <<EOF
api_key: "${api_key}"
panel_base_url: "${panel_url}"
backup_folder: "${backup_folder}"
sleep_interval: ${sleep_interval}
EOF

# === Step 3: Download Python script ===
echo "📥 Downloading PteroCleaner script..."
sudo curl -sL https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/pterocleaner.py -o /etc/pterocleaner/pterocleaner.py
sudo chmod +x /etc/pterocleaner/pterocleaner.py

# === Step 4: Install dependencies and create venv ===
echo "📦 Installing Python and virtual environment..."
sudo apt update
sudo apt install -y python3 python3-venv curl

echo "🐍 Creating virtual environment..."
sudo python3 -m venv /etc/pterocleaner/venv

echo "📦 Installing Python dependencies inside venv..."
sudo /etc/pterocleaner/venv/bin/pip install --upgrade pip
sudo /etc/pterocleaner/venv/bin/pip install requests pyyaml

# === Step 5: Download and install systemd service ===
echo "⚙️  Downloading systemd service file..."
sudo curl -sL https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/pterocleaner.service -o /etc/systemd/system/pterocleaner.service

# Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable pterocleaner
sudo systemctl start pterocleaner

echo ""
echo "✅ PteroCleaner has been installed and is now running in a virtual environment!"
echo "▶️ Manage it with:"
echo "   sudo systemctl start pterocleaner"
echo "   sudo systemctl stop pterocleaner"
echo "   sudo systemctl restart pterocleaner"
echo "   sudo systemctl status pterocleaner"
echo ""
