#!/usr/bin/python3.12

import os
import sys
import tarfile
import datetime
from pathlib import Path
import filecmp
import shutil

def is_changed(dir1, dir2, ignore, check_flag = True):

    comparison = filecmp.dircmp(dir1, dir2, ignore=ignore)
    if comparison.left_only or comparison.right_only:
        check_flag = False
        return check_flag

    for common_file in comparison.common_files:
        file1 = dir1 / common_file
        file2 = dir2 / common_file
        if not filecmp.cmp(file1, file2, shallow=False):
            check_flag = False
            return check_flag

    for subdir in comparison.subdirs:
        if not (check_flag := is_changed(dir1 / subdir, dir2 / subdir, ignore, check_flag)):
            return check_flag

    return check_flag

def get_folder_size(folder_path):
    total_size = 0
    # Проходим по всем файлам в папке и ее подкаталогах
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def cleanup_old_backups(backup_folder, max_size):
    while get_folder_size(backup_folder) > max_size:
        files = [os.path.join(backup_folder, f) for f in os.listdir(backup_folder) if os.path.isfile(os.path.join(backup_folder, f))]
        if not files:
            break
        oldest_file = min(files, key=os.path.getmtime)
        os.remove(oldest_file)
        print(f"🗑 Удалён старый бэкап: {oldest_file}")


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("""
Usage: backup.py <source_dir> <backup_folder> [max_size_mb]

<source_dir>     Directory to back up         (required)
<backup_folder>     Directory to store backups   (required)
[max_size_mb]    Max size of backup dir in MB (optional, default: 50 MB)

Example:
    python3 backup.py /home/user/data /home/user/backups 100
""")
        return

    ignore = [".vscode", "__pycache__"]
    source_folder = Path(args[0].rstrip('/'))                          # что архивировать
    backup_folder = Path(args[1].rstrip('/'))                                # куда сохранять архив
    name_folder = source_folder.name
    max_backup_size_mb = 500

    if len(args) > 2:
        try:
            max_backup_size_mb = int(args[2])
        except ValueError:
            print(f"Error: Invalid max size value '{args[2]}'. It must be an integer.")
            return

    if not os.path.isdir(source_folder):
        print(f"Error: Source directory '{source_folder}' does not exist.")
        return

    os.makedirs(backup_folder, exist_ok=True)                              # создать директорию если ее нет    

    files = list(Path(backup_folder).glob('WebstormProjects_*.tar.gz'))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    if files:
        newest_tar = files[0]
        with tarfile.open(newest_tar, "r:gz") as tar:
            tar.extractall(path=backup_folder)
        path_tmp_backup = backup_folder / name_folder
        if is_changed(source_folder, path_tmp_backup, ignore):
            print("No changes detected.")
            shutil.rmtree(path_tmp_backup)
            return 1
        shutil.rmtree(path_tmp_backup)

    max_backup_size = max_backup_size_mb * 1024 * 1024                      # Преобразуем в байты
    print(f"Backup will be stored in {backup_folder} and the maximum size is {max_backup_size:,} bytes ({max_backup_size_mb} MB).")

    now = datetime.datetime.now()
    date_string = now.strftime("_%d.%m.%Y_%H-%M")


    cleanup_old_backups(backup_folder, max_backup_size)                     # Удаляем старые бэкапы, если место превышает лимит


    folder_name = os.path.basename(source_folder)
    backup_file_path = os.path.join(backup_folder, f"{folder_name}{date_string}.tar.gz")

    
    with tarfile.open(backup_file_path, "w:gz") as tar:
        tar.add(source_folder, arcname=folder_name)

    print(f"✅ Backup saved to: {backup_file_path}")


if __name__ == "__main__":
    main()