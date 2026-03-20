#!/bin/bash

set -e

echo "🔧 Installing PteroCleaner..."

# === Step 1: Prompt for config values ===

read -p "Enter MySQL host [127.0.0.1]: " mysql_host
mysql_host=${mysql_host:-127.0.0.1}

read -p "Enter MySQL database name: " mysql_db
while [[ -z "$mysql_db" ]]; do
    echo "❗ Database name is required!"
    read -p "Enter MySQL database name: " mysql_db
done

read -p "Enter MySQL username: " mysql_user
while [[ -z "$mysql_user" ]]; do
    echo "❗ MySQL username is required!"
    read -p "Enter MySQL username: " mysql_user
done

read -s -p "Enter MySQL password: " mysql_pass
echo ""
while [[ -z "$mysql_pass" ]]; do
    echo "❗ MySQL password is required!"
    read -s -p "Enter MySQL password: " mysql_pass
    echo ""
done

read -p "Enter path to the backups folder [/var/lib/pterodactyl/backups]: " backup_folder
backup_folder=${backup_folder:-/var/lib/pterodactyl/backups}

read -p "Enter scan interval in seconds [300]: " sleep_interval
sleep_interval=${sleep_interval:-300}

# === Step 2: Create config directory and config.yml ===
echo "📝 Writing config..."
sudo mkdir -p /etc/pterocleaner
sudo tee /etc/pterocleaner/config.yml > /dev/null <<EOF
mysql_host: "${mysql_host}"
mysql_db: "${mysql_db}"
mysql_user: "${mysql_user}"
mysql_pass: "${mysql_pass}"
backup_folder: "${backup_folder}"
sleep_interval: ${sleep_interval}
EOF

# === Step 3: Download Python script ===
echo "📥 Downloading PteroCleaner script..."
sudo curl -sL https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/pterocleaner.py -o /etc/pterocleaner/pterocleaner.py
sudo chmod +x /etc/pterocleaner/pterocleaner.py

# === Step 4: Install dependencies and create venv ===
echo "📦 Installing Python and virtual environment..."
if ! sudo apt update; then
    echo "⚠️ apt update failed — continuing anyway..."
fi
sudo apt install -y python3 python3-venv curl

echo "🐍 Creating virtual environment..."
sudo python3 -m venv /etc/pterocleaner/venv

echo "📦 Installing Python dependencies inside venv..."
sudo /etc/pterocleaner/venv/bin/pip install --upgrade pip
sudo /etc/pterocleaner/venv/bin/pip install pyyaml mysql-connector-python

# === Step 5: Download and install systemd service ===
echo "⚙️  Downloading systemd service file..."
sudo curl -sL https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/pterocleaner.service -o /etc/systemd/system/pterocleaner.service

# Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable pterocleaner
sudo systemctl start pterocleaner

echo ""
echo "✅ PteroCleaner has been installed and is now running!"
echo ""
echo "🔒 Note: Backups will NOT be deleted if the database is unreachable."
echo ""
echo "▶️ Manage it with:"
echo "   sudo systemctl start pterocleaner"
echo "   sudo systemctl stop pterocleaner"
echo "   sudo systemctl restart pterocleaner"
echo "   sudo systemctl status pterocleaner"
echo ""
