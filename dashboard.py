# -*- coding: utf-8 -*-
# ============================================================
#  מערכת ניהול תקציב אוגדתי - דשבורד Streamlit
#  פרויקט Vibe Coding - פייתון
#  ------------------------------------------------------------
#  הרצה:  streamlit run dashboard.py
#  הדשבורד נפתח בדפדפן (localhost - על המחשב המקומי בלבד)
# ============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------------------------------
#  שכבה 1: שכבת הנתונים
# ------------------------------------------------------------
categories = ["אימונים", "רווחה וחינוך", "מזון", "התעצמות", "מבצעי", "שוטף"]

# st.session_state = "זיכרון" של הדשבורד ששורד בין לחיצות.
# כאן שומרים את הנתונים כדי שהזנות חדשות לא יימחקו.
if "division_data" not in st.session_state:
    st.session_state.division_data = {
        "חטיבה 401": {
            "אימונים": [2400, 2520], "רווחה וחינוך": [900, 860], "מזון": [1800, 1840],
            "התעצמות": [3200, 3680], "מבצעי": [2100, 2050], "שוטף": [1400, 1390],
        },
        "חטיבה 188": {
            "אימונים": [2200, 2150], "רווחה וחינוך": [850, 900], "מזון": [1700, 1680],
            "התעצמות": [3000, 2950], "מבצעי": [2000, 2240], "שוטף": [1300, 1290],
        },
        "גדוד תקשוב": {
            "אימונים": [600, 620], "רווחה וחינוך": [400, 380], "מזון": [500, 510],
            "התעצמות": [1800, 2100], "מבצעי": [900, 880], "שוטף": [700, 760],
        },
    }

running_projects = [
    ["שדרוג מערך אש\"ל", "חטיבה 401", "חיסכון 12% במזון", True, -4,
     "עומד ביעד, חיסכון מעבר לצפי", "-"],
    ["מיכון מחסני התעצמות", "חטיבה 401", "קיצור אספקה ל-48ש'", False, 18,
     "חריגה תקציבית + עיכוב בלו\"ז", "הקפאת רכש לא קריטי, בחינת ספק חלופי"],
    ["מערך כשירות מבצעי", "חטיבה 188", "זמינות 90%", False, 11,
     "חריגה במבצעי, יעד לא הושג", "ניתוח שורש לעלות, תיעדוף משימות"],
]

review_projects = [
    ["איחוד מטבחים גדודיים", "חטיבה 401", 600, 140],
    ["מעבר לתחזוקה מונעת", "חטיבה 188", 450, 180],
    ["וירטואליזציית שרתים", "גדוד תקשוב", 800, 120],
    ["מערכת ניהול מלאי מרכזית", "אוגדה", 1200, 380],
]

# ------------------------------------------------------------
#  שכבה 2: שכבת הלוגיקה (המנוע) - זהה לגרסת הטרמינל
# ------------------------------------------------------------
def calc_deviation(planned, actual):
    if planned == 0:
        return 0
    return round((actual - planned) / planned * 100, 1)

def get_status(deviation):
    if deviation > 5:
        return "חריגה"
    elif deviation < -5:
        return "חיסכון"
    else:
        return "תקין"

def unit_totals(unit):
    tp = sum(unit[c][0] for c in categories)
    ta = sum(unit[c][1] for c in categories)
    return tp, ta

def payback_years(invest, yearly_saving):
    if yearly_saving == 0:
        return 999
    return round(invest / yearly_saving, 1)

def efficiency_rank(years):
    if years < 3:
        return "גבוה"
    elif years < 5:
        return "בינוני"
    else:
        return "נמוך"

# ------------------------------------------------------------
#  שכבה 3: התצוגה (הדשבורד עצמו)
# ------------------------------------------------------------
st.set_page_config(page_title="תקציב אוגדתי", page_icon="📊", layout="wide")
st.markdown("""
    <style>
    .stApp { direction: rtl; }
    section[data-testid="stSidebar"] { direction: rtl; width: 300px !important; min-width: 300px !important; } }
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
    .stApp div, .stApp span { text-align: right; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { direction: rtl; text-align: right; }
    .stDataFrame { direction: rtl; }
    [data-baseweb="tab-list"] { direction: rtl; }
    </style>
""", unsafe_allow_html=True)
st.title("📊 מערכת ניהול תקציב אוגדתי")
st.caption("נתונים מפוברקים להדגמה · שנת עבודה 2026")

# --- בורר מצב: עריכה או צפייה בלבד ---
mode = st.sidebar.radio("מצב הפעלה:", ["צפייה בלבד (מפקדים)", "עריכה (הזנת נתונים)"])
edit_mode = mode.startswith("עריכה")

data = st.session_state.division_data

# --- כרטיסי סיכום עליונים ---
total_p = sum(unit_totals(data[u])[0] for u in data)
total_a = sum(unit_totals(data[u])[1] for u in data)
total_dev = calc_deviation(total_p, total_a)
flag_count = sum(
    1 for u in data for c in categories
    if get_status(calc_deviation(data[u][c][0], data[u][c][1])) == "חריגה"
)
col1, col2, col3, col4 = st.columns(4)
col1.metric("סה\"כ מתוכנן", f"₪{total_p:,}K")
col2.metric("סה\"כ בפועל", f"₪{total_a:,}K", f"{total_dev}%")
col3.metric("מספר יחידות", len(data))
col4.metric("דגלים אדומים", flag_count)

st.divider()

# --- טאבים לחלקים השונים ---
tab1, tab2, tab3 = st.tabs(["💰 תקציב וקטגוריות", "🚦 פרויקטים רצים", "📈 פרויקטים לבחינה"])

# === טאב 1: תקציב לפי יחידה וקטגוריה ===
with tab1:
    unit_choice = st.selectbox("בחר/י יחידה:", list(data.keys()))
    unit = data[unit_choice]

    # בונים טבלה (DataFrame) להצגה ולגרף
    rows = []
    for c in categories:
        p, a = unit[c][0], unit[c][1]
        dev = calc_deviation(p, a)
        rows.append({"קטגוריה": c, "מתוכנן": p, "בפועל": a,
                     "סטייה %": dev, "סטטוס": get_status(dev)})
    df = pd.DataFrame(rows)

    # גרף עמודות: מתוכנן מול בפועל
    fig = go.Figure()
    fig.add_trace(go.Bar(name="מתוכנן", x=df["קטגוריה"], y=df["מתוכנן"], marker_color="#85B7EB"))
    fig.add_trace(go.Bar(name="בפועל", x=df["קטגוריה"], y=df["בפועל"], marker_color="#185FA5"))
    fig.update_layout(barmode="group", font=dict(size=14), xaxis=dict(tickangle=0),
                      legend=dict(orientation="h", y=1.1), height=400,
                      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    # טבלה עם הדגשת חריגות
    def highlight(row):
        if row["סטטוס"] == "חריגה":
            return ["background-color: #ffd6d6"] * len(row)
        elif row["סטטוס"] == "חיסכון":
            return ["background-color: #d6f5e3"] * len(row)
        return [""] * len(row)
    st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True, hide_index=True)

# === טאב 2: פרויקטים רצים ===
with tab2:
    for proj in running_projects:
        name, unit_n, target, met, bvar, note, solution = proj
        if met:
            st.success(f"✅ **{name}** ({unit_n}) — עומד ביעד")
        else:
            st.error(f"🚩 **{name}** ({unit_n}) — דגל אדום")
        st.write(f"יעד: {target} · סטיית תקציב: {bvar}%")
        st.write(f"מצב: {note}")
        if not met:
            st.info(f"💡 פתרון מוצע: {solution}")
        st.divider()

# === טאב 3: פרויקטים לבחינה ===
with tab3:
    st.write("מדורג לפי מדד התייעלות — תקופת החזר קצרה = עדיפות גבוהה")
    scored = []
    for name, unit_n, invest, saving in review_projects:
        years = payback_years(invest, saving)
        scored.append({"פרויקט": name, "יחידה": unit_n, "השקעה": invest,
                       "חיסכון שנתי": saving, "החזר (שנים)": years,
                       "התייעלות": efficiency_rank(years)})
    rdf = pd.DataFrame(scored).sort_values("החזר (שנים)")
    st.dataframe(rdf, use_container_width=True, hide_index=True)

# === הזנת נתונים (רק במצב עריכה) ===
if edit_mode:
    st.sidebar.divider()
    st.sidebar.subheader("➕ הוספת יחידה")
    with st.sidebar.form("add_unit"):
        new_name = st.text_input("שם היחידה")
        new_vals = {}
        for c in categories:
            col_a, col_b = st.columns(2)
            p = col_a.number_input(f"{c} - מתוכנן", min_value=0, value=0, key=f"p_{c}")
            a = col_b.number_input(f"{c} - בפועל", min_value=0, value=0, key=f"a_{c}")
            new_vals[c] = [p, a]
        submitted = st.form_submit_button("הוסף יחידה")
        if submitted and new_name:
            st.session_state.division_data[new_name] = new_vals
            st.success(f"היחידה '{new_name}' נוספה!")
            st.rerun()
else:
    st.sidebar.info("מצב צפייה — הנתונים מוצגים לקריאה בלבד.")
