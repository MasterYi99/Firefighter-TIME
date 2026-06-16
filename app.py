import streamlit as st
import pandas as pd
import numpy as np

# 網頁基本設定
st.set_page_config(page_title="永利分隊勤務自動排班系統", layout="wide")

st.title("📋 永利分隊勤務自動排班系統 (初版)")
st.caption("依據永利分隊最新修正勤務自動排班規則建置")

# --- 模擬人員資料庫 (直接內建您休宿表中的人員，方便初期調試) ---
@st.cache_data
def get_default_personnel():
    return [
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

personnel_list = get_default_personnel()
df_personnel = pd.DataFrame(personnel_list)

# --- 側邊欄控制與模擬輸入 ---
st.sidebar.header("⚙️ 模擬當日參數設定")
selected_date = st.sidebar.date_input("選擇排班日期")

st.sidebar.subheader("🏳️ 假別動態調整")
# 為了展示，讓使用者快速勾選今天誰「休假」或「外宿」，其餘預設全日班(空白)
on_leave = st.sidebar.multiselect("今日休假同仁 (不排班)", df_personnel['姓名'].tolist(), default=["黃仁炫", "徐盟欽"])
on_out_stay = st.sidebar.multiselect("今日外宿同仁 (08-18在勤)", df_personnel['姓名'].tolist(), default=["林戰培"])

# 大夜跨日排除與收假優先模擬
st.sidebar.subheader("🌙 跨日 fatigue 參數")
prev_night_duty = st.sidebar.multiselect("昨日大夜有值班/救護同仁 (今日08-12排除)", df_personnel['姓名'].tolist(), default=["張景翔", "王雅萱"])
just_returned = st.sidebar.multiselect("今日剛收假同仁 (今日08-12救護優先)", df_personnel['姓名'].tolist(), default=["邱乃鋐", "黃科諺"])

# --- 初始化今日可用人力池與狀態追蹤 ---
# 工時追蹤字典
hours_tracker = {p['姓名']: 0 for p in personnel_list}
# 連續工時追蹤
consecutive_tracker = {p['姓名']: 0 for p in personnel_list}
# 歷史 91 跑車次數 (模擬用，確保平均)
history_91_count = {p['姓名']: np.random.randint(0, 5) for p in personnel_list}

# 時段劃分 (消防隊通常以 2 小時或 4 小時切分，此處採用 2 小時為一個基本單位，共 12 個時段)
time_slots = [
    "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00",
    "16:00-18:00", "18:00-20:00", "20:00-22:00", "22:00-00:00",
    "00:00-02:00", "02:00-04:00", "04:00-06:00", "06:00-08:00"
]

# --- 核心排班演算法 ---
schedule_result = []

for idx, slot in enumerate(time_slots):
    start_hour = int(slot.split(":")[0])
    is_night = start_hour >= 0 and start_hour < 8
    is_first_slot = idx < 2  # 08:00-12:00 屬於首班時段
    
    # 1. 篩選當前時段在勤的可用人力
    available_pool = []
    for p in personnel_list:
        name = p['姓名']
        code = p['編號']
        
        # 排除休假
        if name in on_leave:
            continue
        # 排除外宿班 18:00 以後
        if name in on_out_stay and start_hour >= 18:
            continue
        # 大夜跨日排除 (昨日大夜班，今日 08-12 排除計時勤務，後續邏輯內過濾)
        # 14小時工時限制檢查
        if code.startswith('4') and hours_tracker[name] >= 8: # 役男8小時
            continue
        if not code.startswith('4') and hours_tracker[name] >= 14: # 隊員14小時
            continue
        # 連續工時上限 4 小時限制 (大於等於4小時強制冷卻)
        if consecutive_tracker[name] >= 4:
            consecutive_tracker[name] = 0 # 進入冷卻
            continue
            
        available_pool.append(p)

    # 分流各角色
    leaders = [p for p in available_pool if p['編號'] in ['A', 'B', 'C', 'D']]
    special_ems = [p for p in available_pool if p['編號'].startswith('2')]
    regulars = [p for p in available_pool if p['編號'].startswith('1')]
    substitutes = [p for p in available_pool if p['編號'].startswith('4')]

    # 當前時段指派結果
    duty_watch = "無人"
    duty_91 = ["無人", "無人"]
    duty_92 = ["無人", "無人"]
    duty_11 = []
    duty_12 = []

    # A. 指派值班台 (崗位保證)
    watch_assigned = None
    if not is_night and substitutes:
        # 白天優先役男
        substitutes.sort(key=lambda x: hours_tracker[x['姓名']])
        watch_assigned = substitutes.pop(0)
    elif regulars:
        # 夜間或役男滿時數，由一般隊員輪值 (過濾大夜排除者)
        valid_regs = [r for r in regulars if not (is_first_slot and r['姓名'] in prev_night_duty)]
        if valid_regs:
            valid_regs.sort(key=lambda x: hours_tracker[x['姓名']])
            watch_assigned = valid_regs.pop(0)
            regulars.remove(watch_assigned)
            
    if watch_assigned:
        duty_watch = watch_assigned['姓名']
        hours_tracker[duty_watch] += 2
        consecutive_tracker[duty_watch] += 2
        # 值班合併機制：若是隊員值班，強制編入 12 車基本戰力
        if not watch_assigned['編號'].startswith('4'):
            duty_12.append(duty_watch)

    # B. 指派 91 / 92 救護車 (每台固定 2 人)
    # 合併救護可用人力池 (幹部、役男深夜不排)
    ems_pool = special_ems + [r for r in regulars if not (is_first_slot and r['姓名'] in prev_night_duty)]
    if not is_night:
        ems_pool += substitutes # 役男白天可當救護副手

    # 權重排序：優先指派收假者，其次指派累積跑車與工時最低者
    def ems_priority(x):
        is_returned = 1 if (is_first_slot and x['姓名'] in just_returned) else 0
        return (-is_returned, history_91_count[x['姓名']], hours_tracker[x['姓名']])

    ems_pool.sort(key=ems_priority)

    # 91 車指派
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

    # 92 車指派
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

    # C. 指派 11 車 (主力火警車組，滿編 4 人，1幹部 + 3隊員/專救)
    if leaders:
        leader = leaders.pop(0)
        duty_11.append(leader['姓名'])
        # 湊齊 3 名一般隊員/專救
        firefighters = regulars + special_ems
        firefighters.sort(key=lambda x: hours_tracker[x['姓名']])
        while len(duty_11) < 4 and firefighters:
            f = firefighters.pop(0)
            duty_11.append(f['姓名'])
            if f in regulars: regulars.remove(f)
            if f in special_ems: special_ems.remove(f)

    # D. 指派 12 車 (剩餘沒有值班與救護的人員組成，上限2人)
    remaining_pool = regulars + special_ems
    while len(duty_12) < 2 and remaining_pool:
        f = remaining_pool.pop(0)
        duty_12.append(f['姓名'])

    # 沒被排到計時勤務的人，連續工時冷卻歸零
    all_assigned_duty = [duty_watch] + duty_91 + duty_92
    for p in personnel_list:
        if p['姓名'] not in all_assigned_duty:
            consecutive_tracker[p['姓名']] = 0

    schedule_result.append({
        "時段": slot,
        "值班台": duty_watch,
        "91 救護車": " / ".join(duty_91),
        "92 救護車": " / ".join(duty_92),
        "11 主力車 (帶車官+隊員)": ", ".join(duty_11),
        "12 副力車 (戰力重疊)": ", ".join(duty_12)
    })

df_result = pd.DataFrame(schedule_result)

# --- 網頁畫面呈現與排版 ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"📅 {selected_date} 勤務分配功課表 (自動生成)")
    st.dataframe(df_result, use_container_width=True, hide_index=True)
    
    # 匯出按鈕
    csv = df_result.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 匯出今日勤務分配表 (CSV)",
        data=csv,
        file_name=f"永利分隊勤務分配表_{selected_date}.csv",
        mime="text/csv",
    )

with col2:
    st.subheader("📊 今日同仁計時工時統計")
    st.caption("值班 + 救護累計時數 (上限14h / 役男8h)")
    
    # 將工時轉換為 DataFrame 呈現
    df_hours = pd.DataFrame([
        {"姓名": name, "職稱": next(p['職稱'] for p in personnel_list if p['姓名'] == name), "今日累計時數": hrs}
        for name, hrs in hours_tracker.items()
    ]).sort_values(by="今日累計時數", ascending=False)
    
    # 過濾掉沒上班(0工時)的幹部或休假者，讓畫面更乾淨
    df_hours_active = df_hours[df_hours["今日累計時數"] > 0]
    st.dataframe(df_hours_active, use_container_width=True, hide_index=True)

    # 警示區
    st.subheader("⚠️ 排班安全合規檢查")
    overtime_4xx = df_hours[(df_hours['職稱'] == '役男') & (df_hours['今日累計時數'] > 8)]
    overtime_1xx = df_hours[(df_hours['今日累計時數'] > 14)]
    
    if overtime_4xx.empty and overtime_1xx.empty:
        st.success("✅ 所有同仁工時均符合安全死線！")
    else:
        if not overtime_4xx.empty:
            st.error("🚨 警告：有役男工時超過 8 小時！")
        if not overtime_1xx.empty:
            st.error("🚨 警告：有隊員工時超過 14 小時天花板！")
