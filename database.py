from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
from supabase_client import supabase

# =========================
# 台灣時間
# =========================
tw_tz = timezone(timedelta(hours=8))

# =========================
# 新增任務
# =========================
def add_task(name, url):
    try:
        supabase.table("tasks").insert({
            "name": name,
            "url": url,
            "status": "idle",
            "request_time": "",
            "execute_time": ""
        }).execute()
    except Exception as e:
        st.error(f"資料庫新增任務失敗: {e}")

# =========================
# 取得所有任務
# =========================
def get_tasks():
    try:
        res = supabase.table("tasks") \
            .select("*") \
            .order("id", desc=True) \
            .execute()

        data = res.data or []
        
        # 即使是空的，也確保回傳帶有正確欄位的 DataFrame，避免前端報錯
        if not data:
            return pd.DataFrame(columns=["id", "name", "url", "status", "request_time", "execute_time"])
            
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"資料庫讀取任務失敗: {e}")
        return pd.DataFrame(columns=["id", "name", "url", "status", "request_time", "execute_time"])

# =========================
# 發送定位請求
# =========================
def request_task(task_id):
    try:
        request_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

        supabase.table("tasks") \
            .update({
                "status": "pending",
                "request_time": request_time
            }) \
            .eq("id", task_id) \
            .execute()
    except Exception as e:
        st.error(f"發送定位請求失敗: {e}")

# =========================
# 執行中
# =========================
def running_task(task_id):
    try:
        supabase.table("tasks") \
            .update({
                "status": "running"
            }) \
            .eq("id", task_id) \
            .execute()
    except Exception as e:
        print(f"變更任務狀態為執行中失敗 (ID: {task_id}): {e}")

# =========================
# 完成任務
# =========================
def complete_task(task_id):
    try:
        execute_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

        supabase.table("tasks") \
            .update({
                "status": "done",
                "execute_time": execute_time
            }) \
            .eq("id", task_id) \
            .execute()
    except Exception as e:
        print(f"變更任務狀態為完成失敗 (ID: {task_id}): {e}")

# =========================
# 刪除任務
# =========================
def delete_task(task_id):
    try:
        supabase.table("tasks") \
            .delete() \
            .eq("id", task_id) \
            .execute()
    except Exception as e:
        st.error(f"刪除任務失敗: {e}")

# =========================
# Robot 最後巡邏時間（更新）
# =========================
def update_robot_check_time():
    try:
        current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

        supabase.table("system_status") \
            .update({
                "last_robot_check_time": current_time
            }) \
            .eq("id", 1) \
            .execute()
    except Exception as e:
        print(f"更新 Robot 巡邏時間失敗: {e}")

# =========================
# Robot 最後巡邏時間（讀取）
# =========================
def get_robot_check_time():
    try:
        # 移除原先會與 .execute() 衝突的 .single()
        res = supabase.table("system_status") \
            .select("last_robot_check_time") \
            .eq("id", 1) \
            .execute()

        # 安全檢查：確保回傳的 data 陣列裡有資料
        if res.data and len(res.data) > 0:
            return res.data[0].get("last_robot_check_time", "無紀錄")
        
        return "無紀錄"
    except Exception as e:
        print(f"讀取 Robot 巡邏時間失敗: {e}")
        return "讀取錯誤"

# =========================
# Robot 簽到（同 update）
# =========================
def robot_check_in():
    update_robot_check_time()
