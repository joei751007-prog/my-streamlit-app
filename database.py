from datetime import datetime, timezone, timedelta
import pandas as pd
from supabase_client import supabase

# =========================
# 台灣時間
# =========================
tw_tz = timezone(timedelta(hours=8))

# =========================
# 新增任務
# =========================
def add_task(name, url):
    supabase.table("tasks").insert({
        "name": name,
        "url": url,
        "status": "idle",
        "request_time": "",
        "execute_time": ""
    }).execute()


# =========================
# 取得所有任務
# =========================
def get_tasks():
    res = supabase.table("tasks") \
        .select("*") \
        .order("id", desc=True) \
        .execute()

    data = res.data or []

    # Streamlit 相容 DataFrame
    return pd.DataFrame(data)


# =========================
# 發送定位請求
# =========================
def request_task(task_id):
    request_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    supabase.table("tasks") \
        .update({
            "status": "pending",
            "request_time": request_time
        }) \
        .eq("id", task_id) \
        .execute()


# =========================
# 執行中
# =========================
def running_task(task_id):
    supabase.table("tasks") \
        .update({
            "status": "running"
        }) \
        .eq("id", task_id) \
        .execute()


# =========================
# 完成任務
# =========================
def complete_task(task_id):
    execute_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    supabase.table("tasks") \
        .update({
            "status": "done",
            "execute_time": execute_time
        }) \
        .eq("id", task_id) \
        .execute()


# =========================
# 刪除任務
# =========================
def delete_task(task_id):
    supabase.table("tasks") \
        .delete() \
        .eq("id", task_id) \
        .execute()


# =========================
# Robot 最後巡邏時間（更新）
# =========================
def update_robot_check_time():
    current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    supabase.table("system_status") \
        .update({
            "last_robot_check_time": current_time
        }) \
        .eq("id", 1) \
        .execute()


# =========================
# Robot 最後巡邏時間（讀取）
# =========================
def get_robot_check_time():
    res = supabase.table("system_status") \
        .select("last_robot_check_time") \
        .eq("id", 1) \
        .single() \
        .execute()

    return res.data.get("last_robot_check_time", "")


# =========================
# Robot 簽到（同 update）
# =========================
def robot_check_in():
    update_robot_check_time()
