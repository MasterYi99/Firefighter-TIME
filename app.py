import streamlit as st
import pandas as pd
import numpy as np

# 網頁基本設定
st.set_page_config(page_title="永利分隊勤務自動排班系統", layout="wide")

st.title("📋 永利分隊勤務自動排班系統 (完整修正版)")
st.caption("已修正多行字串縮排與專救A同仁語法 Bug，整合動態人員維護與核心工時管制")

# --- 使用 Session State 保持人員資料，避免網頁重整時動態修改的資料消失 ---
if 'df_personnel' not in st.session_state:
    # 預設名單
    default_personnel = [
        {"職稱": "分隊長", "編號": "A", "姓名": "許哲翊"},
        {"職稱": "小隊長", "編號": "B", "姓名": "郭獻鴻"},
        {"職稱": "小隊長", "編號": "C", "姓名": "蕭淳碩"},
        {"職稱": "小隊長", "編號": "D", "姓名": "王書華"},
        {"職稱": "隊員A", "編號": "101", "姓名": "黃仁炫"},
        {"職稱": "隊員A", "編號": "102", "姓名": "馬筠喨"},
        {"職稱": "隊員A", "編號": "103", "姓名": "許欣融"},
        {"職稱": "隊員B", "編號": "105", "姓名": "黃政偉"},
        {"職稱": "隊員B", "編號": "106", "姓名": "林戰培"},
        {"職稱": "隊員B", "編號": "107", "姓名": "張景翔"},
        {"職稱": "隊員B", "編號": "108", "姓名": "張冠傑"},
        {"職稱": "隊員C", "編號": "109", "姓名": "邱乃鋐"},
        {"職稱": "隊員C", "編號": "110", "姓名": "簡佳懿"},
        {"職稱": "隊員C", "編號": "111", "姓名": "盧柏宏"},
        {"職稱": "隊員C", "編號": "112", "姓名": "黃建嘉"},
        {"職稱": "隊員D", "編號": "113", "姓名": "薛志中"},
        {"職稱": "隊員D", "編號": "114", "姓名": "繆昆霖"},
        {"職稱": "隊員D", "編號": "115", "姓名": "張文嘉"},
        {"職稱": "隊員D", "編號": "116", "姓名": "宋易潤"},
        {"職稱": "隊員A", "編號": "117", "姓名": "劉默"},
        {"職稱": "隊員A", "編號": "118", "姓名": "羅彥鈞"},
        {"職稱": "隊員C", "編號": "119", "姓名": "曾政傑"},
        {"職稱": "專救A", "編號": "202", "姓名": "許辰瑋"},
        {"職稱": "專救A", "編號": "203", "姓名": "王雅萱"},
        {"職稱": "專救A", "編號": "204", "姓名": "林宏叡"},
        {"職稱": "專救B", "編號": "205", "姓名": "徐盟欽"},
        {"職稱": "專救B", "編號": "206", "姓名": "吳致緯"},
        {"職稱": "專救B", "編號": "207", "姓名": "張鈞寗"},
        {"職稱": "專救B", "編號": "208", "姓名": "李芊慧"},
        {"職稱": "專救C", "編號": "209", "姓名": "高承鈺"},
        {"職稱": "專救C", "編號": "210", "姓名": "黃科諺"},
        {"職稱": "專救C", "編號": "211", "姓名": "林冠宇"},
        {"職稱": "專救D", "編號": "212", "姓名": "林俊吉"},
        {"職稱": "專救D", "編號": "213", "姓名": "林忠穎"},
        {"職稱": "專救D", "編號": "214", "姓名": "王羽萱"},
        {"職稱": "役男", "編號": "401", "姓名": "張宇洋"},
        {"職稱": "役男", "編號": "403", "姓名": "盧建丞"}
    ]
    st.session_state.df_personnel = pd.DataFrame(default_personnel)

# --- 建立頁籤分流功能 ---
tab1, tab2 = st.tabs(["📅 今日勤務編排", "👥 人員名單維護"])

# ==============================================================================
# TAB 2: 人員名單維護
# ==============================================================================
with tab2:
    st.header("👥 分隊同仁名單管理")
    st.markdown("""
💡 **操作說明：**
* **修改資料：** 直接用滑鼠點擊表格欄位即可進行修改。
* **新增人員：** 點擊表格最下方的 **「➕ Add row」**。
* **刪除人員：** 點取該列最左側並按鍵盤 `Delete`，或點擊右側垃圾桶圖示。
* 修改完成後，系統會**自動即時更新**至排班名單內！
""")
    
    # 讓使用者利用 st.data_editor 直接動態編輯名單
    edited_df = st.data_editor(
        st.session_state.df_personnel,
        num_rows="dynamic", # 允許動態增加或減少行數
        use_container_width=True,
        column_config={
            "職稱": st.column_config.SelectboxColumn(
                "職稱",
                help="請選擇同仁職稱",
                options=["分隊長", "小隊長", "隊員A", "隊員B", "隊員C", "隊員D", "專救A", "專救B", "專救C", "專救D", "役男"],
                required=True,
            ),
            "編號": st.column_config.TextColumn(
                "編號",
                help="幹部為 A/B/C/D，隊員為 1XX，專救為 2XX，役男為 4XX",
                max_chars=5,
                required=True,
            ),
            "姓名": st.column_config.TextColumn(
                "姓名",
                help="請輸入同仁姓名",
                required=True,
            )
        }
    )
    
    # 將編輯後的資料同步回 Session State
    st.session_state.df_personnel = edited_df

# ==============================================================================
# TAB 1: 今日勤務編排
# ==============================================================================
with tab1:
    # 重新撈取最新的同仁名單字典
    current_personnel = st.session_state.df_personnel.to_dict('records')
    current_names = [p['姓名'] for p in current_personnel if str(p['姓名']) != 'None' and not pd.isna(p['姓名'])]

    # --- 側邊欄控制與模擬輸入 ---
    st.sidebar.header("⚙️ 模擬當日參數設定")
    selected_date = st.sidebar.date_input("選擇排班日期")

    st.sidebar.subheader("🏳️ 假別動態調整")
    on_leave = st.sidebar.multiselect("今日休假同仁 (不排班)", current_names, default=[])
    on_out_stay = st.sidebar.multiselect("今日外宿同仁 (08-18在勤)", current_names, default=[])

    st.sidebar.subheader("🌙 跨日 fatigue 參數")
    prev_night_duty = st.sidebar.multiselect("昨日大夜有值班/救護同仁 (08-12排除)", current_names, default=[])
    just_returned = st.sidebar.multiselect("今日剛收假同仁 (08-12救護優先)", current_names, default=[])

    # --- 初始化今日可用人力池與狀態追蹤 ---
    hours_tracker = {p['姓名']: 0 for p in current_personnel if str(p['姓名']) != 'None' and not pd.isna(p['姓名'])}
    consecutive_tracker = {p['姓名']: 0 for p in current_personnel if str(p['姓名']) != 'None' and not pd.isna(p['姓名'])}
    history_91_count = {p['姓名']: 0 for p in current_personnel if str(p['姓名']) != 'None' and not pd.isna(p['姓名'])}

    time_slots = [
        "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00",
        "16:00-18:00", "18:00-20:00", "20:00-22:00", "22:00-00:00",
        "00:00-02:00", "02:00-04:00", "04:00-06:00", "06:00-08:00"
    ]

    schedule_result = []

    # --- 核心排班迴圈 ---
    for idx, slot in enumerate(time_slots):
        start_hour = int(slot.split(":")[0])
        is_night = start_hour >= 0 and start_hour < 8
        is_first_slot = idx < 2
        
        available_pool = []
        for p in current_personnel:
            name = p['姓名']
            code = str(p['編號'])
            
            if pd.isna(name) or name == 'None' or name == '': continue
            if name in on_leave: continue
            if name in on_out_stay and start_hour >= 18: continue
            if code.startswith('4') and hours_tracker[name] >= 8: continue
            if not code.startswith('4') and hours_tracker[name] >= 14: continue
            if consecutive_tracker[name] >= 4:
                consecutive_tracker[name] = 0
                continue
                
            available_pool.append(p)

        leaders = [p for p in available_pool if str(p['編號']) in ['A', 'B', 'C', 'D']]
        special_ems = [p for p in available_pool if str(p['編號']).startswith('2')]
        regulars = [p for p in available_pool if str(p['編號']).startswith('1')]
        substitutes = [p for p in available_pool if str(p['編號']).startswith('4')]

        duty_watch = "無人"
        duty_91 = ["無人", "無人"]
        duty_92 = ["無人", "無人"]
        duty_11 = []
        duty_12 = []

        # A. 值班台指派
        watch_assigned = None
        if not is_night and substitutes:
            substitutes.sort(key=lambda x: hours_tracker[x['姓名']])
            watch_assigned = substitutes.pop(0)
        elif regulars:
            valid_regs = [r for r in regulars if not (is_first_slot and r['姓名'] in prev_night_duty)]
            if valid_regs:
                valid_regs.sort(key=lambda x: hours_tracker[x['姓名']])
                watch_assigned = valid_regs.pop(0)
                regulars.remove(watch_assigned)
                
        if watch_assigned:
            duty_watch = watch_assigned['姓名']
            hours_tracker[duty_watch] += 2
            consecutive_tracker[duty_watch] += 2
            if not str(watch_assigned['編號']).startswith('4'):
                duty_12.append(duty_watch)

        # B. 91 / 92 救護車指派
        ems_pool = special_ems + [r for r in regulars if not (is_first_slot and r['姓名'] in prev_night_duty)]
        if not is_night:
            ems_pool += substitutes

        def ems_priority(x):
            is_returned = 1 if (is_first_slot and x['姓名'] in just_returned) else 0
            return (-is_returned, history_91_count[x['姓名']], hours_tracker[x['姓名']])

        ems_pool.sort(key=ems_priority)

        if len(ems_pool) >= 2:
            p1 = ems_pool.pop(0)
            p2 = ems_pool.pop(0)
            duty_91 = [p1['姓名'], p2['姓名']]
            for p in [p1, p2]:
                hours_tracker[p['姓名']] += 2
                consecutive_tracker[p['姓名']] += 2
                history_91_count[p['姓名']] += 1
                if p in special_ems: special_ems.remove(p)
                if p in regulars: regulars.remove(p)
                if p in substitutes: substitutes.remove(p)

        if len(ems_pool) >= 2:
            p1 = ems_pool.pop(0)
            p2 = ems_pool.pop(0)
            duty_92 = [p1['姓名'], p2['姓名']]
            for p in [p1, p2]:
                hours_tracker[p['姓名']] += 2
                consecutive_tracker[p['姓名']] += 2
                if p in special_ems: special_ems.remove(p)
                if p in regulars: regulars.remove(p)
                if p in substitutes: substitutes.remove(p)

        # C. 11 車指派
        if leaders:
            leader = leaders.pop(0)
            duty_11.append(leader['姓名'])
            firefighters = regulars + special_ems
            firefighters.sort(key=lambda x: hours_tracker[x['姓名']])
            while len(duty_11) < 4 and firefighters:
                f = firefighters.pop(0)
                duty_11.append(f['姓名'])
                if f in regulars: regulars.remove(f)
                if f in special_ems: special_ems.remove(f)

        # D. 12 車指派
        remaining_pool = regulars + special_ems
        while len(duty_12) < 2 and remaining_pool:
            f = remaining_pool.pop(0)
            duty_12.append(f['姓名'])

        # 冷卻重設
        all_assigned_duty = [duty_watch] + duty_91 + duty_92
        for name in hours_tracker.keys():
            if name not in all_assigned_duty:
                consecutive_tracker[name] = 0

        schedule_result.append({
            "時段": slot,
            "值班台": duty_watch,
            "91 救護車": " / ".join(duty_91),
            "92 救護車": " / ".join(duty_92),
            "11 主力車": ", ".join(duty_11),
            "12 副力車": ", ".join(duty_12)
        })

    df_result = pd.DataFrame(schedule_result)

    # --- 排班結果渲染 ---
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"📅 {selected_date} 勤務分配功課表")
        st.dataframe(df_result, use_container_width=True, hide_index=True)
        
        csv = df_result.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 匯出今日勤務分配表 (CSV)",
            data=csv,
            file_name=f"永利分隊勤務分配表_{selected_date}.csv",
            mime="text/csv",
        )

    with col2:
        st.subheader("📊 今日同仁計時工時統計")
        df_hours = pd.DataFrame([
            {"姓名": name, "職稱": next((p['職稱'] for p in current_personnel if p['姓名'] == name), "未指定"), "今日累計時數": hrs}
            for name, hrs in hours_tracker.items()
        ]).sort_values(by="今日累計時數", ascending=False)
        
        df_hours_active = df_hours[df_hours["今日累計時數"] > 0]
        st.dataframe(df_hours_active, use_container_width=True, hide_index=True)

        st.subheader("⚠️ 安全合規檢查")
        overtime_4xx = df_hours[(df_hours['職稱'] == '役男') & (df_hours['今日累計時數'] > 8)]
        overtime_1xx = df_hours[(df_hours['今日累計時數'] > 14)]
        
        if overtime_4xx.empty and overtime_1xx.empty:
            st.success("✅ 工時符合安全死線！")
        else:
            if not overtime_4xx.empty: st.error("🚨 役男工時超時！")
            if not overtime_1xx.empty: st.error("🚨 隊員工時破天花板！")
