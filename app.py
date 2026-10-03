from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from supabase_client import supabase
from database import (
    add_task,
    get_tasks,
    request_task,
    pause_task,
    resume_task,
    delete_task,
    get_robot_check_time,
    robot_check_in
)

# 台灣時間設定
tw_tz = timezone(timedelta(hours=8))

# ========================================================
# 🚀 關鍵 1：API 穿透入口 (必須放在密碼驗證最上方)
# 當機器人回報 GET /?api=complete&task_id=... 時直接攔截處理
# ========================================================
query = st.query_params

if "api" in query and query["api"] == "complete":
    task_id = int(query["task_id"])
    current_time_obj = datetime.now(tw_tz)
    current_time_iso = current_time_obj.isoformat()
    
    try:
        task_res = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if task_res.data and len(task_res.data) > 0:
            task_info = task_res.data[0]
            task_type = task_info.get("task_type")
            
            # 分支 A：單次任務
            if task_type == "single":
                supabase.table("tasks").update({
                    "status": "done",
                    "execute_time": current_time_iso
                }).eq("id", task_id).execute()
                
            # 分支 B：定時任務 (計算下次執行時間)
            elif task_type == "periodic":
                seconds = task_info.get("interval_seconds") or 600
                next_time_obj = current_time_obj + timedelta(seconds=seconds)
                next_time_iso = next_time_obj.isoformat()
                
                supabase.table("tasks").update({
                    "status": "定時中",
                    "last_execute_time": current_time_iso,
                    "next_execute_time": next_time_iso
                }).eq("id", task_id).execute()
                
        st.write("OK")
    except Exception as e:
        st.write(f"API 處理失敗: {e}")
        
    st.stop()


# ========================================================
# 頁面基本設定
# ========================================================
st.set_page_config(
    page_title="PIAYIXIA 定位任務系統",
    layout="wide"
)

# ========================================================
# 🔐 關鍵 2：整站密碼通關驗證 (未登入不渲染後續畫面)
# ========================================================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 PIAYIXIA 定位任務系統 - 身分驗證")
    password = st.text_input("請輸入系統管理密碼", type="password")
    if st.button("登入"):
        if password == st.secrets.get("password", "admin123456"):
            st.session_state.login = True
            st.success("驗證成功")
            st.rerun()
        else:
            st.error("密碼錯誤，請重新輸入")
    st.stop()


# ========================================================
# 自動刷新 (10 秒)
# ========================================================
st_autorefresh(
    interval=10 * 1000,
    key="auto_refresh"
)

# ========================================================
# 時間格式化輔助函式
# ========================================================
def format_time(iso_string):
    if iso_string is None or pd.isna(iso_string) or iso_string == "" or iso_string == "none":
        return "-"
    try:
        dt = pd.to_datetime(str(iso_string)).tz_convert("Asia/Taipei")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        if isinstance(iso_string, str):
            return iso_string.replace("T", " ").split(".")[0][:19]
        return "-"

# ========================================================
# 頁面頂部控制列
# ========================================================
top_col1, top_col2, top_col3, top_col4 = st.columns([6, 1.5, 1, 1])

with top_col1:
    st.title("📡 PIAYIXIA定位任務系統_大雅版_V2.0")
    robot_time = get_robot_check_time()
    st.info(f"🤖 Robot 最後巡邏時間：{robot_time}")

with top_col2:
    if st.button("🤖 Robot 簽到", use_container_width=True):
        robot_check_in()
        st.success("簽到成功")
        st.rerun()

with top_col3:
    if st.button("刷新頁面", use_container_width=True):
        st.rerun()

with top_col4:
    if st.button("登出系統", use_container_width=True):
        st.session_state.login = False
        st.rerun()

st.divider()

# ========================================================
# ➕ 新增任務區塊 (完整打包進 Form，防止外部重繪干擾)
# ========================================================
st.subheader("➕ 新增任務")

# 透過 Form 打包，防止任何背景簽到、按鈕或自動重繪干擾輸入中的表單
with st.form("my_form", clear_on_submit=True):
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        task_type_display = st.selectbox("任務類型", ["單次任務", "定時任務"])
    with r1_col2:
        interval_seconds = st.number_input("執行間隔 (秒，僅定時任務生效)", min_value=10, value=600, step=10)

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        code = st.text_input("代號")
        telecom = st.selectbox("電信業者", ["中華", "民營"])
    with f_col2:
        name = st.text_input("姓名")
        phone = st.text_input("門號")

    url = st.text_input("定位網址")
        
    submitted = st.form_submit_button("＋ 建立任務")
    
    if submitted:
        if code and name and phone and url:
            clean_code = code.replace(" ", "")
            clean_name = name.replace(" ", "")
            clean_phone = phone.replace(" ", "")
            clean_url = url.replace(" ", "")
            
            # 判斷任務類型
            task_type = "single" if task_type_display == "單次任務" else "periodic"
            actual_interval = interval_seconds if task_type == "periodic" else None
            
            add_task(clean_name, clean_code, telecom, clean_phone, clean_url, task_type, actual_interval)
            st.success("任務新增成功！")
            st.rerun()
        else:
            st.error("請確認所有欄位皆已輸入完整（代號、姓名、門號、定位網址）！")

st.divider()

# ========================================================
# 📋 任務操作與監控列表 (前台操作與機器人巡邏唯一依據)
# ========================================================
st.subheader("📋 任務操作與監控列表")

# 欄位寬度比例配置
col_layout = [1, 1.2, 1.5, 1, 2, 4, 1.8, 1.2, 3.5, 2]
headers = ["ID", "代號", "姓名", "業者", "門號", "網址", "類型/間隔", "狀態", "時間紀錄", "操作/刪除"]

header_cols = st.columns(col_layout)
for h_col, h_text in zip(header_cols, headers):
    with h_col:
        st.markdown(f"**{h_text}**")

df = get_tasks()

for _, row in df.iterrows():
    r_cols = st.columns(col_layout)
    
    # 1. ID
    with r_cols[0]:
        st.write(str(row["id"]))
        
    # 2. 代號
    with r_cols[1]:
        st.write(str(row["code"]) if pd.notna(row["code"]) and row["code"] != "" else "-")
        
    # 3. 姓名
    with r_cols[2]:
        st.write(str(row["name"]))
        
    # 4. 業者
    with r_cols[3]:
        st.write(str(row["telecom"]) if pd.notna(row["telecom"]) else "-")
        
    # 5. 門號
    with r_cols[4]:
        st.write(str(row["phone"]) if pd.notna(row["phone"]) else "-")
        
    # 6. 網址
    with r_cols[5]:
        st.write(str(row["url"]))
        
    # 7. 類型/間隔
    with r_cols[6]:
        if row["task_type"] == "single":
            st.write("單次")
        else:
            st.write(f"定時 ({row['interval_seconds']}s)")
            
    # 8. 狀態
    with r_cols[7]:
        st.write(str(row["status"]))
        
    # 9. 時間紀錄
    with r_cols[8]:
        if row["task_type"] == "single":
            req_t = format_time(row["request_time"])
            exe_t = format_time(row["execute_time"])
            st.write(f"請求: {req_t}\n執行: {exe_t}")
        else:
            last_t = format_time(row["last_execute_time"])
            next_t = format_time(row["next_execute_time"])
            st.write(f"上次: {last_t}\n下次: {next_t}")
            
    # 10. 操作 / 刪除按鈕
    with r_cols[9]:
        if row["task_type"] == "single":
            if row["status"] in ["pending", "running"]:
                st.write("執行中...")
            else:
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("定位", key=f"req_{row['id']}"):
                        request_task(row["id"])
                        st.rerun()
                with b_col2:
                    if st.button("刪除", key=f"del_{row['id']}"):
                        delete_task(row["id"])
                        st.rerun()
        else:
            b_col1, b_col2 = st.columns(2)
            if row["status"] == "定時中":
                with b_col1:
                    if st.button("暫停", key=f"pause_{row['id']}"):
                        pause_task(row["id"])
                        st.rerun()
                with b_col2:
                    if st.button("刪除", key=f"del_{row['id']}"):
                        delete_task(row["id"])
                        st.rerun()
            elif row["status"] == "暫停":
                with b_col1:
                    if st.button("繼續", key=f"resume_{row['id']}"):
                        resume_task(row["id"])
                        st.rerun()
                with b_col2:
                    if st.button("刪除", key=f"del_{row['id']}"):
                        delete_task(row["id"])
                        st.rerun()
            else:
                st.write("執行中...")