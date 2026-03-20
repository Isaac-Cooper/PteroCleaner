#!/usr/bin/env python3
import os
import re
import time
import yaml
import mysql.connector

# Load config
CONFIG_PATH = "/etc/pterocleaner/config.yml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

BACKUP_FOLDER = config["backup_folder"]
SLEEP_INTERVAL = config.get("sleep_interval", 300)

DB_HOST = config["mysql_host"]
DB_USER = config["mysql_user"]
DB_PASS = config["mysql_pass"]
DB_NAME = config["mysql_db"]

# Optional dev-only dry run (hidden unless manually added)
DRY_RUN = config.get("dry_run", False)

# How many consecutive scans a backup must be "suspect" before deletion
CONFIRMATION_CYCLES = 5

# In-memory tracking of suspect counts: {uuid: count}
suspect_counts = {}

def db_connect():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

def get_valid_backups():
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.uuid
            FROM backups b
            JOIN servers s ON b.server_id = s.id
            WHERE b.deleted_at IS NULL
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {row[0] for row in rows}
    except Exception as e:
        print(f"❌ Database error while fetching valid backups: {e}")
        return None

def get_all_db_backups():
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT uuid FROM backups")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {row[0] for row in rows}
    except Exception as e:
        print(f"❌ Database error while fetching all backups: {e}")
        return None

def list_backup_files():
    uuids = set()
    try:
        for filename in os.listdir(BACKUP_FOLDER):
            match = re.match(r"([a-f0-9\-]{36})\.tar\.gz$", filename)
            if match:
                uuids.add(match.group(1))
    except Exception as e:
        print(f"❌ Error listing backup folder: {e}")
    return uuids

def delete_file(backup_id):
    file_path = os.path.join(BACKUP_FOLDER, f"{backup_id}.tar.gz")

    if DRY_RUN:
        print(f"🧪 [DRY-RUN] Would delete file: {file_path}")
        return

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"🗑️  Deleted file: {file_path}")
        except Exception as e:
            print(f"❌ Failed to delete file {file_path}: {e}")
    else:
        print(f"ℹ️  File for {backup_id} not found on disk, skipping file deletion.")

def delete_db_row(backup_id):
    if DRY_RUN:
        print(f"🧪 [DRY-RUN] Would delete DB row for backup {backup_id}")
        return

    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM backups WHERE uuid = %s", (backup_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"🗑️  Deleted DB row for backup {backup_id}")
    except Exception as e:
        print(f"⚠️  Could not delete DB row for {backup_id}: {e} (ignored)")

def process_deletions(suspects, disk_backups, db_backups_all, db_healthy):
    global suspect_counts

    # Absolute safety: do nothing if DB is unhealthy
    if not db_healthy:
        print("🚫 Skipping deletion processing due to DB issues.")
        suspect_counts.clear()
        return

    # Increment counts
    for uuid in suspects:
        suspect_counts[uuid] = suspect_counts.get(uuid, 0) + 1

    # Reset counts for no longer suspects
    current_suspects = set(suspects)
    for uuid in list(suspect_counts.keys()):
        if uuid not in current_suspects:
            del suspect_counts[uuid]

    # Process confirmed deletions
    for uuid, count in list(suspect_counts.items()):
        if count >= CONFIRMATION_CYCLES:
            print(f"🔴 Backup {uuid} confirmed orphaned after {count} scans.")

            if DRY_RUN:
                print(f"🧪 [DRY-RUN] Would delete backup {uuid}")

            # Delete file
            if uuid in disk_backups:
                delete_file(uuid)
            else:
                print(f"ℹ️  No file on disk for {uuid}, skipping file deletion.")

            # Delete DB row if safe
            if uuid in db_backups_all and uuid in disk_backups:
                delete_db_row(uuid)
            else:
                if uuid not in db_backups_all:
                    print(f"ℹ️  {uuid} not present in DB, skipping DB deletion.")
                elif uuid not in disk_backups:
                    print(f"ℹ️  {uuid} has no local file, keeping DB row (may be remote).")

            del suspect_counts[uuid]

def main_loop():
    if DRY_RUN:
        print("🧪 Running in DRY-RUN mode — no deletions will occur.")

    while True:
        try:
            print("🔍 Scanning backups (DB + filesystem)...")

            disk_backups = list_backup_files()
            valid_backups = get_valid_backups()
            db_backups_all = get_all_db_backups()

            db_healthy = valid_backups is not None and db_backups_all is not None

            if not db_healthy:
                print("🚫 Database unavailable — skipping this cycle.")
                suspect_counts.clear()
                time.sleep(20)
                continue

            # Orphan files (on disk but not in DB)
            orphan_files = disk_backups - db_backups_all

            # Invalid DB entries
            db_invalid = db_backups_all - valid_backups
            db_invalid_with_file = {uuid for uuid in db_invalid if uuid in disk_backups}

            suspects = orphan_files | db_invalid_with_file

            if suspects:
                print("🟠 Suspect backups detected:")
                for uuid in sorted(suspects):
                    print(f" - {uuid}.tar.gz")
            else:
                print("✅ No suspect backups this cycle.")

            process_deletions(suspects, disk_backups, db_backups_all, db_healthy)

            print(f"⏳ Sleeping {SLEEP_INTERVAL} seconds...\n")
            time.sleep(SLEEP_INTERVAL)

        except Exception as e:
            print(f"🟠 Error in main loop: {e}")
            print("⏳ Sleeping 20 seconds...\n")
            time.sleep(20)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
