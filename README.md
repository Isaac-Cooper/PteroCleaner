# 🧹 PteroCleaner

**PteroCleaner** is a lightweight Python tool that automatically detects and deletes orphaned backup files from your Pterodactyl node.

It compares local backup files (e.g., `UUID.tar.gz`) in a specified folder with backups listed in the Pterodactyl Panel API. If a backup exists locally but not in the panel, and it persists for two consecutive scans, it will be automatically deleted.

Please Note: PteroCleaner may have bugs and may delete backups by accident, use at your own risk.
---

## 🚀 Features

- ⏱ Runs every N seconds (default: 5 minutes)
- 🔍 Detects orphaned backups that no longer exist in the Pterodactyl panel
- 🧼 Automatically deletes those backups to save space
- 🧠 Double-check system: only deletes if the orphan still exists after 1 full scan
- 🛠 Fully systemd-integrated for background operation
- 🧾 Configurable via `config.yml`
- 🐧 Linux support (Debian/Ubuntu)

---

## 📦 Installation

You can install PteroCleaner with a **single command**:

```bash
bash <(curl -s https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/install.sh)
```

This script will:

- Prompt you for your API key and panel URL
- Let you optionally configure scan interval and backup folder path
- Install Python and dependencies
- Set up a systemd service
- Start the cleaner in the background

**Ensure that the API KEY is a client api key that has administrator permissions.**

---

## ⚙️ Configuration

During install, a config file will be generated at:

```
/etc/pterocleaner/config.yml
```

Here’s what it looks like:

```yaml
api_key: "your_pterodactyl_client_api_key"
panel_base_url: "https://panel.example.com"
backup_folder: "/var/lib/pterodactyl/backups"
sleep_interval: 300  # time in seconds between scans
```

You can edit this file any time and restart the service to apply changes:

```bash
sudo systemctl restart pterocleaner
```

---

## 🧠 How It Works

1. Every N seconds, PteroCleaner scans `/var/lib/pterodactyl/backups` for `*.tar.gz` files.
2. It loads the list of **all server backups** via the Pterodactyl API (`/client/servers/{identifier}/backups`).
3. If a file exists in both the previous and current scan, but **is not present in the API**, it's considered orphaned.
4. That file is deleted.

It handles:

- ✅ Pagination from the API
- ✅ Multiple servers
- ✅ Invalid/missing backups gracefully

---

## 🔁 Systemd Integration

The systemd unit is called `pterocleaner`:

```bash
# Start the service
sudo systemctl start pterocleaner

# Stop the service
sudo systemctl stop pterocleaner

# Check status
sudo systemctl status pterocleaner

# Enable to start on boot
sudo systemctl enable pterocleaner
```

---

## ❓ Troubleshooting

### 🔐 Permission Errors
Ensure that the backup folder is readable and deletable by the user running the service (typically root).

### 🛑 Nothing is deleting
- Wait for two scan intervals: deletion only happens if the orphaned backup exists in **two consecutive scans**.
- Make sure the API key is a **Client API Key** that has **Administrator** access.
- Check the logs:

```bash
journalctl -u pterocleaner -f
```

---

## 🧪 Example Use Case

You’re running a node with `/var/lib/pterodactyl/backups` filling up. Over time, users delete backups via the panel — but the files aren't cleaned on disk. This script helps you safely and automatically clean those unused files.

---

## 📄 License

GNU General Public License v3.0 — feel free to use, modify, and contribute!

---

## 🤝 Contributing

Pull requests and issues are welcome. Be sure to:

- Keep logic simple
- Match existing style
- Test on Debian/Ubuntu

---

## 🧼 Keep your nodes clean — with **PteroCleaner**.
