"""
⚡ Smart Energy Consumption Tracker — v2.0
Full-stack Streamlit dashboard with appliance-level intelligence,
rich analytics, smart insights, warnings, and actionable tips.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="⚡ Smart Energy Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════
APPLIANCES = ["AC", "Fan", "Refrigerator", "Washing Machine", "Lights", "Others"]

APPLIANCE_ICONS = {
    "AC": "❄️", "Fan": "🌀", "Refrigerator": "🧊",
    "Washing Machine": "🫧", "Lights": "💡", "Others": "🔌"
}

# Hex colours for Plotly discrete colour maps
COLORS_HEX = {
    "AC": "#00C9FF",
    "Fan": "#92FE9D",
    "Refrigerator": "#FC5C7D",
    "Washing Machine": "#A855F7",
    "Lights": "#F7971E",
    "Others": "#C6EA8D",
}

# *** BUG FIX ***
# Pre-built rgba() strings for fillcolor — NEVER use string replace on hex.
# Plotly requires valid rgb/rgba/hsl/hex strings, not malformed ones like "rgba(00C9FF,0.6)".
COLORS_RGBA = {
    "AC":              "rgba(0,201,255,0.50)",
    "Fan":             "rgba(146,254,157,0.50)",
    "Refrigerator":    "rgba(252,92,125,0.50)",
    "Washing Machine": "rgba(168,85,247,0.50)",
    "Lights":          "rgba(247,151,30,0.50)",
    "Others":          "rgba(198,234,141,0.50)",
}

RATE_PER_UNIT = 8.0       # ₹ / kWh default
WATTAGE = {               # kW per appliance (hours → kWh)
    "AC": 1.5, "Fan": 0.075, "Refrigerator": 0.15,
    "Washing Machine": 0.5, "Lights": 0.06, "Others": 0.1
}

# ═══════════════════════════════════════════════════════════
# CUSTOM CSS — DARK FUTURISTIC THEME
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; }
h1, h2, h3 { font-family: 'Orbitron', monospace; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060818 0%, #0d1540 55%, #060818 100%) !important;
    border-right: 1px solid rgba(0,201,255,0.15);
}
section[data-testid="stSidebar"] * { color: #c8d8ff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(0,201,255,0.15) !important; }

/* METRIC CARDS */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(0,201,255,0.07) 0%, rgba(10,10,40,0.92) 100%);
    border: 1px solid rgba(0,201,255,0.22);
    border-radius: 18px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 0 25px rgba(0,201,255,0.06);
    transition: transform 0.25s, box-shadow 0.25s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 40px rgba(0,201,255,0.18);
}
[data-testid="metric-container"] label {
    color: #00C9FF !important;
    font-weight: 600; font-size: 0.72rem;
    letter-spacing: 0.1em; text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 1.7rem !important; font-weight: 700;
}

/* TABS */
button[data-baseweb="tab"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important; font-weight: 700 !important;
    letter-spacing: 0.04em !important; color: #7eb3ff !important;
}
button[data-baseweb="tab"][aria-selected="true"] { color: #00C9FF !important; }
[data-baseweb="tab-list"] { border-bottom: 1px solid rgba(0,201,255,0.15) !important; }

/* HERO */
.hero-banner {
    background: linear-gradient(135deg, #060818 0%, #0d1540 45%, #1a0533 100%);
    border-radius: 22px; padding: 2.2rem 2.8rem; margin-bottom: 1.5rem;
    border: 1px solid rgba(0,201,255,0.22);
    box-shadow: 0 0 60px rgba(0,201,255,0.05), 0 0 120px rgba(168,85,247,0.04);
}
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem; font-weight: 900; margin: 0; line-height: 1.2;
    background: linear-gradient(90deg, #00C9FF, #92FE9D, #A855F7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub { color: #7eb3ff; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 300; }

/* CARDS */
.insight-card {
    background: linear-gradient(135deg, rgba(0,201,255,0.05), rgba(10,10,40,0.85));
    border-left: 3px solid #00C9FF; border-radius: 12px;
    padding: 0.9rem 1.3rem; margin: 0.45rem 0;
    color: #c8d8ff; font-size: 0.93rem; line-height: 1.65;
}
.rec-card {
    background: linear-gradient(135deg, rgba(146,254,157,0.05), rgba(10,10,40,0.85));
    border-left: 3px solid #92FE9D; border-radius: 12px;
    padding: 0.9rem 1.3rem; margin: 0.45rem 0;
    color: #c8d8ff; font-size: 0.93rem; line-height: 1.65;
}
.tip-card {
    background: linear-gradient(135deg, rgba(247,151,30,0.07), rgba(10,10,40,0.85));
    border-left: 3px solid #F7971E; border-radius: 12px;
    padding: 0.9rem 1.3rem; margin: 0.45rem 0;
    color: #c8d8ff; font-size: 0.93rem; line-height: 1.65;
}
.alert-danger {
    background: linear-gradient(135deg, rgba(252,92,125,0.13), rgba(10,10,40,0.88));
    border: 1px solid rgba(252,92,125,0.38); border-left: 4px solid #FC5C7D;
    border-radius: 12px; padding: 1rem 1.3rem; margin: 0.45rem 0;
    color: #ffc8d4; font-size: 0.93rem; font-weight: 500;
}
.alert-warning-card {
    background: linear-gradient(135deg, rgba(247,151,30,0.10), rgba(10,10,40,0.88));
    border: 1px solid rgba(247,151,30,0.32); border-left: 4px solid #F7971E;
    border-radius: 12px; padding: 1rem 1.3rem; margin: 0.45rem 0;
    color: #ffe0b0; font-size: 0.93rem; font-weight: 500;
}
.alert-ok {
    background: linear-gradient(135deg, rgba(146,254,157,0.07), rgba(10,10,40,0.88));
    border: 1px solid rgba(146,254,157,0.28); border-left: 4px solid #92FE9D;
    border-radius: 12px; padding: 1rem 1.3rem; margin: 0.45rem 0;
    color: #b0ffc0; font-size: 0.93rem;
}
.section-title {
    font-family: 'Orbitron', monospace; font-size: 1rem; font-weight: 700;
    color: #00C9FF; letter-spacing: 0.08em; text-transform: uppercase;
    margin: 1.5rem 0 0.75rem 0;
    border-bottom: 1px solid rgba(0,201,255,0.15); padding-bottom: 0.4rem;
}
.kpi-divider { border: none; border-top: 1px solid rgba(0,201,255,0.1); margin: 1rem 0; }

/* BUTTONS */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(135deg, #00C9FF, #0072ff) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-family: 'Orbitron', monospace !important; font-size: 0.76rem !important;
    font-weight: 700 !important; letter-spacing: 0.05em !important;
    box-shadow: 0 4px 20px rgba(0,201,255,0.22) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,201,255,0.38) !important;
}
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060818; }
::-webkit-scrollbar-thumb { background: rgba(0,201,255,0.28); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SAMPLE DATA — rich 180-day dataset
# ═══════════════════════════════════════════════════════════
def generate_sample_data() -> pd.DataFrame:
    """
    Realistic 180-day dataset with:
    - Seasonal summer spike (last 60 days = hotter months)
    - Weekend bumps for AC, Lights, Washing Machine
    - Washing machine 3x/week rhythm
    - Gradual consumption creep (+0.5%/week)
    - Two deliberate anomaly spikes (parties / broken AC)
    """
    np.random.seed(7)
    days  = 180
    dates = [datetime.today() - timedelta(days=i) for i in range(days - 1, -1, -1)]
    rows  = []

    for idx, d in enumerate(dates):
        is_weekend  = d.weekday() >= 5
        is_wash_day = d.weekday() in (0, 3, 5)          # Mon, Thu, Sat
        summer      = 1.40 if idx > 120 else 1.0        # summer spike last 60 days
        creep       = 1.0 + (idx / 7) * 0.005           # gradual +0.5%/week

        row = {"Date": pd.Timestamp(d.date())}
        row["AC"]              = max(0, round((3.8 + np.random.normal(0, 0.35))
                                             * summer * creep
                                             + (0.9 if is_weekend else 0), 2))
        row["Fan"]             = max(0, round(1.1 + np.random.normal(0, 0.12)
                                             + (0.2 if is_weekend else 0), 2))
        row["Refrigerator"]    = max(0, round(1.52 + np.random.normal(0, 0.04), 2))  # near-constant
        row["Washing Machine"] = (
            max(0, round(1.4 + np.random.normal(0, 0.15), 2))
            if is_wash_day else round(np.random.uniform(0, 0.04), 2)
        )
        row["Lights"]          = max(0, round(0.55 + np.random.normal(0, 0.08)
                                             + (0.28 if is_weekend else 0), 2))
        row["Others"]          = max(0, round(0.45 + np.random.normal(0, 0.1), 2))

        # Two dramatic anomaly spikes
        if idx in (30, 108):
            row["AC"]     += 4.5
            row["Others"] += 2.2

        row["Total Units"] = round(sum(row[a] for a in APPLIANCES), 2)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# ═══════════════════════════════════════════════════════════
# DATA PROCESSING
# ═══════════════════════════════════════════════════════════
def validate_uploaded_df(df: pd.DataFrame):
    df.columns = [c.strip().title() for c in df.columns]
    aliases = {"Fridge": "Refrigerator", "Washing": "Washing Machine",
               "Light": "Lights", "Other": "Others", "Ac": "AC"}
    df.rename(columns=aliases, inplace=True)
    if "Date" not in df.columns:
        st.error("❌ Uploaded file must have a 'Date' column.")
        return None
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    for col in APPLIANCES:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "Total Units" not in df.columns:
        df["Total Units"] = df[APPLIANCES].sum(axis=1)
    df["Total Units"] = pd.to_numeric(df["Total Units"], errors="coerce").fillna(
        df[APPLIANCES].sum(axis=1))
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def aggregate_df(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    df = df.copy()
    if mode == "Weekly":
        df["Period"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    elif mode == "Monthly":
        df["Period"] = df["Date"].dt.to_period("M").apply(lambda r: r.start_time)
    else:
        df["Period"] = df["Date"]
    agg = df.groupby("Period")[APPLIANCES + ["Total Units"]].sum().reset_index()
    agg.rename(columns={"Period": "Date"}, inplace=True)
    return agg


def detect_anomalies(df: pd.DataFrame, mult: float):
    mean_v = df["Total Units"].mean()
    thr    = mean_v * mult
    return df[df["Total Units"] > thr].copy(), thr


# ═══════════════════════════════════════════════════════════
# INSIGHTS ENGINE
# ═══════════════════════════════════════════════════════════
def generate_insights(df: pd.DataFrame, agg: pd.DataFrame, rate: float) -> list:
    insights = []
    app_totals = {a: df[a].sum() for a in APPLIANCES}
    total_kwh  = df["Total Units"].sum()

    top_app  = max(app_totals, key=app_totals.get)
    top_pct  = app_totals[top_app] / total_kwh * 100
    insights.append(
        f"⚡ <b>{top_app}</b> is your #1 energy consumer — "
        f"<b>{top_pct:.1f}%</b> of total usage "
        f"({app_totals[top_app]:.1f} kWh · ₹{app_totals[top_app]*rate:,.0f})."
    )

    fridge_cv = df["Refrigerator"].std() / (df["Refrigerator"].mean() + 1e-9)
    if fridge_cv < 0.15:
        insights.append(
            "🧊 <b>Refrigerator</b> runs a perfectly constant baseline — expected behaviour. "
            "A BEE 5-star model could cut this load by ~30%."
        )

    if len(agg) >= 6:
        half = len(agg) // 2
        d1   = agg.iloc[:half]["Total Units"].mean()
        d2   = agg.iloc[half:]["Total Units"].mean()
        dp   = (d2 - d1) / d1 * 100
        if dp > 10:
            insights.append(
                f"📈 Consumption has <b>risen {dp:.1f}%</b> in the second half of the period. "
                "Possible reasons: hotter weather, new appliances, or changed habits."
            )
        elif dp < -10:
            insights.append(
                f"📉 Great progress! Consumption <b>dropped {abs(dp):.1f}%</b> in the second half — "
                "your conservation efforts are working."
            )
        else:
            insights.append("📊 Consumption is <b>stable</b> across the entire period — consistent usage pattern.")

    df2 = df.copy()
    df2["DT"] = df2["Date"].dt.dayofweek.apply(lambda x: "Weekend" if x >= 5 else "Weekday")
    wknd = df2[df2["DT"] == "Weekend"]["Total Units"].mean()
    wkdy = df2[df2["DT"] == "Weekday"]["Total Units"].mean()
    dp   = (wknd - wkdy) / wkdy * 100
    if dp > 8:
        insights.append(
            f"🏠 <b>Weekend usage is {dp:.1f}% higher</b> than weekdays "
            f"({wknd:.2f} vs {wkdy:.2f} kWh/day). AC, entertainment, and cooking drive this."
        )
    else:
        insights.append(
            f"🏢 Weekday & weekend usage are similar ({wkdy:.2f} vs {wknd:.2f} kWh/day) — "
            "a consistent household routine."
        )

    sorted_apps = sorted(app_totals, key=app_totals.get, reverse=True)
    top2_pct    = (app_totals[sorted_apps[0]] + app_totals[sorted_apps[1]]) / total_kwh * 100
    insights.append(
        f"🔝 <b>{sorted_apps[0]}</b> + <b>{sorted_apps[1]}</b> together account for "
        f"<b>{top2_pct:.0f}%</b> of all energy. Targeting these two delivers the highest savings."
    )

    wash_days = (df["Washing Machine"] > 0.3).sum()
    freq      = wash_days / (len(df) / 7)
    insights.append(
        f"🫧 Washing machine runs ~<b>{freq:.1f}×/week</b>. "
        "Full cold-water loads can save 30-40% of wash energy."
    )

    daily_avg    = df["Total Units"].mean()
    monthly_cost = daily_avg * 30 * rate
    insights.append(
        f"💰 Estimated monthly bill: <b>₹{monthly_cost:,.0f}</b> · "
        f"Projected annual: <b>₹{monthly_cost*12:,.0f}</b> at ₹{rate}/kWh."
    )
    return insights


def generate_warnings(df: pd.DataFrame, anomalies: pd.DataFrame,
                      spike_thr: float, rate: float) -> list:
    out = []
    for _, row in anomalies.iterrows():
        excess = row["Total Units"] - spike_thr
        out.append({"level": "danger",
                    "msg": (f"🚨 <b>{row['Date'].strftime('%d %b %Y')}</b> — "
                            f"<b>{row['Total Units']:.2f} kWh</b> consumed "
                            f"(threshold {spike_thr:.2f} kWh · excess ≈ ₹{excess*rate:.0f} extra).")})

    ac_pct = df["AC"].sum() / df["Total Units"].sum() * 100
    if ac_pct > 45:
        out.append({"level": "warning",
                    "msg": (f"⚠️ <b>AC = {ac_pct:.1f}% of total usage</b> — dangerously high. "
                            "A programmable thermostat and 24°C set-point can cut this by 15-20%.")})

    daily_avg = df["Total Units"].mean()
    if daily_avg > 12:
        out.append({"level": "warning",
                    "msg": (f"⚠️ Daily average of <b>{daily_avg:.2f} kWh</b> exceeds the "
                            "typical Indian household benchmark of 10 kWh/day.")})

    lights_pct = df["Lights"].sum() / df["Total Units"].sum() * 100
    if lights_pct > 12:
        out.append({"level": "warning",
                    "msg": (f"⚠️ Lighting consumes <b>{lights_pct:.1f}%</b> of total energy. "
                            "A full LED switch can reduce this by 70-80% immediately.")})
    return out


def generate_recommendations(df: pd.DataFrame) -> list:
    recs = []
    app_totals = {a: df[a].sum() for a in APPLIANCES}
    total_kwh  = df["Total Units"].sum()

    if app_totals["AC"] / total_kwh > 0.35:
        recs.append("❄️ <b>Set AC to 24°C</b> — each 1°C reduction increases energy use ~6%. "
                    "Use sleep/timer mode to auto-shut 2 hrs after bedtime.")
        recs.append("🪟 <b>Seal gaps around doors & windows</b> with weather-stripping tape "
                    "(₹200). Poor insulation forces AC to run 20-30% longer.")
    if app_totals["Lights"] > 15:
        recs.append("💡 <b>Replace all bulbs with LEDs</b>. A 9W LED replaces a 60W incandescent — "
                    "85% savings. Payback period: ~3 months.")
        recs.append("🌅 <b>Use natural light</b> during daytime and fit motion sensors in bathrooms "
                    "and corridors to eliminate forgotten-light waste.")
    if app_totals["Washing Machine"] / total_kwh > 0.10:
        recs.append("🫧 <b>Always run a full load</b> — a half-full machine uses nearly the same power. "
                    "Use cold water (30°C) for lightly soiled clothes; saves ~40% of wash energy.")
    if app_totals["Others"] > app_totals["Lights"] * 0.8:
        recs.append("🔌 <b>Kill standby (phantom) power</b> — TVs, set-top boxes, chargers left on "
                    "standby waste 50-100 kWh/month. Use smart power strips or switch off at the wall.")
    recs.append("⏰ <b>Shift heavy loads to off-peak hours</b> (10 PM – 6 AM). "
                "Run washing machine, water heater, and dishwasher at night.")
    recs.append("🌡️ <b>Service your refrigerator twice a year</b> — clean condenser coils, check door seals. "
                "A well-maintained fridge uses 10-15% less power.")
    recs.append("☀️ <b>Explore rooftop solar</b> — a 3 kWp system generates ~360 kWh/month in India. "
                "Government subsidy (PM Surya Ghar) can cover 40-70% of installation cost.")
    recs.append("⭐ <b>Choose BEE 5-star appliances</b> when replacing old ones. "
                "A 5-star AC uses 30-40% less energy than a 3-star — check BEE labels always.")
    return recs


def quick_save_tips() -> list:
    return [
        "🌙 Turn off AC 30 min before sleeping — the room stays cool through thermal inertia.",
        "🧊 Never put hot food directly into the fridge — let it cool to room temperature first.",
        "☀️ Dry clothes in sunlight instead of a dryer whenever weather permits.",
        "🔋 Unplug phone chargers after the phone is fully charged — idle chargers draw power.",
        "💧 Use a microwave instead of an oven when possible — it uses ~3× less energy.",
        "🚿 Replace your electric geyser with a solar water heater — payback in 2-3 years.",
        "📺 Reduce TV screen brightness by 30% — saves ~40% of the TV's power consumption.",
        "🌿 Plant trees/shrubs on the west side of your home to reduce AC load by 10-15%.",
    ]


# ═══════════════════════════════════════════════════════════
# SHARED PLOTLY LAYOUT DEFAULTS
# ═══════════════════════════════════════════════════════════
BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(8,11,26,0.85)",
    font=dict(family="Exo 2, sans-serif", color="#c8d8ff"),
    title_font=dict(family="Orbitron, monospace", size=14, color="#00C9FF"),
    margin=dict(t=52, b=44, l=44, r=20),
)
GRID = dict(gridcolor="rgba(0,201,255,0.07)", linecolor="rgba(0,201,255,0.15)")


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ ENERGY TRACKER")
    st.markdown("---")
    data_source = st.radio(
        "📥 Data Source",
        ["🔬 Sample Data", "📝 Manual Entry", "📂 Upload Excel/CSV"],
        index=0
    )
    st.markdown("---")
    entry_mode  = st.selectbox("📅 Aggregation Mode", ["Daily", "Weekly", "Monthly"])
    rate        = st.number_input("💰 Tariff Rate (₹/kWh)", 1.0, 30.0, RATE_PER_UNIT, 0.5)
    threshold_p = st.slider("⚠️ Spike Alert (% above avg)", 30, 200, 70, 5)
    THRESHOLD_MULT = 1 + threshold_p / 100
    st.markdown("---")
    st.caption("v2.0 · Streamlit + Plotly")
    st.caption(f"Tariff: ₹{rate}/kWh")


# ═══════════════════════════════════════════════════════════
# DATA COLLECTION
# ═══════════════════════════════════════════════════════════
df_raw = None

if data_source == "🔬 Sample Data":
    df_raw = generate_sample_data()
    st.markdown("""<div class='hero-banner'>
        <p class='hero-title'>⚡ Smart Energy Tracker</p>
        <p class='hero-sub'>180-day simulation · Appliance-level intelligence · Real-time analytics</p>
    </div>""", unsafe_allow_html=True)
    st.markdown(
        "<div class='alert-ok'>🔬 Showing a realistic 180-day simulation with seasonal patterns, "
        "weekend spikes, and deliberate anomalies. Switch to Manual Entry or Upload for real data.</div>",
        unsafe_allow_html=True
    )

elif data_source == "📝 Manual Entry":
    st.markdown("""<div class='hero-banner'>
        <p class='hero-title'>⚡ Smart Energy Tracker</p>
        <p class='hero-sub'>Enter appliance consumption manually</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<p class='section-title'>📝 New Entry</p>", unsafe_allow_html=True)

    if entry_mode == "Daily":
        sel_date  = st.date_input("Date", value=datetime.today())
        n_periods = 1
    elif entry_mode == "Weekly":
        sel_date  = st.date_input("Week Starting", value=datetime.today() - timedelta(days=6))
        n_periods = 7
    else:
        month_sel = st.selectbox(
            "Month",
            [datetime.today().replace(day=1) - timedelta(days=30*i) for i in range(12)],
            format_func=lambda d: d.strftime("%B %Y")
        )
        n_periods = (month_sel.replace(month=month_sel.month % 12 + 1, day=1) - timedelta(days=1)).day

    input_method = st.radio("Input method", ["Units (kWh)", "Hours used per day"], horizontal=True)
    cols_in = st.columns(3)
    appl_data = {}
    for i, app in enumerate(APPLIANCES):
        with cols_in[i % 3]:
            icon = APPLIANCE_ICONS[app]
            if input_method == "Units (kWh)":
                v = st.number_input(f"{icon} {app} (kWh)", 0.0, 100.0, 0.0, 0.1, key=f"u_{app}")
                appl_data[app] = v
            else:
                h = st.number_input(f"{icon} {app} (hrs/day)", 0.0, 24.0, 0.0, 0.5, key=f"h_{app}")
                appl_data[app] = round(h * WATTAGE[app] * n_periods, 3)

    if st.button("➕ Add Entry", type="primary"):
        if entry_mode == "Daily":
            dates_list = [pd.Timestamp(sel_date)]
            per_day    = {a: appl_data[a] for a in APPLIANCES}
        elif entry_mode == "Weekly":
            dates_list = [pd.Timestamp(sel_date) + timedelta(days=i) for i in range(7)]
            per_day    = {a: round(appl_data[a] / 7, 3) for a in APPLIANCES}
        else:
            dates_list = [pd.Timestamp(month_sel.replace(day=d+1)) for d in range(n_periods)]
            per_day    = {a: round(appl_data[a] / n_periods, 3) for a in APPLIANCES}
        rows_new = []
        for d in dates_list:
            r = {"Date": d}; r.update(per_day)
            r["Total Units"] = round(sum(per_day.values()), 3)
            rows_new.append(r)
        new_df = pd.DataFrame(rows_new)
        if "manual_df" in st.session_state and st.session_state.manual_df is not None:
            st.session_state.manual_df = (
                pd.concat([st.session_state.manual_df, new_df], ignore_index=True)
                .drop_duplicates("Date").sort_values("Date")
            )
        else:
            st.session_state.manual_df = new_df
        st.success(f"✅ Added {len(rows_new)} day(s).")

    if "manual_df" in st.session_state and st.session_state.manual_df is not None:
        df_raw = st.session_state.manual_df.copy()
        st.caption(f"📦 {len(df_raw)} records collected")
        if st.button("🗑️ Clear All"):
            st.session_state.manual_df = None
            st.rerun()

else:  # Upload
    st.markdown("""<div class='hero-banner'>
        <p class='hero-title'>⚡ Smart Energy Tracker</p>
        <p class='hero-sub'>Upload your Excel or CSV data for instant analysis</p>
    </div>""", unsafe_allow_html=True)
    with st.expander("📋 Required Format"):
        fmt = pd.DataFrame({
            "Date": ["2024-01-01", "2024-01-02"],
            "AC": [4.5, 3.8], "Fan": [1.2, 1.0], "Refrigerator": [1.5, 1.5],
            "Washing Machine": [0.8, 0.0], "Lights": [0.6, 0.7],
            "Others": [0.3, 0.4], "Total Units": [8.9, 7.4]
        })
        st.dataframe(fmt, use_container_width=True)
    uploaded = st.file_uploader("Drop file here", type=["xlsx", "csv"])
    if uploaded:
        with st.spinner("🔄 Validating data…"):
            raw = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
            df_raw = validate_uploaded_df(raw)
            if df_raw is not None:
                st.success(f"✅ {len(df_raw)} records loaded!")


# ═══════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════
if df_raw is not None and len(df_raw) > 0:
    df_raw["Date"] = pd.to_datetime(df_raw["Date"])
    agg = aggregate_df(df_raw, entry_mode)

    total_kwh    = df_raw["Total Units"].sum()
    avg_kwh      = df_raw["Total Units"].mean()
    total_cost   = total_kwh * rate
    daily_avg    = avg_kwh
    proj_monthly = daily_avg * 30 * rate
    top_app      = max(APPLIANCES, key=lambda a: df_raw[a].sum())
    anomalies, spike_thr = detect_anomalies(df_raw, THRESHOLD_MULT)

    # KPI ROW
    st.markdown("<p class='section-title'>📊 Key Metrics</p>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("⚡ Total kWh",      f"{total_kwh:.1f}")
    k2.metric("📅 Avg / Day",      f"{avg_kwh:.2f} kWh")
    k3.metric("💰 Total Cost",     f"₹{total_cost:,.0f}")
    k4.metric("📆 Proj. Monthly",  f"₹{proj_monthly:,.0f}")
    k5.metric("🔥 Top Consumer",   top_app)
    k6.metric("🚨 Spike Days",     str(len(anomalies)),
              delta=f"+{len(anomalies)} alerts" if len(anomalies) else None,
              delta_color="inverse")
    st.markdown("<hr class='kpi-divider'>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Trends", "🏠 Appliances", "🗓️ Patterns",
        "💡 Insights", "⚠️ Alerts & Tips", "📋 Data & Export"
    ])

    # ═══ TAB 1 — TRENDS ═══════════════════════════════════
    with tab1:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=agg["Date"], y=agg["Total Units"],
            mode="lines+markers",
            line=dict(color="#00C9FF", width=2.5, shape="spline"),
            marker=dict(size=5, color="#00C9FF"),
            fill="tozeroy", fillcolor="rgba(0,201,255,0.07)",
            name="Total kWh"
        ))
        if len(agg) >= 7:
            roll = agg["Total Units"].rolling(7, min_periods=1).mean()
            fig_line.add_trace(go.Scatter(
                x=agg["Date"], y=roll, mode="lines",
                line=dict(color="#F7971E", width=2, dash="dot"),
                name="7-period rolling avg"
            ))
        agg_spikes = agg[agg["Total Units"] > spike_thr]
        if len(agg_spikes):
            fig_line.add_trace(go.Scatter(
                x=agg_spikes["Date"], y=agg_spikes["Total Units"], mode="markers",
                marker=dict(color="#FC5C7D", size=13, symbol="star",
                            line=dict(color="#fff", width=1)),
                name="⚠️ Spike"
            ))
        fig_line.add_hline(y=avg_kwh, line_dash="dash",
                           line_color="rgba(146,254,157,0.6)",
                           annotation_text=f"  Avg {avg_kwh:.2f} kWh",
                           annotation_font_color="#92FE9D")
        fig_line.update_layout(
            title=f"⚡ {entry_mode} Energy Trend (kWh)",
            height=410,
            legend=dict(orientation="h", y=-0.18, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(title="Date", **GRID),
            yaxis=dict(title="kWh", **GRID),
            **BASE_LAYOUT
        )
        st.plotly_chart(fig_line, use_container_width=True)

        col_area, col_cum = st.columns(2)

        with col_area:
            # ★ BUG FIX: fillcolor uses pre-built rgba() strings from COLORS_RGBA dict
            fig_stack = go.Figure()
            for app in APPLIANCES:
                fig_stack.add_trace(go.Scatter(
                    x=agg["Date"], y=agg[app],
                    name=f"{APPLIANCE_ICONS[app]} {app}",
                    stackgroup="one",
                    line=dict(color=COLORS_HEX[app], width=0.8),
                    fillcolor=COLORS_RGBA[app],          # ← CORRECT rgba string
                ))
            fig_stack.update_layout(
                title="🏠 Stacked Appliance Area",
                height=370,
                legend=dict(orientation="h", y=-0.25, bgcolor="rgba(0,0,0,0)", font_size=10),
                xaxis=dict(**GRID), yaxis=dict(title="kWh", **GRID),
                **BASE_LAYOUT
            )
            st.plotly_chart(fig_stack, use_container_width=True)

        with col_cum:
            cumulative = agg["Total Units"].cumsum()
            proj_x = [agg["Date"].iloc[-1], agg["Date"].iloc[-1] + timedelta(days=30)]
            proj_y = [cumulative.iloc[-1], cumulative.iloc[-1] + daily_avg * 30]
            fig_cum = go.Figure()
            fig_cum.add_trace(go.Scatter(
                x=agg["Date"], y=cumulative,
                fill="tozeroy", fillcolor="rgba(168,85,247,0.12)",
                line=dict(color="#A855F7", width=2.5),
                name="Cumulative kWh"
            ))
            fig_cum.add_trace(go.Scatter(
                x=proj_x, y=proj_y,
                line=dict(color="#F7971E", width=2, dash="dot"),
                name="30-day projection"
            ))
            fig_cum.update_layout(
                title="📈 Cumulative Usage + Projection",
                height=370,
                legend=dict(orientation="h", y=-0.18, bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(**GRID), yaxis=dict(title="kWh", **GRID),
                **BASE_LAYOUT
            )
            st.plotly_chart(fig_cum, use_container_width=True)

    # ═══ TAB 2 — APPLIANCES ═══════════════════════════════
    with tab2:
        app_totals = {a: round(df_raw[a].sum(), 2) for a in APPLIANCES}
        app_df = (
            pd.DataFrame({"Appliance": list(app_totals.keys()),
                          "kWh": list(app_totals.values())})
            .sort_values("kWh", ascending=False).reset_index(drop=True)
        )
        app_df["Cost (₹)"]  = (app_df["kWh"] * rate).round(0)
        app_df["Share (%)"] = (app_df["kWh"] / app_df["kWh"].sum() * 100).round(1)
        app_df["Avg/Day"]   = (app_df["kWh"] / max(len(df_raw), 1)).round(3)

        c_bar, c_pie = st.columns(2)
        with c_bar:
            fig_bar = go.Figure(go.Bar(
                x=app_df["Appliance"], y=app_df["kWh"],
                marker=dict(color=[COLORS_HEX[a] for a in app_df["Appliance"]], opacity=0.9),
                text=app_df.apply(lambda r: f"{r['kWh']:.1f} kWh<br>₹{r['Cost (₹)']:,.0f}", axis=1),
                textposition="outside", textfont=dict(size=10),
            ))
            fig_bar.update_layout(
                title="🔋 Total Consumption by Appliance", height=400,
                showlegend=False,
                xaxis=dict(**GRID), yaxis=dict(title="kWh", **GRID),
                **BASE_LAYOUT
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_pie:
            fig_pie = go.Figure(go.Pie(
                labels=[f"{APPLIANCE_ICONS[a]} {a}" for a in app_df["Appliance"]],
                values=app_df["kWh"], hole=0.5,
                marker=dict(colors=[COLORS_HEX[a] for a in app_df["Appliance"]],
                            line=dict(color="#080b1a", width=2)),
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>%{value:.1f} kWh<br>%{percent}<extra></extra>",
            ))
            fig_pie.update_layout(
                title="🍕 Energy Share (%)", height=400,
                showlegend=False, **BASE_LAYOUT
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<p class='section-title'>💰 Appliance Cost Breakdown</p>", unsafe_allow_html=True)
        tbl = app_df.copy()
        tbl.insert(0, "Icon", [APPLIANCE_ICONS[a] for a in tbl["Appliance"]])
        tbl["kWh"]       = tbl["kWh"].apply(lambda x: f"{x:.2f}")
        tbl["Cost (₹)"]  = tbl["Cost (₹)"].apply(lambda x: f"₹{x:,.0f}")
        tbl["Share (%)"] = tbl["Share (%)"].apply(lambda x: f"{x:.1f}%")
        tbl["Avg/Day"]   = tbl["Avg/Day"].apply(lambda x: f"{x:.3f} kWh")
        st.dataframe(tbl, use_container_width=True, hide_index=True)

        avg_day_df = pd.DataFrame({
            "Appliance": APPLIANCES,
            "Avg kWh/day": [round(df_raw[a].mean(), 3) for a in APPLIANCES]
        }).sort_values("Avg kWh/day")
        fig_horiz = go.Figure(go.Bar(
            x=avg_day_df["Avg kWh/day"], y=avg_day_df["Appliance"], orientation="h",
            marker_color=[COLORS_HEX[a] for a in avg_day_df["Appliance"]],
            text=avg_day_df["Avg kWh/day"].apply(lambda x: f"{x:.3f}"),
            textposition="outside",
        ))
        fig_horiz.update_layout(
            title="📊 Average Daily Consumption per Appliance", height=330,
            showlegend=False,
            xaxis=dict(title="kWh/day", **GRID), yaxis=dict(**GRID),
            **BASE_LAYOUT
        )
        st.plotly_chart(fig_horiz, use_container_width=True)

    # ═══ TAB 3 — PATTERNS ══════════════════════════════════
    with tab3:
        df2 = df_raw.copy()
        df2["Weekday"] = df2["Date"].dt.day_name()
        df2["DayType"] = df2["Date"].dt.dayofweek.apply(lambda x: "Weekend" if x >= 5 else "Weekday")
        df2["Week"]    = df2["Date"].dt.isocalendar().week.astype(str)
        df2["Month"]   = df2["Date"].dt.strftime("%b %Y")
        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        c1, c2 = st.columns(2)
        with c1:
            wkd_avg = df2.groupby("Weekday")["Total Units"].mean().reindex(order).reset_index()
            wkd_avg.columns = ["Weekday", "Avg kWh"]
            fig_wkd = px.bar(wkd_avg, x="Weekday", y="Avg kWh",
                             color="Avg kWh", color_continuous_scale="Turbo",
                             title="📅 Avg Usage by Day of Week", text_auto=".2f")
            fig_wkd.update_layout(height=360, coloraxis_showscale=False,
                                  xaxis=dict(**GRID), yaxis=dict(**GRID), **BASE_LAYOUT)
            st.plotly_chart(fig_wkd, use_container_width=True)
        with c2:
            dt_avg = df2.groupby("DayType")["Total Units"].mean().reset_index()
            fig_dt = px.bar(dt_avg, x="DayType", y="Total Units", color="DayType",
                            color_discrete_map={"Weekday":"#00C9FF","Weekend":"#FC5C7D"},
                            title="🏠 Weekday vs Weekend", text_auto=".2f")
            fig_dt.update_layout(height=360, showlegend=False,
                                 xaxis=dict(**GRID), yaxis=dict(**GRID), **BASE_LAYOUT)
            st.plotly_chart(fig_dt, use_container_width=True)

        if len(df_raw) >= 14:
            pivot = df2.pivot_table(index="Weekday", columns="Week",
                                    values="Total Units", aggfunc="mean")
            pivot = pivot.reindex(order)
            fig_heat = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[f"W{c}" for c in pivot.columns],
                y=pivot.index.tolist(),
                colorscale="Plasma",
                colorbar=dict(title="kWh", tickfont=dict(color="#c8d8ff")),
                hovertemplate="Day: %{y}<br>Week: %{x}<br>%.2f kWh<extra></extra>",
            ))
            fig_heat.update_layout(
                title="🌡️ Energy Heatmap — Day × Week", height=390,
                xaxis=dict(title="Week", tickfont=dict(size=9), **GRID),
                yaxis=dict(title="Day", **GRID),
                **BASE_LAYOUT
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        if df2["Month"].nunique() > 1:
            monthly = df2.groupby("Month")[APPLIANCES].sum().reset_index()
            monthly_melt = monthly.melt("Month", var_name="Appliance", value_name="kWh")
            fig_monthly = px.bar(monthly_melt, x="Month", y="kWh", color="Appliance",
                                 color_discrete_map=COLORS_HEX, barmode="group",
                                 title="📅 Monthly Comparison by Appliance")
            fig_monthly.update_layout(
                height=400, legend=dict(orientation="h", y=-0.22, bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(**GRID), yaxis=dict(title="kWh", **GRID), **BASE_LAYOUT
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

        melt_box = df_raw[APPLIANCES + ["Date"]].melt("Date", var_name="Appliance", value_name="kWh")
        fig_box = px.box(melt_box, x="Appliance", y="kWh", color="Appliance",
                         color_discrete_map=COLORS_HEX,
                         title="📦 Consumption Distribution per Appliance", points="outliers")
        fig_box.update_layout(height=390, showlegend=False,
                              xaxis=dict(**GRID), yaxis=dict(title="kWh", **GRID), **BASE_LAYOUT)
        st.plotly_chart(fig_box, use_container_width=True)

    # ═══ TAB 4 — INSIGHTS ══════════════════════════════════
    with tab4:
        insights = generate_insights(df_raw, agg, rate)
        st.markdown("<p class='section-title'>💡 Smart Insights</p>", unsafe_allow_html=True)
        for ins in insights:
            st.markdown(f"<div class='insight-card'>{ins}</div>", unsafe_allow_html=True)

        st.markdown("<p class='section-title'>📆 Cost Projections</p>", unsafe_allow_html=True)
        periods    = ["1 Month",  "3 Months", "6 Months", "1 Year"]
        mults      = [30,         90,          180,         365]
        proj_costs = [daily_avg * m * rate for m in mults]
        proj_kwhs  = [daily_avg * m         for m in mults]
        pc1,pc2,pc3,pc4 = st.columns(4)
        for col, period, cost, kwh in zip([pc1,pc2,pc3,pc4], periods, proj_costs, proj_kwhs):
            col.metric(f"📅 {period}", f"₹{cost:,.0f}", f"{kwh:.0f} kWh")

        fig_proj = go.Figure(go.Bar(
            x=periods, y=proj_costs,
            marker_color=["#00C9FF","#92FE9D","#F7971E","#FC5C7D"],
            text=[f"₹{c:,.0f}" for c in proj_costs], textposition="outside",
        ))
        fig_proj.update_layout(
            title="💰 Projected Energy Cost", height=340,
            showlegend=False,
            xaxis=dict(**GRID), yaxis=dict(title="₹", **GRID), **BASE_LAYOUT
        )
        st.plotly_chart(fig_proj, use_container_width=True)

        st.markdown("<p class='section-title'>💸 Potential Monthly Savings</p>", unsafe_allow_html=True)
        s1,s2,s3 = st.columns(3)
        s1.metric("❄️ AC: set 24°C + timer",  f"₹{df_raw['AC'].sum()*0.15*rate/max(len(df_raw)/30,1):,.0f}/mo",  "15% reduction")
        s2.metric("💡 Full LED conversion",    f"₹{df_raw['Lights'].sum()*0.75*rate/max(len(df_raw)/30,1):,.0f}/mo", "75% lighting save")
        s3.metric("🔌 Kill standby power",     f"₹{df_raw['Others'].sum()*0.10*rate/max(len(df_raw)/30,1):,.0f}/mo", "10% Others save")

    # ═══ TAB 5 — ALERTS & TIPS ═════════════════════════════
    with tab5:
        warnings_list = generate_warnings(df_raw, anomalies, spike_thr, rate)
        recs          = generate_recommendations(df_raw)
        tips          = quick_save_tips()

        st.markdown("<p class='section-title'>🚨 Alerts & Warnings</p>", unsafe_allow_html=True)
        if not warnings_list:
            st.markdown(
                "<div class='alert-ok'>✅ No alerts detected — your consumption looks healthy!</div>",
                unsafe_allow_html=True)
        else:
            for w in warnings_list:
                css = "alert-danger" if w["level"] == "danger" else "alert-warning-card"
                st.markdown(f"<div class='{css}'>{w['msg']}</div>", unsafe_allow_html=True)

        if len(anomalies) > 0:
            fig_spike = go.Figure(go.Bar(
                x=df_raw["Date"], y=df_raw["Total Units"],
                marker_color=[
                    "#FC5C7D" if v > spike_thr else "#00C9FF"
                    for v in df_raw["Total Units"]
                ],
                hovertemplate="Date: %{x}<br>kWh: %{y:.2f}<extra></extra>",
            ))
            fig_spike.add_hline(y=spike_thr, line_color="#F7971E", line_dash="dash",
                                annotation_text=f"  Threshold ({spike_thr:.1f} kWh)",
                                annotation_font_color="#F7971E")
            fig_spike.update_layout(
                title="🚨 Daily Usage — Spikes in Red", height=360,
                showlegend=False,
                xaxis=dict(title="Date", **GRID), yaxis=dict(title="kWh", **GRID),
                **BASE_LAYOUT
            )
            st.plotly_chart(fig_spike, use_container_width=True)

        st.markdown("<p class='section-title'>🌱 Personalised Recommendations</p>", unsafe_allow_html=True)
        for rec in recs:
            st.markdown(f"<div class='rec-card'>{rec}</div>", unsafe_allow_html=True)

        st.markdown("<p class='section-title'>⚡ Quick-Win Tips</p>", unsafe_allow_html=True)
        tip_cols = st.columns(2)
        for i, tip in enumerate(tips):
            with tip_cols[i % 2]:
                st.markdown(f"<div class='tip-card'>{tip}</div>", unsafe_allow_html=True)

        st.markdown("<p class='section-title'>🌍 Environmental Impact</p>", unsafe_allow_html=True)
        co2_kg = total_kwh * 0.82
        trees  = co2_kg / 21.77
        ei1, ei2, ei3 = st.columns(3)
        ei1.metric("🌿 CO₂ Emitted",      f"{co2_kg:.0f} kg",    f"{co2_kg/1000:.2f} tonnes")
        ei2.metric("🌳 Trees to Offset",   f"{trees:.0f} trees",  "to neutralise impact")
        ei3.metric("☀️ 30% Solar Target",  f"{total_kwh*0.3:.0f} kWh", "from renewable sources")

    # ═══ TAB 6 — DATA & EXPORT ═════════════════════════════
    with tab6:
        st.markdown("<p class='section-title'>📋 Raw Dataset</p>", unsafe_allow_html=True)
        disp_df = df_raw.copy()
        disp_df["Date"]     = disp_df["Date"].dt.strftime("%Y-%m-%d")
        disp_df["Cost (₹)"] = (disp_df["Total Units"] * rate).round(2)
        disp_df["CO₂ (kg)"] = (disp_df["Total Units"] * 0.82).round(3)
        st.dataframe(disp_df, use_container_width=True, height=420)

        st.markdown("<p class='section-title'>📊 Summary Statistics</p>", unsafe_allow_html=True)
        stats = df_raw[APPLIANCES + ["Total Units"]].describe().round(3)
        st.dataframe(stats, use_container_width=True)

        st.markdown("<p class='section-title'>⬇️ Export</p>", unsafe_allow_html=True)
        dl1, dl2 = st.columns(2)
        with dl1:
            csv_b = disp_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv_b,
                               file_name="energy_data.csv", mime="text/csv", type="primary")
        with dl2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                disp_df.to_excel(w, sheet_name="Raw Data", index=False)
                agg.to_excel(w, sheet_name=f"{entry_mode} Aggregated", index=False)
                stats.to_excel(w, sheet_name="Summary Stats")
            st.download_button(
                "⬇️ Download Excel Report", buf.getvalue(),
                file_name="energy_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

# ═══════════════════════════════════════════════════════════
# LANDING (no data yet)
# ═══════════════════════════════════════════════════════════
else:
    st.markdown("""<div class='hero-banner'>
        <p class='hero-title'>⚡ Smart Energy Tracker</p>
        <p class='hero-sub'>Select a data source from the sidebar to begin →</p>
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.info("🔬 **Sample Data**\nInstant 180-day simulation with seasonal patterns & anomalies.")
    c2.info("📝 **Manual Entry**\nLog appliance readings daily, weekly, or monthly.")
    c3.info("📂 **Upload Excel/CSV**\nUpload structured data for instant analysis.")
