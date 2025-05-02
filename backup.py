#!/usr/bin/python3.12

import os
import sys
import tarfile
import datetime


def get_folder_size(folder_path):
    total_size = 0
    # Проходим по всем файлам в папке и ее подкаталогах
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def cleanup_old_backups(backup_dir, max_size):
    while get_folder_size(backup_dir) > max_size:
        files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))]
        if not files:
            break
        oldest_file = min(files, key=os.path.getmtime)
        os.remove(oldest_file)
        print(f"🗑 Удалён старый бэкап: {oldest_file}")


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("""
Usage: backup.py <source_dir> <backup_dir> [max_size_mb]

<source_dir>     Directory to back up         (required)
<backup_dir>     Directory to store backups   (required)
[max_size_mb]    Max size of backup dir in MB (optional, default: 50 MB)

Example:
    python3 backup.py /home/user/data /home/user/backups 100
""")
        return

    folder_to_backup = args[0].rstrip('/')                          # что архивировать
    backup_dir = args[1].rstrip('/')                                # куда сохранять архив
    max_backup_size_mb = 500

    if len(args) > 2:
        try:
            max_backup_size_mb = int(args[2])
        except ValueError:
            print(f"Error: Invalid max size value '{args[2]}'. It must be an integer.")
            return

    max_backup_size = max_backup_size_mb * 1024 * 1024              # Преобразуем в байты
    print(f"Backup will be stored in {backup_dir} and the maximum size is {max_backup_size:,} bytes ({max_backup_size_mb} MB).")

    if not os.path.isdir(folder_to_backup):
        print(f"Error: Source directory '{folder_to_backup}' does not exist.")
        return


    now = datetime.datetime.now()
    date_string = now.strftime("_%d.%m.%Y_%H-%M")

    os.makedirs(backup_dir, exist_ok=True)                              # создать директорию если ее нет    

    cleanup_old_backups(backup_dir, max_backup_size)                    # Удаляем старые бэкапы, если место превышает лимит


    folder_name = os.path.basename(folder_to_backup)
    backup_file_path = os.path.join(backup_dir, f"{folder_name}{date_string}.tar.gz")

    
    with tarfile.open(backup_file_path, "w:gz") as tar:
        tar.add(folder_to_backup, arcname=folder_name)

    print(f"✅ Backup saved to: {backup_file_path}")


if __name__ == "__main__":
    main()