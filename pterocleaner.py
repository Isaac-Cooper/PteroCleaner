#!/usr/bin/env python3
import os
import re
import time
import yaml
import requests

# Load config
CONFIG_PATH = "/etc/pterocleaner/config.yml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

API_KEY = config["api_key"]
BACKUP_FOLDER = config["backup_folder"]
PANEL_BASE_URL = config["panel_base_url"]
SLEEP_INTERVAL = config.get("sleep_interval", 300)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_all_servers():
    servers = []
    url = f"{PANEL_BASE_URL}/api/application/servers"
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        servers += data["data"]
        url = data["meta"]["pagination"]["links"].get("next")
        print([srv["attributes"]["identifier"] for srv in servers])
    return [srv["attributes"]["identifier"] for srv in servers]  # Corrected: use identifier

def get_all_backups(server_identifier):
    backups = []
    url = f"{PANEL_BASE_URL}/api/client/servers/{server_identifier}/backups"
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code not in (200):
            print(f"⚠️  Skipping server {server_identifier}: {response.status_code} error.")
            break
        response.raise_for_status()
        data = response.json()
        backups += data["data"]
        url = data["meta"]["pagination"]["links"].get("next")
    return [backup["attributes"]["uuid"] for backup in backups]

def list_backup_files():
    return {
        match.group(1)
        for filename in os.listdir(BACKUP_FOLDER)
        if (match := re.match(r"([a-f0-9\-]{36})\.tar\.gz$", filename))
    }

def delete_orphaned_backups(orphaned_ids):
    for backup_id in orphaned_ids:
        file_path = os.path.join(BACKUP_FOLDER, f"{backup_id}.tar.gz")
        try:
            os.remove(file_path)
            print(f"🗑️  Deleted orphaned backup: {file_path}")
        except Exception as e:
            print(f"❌ Failed to delete {file_path}: {e}")

def main_loop():
    old_backup_ids = set()

    while True:
        try:
            while True:
                print("🔍 Scanning backups folder and checking API...")
        
                new_backup_ids = list_backup_files()
                shared_ids = old_backup_ids & new_backup_ids
        
                all_server_ids = get_all_servers()
                all_known_backup_ids = set()
        
                for server_id in all_server_ids:
                    backup_ids = get_all_backups(server_id)
                    all_known_backup_ids.update(backup_ids)
        
                orphaned = [
                    backup_id for backup_id in shared_ids
                    if backup_id not in all_known_backup_ids
                ]
        
                if orphaned:
                    print("🟠 Found orphaned backups not in API:")
                    for backup_id in orphaned:
                        print(f" - {backup_id}.tar.gz")
                    delete_orphaned_backups(orphaned)
                else:
                    print("✅ No orphaned backups found.")
        
                old_backup_ids = new_backup_ids
                print(f"⏳ Sleeping {SLEEP_INTERVAL} seconds...\n")
                time.sleep(SLEEP_INTERVAL)
        except Exception as E:
            print("🟠 Error: " + str(E))
            print(f"⏳ Sleeping 20 seconds...\n")
            time.sleep(20)
            

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
