from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import subprocess
import os
from datetime import datetime
from typing import List
import glob

router = APIRouter()

# Configuration
BACKUP_DIR = os.path.join(os.getcwd(), "storage", "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# Database credentials (should be loaded from env in a real scenario, but reusing standard approach)
# Assuming these are available in environment or config. 
# For now, we will try to load from os.environ or use defaults consistent with .env file observed
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "reports")

import shutil

def get_mysql_command(command_name):
    """
    Finds the full path to a MySQL command (mysqldump or mysql).
    Checks system PATH first, then common installation directories.
    """
    # Check system PATH
    path = shutil.which(command_name)
    if path:
        return path
        
    # Check common paths
    common_paths = [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files\MySQL\MySQL Workbench 8.0",
        r"C:\laragon\bin\mysql\mysql-8.0.30-winx64\bin",
    ]
    
    for base_path in common_paths:
        full_path = os.path.join(base_path, f"{command_name}.exe")
        if os.path.exists(full_path):
            return full_path
            
    return command_name # Return original name to let subprocess fail naturally if not found

@router.post("/backup", summary="Create a database backup")
def create_backup():
    """
    Creates a backup of the database using mysqldump.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{DB_NAME}_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    # Command to run mysqldump
    mysqldump_cmd = get_mysql_command("mysqldump")
    
    cmd = [
        mysqldump_cmd,
        f"-h{DB_HOST}",
        f"-P{DB_PORT}",
        f"-u{DB_USER}",
    ]
    
    if DB_PASSWORD:
        cmd.append(f"-p{DB_PASSWORD}")
    
    cmd.append(DB_NAME)

    try:
        with open(filepath, "w") as f:
            process = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
        if process.returncode != 0:
            os.remove(filepath) # Clean up partial file
            raise Exception(f"Backup failed: {process.stderr}")
            
        return {
            "message": "Backup created successfully",
            "filename": filename,
            "path": filepath,
            "size": os.path.getsize(filepath)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backups", summary="List all backups")
def list_backups():
    """
    Lists all available backup files.
    """
    try:
        files = glob.glob(os.path.join(BACKUP_DIR, "*.sql"))
        files.sort(key=os.path.getmtime, reverse=True)
        
        backups = []
        for f in files:
            stats = os.stat(f)
            backups.append({
                "filename": os.path.basename(f),
                "created_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "size_bytes": stats.st_size
            })
            
        return backups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore/{filename}", summary="Restore database from backup")
def restore_backup(filename: str):
    """
    Restores the database from a specified backup file.
    WARNING: This will overwrite current data.
    """
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Backup file not found")
        
    # Command to restore
    mysql_cmd = get_mysql_command("mysql")
    cmd = [
        mysql_cmd,
        f"-h{DB_HOST}",
        f"-P{DB_PORT}",
        f"-u{DB_USER}",
    ]
    
    if DB_PASSWORD:
        cmd.append(f"-p{DB_PASSWORD}")
        
    cmd.append(DB_NAME)
    
    try:
        # We need to pipe the file content to the mysql command
        with open(filepath, "r") as f:
            process = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            
        if process.returncode != 0:
            raise Exception(f"Restore failed: {process.stderr}")
            
        return {"message": f"Database restored successfully from {filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
