# 🧹 PteroCleaner

**PteroCleaner** is a lightweight Python tool that automatically detects and deletes orphaned backup files from your Pterodactyl node.

Instead of relying on the panel API, it now directly compares local backup files with the **Pterodactyl database**, making detection more accurate and reliable.

> ⚠️ **Warning:** PteroCleaner may have bugs and could delete backups unintentionally. Use at your own risk.

---

## 🚀 Features

- ⏱ Runs every N seconds (default: 5 minutes)
- 🔍 Detects orphaned backups using the **database (MySQL)** instead of API
- 🧼 Automatically deletes unused backups to save disk space
- 🧠 Multi-check system: only deletes after multiple confirmation cycles (default: 5)
- 🔒 Safety-first design:
  - No deletions if database is unreachable
- 🧪 Hidden `dry_run` mode for safe testing
- 🛠 Fully systemd-integrated for background operation
- 🧾 Configurable via `config.yml`
- 🐧 Linux support (Debian/Ubuntu)

---

## 📦 Installation

Install with:

```bash
bash <(curl -s https://raw.githubusercontent.com/Isaac-Cooper/PteroCleaner/main/install.sh)
```

This will:
- Ask for MySQL credentials
- Configure paths and interval
- Install dependencies
- Create systemd service

---

## ⚙️ Configuration

Location:

```
/etc/pterocleaner/config.yml
```

Example:

```yaml
mysql_host: "127.0.0.1"
mysql_db: "panel"
mysql_user: "pterodactyl"
mysql_pass: "your_password"

backup_folder: "/var/lib/pterodactyl/backups"
sleep_interval: 300
```

Optional (not included by default):

```yaml
dry_run: true
```

When enabled:
- No deletions happen
- Only logs actions

---

## 🧠 How It Works

1. Scans backup directory for `*.tar.gz` files
2. Fetches:
   - Valid backups (linked + not deleted)
   - All backups in database
3. Detects:
   - Files not in DB (orphaned)
   - Invalid DB backups with local files
4. Tracks across multiple scans
5. Deletes only after confirmation threshold

---

## 🔒 Safety Features

- No database = no deletion
- Multi-cycle confirmation system
- Dry-run support for testing
- Skips:
  - Remote-only backups
  - Unknown states

---

## 🔁 Systemd Usage

```bash
sudo systemctl start pterocleaner
sudo systemctl stop pterocleaner
sudo systemctl restart pterocleaner
sudo systemctl status pterocleaner
sudo systemctl enable pterocleaner
```

---

## ❓ Troubleshooting

**Permission issues:**
Ensure access to backups folder

**Logs:**
```bash
journalctl -u pterocleaner -f
```

**Nothing deleting:**
- Wait multiple cycles
- Check DB credentials

**Database errors:**
- No deletion will occur
- Fix config.yml
- Ensure that the database is listening on 0.0.0.0 rather than 172.0.0.1

---

## 🧪 Example Use Case

Backups remain on disk after deletion in panel.  
This tool removes them safely over time.

---

## 📄 License

GNU GPL v3

---

## 🤝 Contributing

PRs welcome.  
Keep code simple and tested.

---

## 🧼 Keep your nodes clean — with PteroCleaner
