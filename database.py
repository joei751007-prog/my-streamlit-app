from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
from supabase_client import supabase

# =========================
# 台灣時間設定
# =========================
tw_tz = timezone(timedelta(hours=8))

# =========================
# 新增任務 (支援代號、業者、門號、單次與定時)
# =========================
def add_task(name, code, telecom, phone, url, task_type, interval_seconds=None):
    try:
        current_time = datetime.now(tw_tz).isoformat()
        
        payload = {
            "name": name,
            "code": code,
            "telecom": telecom,
            "phone": phone,
            "url": url,
            "task_type": task_type,
            "interval_seconds": interval_seconds if task_type == "periodic" else None,
            "request_time": None,
            "execute_time": None,
            "last_execute_time": None,
        }
        
        if task_type == "single":
            payload["status"] = "idle"
            payload["next_execute_time"] = None
        elif task_type == "periodic":
            payload["status"] = "定時中"
            payload["next_execute_time"] = current_time
            
        supabase.table("tasks").insert(payload).execute()
    except Exception as e:
        st.error(f"資料庫新增任務失敗: {e}")

# =========================
# 取得所有任務 (完整欄位對齊)
# =========================
def get_tasks():
    all_columns = [
        "id", "name", "code", "telecom", "phone", "url", "task_type", 
        "interval_seconds", "status", "request_time", "execute_time", 
        "last_execute_time", "next_execute_time"
    ]
    try:
        res = supabase.table("tasks") \
            .select("*") \
            .order("id", desc=True) \
            .execute()

        data = res.data or []
        if not data:
            return pd.DataFrame(columns=all_columns)
            
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"資料庫讀取任務失敗: {e}")
        return pd.DataFrame(columns=all_columns)

# =========================
# 發送定位請求 (單次任務專用)
# =========================
def request_task(task_id):
    try:
        request_time = datetime.now(tw_tz).isoformat()
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
# 暫停定時任務
# =========================
def pause_task(task_id):
    try:
        supabase.table("tasks") \
            .update({
                "status": "暫停",
                "next_execute_time": None
            }) \
            .eq("id", task_id) \
            .execute()
    except Exception as e:
        st.error(f"暫停任務失敗: {e}")

# =========================
# 繼續定時任務
# =========================
def resume_task(task_id):
    try:
        current_time = datetime.now(tw_tz).isoformat()
        supabase.table("tasks") \
            .update({
                "status": "定時中",
                "next_execute_time": current_time
            }) \
            .eq("id", task_id) \
            .execute()
    except Exception as e:
        st.error(f"恢復任務失敗: {e}")

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
# Robot 巡邏與簽到時間
# =========================
def update_robot_check_time():
    try:
        current_time = datetime.now(tw_tz).isoformat()
        supabase.table("system_status") \
            .update({"last_robot_check_time": current_time}) \
            .eq("id", 1) \
            .execute()
    except Exception as e:
        print(f"更新 Robot 巡邏時間失敗: {e}")

def get_robot_check_time():
    try:
        res = supabase.table("system_status") \
            .select("last_robot_check_time") \
            .eq("id", 1) \
            .execute()

        if res.data and len(res.data) > 0:
            raw_time = res.data[0].get("last_robot_check_time")
            if raw_time:
                dt = pd.to_datetime(raw_time).tz_convert("Asia/Taipei")
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return "無紀錄"
        return "無紀錄"
    except Exception as e:
        print(f"讀取 Robot 巡邏時間失敗: {e}")
        return "讀取錯誤"

def robot_check_in():
    update_robot_check_time()