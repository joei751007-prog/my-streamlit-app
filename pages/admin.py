import streamlit as st
from database import (
    get_tasks,
    complete_task,
    robot_check_in,
    get_robot_check_time
)
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="後台管理")

st.title("後台管理")

# =========================
# API 入口（一定要最上面）
# =========================
query = st.query_params

if "api" in query and query["api"] == "complete":

    task_id = int(query["task_id"])

    complete_task(task_id)

    st.write("OK")

    st.stop()

# 初始化登入狀態
if "login" not in st.session_state:
    st.session_state.login = False


# 尚未登入
if not st.session_state.login:

    password = st.text_input(
        "請輸入管理密碼",
        type="password"
    )

    if st.button("登入"):

        if password == "admin123":

            st.session_state.login = True

            st.success("登入成功")

            st.rerun()

        else:

            st.error("密碼錯誤")

    st.stop()

# =========================
# 登入後畫面（這裡才開始）
# =========================
if st.session_state.login:
    st.success("登入成功")

if st.button("登出"):

    st.session_state.login = False

    st.rerun()

if st.button("刷新頁面"):

    st.rerun()

st_autorefresh(
    interval=5 * 1000,
    key="admin_refresh"
)

robot_time = get_robot_check_time()

st.info(f"Robot 最後簽到時間：{robot_time}")

st.divider()

if st.button("Robot 簽到"):

    robot_check_in()

    st.success("簽到成功")

    st.rerun()


df = get_tasks()

for _, row in df.iterrows():

    col0, col1, col2, col3, col4, col5 = st.columns(
    [1, 2, 4, 2, 3, 3]
    )
    with col0:
        st.write(row["id"])
        
    with col1:
        st.write(row["name"])

    with col2:
        st.write(row["url"])

    with col3:
        st.write(row["status"])

    with col4:
        st.write(row["request_time"])

    with col5:
        st.write(row["execute_time"])

    # with col5:

    #     if row["status"] == "pending":

    #         if st.button(
    #             "完成",
    #             key=f"done_{row['id']}"
    #         ):
    #             complete_task(row["id"])
    #             st.rerun()

