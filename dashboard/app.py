"""
SecureCommerce AI — Streamlit Dashboard
Run from the project root:  streamlit run dashboard/dashboard.py
"""

import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SecureCommerce AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# THEME — dark security aesthetic, single accent colour
# ─────────────────────────────────────────────────────────────
ACCENT   = "#00C2FF"   # electric blue — the one signature element
RED      = "#FF4B4B"
AMBER    = "#FFB347"
GREEN    = "#00E676"
BG_CARD  = "#0F1923"
BG_PAGE  = "#060D14"
TEXT_DIM = "#7A8FA6"

st.markdown(f"""
<style>
/* ── page background ── */
.stApp {{ background-color: {BG_PAGE}; }}

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {BG_CARD};
    border-right: 1px solid #1A2940;
}}
section[data-testid="stSidebar"] * {{ color: #C8D8E8 !important; }}

/* ── metric cards ── */
div[data-testid="metric-container"] {{
    background: {BG_CARD};
    border: 1px solid #1A2940;
    border-radius: 8px;
    padding: 16px 20px;
}}
div[data-testid="metric-container"] label {{
    color: {TEXT_DIM} !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
    color: #E8F4FF !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}}

/* ── section headers ── */
.section-header {{
    color: {ACCENT};
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-bottom: 1px solid #1A2940;
    padding-bottom: 6px;
    margin-bottom: 14px;
    margin-top: 28px;
}}

/* ── alert rows ── */
.alert-high   {{ border-left: 3px solid {RED};   background:{BG_CARD}; padding:10px 14px; border-radius:6px; margin-bottom:6px; }}
.alert-medium {{ border-left: 3px solid {AMBER}; background:{BG_CARD}; padding:10px 14px; border-radius:6px; margin-bottom:6px; }}
.alert-low    {{ border-left: 3px solid {GREEN};  background:{BG_CARD}; padding:10px 14px; border-radius:6px; margin-bottom:6px; }}

.alert-text {{ color:#C8D8E8; font-size:0.82rem; }}
.alert-meta {{ color:{TEXT_DIM}; font-size:0.72rem; margin-top:2px; }}

/* ── dataframe ── */
div[data-testid="stDataFrame"] {{ background: {BG_CARD}; border-radius:8px; }}

/* ── top bar ── */
.topbar {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 20px 0;
    border-bottom: 1px solid #1A2940;
    margin-bottom: 24px;
}}
.topbar-title {{
    font-size: 1.3rem;
    font-weight: 700;
    color: #E8F4FF;
    letter-spacing: 0.02em;
}}
.topbar-sub {{
    font-size: 0.75rem;
    color: {TEXT_DIM};
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.badge {{
    background: {ACCENT}18;
    border: 1px solid {ACCENT}55;
    color: {ACCENT};
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
}}
.live-dot {{
    width: 8px; height: 8px;
    background: {GREEN};
    border-radius: 50%;
    display: inline-block;
    animation: pulse 1.5s infinite;
    margin-right: 6px;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; box-shadow: 0 0 0 0 {GREEN}66; }}
    50%      {{ opacity:.7; box-shadow: 0 0 0 5px transparent; }}
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MONGODB CONNECTION
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    uri = (
        f"mongodb://"
        f"{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
        f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@"
        f"{os.getenv('MONGO_HOST', 'localhost')}:"
        f"{os.getenv('MONGO_PORT', '27017')}/"
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    return client[os.getenv("MONGO_DATABASE", "securecommerce_ai")]

# ─────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────
def load_events(db, limit: int = 10000) -> pd.DataFrame:
    """
    Fetch the most recent `limit` documents from MongoDB, sorted by
    insertion order. No time-window filter is applied here — callers
    slice by timestamp after loading so the charts always have data
    even when the producer has been idle for a while.
    """
    cursor = db.login_logs.find(
        {},
        {
            "_id": 0,
            "event_id": 1, "timestamp": 1, "user_id": 1,
            "username": 1, "ip_address": 1, "country": 1,
            "city": 1, "latitude": 1, "longitude": 1,
            "attack_type": 1, "failed_attempts": 1,
            "login_status": 1, "device": 1,
            "ml_prediction": 1, "alert": 1,
        },
    ).sort("_id", -1).limit(limit)

    df = pd.DataFrame(list(cursor))
    if df.empty:
        return df

    # Parse timestamps robustly — handles ISO strings with or without tz suffix
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Unpack nested dicts from consumer enrichment
    df["is_anomaly"] = df["ml_prediction"].apply(
        lambda x: x.get("is_anomaly", False) if isinstance(x, dict) else False
    )
    df["risk_level"] = df["alert"].apply(
        lambda x: x.get("risk_level", "LOW") if isinstance(x, dict) else "LOW"
    )
    df["anomaly_score"] = df["ml_prediction"].apply(
        lambda x: x.get("anomaly_score", 0.0) if isinstance(x, dict) else 0.0
    )
    return df


def filter_by_window(df: pd.DataFrame, hours: int) -> pd.DataFrame:
    """
    Return rows within the last `hours` hours.
    If that yields an empty frame, fall back to the most recent 2000 rows
    and show a banner so the user knows they're seeing historical data.
    """
    if df.empty:
        return df
    since = pd.Timestamp.utcnow() - pd.Timedelta(hours=hours)
    windowed = df[df["timestamp"] >= since]
    return windowed


def load_totals(db) -> dict:
    total   = db.login_logs.count_documents({})
    attacks = db.login_logs.count_documents({"attack_type": {"$ne": "NORMAL"}})
    anomaly = db.login_logs.count_documents({"ml_prediction.is_anomaly": True})
    high    = db.login_logs.count_documents({"alert.risk_level": "HIGH"})
    return dict(total=total, attacks=attacks, anomaly=anomaly, high=high)

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#C8D8E8", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#1A2940", linecolor="#1A2940"),
    yaxis=dict(gridcolor="#1A2940", linecolor="#1A2940"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ SecureCommerce AI")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["📊 Overview", "🚨 Live Alerts", "🗺️ Geo Intelligence", "📈 ML Performance"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<p style="color:#7A8FA6;font-size:0.7rem;text-transform:uppercase;letter-spacing:.1em">Time Window</p>', unsafe_allow_html=True)
    time_window = st.selectbox(
        "Time window",
        [1, 6, 12, 24],
        format_func=lambda x: f"Last {x} hour{'s' if x > 1 else ''}",
        label_visibility="collapsed",
    )

    st.markdown("---")
    auto_refresh = st.toggle("Auto-refresh (30s)", value=True)
    if auto_refresh:
        st.markdown(f'<span class="live-dot"></span><span style="color:#00E676;font-size:.75rem">Live</span>', unsafe_allow_html=True)

    st.markdown("---")
    risk_filter = st.multiselect(
        "Risk level filter",
        ["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"],
    )
    attack_filter = st.multiselect(
        "Attack type filter",
        ["BRUTE_FORCE", "CREDENTIAL_STUFFING", "NORMAL"],
        default=["BRUTE_FORCE", "CREDENTIAL_STUFFING", "NORMAL"],
    )

    st.markdown("---")
    st.markdown(f'<p style="color:{TEXT_DIM};font-size:.65rem">Model: Isolation Forest · 300 trees<br>Features: 7 behavioural signals<br>Precision: 53.8% · Recall: 53.9%</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
try:
    db      = get_db()
    df_all  = load_events(db)          # all recent 10k docs, parsed
    totals  = load_totals(db)
    db_ok   = True
except Exception as e:
    db_ok = False
    st.error(f"MongoDB connection failed: {e}")
    st.stop()

# Apply time-window filter; fall back to most-recent 2000 rows if empty
df = filter_by_window(df_all, hours=time_window)
using_fallback = False
if df.empty and not df_all.empty:
    df = df_all.head(2000)
    using_fallback = True

# Apply sidebar filters (risk + attack type)
if not df.empty:
    df = df[df["risk_level"].isin(risk_filter)]
    df = df[df["attack_type"].isin(attack_filter)]

# ─────────────────────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div>
    <div class="topbar-title">SecureCommerce AI</div>
    <div class="topbar-sub">Fraud &amp; Anomaly Detection · Real-time</div>
  </div>
  <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
    <span class="badge">Isolation Forest</span>
    <span class="badge" style="color:{GREEN};border-color:{GREEN}55;background:{GREEN}18">
      <span class="live-dot"></span>Live
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# AUTO REFRESH
# ─────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(0.1)
    st.markdown(f'<p style="color:{TEXT_DIM};font-size:.68rem;text-align:right">Last updated: {datetime.utcnow().strftime("%H:%M:%S UTC")} · refreshes every 30s</p>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════
if page == "📊 Overview":

    # ── KPI row ─────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Events", f"{totals['total']:,}")
    c2.metric("Attacks Detected", f"{totals['attacks']:,}",
              delta=f"{100*totals['attacks']/max(totals['total'],1):.1f}% rate",
              delta_color="inverse")
    c3.metric("ML Anomalies", f"{totals['anomaly']:,}")
    c4.metric("High Risk Alerts", f"{totals['high']:,}", delta_color="inverse")
    if not df.empty:
        window_rate = len(df[df["is_anomaly"]]) / max(len(df), 1) * 100
        label = f"Anomaly Rate ({time_window}h)" if not using_fallback else "Anomaly Rate (all)"
        c5.metric(label, f"{window_rate:.1f}%")
    else:
        c5.metric("Anomaly Rate", "—")

    # ── Window / fallback banner ─────────────────────────────
    if using_fallback:
        st.info(
            f"ℹ️ No new events in the last **{time_window}h** — showing the "
            f"**{len(df_all.head(2000)):,} most recent events** from the database instead. "
            "Start the producer to stream fresh data, or widen the time window."
        )

    if df.empty:
        st.error("No events found in MongoDB at all. Make sure the producer and consumer are running.")
        st.stop()

    # ── Event volume timeline ────────────────────────────────
    st.markdown('<div class="section-header">Event Volume</div>', unsafe_allow_html=True)

    df_ts = df.copy()
    df_ts["minute"] = df_ts["timestamp"].dt.floor("1min")
    vol = (
        df_ts.groupby(["minute", "is_anomaly"])
        .size()
        .reset_index(name="count")
    )
    vol["type"] = vol["is_anomaly"].map({True: "Anomaly", False: "Normal"})

    fig_vol = px.area(
        vol, x="minute", y="count", color="type",
        color_discrete_map={"Normal": "rgba(0,194,255,0.4)", "Anomaly": RED},
        template="none",
    )
    fig_vol.update_traces(line_width=1.5)
    fig_vol.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=True)
    st.plotly_chart(fig_vol, use_container_width=True)

    # ── Two charts side-by-side ──────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">Attack Distribution</div>', unsafe_allow_html=True)
        atk_counts = df["attack_type"].value_counts().reset_index()
        atk_counts.columns = ["attack_type", "count"]
        color_map = {"NORMAL": ACCENT, "BRUTE_FORCE": RED, "CREDENTIAL_STUFFING": AMBER}
        fig_pie = px.pie(
            atk_counts, names="attack_type", values="count",
            color="attack_type", color_discrete_map=color_map,
            hole=0.55, template="none",
        )
        fig_pie.update_traces(textinfo="percent+label", textfont_size=11,
                              marker=dict(line=dict(color=BG_PAGE, width=2)))
        fig_pie.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Risk Level Breakdown</div>', unsafe_allow_html=True)
        risk_counts = df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["risk_level", "count"]
        risk_color = {"HIGH": RED, "MEDIUM": AMBER, "LOW": GREEN}
        fig_risk = px.bar(
            risk_counts, x="risk_level", y="count",
            color="risk_level", color_discrete_map=risk_color,
            template="none", text="count",
        )
        fig_risk.update_traces(textposition="outside", marker_line_width=0)
        fig_risk.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=False,
                               xaxis_title="", yaxis_title="Events")
        st.plotly_chart(fig_risk, use_container_width=True)

    # ── Top targeted users / top countries ──────────────────
    col_u, col_c = st.columns(2)

    with col_u:
        st.markdown('<div class="section-header">Most Targeted Users</div>', unsafe_allow_html=True)
        attacks_only = df[df["attack_type"] != "NORMAL"]
        if not attacks_only.empty:
            top_users = (
                attacks_only.groupby("username")
                .size()
                .sort_values(ascending=True)
                .tail(8)
                .reset_index(name="attacks")
            )
            fig_users = px.bar(
                top_users, x="attacks", y="username",
                orientation="h", template="none",
                color_discrete_sequence=[RED],
            )
            fig_users.update_layout(**PLOTLY_LAYOUT, height=260,
                                    xaxis_title="Attacks", yaxis_title="")
            st.plotly_chart(fig_users, use_container_width=True)
        else:
            st.caption("No attacks in this window.")

    with col_c:
        st.markdown('<div class="section-header">Attack Source Countries</div>', unsafe_allow_html=True)
        attacks_only = df[df["attack_type"] != "NORMAL"]
        if not attacks_only.empty:
            top_countries = (
                attacks_only.groupby("country")
                .size()
                .sort_values(ascending=True)
                .tail(8)
                .reset_index(name="count")
            )
            fig_ctry = px.bar(
                top_countries, x="count", y="country",
                orientation="h", template="none",
                color_discrete_sequence=[AMBER],
            )
            fig_ctry.update_layout(**PLOTLY_LAYOUT, height=260,
                                   xaxis_title="Events", yaxis_title="")
            st.plotly_chart(fig_ctry, use_container_width=True)
        else:
            st.caption("No attacks in this window.")

    # ── Failed attempts heatmap by hour ─────────────────────
    st.markdown('<div class="section-header">Login Failures by Hour</div>', unsafe_allow_html=True)
    df["hour"] = df["timestamp"].dt.hour
    hourly = df.groupby(["hour", "attack_type"])["failed_attempts"].sum().reset_index()
    fig_heat = px.bar(
        hourly, x="hour", y="failed_attempts", color="attack_type",
        color_discrete_map={"NORMAL": "rgba(0,194,255,0.27)", "BRUTE_FORCE": RED, "CREDENTIAL_STUFFING": AMBER},
        template="none", barmode="stack",
    )
    fig_heat.update_layout(**PLOTLY_LAYOUT, height=200,
                           xaxis_title="Hour (UTC)", yaxis_title="Failed Attempts")
    st.plotly_chart(fig_heat, use_container_width=True)


# ═════════════════════════════════════════════════════════════
# PAGE 2 — LIVE ALERTS
# ═════════════════════════════════════════════════════════════
elif page == "🚨 Live Alerts":

    st.markdown('<div class="section-header">Active Alerts</div>', unsafe_allow_html=True)

    if using_fallback:
        st.info(f"ℹ️ Showing most recent {len(df_all.head(2000)):,} events (no new data in last {time_window}h).")

    if df.empty:
        st.error("No events in MongoDB. Start the producer and consumer.")
        st.stop()

    alerts = df[df["is_anomaly"]].sort_values("timestamp", ascending=False).head(100)

    if alerts.empty:
        st.success("No anomalies detected in the selected window.")
    else:
        for _, row in alerts.iterrows():
            risk  = row.get("risk_level", "LOW")
            cls   = f"alert-{risk.lower()}"
            icon  = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(risk, "⚪")
            score = row.get("anomaly_score", 0.0)
            ts    = row["timestamp"].strftime("%H:%M:%S UTC")
            st.markdown(f"""
<div class="{cls}">
  <div class="alert-text">{icon} <strong>{row['attack_type']}</strong> — {row.get('username','?')} &nbsp;·&nbsp; {row.get('ip_address','?')} &nbsp;·&nbsp; {row.get('country','?')}</div>
  <div class="alert-meta">Risk: {risk} &nbsp;|&nbsp; Failed Attempts: {int(row.get('failed_attempts',0))} &nbsp;|&nbsp; Anomaly Score: {score:.4f} &nbsp;|&nbsp; {ts}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Full Event Log</div>', unsafe_allow_html=True)

    show_cols = ["timestamp", "username", "ip_address", "country",
                 "attack_type", "risk_level", "failed_attempts",
                 "login_status", "device", "anomaly_score"]
    show_cols = [c for c in show_cols if c in df.columns]
    display_df = df[show_cols].copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.dataframe(
        display_df.head(500),
        use_container_width=True,
        height=400,
        column_config={
            "risk_level": st.column_config.TextColumn("Risk"),
            "anomaly_score": st.column_config.NumberColumn("ML Score", format="%.4f"),
            "failed_attempts": st.column_config.NumberColumn("Failures"),
        }
    )

    st.download_button(
        "⬇ Export to CSV",
        data=df[show_cols].to_csv(index=False),
        file_name=f"securecommerce_alerts_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


# ═════════════════════════════════════════════════════════════
# PAGE 3 — GEO INTELLIGENCE
# ═════════════════════════════════════════════════════════════
elif page == "🗺️ Geo Intelligence":

    st.markdown('<div class="section-header">Global Attack Map</div>', unsafe_allow_html=True)

    if using_fallback:
        st.info(f"ℹ️ Showing most recent {len(df_all.head(2000)):,} events (no new data in last {time_window}h).")

    if df.empty:
        st.error("No events in MongoDB. Start the producer and consumer.")
        st.stop()

    geo = df.dropna(subset=["latitude", "longitude"]).copy()
    geo["latitude"]  = pd.to_numeric(geo["latitude"],  errors="coerce")
    geo["longitude"] = pd.to_numeric(geo["longitude"], errors="coerce")
    geo = geo.dropna(subset=["latitude", "longitude"])

    attacks_geo = geo[geo["attack_type"] != "NORMAL"]
    normal_geo  = geo[geo["attack_type"] == "NORMAL"]

    fig_map = go.Figure()

    if not normal_geo.empty:
        fig_map.add_trace(go.Scattergeo(
            lat=normal_geo["latitude"], lon=normal_geo["longitude"],
            mode="markers",
            marker=dict(size=4, color=ACCENT, opacity=0.3),
            name="Normal",
            hovertemplate="<b>Normal Login</b><br>%{customdata[0]}, %{customdata[1]}<extra></extra>",
            customdata=normal_geo[["city", "country"]].values,
        ))

    if not attacks_geo.empty:
        color_col = attacks_geo["attack_type"].map(
            {"BRUTE_FORCE": RED, "CREDENTIAL_STUFFING": AMBER}
        ).fillna(RED)
        fig_map.add_trace(go.Scattergeo(
            lat=attacks_geo["latitude"], lon=attacks_geo["longitude"],
            mode="markers",
            marker=dict(size=7, color=color_col.tolist(), opacity=0.85,
                        line=dict(width=0.5, color="#000")),
            name="Attack",
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}, %{customdata[2]}<br>"
                "User: %{customdata[3]}<br>"
                "Failures: %{customdata[4]}<extra></extra>"
            ),
            customdata=attacks_geo[["attack_type", "city", "country", "username", "failed_attempts"]].values,
        ))

    fig_map.update_geos(
        showcoastlines=True, coastlinecolor="#1A2940",
        showland=True,       landcolor="#0A1520",
        showocean=True,      oceancolor=BG_PAGE,
        showframe=False,
        projection_type="natural earth",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=0, b=0),
        height=450,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#C8D8E8")),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Country summary table ────────────────────────────────
    st.markdown('<div class="section-header">Country Summary</div>', unsafe_allow_html=True)
    country_stats = (
        df.groupby("country")
        .agg(
            total_events=("event_id", "count"),
            attacks=("attack_type", lambda x: (x != "NORMAL").sum()),
            anomalies=("is_anomaly", "sum"),
            avg_failures=("failed_attempts", "mean"),
        )
        .sort_values("attacks", ascending=False)
        .reset_index()
    )
    country_stats["attack_rate"] = (
        country_stats["attacks"] / country_stats["total_events"] * 100
    ).round(1).astype(str) + "%"
    country_stats["avg_failures"] = country_stats["avg_failures"].round(2)

    st.dataframe(country_stats.head(30), use_container_width=True, height=350)


# ═════════════════════════════════════════════════════════════
# PAGE 4 — ML PERFORMANCE
# ═════════════════════════════════════════════════════════════
elif page == "📈 ML Performance":

    st.markdown('<div class="section-header">Model Metrics</div>', unsafe_allow_html=True)

    # Static metrics from last evaluate run
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precision",  "53.79%", "Target: 50–70%")
    col2.metric("Recall",     "53.91%")
    col3.metric("F1-Score",   "53.85%")
    col4.metric("Accuracy",   "97.22%")

    st.markdown('<div class="section-header">Confusion Matrix (training data)</div>', unsafe_allow_html=True)
    cm_data = [[43554, 634], [631, 738]]
    fig_cm = go.Figure(go.Heatmap(
        z=cm_data,
        x=["Pred: Normal", "Pred: Attack"],
        y=["Actual: Normal", "Actual: Attack"],
        colorscale=[[0, BG_CARD], [1, ACCENT]],
        text=[[f"{v:,}" for v in row] for row in cm_data],
        texttemplate="%{text}",
        textfont=dict(size=18, color="#E8F4FF"),
        showscale=False,
    ))
    fig_cm.update_layout(**PLOTLY_LAYOUT, height=280, width=420)
    col_cm, col_info = st.columns([1, 1])
    with col_cm:
        st.plotly_chart(fig_cm, use_container_width=True)
    with col_info:
        st.markdown(f"""
<div style="color:#C8D8E8;font-size:.83rem;line-height:1.8;padding-top:20px">
<b style="color:{ACCENT}">Model:</b> Isolation Forest<br>
<b style="color:{ACCENT}">Estimators:</b> 300 trees<br>
<b style="color:{ACCENT}">Contamination:</b> 0.0301 (auto-derived)<br>
<b style="color:{ACCENT}">Training samples:</b> 45,557<br>
<b style="color:{ACCENT}">True attack rate:</b> 3.005%<br>
<b style="color:{ACCENT}">Features:</b> 7 behavioural signals<br>
<br>
<span style="color:{TEXT_DIM};font-size:.75rem">
failed_attempts · login_attempt_rate<br>
unique_ip_count · device_switch_rate<br>
country_switch_rate · travel_speed_kmh<br>
response_time_ms
</span>
</div>
""", unsafe_allow_html=True)

    # ── Live anomaly score distribution ─────────────────────
    if not df.empty:
        st.markdown('<div class="section-header">Live Anomaly Score Distribution</div>', unsafe_allow_html=True)
        scored = df[df["anomaly_score"] != 0.0]
        if not scored.empty:
            fig_hist = px.histogram(
                scored, x="anomaly_score", color="is_anomaly",
                nbins=60, template="none",
                color_discrete_map={True: RED, False: "rgba(0,194,255,0.53)"},
                barmode="overlay",
                labels={"anomaly_score": "Anomaly Score", "is_anomaly": "Flagged"},
            )
            fig_hist.update_traces(opacity=0.75)
            fig_hist.update_layout(**PLOTLY_LAYOUT, height=250)
            st.plotly_chart(fig_hist, use_container_width=True)

        # ── Feature value comparison: normal vs anomaly ──────
        st.markdown('<div class="section-header">Feature Comparison: Normal vs Flagged</div>', unsafe_allow_html=True)
        if "failed_attempts" in df.columns:
            compare_cols = ["failed_attempts", "anomaly_score"]
            compare_cols = [c for c in compare_cols if c in df.columns]
            for col in compare_cols:
                fig_box = px.box(
                    df, x="is_anomaly", y=col, color="is_anomaly",
                    color_discrete_map={True: RED, False: ACCENT},
                    template="none",
                    labels={"is_anomaly": "Anomaly", col: col.replace("_", " ").title()},
                )
                fig_box.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# AUTO REFRESH TRIGGER
# ─────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(30)
    st.rerun()