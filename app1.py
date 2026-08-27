import itertools
import random
import pandas as pd
import streamlit as st

# 頁面配置
st.set_page_config(page_title="羽球智慧排場系統", page_icon="🏸", layout="wide")

# 自訂 CSS：模擬羽球場地視覺效果
st.markdown(
    """
<style>
.court-container {
    background-color: #1b7340;
    border: 3px solid #ffffff;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    color: white;
}
.court-header {
    text-align: center;
    font-size: 1.1rem;
    font-weight: bold;
    border-bottom: 2px dashed #ffffff;
    padding-bottom: 6px;
    margin-bottom: 10px;
}
.team-box {
    background-color: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 6px;
    padding: 8px;
    min-height: 70px;
}
.vs-divider {
    text-align: center;
    font-weight: 900;
    color: #ffeb3b;
    font-size: 1.1rem;
    margin: 4px 0;
}
.player-tag {
    font-size: 0.95rem;
    line-height: 1.4;
}
.idle-court {
    background-color: #555555;
    border: 2px dashed #bbbbbb;
}
/* 讓下拉選單（含收合後的顯示框）可以完整換行顯示程度描述，不被截斷 */
div[data-baseweb="select"] * {
    white-space: normal !important;
    word-break: break-word;
}
div[data-baseweb="popover"] li {
    white-space: normal !important;
    line-height: 1.4;
    align-items: flex-start !important;
    padding-top: 6px;
    padding-bottom: 6px;
}
</style>
""",
    unsafe_allow_html=True,
)

# 台灣羽球推廣協會分級定義 (完整版 1~18 級)
LEVEL_MAP = {
    1: "第 1 級【新手階】剛接觸羽球學會比賽規則，並懂得比賽禮儀",
    2: "第 2 級【新手階】球齡一年內，對發力不熟｜中場距離中高球來回10拍，發球有一半以上成功率",
    3: "第 3 級【新手階】球齡一年內，對發力不熟｜定點有一半可以打到2/3場後，發球有九成以上成功率",
    4: "第 4 級【初階】球齡1~3年｜清楚握拍。長球男生定點可到後場/女生到中後場；會平推；正反轉拍不順",
    5: "第 5 級【初階】球齡1~3年｜清楚握拍，略懂基本腳步，基本球路在非受迫時有一定表現",
    6: "第 6 級【初中階】球齡3~5年｜懂基本腳步與輪轉(尚不熟)，開始會殺切球，非受迫移動長球至中後場",
    7: "第 7 級【初中階】球齡3~5年｜殺切長不論定點或移動成功率7成以上，有基本防守能力但無變化",
    8: "第 8 級【中階】球齡5~10年｜有基本戰略打點，熟悉輪轉，切殺長均7成準確，防守些微變化",
    9: "第 9 級【中階】球齡5~10年｜三種球路9成以上準確與質量，發力已有強度，防守有一定變化穩定度",
    10: "第 10 級【中進階】球齡10年以上｜輪轉概念熟念並能活化運用，策略性戰略及打點皆能有效得分",
    11: "第 11 級【中進階】球齡10年以上｜切殺長吊兼具準確/發力/速度/策略，輕鬆完成反拍，防守具威脅性",
    12: "第 12 級【中進階】球齡10年以上｜高速度移位與靈敏步法，殺切吊具高強度侵略性，常有一擊必殺球路",
    13: "第 13 級【高階】校隊前段/體保/社會甲組等｜球路穩定熟練，防守無死角，球速質量高，戰略組織佳",
    14: "第 14 級【高階】校隊前段/體保/社會甲組等｜攻防無死角，戰術多變，具備頂尖對抗能力與爆發力",
    15: "第 15 級【高階】校隊前段/體保/社會甲組等｜爆發力極強，球速質量頂級，戰略組織與抗壓屬上等",
    16: "第 16 級【職業級】甲組、國家代表選手｜各種球路、戰術、步法已爐火純青",
    17: "第 17 級【職業級】甲組、國家代表選手｜國家代表隊等級，具備成熟穩定的個人技術體系",
    18: "第 18 級【職業級】甲組、國家代表選手｜國際水準，發展出獨特個人專屬球路風格",
}

# 預設內建名單
DEFAULT_PLAYERS = {
    "威儀": {"gender": "男", "level": 3},
    "子瑩": {"gender": "女", "level": 2},
    "亘佑": {"gender": "男", "level": 5},
    "婷婷": {"gender": "女", "level": 1},
    "德偉": {"gender": "男", "level": 6},
    "德馨": {"gender": "女", "level": 4},
    "國權": {"gender": "男", "level": 5},
    "怡柔": {"gender": "女", "level": 2},
    "詠恩": {"gender": "女", "level": 1},
    "婁恩": {"gender": "女", "level": 1},
    "奐宇": {"gender": "男", "level": 1},
    "貝貝": {"gender": "女", "level": 4},
    "佳恩": {"gender": "女", "level": 6},
    "威宏": {"gender": "男", "level": 1},
    "玉山": {"gender": "男", "level": 3},
    "秉鈞": {"gender": "男", "level": 2},
    "偉群": {"gender": "男", "level": 5},
    "靖媚": {"gender": "女", "level": 1},
    "浩光": {"gender": "男", "level": 2},
    "威仰": {"gender": "男", "level": 5},
}

# 初始化 Session State
if "players" not in st.session_state:
    st.session_state.players = {}
    for name, info in DEFAULT_PLAYERS.items():
        st.session_state.players[name] = {
            "gender": info["gender"],
            "level": info["level"],
            "played": 0,
            "resting_rounds": 0,
            "status": "idle",
        }

if "courts" not in st.session_state:
    st.session_state.courts = {i: None for i in range(1, 6)}
if "partner_history" not in st.session_state:
    st.session_state.partner_history = {}

# 允許的隊伍戰力總和差距上限
MAX_LEVEL_DIFF = 3
# 同隊兩人的級數差距上限
MAX_PARTNER_LEVEL_DIFF = 3


def get_partner_count(p1, p2):
    return st.session_state.partner_history.get(frozenset((p1, p2)), 0)


# 核心演算法：挑選 4 人並進行戰力平衡配對
def select_and_balance_match():
    available = [
        name
        for name, data in st.session_state.players.items()
        if data["status"] == "idle"
    ]
    if len(available) < 4:
        return None

    # 優先排序：出賽次數少 > 休息輪次多
    sorted_players = sorted(
        available,
        key=lambda x: (
            st.session_state.players[x]["played"],
            -st.session_state.players[x]["resting_rounds"],
            random.random(),
        ),
    )
    priority_rank = {name: idx for idx, name in enumerate(sorted_players)}

    def best_split(four, strict_partner=True):
        best = None
        for comb in itertools.combinations(four, 2):
            t1 = list(comb)
            t2 = [p for p in four if p not in t1]
            if strict_partner:
                partner_diff_t1 = abs(
                    st.session_state.players[t1[0]]["level"]
                    - st.session_state.players[t1[1]]["level"]
                )
                partner_diff_t2 = abs(
                    st.session_state.players[t2[0]]["level"]
                    - st.session_state.players[t2[1]]["level"]
                )
                if partner_diff_t1 > MAX_PARTNER_LEVEL_DIFF or partner_diff_t2 > MAX_PARTNER_LEVEL_DIFF:
                    continue
            sum1 = sum(st.session_state.players[p]["level"] for p in t1)
            sum2 = sum(st.session_state.players[p]["level"] for p in t2)
            diff = abs(sum1 - sum2)
            repeat = get_partner_count(t1[0], t1[1]) + get_partner_count(t2[0], t2[1])
            score = (repeat, diff)
            if best is None or score < best[0]:
                best = (score, (t1, t2, sum1, sum2, diff))
        return best

    valid_matches = []
    relaxed_matches = []
    fallback_matches = []

    for four in itertools.combinations(sorted_players, 4):
        result = best_split(four, strict_partner=True)
        if result is not None:
            _, (t1, t2, sum1, sum2, diff) = result
            repeat = get_partner_count(t1[0], t1[1]) + get_partner_count(t2[0], t2[1])
            priority_cost = sum(priority_rank[p] for p in four)
            entry = (repeat, priority_cost, diff, (t1, t2, sum1, sum2))
            if diff <= MAX_LEVEL_DIFF:
                valid_matches.append(entry)
            else:
                relaxed_matches.append(entry)

        result_fb = best_split(four, strict_partner=False)
        if result_fb is not None:
            _, (t1_fb, t2_fb, sum1_fb, sum2_fb, diff_fb) = result_fb
            repeat_fb = get_partner_count(t1_fb[0], t1_fb[1]) + get_partner_count(t2_fb[0], t2_fb[1])
            priority_cost_fb = sum(priority_rank[p] for p in four)
            fallback_matches.append((repeat_fb, priority_cost_fb, diff_fb, (t1_fb, t2_fb, sum1_fb, sum2_fb)))

    if valid_matches:
        pool = valid_matches
    elif relaxed_matches:
        pool = relaxed_matches
    else:
        pool = fallback_matches

    if not pool:
        return None

    pool.sort(key=lambda e: (e[0], e[1], e[2]))
    return pool[0][3]


# 排入指定場地
def assign_court(court_id):
    match_data = select_and_balance_match()
    if match_data:
        t1, t2, sum1, sum2 = match_data
        for p in t1 + t2:
            st.session_state.players[p]["status"] = "playing"
            st.session_state.players[p]["played"] += 1
            st.session_state.players[p]["resting_rounds"] = 0

        for name, data in st.session_state.players.items():
            if data["status"] == "idle":
                data["resting_rounds"] += 1

        st.session_state.courts[court_id] = {
            "team1": t1,
            "team2": t2,
            "sum1": sum1,
            "sum2": sum2,
            "diff_exceeded": abs(sum1 - sum2) > MAX_LEVEL_DIFF,
            "partner_diff_exceeded": (
                abs(st.session_state.players[t1[0]]["level"] - st.session_state.players[t1[1]]["level"]) > MAX_PARTNER_LEVEL_DIFF
                or abs(st.session_state.players[t2[0]]["level"] - st.session_state.players[t2[1]]["level"]) > MAX_PARTNER_LEVEL_DIFF
            ),
        }

        for team in (t1, t2):
            key = frozenset(team)
            st.session_state.partner_history[key] = (
                st.session_state.partner_history.get(key, 0) + 1
            )

        return True
    return False


# 結束場地並即刻滾動下一場
def finish_court(court_id):
    current = st.session_state.courts[court_id]
    if current:
        for p in current["team1"] + current["team2"]:
            if p in st.session_state.players:
                st.session_state.players[p]["status"] = "idle"
        st.session_state.courts[court_id] = None

    assign_court(court_id)


# --- 側邊欄：球員管理 ---
with st.sidebar:
    st.header("📋 球員管理中心")
    tab_add, tab_edit = st.tabs(["➕ 登記新增", "✏️ 編輯 / 修改"])

    with tab_add:
        level_input = st.selectbox(
            "羽球程度級數",
            options=list(LEVEL_MAP.keys()),
            format_func=lambda x: LEVEL_MAP[x],
            index=2,
            key="add_level_select",
        )
        st.info(f"📖 完整說明：{LEVEL_MAP[level_input]}")

        with st.form("add_player_form", clear_on_submit=True):
            name_input = st.text_input("球員姓名", placeholder="例如：王小明").strip()
            gender_input = st.selectbox("性別", ["男", "女"])
            submit_btn = st.form_submit_button("確認登記加入", use_container_width=True)

            if submit_btn:
                if not name_input:
                    st.error("請輸入球員姓名！")
                elif name_input in st.session_state.players:
                    st.warning("此球員姓名已存在！")
                else:
                    st.session_state.players[name_input] = {
                        "gender": gender_input,
                        "level": level_input,
                        "played": 0,
                        "resting_rounds": 0,
                        "status": "idle",
                    }
                    st.success(f"已登記：{name_input}")
                    st.rerun()

    with tab_edit:
        if not st.session_state.players:
            st.info("目前尚無球員名單。")
        else:
            selected_player = st.selectbox(
                "選擇要修改的球員",
                options=list(st.session_state.players.keys()),
                key="edit_player_select",
            )
            p_data = st.session_state.players[selected_player]

            new_level = st.selectbox(
                "羽球程度級數",
                options=list(LEVEL_MAP.keys()),
                format_func=lambda x: LEVEL_MAP[x],
                index=list(LEVEL_MAP.keys()).index(p_data["level"]),
                key="edit_level_select",
            )
            st.info(f"📖 完整說明：{LEVEL_MAP[new_level]}")

            with st.form("edit_player_form"):
                new_name = st.text_input("修改姓名", value=selected_player).strip()
                new_gender = st.selectbox(
                    "性別", ["男", "女"], index=0 if p_data["gender"] == "男" else 1
                )
                new_played = st.number_input(
                    "已出賽次數 (可手動校正)",
                    min_value=0,
                    value=p_data["played"],
                    step=1,
                )

                status_options = {
                    "idle": "場下待命 (可被排入)",
                    "paused": "暫停/請假 (不排入)",
                    "playing": "比賽中",
                }
                curr_status = p_data["status"]
                available_status = ["idle", "paused"]
                if curr_status == "playing":
                    available_status.append("playing")

                new_status = st.selectbox(
                    "目前狀態",
                    options=available_status,
                    index=available_status.index(curr_status),
                    format_func=lambda x: status_options[x],
                )

                save_col1, save_col2 = st.columns(2)
                with save_col1:
                    update_btn = st.form_submit_button("💾 儲存修改", use_container_width=True)
                with save_col2:
                    delete_btn = st.form_submit_button("🗑️ 刪除球員", use_container_width=True)

                if update_btn:
                    if not new_name:
                        st.error("姓名不能為空！")
                    elif new_name != selected_player and new_name in st.session_state.players:
                        st.error("已存在相同姓名的其他球員！")
                    else:
                        st.session_state.players.pop(selected_player)
                        st.session_state.players[new_name] = {
                            "gender": new_gender,
                            "level": new_level,
                            "played": new_played,
                            "resting_rounds": p_data["resting_rounds"],
                            "status": new_status,
                        }

                        for c_id, match in st.session_state.courts.items():
                            if match:
                                if selected_player in match["team1"]:
                                    idx = match["team1"].index(selected_player)
                                    match["team1"][idx] = new_name
                                    match["sum1"] = sum(st.session_state.players[p]["level"] for p in match["team1"])
                                if selected_player in match["team2"]:
                                    idx = match["team2"].index(selected_player)
                                    match["team2"][idx] = new_name
                                    match["sum2"] = sum(st.session_state.players[p]["level"] for p in match["team2"])

                        updated_history = {}
                        for key, count in st.session_state.partner_history.items():
                            if selected_player in key:
                                key = frozenset(new_name if p == selected_player else p for p in key)
                            updated_history[key] = updated_history.get(key, 0) + count
                        st.session_state.partner_history = updated_history

                        st.success(f"球員 {new_name} 資料已更新！")
                        st.rerun()

                if delete_btn:
                    if p_data["status"] == "playing":
                        st.error("該球員目前正在場上比賽，請先結束該場比賽再刪除！")
                    else:
                        del st.session_state.players[selected_player]
                        st.success(f"已刪除球員：{selected_player}")
                        st.rerun()

    if st.session_state.players:
        st.markdown("---")
        st.subheader("📊 即時球員名單")
        df_list = []
        for name, data in st.session_state.players.items():
            status_text = {
                "idle": "🟢 待命中",
                "playing": "🔴 比賽中",
                "paused": "⚪ 請假中",
            }.get(data["status"], "未知")
            df_list.append(
                {
                    "姓名": name,
                    "性別": data["gender"],
                    "級數": f"{data['level']} 級",
                    "出賽數": data["played"],
                    "狀態": status_text,
                }
            )
        st.dataframe(pd.DataFrame(df_list), use_container_width=True, hide_index=True)


# --- 主畫面：場地配置與智慧即時對戰 ---
st.title("🏸 雙打智慧即時排場系統")

top_col1, top_col2 = st.columns([2, 4])
with top_col1:
    court_count = st.slider("設定啟用場地數 (最多 5 面)", min_value=1, max_value=5, value=2)
with top_col2:
    st.caption("提示：點擊場地下方的「結束此場」會立刻將該場人員換下，並以出賽最少者自動補進下一場。")
    if st.button("🚀 為所有空場自動補滿對戰組合"):
        for c_id in range(1, court_count + 1):
            if st.session_state.courts[c_id] is None:
                assign_court(c_id)
        st.rerun()

st.markdown("---")

cols = st.columns(court_count)

for i in range(court_count):
    court_id = i + 1
    match = st.session_state.courts.get(court_id)

    with cols[i]:
        if match:
            p1, p2 = match["team1"]
            p3, p4 = match["team2"]
            d1, d2 = st.session_state.players[p1], st.session_state.players[p2]
            d3, d4 = st.session_state.players[p3], st.session_state.players[p4]

            level_diff = abs(match["sum1"] - match["sum2"])
            header_label = f"🏸 第 {court_id} 場地 (進行中)"
            if match.get("diff_exceeded"):
                header_label += f" ⚠️ 差距 {level_diff}"

            st.markdown(
                f"""
            <div class="court-container">
                <div class="court-header">{header_label}</div>
                <div class="team-box">
                    <div class="player-tag">🔵 <b>{p1}</b> ({d1['gender']} / {d1['level']}級)</div>
                    <div class="player-tag">🔵 <b>{p2}</b> ({d2['gender']} / {d2['level']}級)</div>
                    <div style="font-size:0.75rem; text-align:right; color:#ffd700;">隊伍戰力: {match['sum1']}</div>
                </div>
                <div class="vs-divider">VS</div>
                <div class="team-box">
                    <div class="player-tag">🔴 <b>{p3}</b> ({d3['gender']} / {d3['level']}級)</div>
                    <div class="player-tag">🔴 <b>{p4}</b> ({d4['gender']} / {d4['level']}級)</div>
                    <div style="font-size:0.75rem; text-align:right; color:#ffd700;">隊伍戰力: {match['sum2']}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if match.get("diff_exceeded") or match.get("partner_diff_exceeded"):
                warnings = []
                if match.get("partner_diff_exceeded"):
                    warnings.append(f"同隊隊友級數差超過 {MAX_PARTNER_LEVEL_DIFF} 級")
                if match.get("diff_exceeded"):
                    warnings.append(f"跨隊戰力差超過 {MAX_LEVEL_DIFF}")
                st.caption(
                    f"⚠️ 目前場下待命人數有限，無法完全滿足所有條件（{'、'.join(warnings)}），"
                    "已自動選擇最佳可能組合。"
                )

            # 新增：手動調整對戰組合功能
            with st.expander("🔄 手動調整對戰組合"):
                current_4 = [p1, p2, p3, p4]
                idle_players = [name for name, data in st.session_state.players.items() if data["status"] == "idle"]
                options = current_4 + idle_players

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**🔵 隊伍 1**")
                    # 【修正重點】：在 key 後面加上目前的球員變數 (p1, p2...)，強制刷新元件狀態
                    new_p1 = st.selectbox("球員 A", options, index=options.index(p1), key=f"c{court_id}_p1_{p1}")
                    new_p2 = st.selectbox("球員 B", options, index=options.index(p2), key=f"c{court_id}_p2_{p2}")
                with col_b:
                    st.markdown("**🔴 隊伍 2**")
                    new_p3 = st.selectbox("球員 C", options, index=options.index(p3), key=f"c{court_id}_p3_{p3}")
                    new_p4 = st.selectbox("球員 D", options, index=options.index(p4), key=f"c{court_id}_p4_{p4}")

                if st.button("💾 確認修改組合", key=f"save_court_{court_id}", use_container_width=True):
                    new_four = [new_p1, new_p2, new_p3, new_p4]
                    if len(set(new_four)) < 4:
                        st.error("⚠️ 四個位置的球員不能重複選擇！")
                    else:
                        # 1. 舊球員先退回場下 (扣除這次出賽紀錄)
                        for p in current_4:
                            st.session_state.players[p]["status"] = "idle"
                            st.session_state.players[p]["played"] = max(0, st.session_state.players[p]["played"] - 1)

                        # 2. 新球員登錄上場 (增加出賽紀錄並重置休息)
                        for p in new_four:
                            st.session_state.players[p]["status"] = "playing"
                            st.session_state.players[p]["played"] += 1
                            st.session_state.players[p]["resting_rounds"] = 0

                        # 3. 更新場地與戰力資料
                        match["team1"] = [new_p1, new_p2]
                        match["team2"] = [new_p3, new_p4]
                        match["sum1"] = sum(st.session_state.players[p]["level"] for p in match["team1"])
                        match["sum2"] = sum(st.session_state.players[p]["level"] for p in match["team2"])
                        match["diff_exceeded"] = abs(match["sum1"] - match["sum2"]) > MAX_LEVEL_DIFF
                        match["partner_diff_exceeded"] = (
                            abs(st.session_state.players[new_p1]["level"] - st.session_state.players[new_p2]["level"]) > MAX_PARTNER_LEVEL_DIFF or
                            abs(st.session_state.players[new_p3]["level"] - st.session_state.players[new_p4]["level"]) > MAX_PARTNER_LEVEL_DIFF
                        )
                        st.rerun()
            if st.button(
                f"⏹️ 結束第 {court_id} 場 (排下一組)",
                key=f"btn_{court_id}",
                use_container_width=True,
            ):
                finish_court(court_id)
                st.rerun()

        else:
            st.markdown(
                f"""
            <div class="court-container idle-court">
                <div class="court-header">🏸 第 {court_id} 場地 (閒置中)</div>
                <div style="text-align:center; padding: 42px 0; color:#cccccc;">目前無對戰</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"▶️ 立即排入對戰", key=f"start_{court_id}", use_container_width=True
            ):
                if not assign_court(court_id):
                    st.warning("場下可用且待命人數不足 4 人，無法開場！")
                else:
                    st.rerun()