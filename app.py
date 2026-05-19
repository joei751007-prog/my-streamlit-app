import streamlit as st
from streamlit_autorefresh import st_autorefresh

from database import (
    add_task,
    get_tasks,
    request_task,
    delete_task,
    get_robot_check_time
)

# =========================
# 頁面設定
# =========================
st.set_page_config(
    page_title="定位系統",
    layout="wide"
)

st.title("PIAYIXIA定位任務系統_V1.0_By沒時間玩咚奇剛")

# =========================
# 自動刷新（放這裡）
# =========================
st_autorefresh(
    interval=10 * 1000,
    key="auto_refresh"
)

# =========================
# 手動刷新按鈕
# =========================
if st.button("刷新頁面"):
    st.rerun()


# =========================
# Robot 最後巡邏時間
# =========================
robot_time = get_robot_check_time()

st.info(
    f"Robot 最後巡邏時間：{robot_time}"
)

# =========================
# 新增資料
# =========================
st.subheader("新增資料")

with st.form("my_form", clear_on_submit=True):
    name = st.text_input("名稱")
    url = st.text_input("網址")
    submitted = st.form_submit_button("新增")
    
    if submitted:
        if name and url:
            add_task(name, url)
            st.success("新增成功")
            # 這裡甚至不需要 st.rerun()，畫面會自動更新
        else:
            st.error("請輸入完整資料")


st.divider()

# =========================
# 任務列表
# =========================
st.subheader("任務列表")

# =========================
# 表頭
# =========================
header1, header2, header3, header4, header5, header6 = st.columns(
    [2, 4, 2, 2, 8, 2]
)

with header1:
    st.markdown("**姓名**")

with header2:
    st.markdown("**網址**")

with header3:
    st.markdown("**定位按鈕**")

with header4:
    st.markdown("**狀態**")

with header5:
    st.markdown("**請求 / 執行時間**")

with header6:
    st.markdown("**刪除**")


# =========================
# 顯示任務
# =========================
df = get_tasks()


for _, row in df.iterrows():

    col1, col2, col3, col4, col5, col6 = st.columns(
        [2, 4, 2, 2, 8, 2]
    )

    # 姓名
    with col1:
        st.write(row["name"])

    # 網址
    with col2:
        st.write(row["url"])

    # 定位按鈕
    with col3:

        if row["status"] not in ["pending", "running"]:

            if st.button(
                "定位",
                key=f"request_{row['id']}"
            ):

                request_task(row["id"])

                st.rerun()

        else:

            st.write("-")

    # 狀態
    with col4:
        st.write(row["status"])

    # 執行時間
    with col5:

        request_time = row["request_time"]
        execute_time = row["execute_time"]

        st.write(
            f"請求：{request_time} / 執行：{execute_time}"
        )

    # 刪除按鈕
    with col6:

        if row["status"] == "pending":

            st.write("等任務完成再刪除")

        else:

            if st.button(
                "刪除",
                key=f"delete_{row['id']}"
            ):

                delete_task(row["id"])

                st.rerun()
