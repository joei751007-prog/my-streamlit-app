import sqlite3
from datetime import datetime, timezone, timedelta
import pandas as pd

DB_NAME = "tasks.db"

# 建立台灣時區 (UTC+8)
tw_tz = timezone(timedelta(hours=8))

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


# 新增任務

def add_task(name, url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (
            name,
            url,
            status,
            request_time,
            execute_time
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            url,
            "idle",
            "",
            ""
        )
    )

    conn.commit()
    conn.close()

# 取得所有任務

def get_tasks():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM tasks ORDER BY id DESC",
        conn
    )

    conn.close()

    return df

# 發送定位請求

def request_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    request_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE tasks
        SET status=?, request_time=?
        WHERE id=?
        """,
        (
            "pending",
            request_time,
            task_id
        )
    )

    conn.commit()
    conn.close()

# 完成任務

def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    execute_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE tasks
        SET status=?, execute_time=?
        WHERE id=?
        """,
        (
            "done",
            execute_time,
            task_id
        )
    )

    conn.commit()
    conn.close()

# 執行中

def running_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status=?
        WHERE id=?
        """,
        (
            "running",
            task_id
        )
    )

    conn.commit()
    conn.close()

# 刪除任務

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )

    conn.commit()
    conn.close()

# 更新 Robot 最後巡邏時間

def update_robot_check_time():

    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE system_status
        SET last_robot_check_time=?
        WHERE id=1
        """,
        (current_time,)
    )

    conn.commit()
    conn.close()

# 取得 Robot 最後巡邏時間

def get_robot_check_time():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT last_robot_check_time
        FROM system_status
        WHERE id=1
        """
    )

    result = cursor.fetchone()

    conn.close()

    return result[0]

# Robot 簽到

def robot_check_in():

    conn = get_connection()
    cursor = conn.cursor()

    current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        UPDATE system_status
        SET last_robot_check_time=?
        WHERE id=1
        """,
        (current_time,)
    )

    conn.commit()
    conn.close()
