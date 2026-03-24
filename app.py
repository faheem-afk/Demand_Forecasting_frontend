import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Demand Forecasting Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
[data-testid="stHeader"]         { display: none !important; }
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"]     { display: none !important; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1200px !important; }
section[data-testid="stMain"]    { background: #F8F7F4; }
h1,h2,h3 { font-family:'DM Serif Display',serif !important; font-weight:400 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ── header ── */
.dash-eyebrow { font-size:11px;font-weight:500;letter-spacing:1.4px;text-transform:uppercase;color:#C97B2A;margin-bottom:8px;font-family:'DM Sans',sans-serif; }
.dash-title { font-family:'DM Serif Display',serif;font-size:38px;font-weight:400;color:#1C1917;line-height:1.15;margin-bottom:6px; }
.dash-sub { font-size:14px;font-weight:300;color:#78716C;line-height:1.7;margin-bottom:0;font-family:'DM Sans',sans-serif; }

/* ── KPI strip ── */
.kpi-strip { display:flex;gap:0;border:1px solid #E7E5E0;border-radius:12px;overflow:hidden;background:#FFF;margin:20px 0 8px; }
.kpi-item { flex:1;padding:20px 18px;border-right:1px solid #E7E5E0;position:relative; }
.kpi-item:last-child { border-right:none; }
.kpi-label { font-size:10px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:#A8A29E;margin-bottom:6px;font-family:'DM Sans',sans-serif; }
.kpi-val { font-family:'DM Serif Display',serif;font-size:30px;color:#1C1917;line-height:1;margin-bottom:4px; }
.kpi-delta-up { font-size:11px;color:#16A34A;font-family:'DM Sans',sans-serif;font-weight:500; }
.kpi-delta-down { font-size:11px;color:#DC2626;font-family:'DM Sans',sans-serif;font-weight:500; }
.kpi-meta { font-size:11px;color:#A8A29E;font-family:'DM Sans',sans-serif;font-weight:300; }

/* ── insight box ── */
.insight { background:#1C1917;border-radius:10px;padding:16px 20px;margin:12px 0 20px;display:flex;gap:12px;align-items:flex-start; }
.insight-dot { width:5px;height:5px;border-radius:50%;background:#F59E0B;flex-shrink:0;margin-top:5px; }
.insight-text { font-size:13px;font-weight:300;color:#D4CFCB;line-height:1.65;font-family:'DM Sans',sans-serif; }
.insight-text strong { color:#fff;font-weight:500; }

/* ── section labels ── */
.sec-tag { font-size:11px;font-weight:500;letter-spacing:1.2px;text-transform:uppercase;color:#C97B2A;margin-bottom:6px;font-family:'DM Sans',sans-serif; }
.sec-title { font-family:'DM Serif Display',serif;font-size:22px;color:#1C1917;margin-bottom:3px; }
.sec-sub { font-size:13px;color:#A8A29E;font-weight:300;font-family:'DM Sans',sans-serif;margin-bottom:14px; }

/* ── tab styling ── */
div[data-testid="stTabs"] button {
    font-family:'DM Sans',sans-serif !important;
    font-size:13px !important;font-weight:500 !important;color:#A8A29E !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color:#1C1917 !important;border-bottom-color:#F59E0B !important;
}

/* ── selectbox labels ── */
div[data-testid="stSelectbox"] label {
    font-size:11px !important;font-weight:500 !important;color:#A8A29E !important;
    text-transform:uppercase !important;letter-spacing:.5px !important;
    font-family:'DM Sans',sans-serif !important;
}

/* ── footer ── */
.dash-footer { background:#1C1917;border-radius:10px;padding:24px 32px;text-align:center;margin-top:40px; }
.dash-footer-title { font-family:'DM Serif Display',serif;font-size:18px;color:#fff;margin-bottom:6px; }
.dash-footer-sub { font-size:12px;color:#78716C;font-family:'DM Sans',sans-serif; }
.dash-footer-sub a { color:#F59E0B;text-decoration:none; }
</style>
""", unsafe_allow_html=True)

# ── data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("df_predictions.csv")
    return df

@st.cache_data
def compute_subsets(df):
    n_future_weeks = df[df["period"] == "Future"].week_number.nunique()
    future_df = df[df["period"] == "Future"]
    prev_weeks = (
        df[df["period"] == "past"]
        .week_number.sort_values().drop_duplicates()
        .iloc[-n_future_weeks:].tolist()
    )
    prev_df = df[df["period"].isin(["past"]) & df["week_number"].isin(prev_weeks)]
    return future_df, prev_df, n_future_weeks

df = load_data()
future_df, prev_df, n_weeks = compute_subsets(df)

# ── KPI helpers ───────────────────────────────────────────────────
def pct_delta(curr, prev):
    if prev == 0: return 0
    return (curr - prev) / prev * 100

total_future  = int(future_df["num_orders"].sum())
total_prev    = int(prev_df["num_orders"].sum())
delta_total   = pct_delta(total_future, total_prev)
n_cities      = future_df["city_name"].nunique()
n_meals       = future_df["meal_name"].nunique()
n_categories  = future_df["meal_category"].nunique()
top_city      = future_df.groupby("city_name")["num_orders"].sum().idxmax()
top_meal      = future_df.groupby("meal_name")["num_orders"].sum().idxmax()
future_weeks  = sorted(future_df.week_number.unique())

# ── plotly theme helper ───────────────────────────────────────────
AMBER    = "#F59E0B"
AMBER2   = "#FCD34D"
DARK     = "#1C1917"
MID      = "#78716C"
LIGHT    = "#E7E5E0"
BG       = "#F8F7F4"
WHITE    = "#FFFFFF"
GREEN    = "#16A34A"
RED      = "#DC2626"
PALETTE  = [AMBER, "#D97706", "#92400E", "#1C1917", "#A8A29E", "#E7E5E0"]

def base_layout(height=400):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=WHITE,
        font_family="DM Sans", font_color=DARK,
        height=height, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor=LIGHT, linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
        yaxis=dict(gridcolor=LIGHT, linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
    )

# ══════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════
st.markdown('<div class="dash-eyebrow">Meal Demand · Forecasting Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-title">Demand forecasting dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<p class="dash-sub">Forecasting {n_weeks} weeks ahead across {n_cities} cities and {n_meals} meals · Weeks {future_weeks[0]}–{future_weeks[-1]}</p>', unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────
delta_sign  = "▲ +" if delta_total >= 0 else "▼ "
delta_class = "kpi-delta-up" if delta_total >= 0 else "kpi-delta-down"

st.markdown(f"""
<div class="kpi-strip">
  <div class="kpi-item">
    <div class="kpi-label">Forecasted orders</div>
    <div class="kpi-val">{total_future:,}</div>
    <div class="{delta_class}">{delta_sign}{abs(delta_total):.1f}% vs prev period</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">Cities covered</div>
    <div class="kpi-val">{n_cities}</div>
    <div class="kpi-meta">Active markets</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">Meals tracked</div>
    <div class="kpi-val">{n_meals}</div>
    <div class="kpi-meta">{n_categories} categories</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">Top city</div>
    <div class="kpi-val" style="font-size:20px;margin-top:4px">{top_city}</div>
    <div class="kpi-meta">Highest forecasted volume</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">Top meal</div>
    <div class="kpi-val" style="font-size:16px;margin-top:8px;line-height:1.2">{top_meal}</div>
    <div class="kpi-meta">Highest forecasted demand</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TABS
# ══════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Weekly trend",
    "City intelligence",
    "Meal performance",
    "Demand heatmap",
    "Forecast detail"
])


# ══════════════════════════════════════════
# TAB 1 — Weekly trend
# ══════════════════════════════════════════
with tab1:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight">
        <div class="insight-dot"></div>
        <div class="insight-text">
            <strong>Reading this chart:</strong> The amber region shows forecasted weeks — 
            the transition from past to future is where the model takes over from actuals. 
            A smooth continuation signals a well-calibrated model; sharp discontinuities 
            indicate a structural shift the model has detected.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-tag">Aggregate trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">Total weekly order demand — all cities & meals</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Past actuals vs forecasted future</div>', unsafe_allow_html=True)

    weekly_total = (
        df.groupby(["week_number", "period"])["num_orders"]
        .sum().reset_index()
    )
    weekly_total["period_label"] = weekly_total["period"].map(
        {"past": "Actuals", "Future": "Forecast"}
    )

    fig = px.line(
        weekly_total, x="week_number", y="num_orders",
        color="period_label",
        color_discrete_map={"Actuals": DARK, "Forecast": AMBER},
        labels={"week_number": "Week", "num_orders": "Orders", "period_label": ""},
        height=380
    )
    fig.update_traces(line_width=2)
    fig.update_layout(
        **base_layout(380),
        legend=dict(orientation="h", y=1.08, x=0, font_size=12,
                    bgcolor="rgba(0,0,0,0)")
    )
    # shade forecast region
    if future_weeks:
        fig.add_vrect(
            x0=future_weeks[0], x1=future_weeks[-1],
            fillcolor=AMBER, opacity=0.06,
            layer="below", line_width=0,
            annotation_text="Forecast period",
            annotation_position="top left",
            annotation_font=dict(size=10, color=AMBER)
        )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-tag">By meal type</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">Forecasted demand split by meal type</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">How demand distributes across meal types in the forecast window</div>', unsafe_allow_html=True)

    type_df = (
        future_df.groupby("meal_type")["num_orders"]
        .sum().reset_index().sort_values("num_orders", ascending=True)
    )
    fig2 = px.bar(
        type_df, x="num_orders", y="meal_type",
        orientation="h",
        color="num_orders",
        color_continuous_scale=[LIGHT, AMBER],
        labels={"num_orders": "Forecasted orders", "meal_type": ""},
        height=280
    )
    fig2.update_layout(
    paper_bgcolor=BG, plot_bgcolor=WHITE,
    font_family="DM Sans", font_color=MID,
    height=280, margin=dict(l=0, r=0, t=10, b=0),
    coloraxis_showscale=False,
    xaxis=dict(gridcolor=LIGHT, linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
    yaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK)
    )
    
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════
# TAB 2 — City intelligence
# ══════════════════════════════════════════
with tab2:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight">
        <div class="insight-dot"></div>
        <div class="insight-text">
            <strong>Key finding:</strong> The top 10 cities account for a disproportionate share 
            of total demand — a pattern consistent with urban food delivery concentration. 
            The trend sparklines reveal which cities are accelerating vs plateauing in the forecast window.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns([1.4, 1])

    with col_l:
        st.markdown('<div class="sec-tag">Volume ranking</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Top 15 cities by forecasted orders</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Total demand across all meals in forecast window</div>', unsafe_allow_html=True)

        top_cities = (
            future_df.groupby("city_name")["num_orders"]
            .sum().reset_index()
            .sort_values("num_orders", ascending=True)
            .tail(15)
        )
        fig = px.bar(
            top_cities, x="num_orders", y="city_name",
            orientation="h",
            color="num_orders",
            color_continuous_scale=[LIGHT, AMBER, "#92400E"],
            labels={"num_orders": "Forecasted orders", "city_name": ""},
            height=460
        )
        fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=WHITE,
        font_family="DM Sans", font_color=MID,
        height=460, margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor=LIGHT, linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK)
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="sec-tag">City comparison</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Week-by-week trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Compare up to 3 cities</div>', unsafe_allow_html=True)

        all_cities = sorted(future_df["city_name"].unique())
        default_cities = all_cities[:3]
        sel_cities = st.multiselect(
            "Select cities",
            all_cities,
            default=default_cities,
            max_selections=3,
            key="city_compare"
        )

        if sel_cities:
            comp_df = (
                future_df[future_df["city_name"].isin(sel_cities)]
                .groupby(["week_number", "city_name"])["num_orders"]
                .sum().reset_index()
            )
            fig2 = px.line(
                comp_df, x="week_number", y="num_orders",
                color="city_name",
                color_discrete_sequence=[AMBER, DARK, "#92400E"],
                labels={"week_number": "Week", "num_orders": "Orders", "city_name": ""},
                height=380
            )
            fig2.update_traces(line_width=2)
            fig2.update_layout(
                paper_bgcolor=BG, plot_bgcolor=WHITE,
                font_family="DM Sans", font_color=MID,
                height=380, margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False,
                xaxis=dict(gridcolor=LIGHT, linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
                yaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
                legend=dict(orientation="h", y=1.08, font_size=11,
                            bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-tag">Ranked table</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">All cities — forecasted demand with trend</div>', unsafe_allow_html=True)

    top_cities_tbl = (
        future_df.groupby("city_name")["num_orders"]
        .sum().reset_index()
        .sort_values("num_orders", ascending=False)
        .head(20)
    )
    top_cities_tbl["trend"] = top_cities_tbl.city_name.apply(
        lambda c: future_df[future_df.city_name == c]
        .groupby("week_number").num_orders.sum()
        .sort_index().tolist()
    )
    prev_city = prev_df.groupby("city_name")["num_orders"].sum()
    top_cities_tbl["vs_prev"] = top_cities_tbl.apply(
        lambda r: round(pct_delta(r["num_orders"], prev_city.get(r["city_name"], 0)), 1),
        axis=1
    )

    st.dataframe(
        top_cities_tbl.rename(columns={
            "city_name": "City",
            "num_orders": "Forecasted orders",
            "trend": "Trend",
            "vs_prev": "vs prev (%)"
        }),
        column_config={
            "City": st.column_config.TextColumn(width="medium"),
            "Forecasted orders": st.column_config.NumberColumn(format="%d"),
            "Trend": st.column_config.LineChartColumn(
                f"Weeks {future_weeks[0]}–{future_weeks[-1]}", width="large"
            ),
            "vs prev (%)": st.column_config.NumberColumn(format="%.1f%%")
        },
        hide_index=True, use_container_width=True
    )


# ══════════════════════════════════════════
# TAB 3 — Meal performance
# ══════════════════════════════════════════
with tab3:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight">
        <div class="insight-dot"></div>
        <div class="insight-text">
            <strong>Key finding:</strong> Meal category breakdown reveals which food segments 
            drive the bulk of demand — a signal that directly informs procurement and kitchen 
            capacity planning. The meal type split (breakfast / lunch / dinner / dessert) 
            shows intraday demand patterns across the forecast window.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="sec-tag">By category</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Demand by meal category</div>', unsafe_allow_html=True)
        cat_df = (
            future_df.groupby("meal_category")["num_orders"]
            .sum().reset_index().sort_values("num_orders", ascending=False)
        )
        fig = px.pie(
            cat_df, names="meal_category", values="num_orders",
            color_discrete_sequence=[AMBER, "#D97706", "#92400E", DARK, "#A8A29E", LIGHT],
            hole=0.45,
            height=300
        )
        fig.update_layout(
            paper_bgcolor=BG, font_family="DM Sans",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font_size=11, orientation="v")
        )
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          textfont_size=10)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="sec-tag">By meal type</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">Demand by meal type</div>', unsafe_allow_html=True)
        mtype_df = (
            future_df.groupby("meal_type")["num_orders"]
            .sum().reset_index().sort_values("num_orders", ascending=False)
        )
        fig2 = px.pie(
            mtype_df, names="meal_type", values="num_orders",
            color_discrete_sequence=[AMBER, "#D97706", "#92400E", DARK],
            hole=0.45, height=300
        )
        fig2.update_layout(
            paper_bgcolor=BG, font_family="DM Sans",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font_size=11)
        )
        fig2.update_traces(textposition="inside", textinfo="percent+label",
                           textfont_size=10)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="sec-tag">Top meals</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">Top 20 meals by forecasted volume</div>', unsafe_allow_html=True)

    top_meals_tbl = (
        future_df.groupby(["meal_name", "meal_category", "meal_type"])["num_orders"]
        .sum().reset_index()
        .sort_values("num_orders", ascending=False).head(20)
    )
    top_meals_tbl["trend"] = top_meals_tbl.meal_name.apply(
        lambda m: future_df[future_df.meal_name == m]
        .groupby("week_number").num_orders.sum()
        .sort_index().tolist()
    )
    prev_meal = prev_df.groupby("meal_name")["num_orders"].sum()
    top_meals_tbl["vs_prev"] = top_meals_tbl.apply(
        lambda r: round(pct_delta(r["num_orders"], prev_meal.get(r["meal_name"], 0)), 1),
        axis=1
    )

    st.dataframe(
        top_meals_tbl.rename(columns={
            "meal_name": "Meal", "meal_category": "Category",
            "meal_type": "Type", "num_orders": "Forecasted orders",
            "trend": "Trend", "vs_prev": "vs prev (%)"
        }),
        column_config={
            "Meal": st.column_config.TextColumn(width="large"),
            "Category": st.column_config.TextColumn(width="small"),
            "Type": st.column_config.TextColumn(width="small"),
            "Forecasted orders": st.column_config.NumberColumn(format="%d"),
            "Trend": st.column_config.LineChartColumn(
                f"Weeks {future_weeks[0]}–{future_weeks[-1]}", width="medium"
            ),
            "vs prev (%)": st.column_config.NumberColumn(format="%.1f%%")
        },
        hide_index=True, use_container_width=True
    )


# ══════════════════════════════════════════
# TAB 4 — Demand heatmap
# ══════════════════════════════════════════
with tab4:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight">
        <div class="insight-dot"></div>
        <div class="insight-text">
            <strong>How to read this:</strong> Dark amber cells indicate high demand combinations — 
            these are the city-meal pairs that procurement and logistics should prioritise. 
            White cells are low or zero demand. Use the category filter to focus on specific food segments.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        cat_filter = st.selectbox(
            "Meal category",
            ["All"] + sorted(future_df["meal_category"].unique()),
            key="heatmap_cat"
        )
        top_n_cities = st.selectbox("Top N cities", [10, 15, 20, 30], key="heatmap_n")

    heat_df = future_df if cat_filter == "All" else future_df[future_df["meal_category"] == cat_filter]

    top_city_list = (
        heat_df.groupby("city_name")["num_orders"].sum()
        .nlargest(top_n_cities).index.tolist()
    )
    heat_pivot = (
        heat_df[heat_df["city_name"].isin(top_city_list)]
        .groupby(["city_name", "meal_name"])["num_orders"]
        .sum().reset_index()
    )

    st.markdown('<div class="sec-tag">City × meal matrix</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">Demand heatmap — top {top_n_cities} cities</div>', unsafe_allow_html=True)

    meal_order = (
        heat_pivot.groupby("meal_name")["num_orders"].sum()
        .sort_values(ascending=False).index.tolist()
    )
    city_order = (
        heat_pivot.groupby("city_name")["num_orders"].sum()
        .sort_values(ascending=False).index.tolist()
    )

    fig = (
        alt.Chart(heat_pivot)
        .mark_rect()
        .encode(
            x=alt.X("meal_name:O", sort=meal_order, title="Meal",
                    axis=alt.Axis(labelAngle=-45, labelFontSize=10)),
            y=alt.Y("city_name:O", sort=city_order, title="City",
                    axis=alt.Axis(labelFontSize=10)),
            color=alt.Color(
                "num_orders:Q",
                scale=alt.Scale(scheme="oranges"),
                title="Orders"
            ),
            tooltip=["city_name:N", "meal_name:N",
                     alt.Tooltip("num_orders:Q", format=",")]
        )
        .properties(height=max(320, top_n_cities * 22))
        .configure_axis(grid=False)
        .configure_view(stroke=None)
        .interactive()
    )
    st.altair_chart(fig, use_container_width=True)


# ══════════════════════════════════════════
# TAB 5 — Forecast detail
# ══════════════════════════════════════════
with tab5:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight">
        <div class="insight-dot"></div>
        <div class="insight-text">
            <strong>Drill-down view:</strong> Select a city and meal to see the full week-by-week 
            forecast alongside historical actuals. The table below shows the pivot of forecasted 
            orders per week — ready to export for operations planning.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sel_city = st.selectbox(
            "City",
            sorted(df["city_name"].unique()),
            key="detail_city"
        )
    with col2:
        sel_meal = st.selectbox(
            "Meal",
            sorted(df["meal_name"].unique()),
            key="detail_meal"
        )

    mask  = (df["city_name"] == sel_city) & (df["meal_name"] == sel_meal)
    drill = df[mask].copy()

    if drill.empty:
        st.markdown("""
        <div style="background:#FFF;border:1px solid #E7E5E0;border-radius:10px;padding:28px;text-align:center;margin-top:16px;">
            <div style="font-family:'DM Serif Display',serif;font-size:18px;color:#1C1917;margin-bottom:6px;">No data for this combination</div>
            <div style="font-size:13px;color:#A8A29E;font-family:'DM Sans',sans-serif;">Try a different city or meal selection.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        drill["period_label"] = drill["period"].map(
            {"past": "Actuals", "Future": "Forecast"}
        )
        st.markdown('<div class="sec-tag">Week-by-week</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">{sel_meal} in {sel_city}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-sub">Actuals + {n_weeks}-week forecast</div>', unsafe_allow_html=True)

        fig = px.line(
            drill, x="week_number", y="num_orders",
            color="period_label",
            color_discrete_map={"Actuals": DARK, "Forecast": AMBER},
            labels={"week_number": "Week", "num_orders": "Orders", "period_label": ""},
            height=360, markers=True
        )
        fig.update_traces(line_width=2, marker_size=5)
        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor=WHITE,
            font_family="DM Sans", font_color=MID,
            height=360, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor=LIGHT, linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", linecolor=LIGHT, tickfont_size=11, tickfont_color=DARK, title_font_color=DARK),
            legend=dict(orientation="h", y=1.08, font_size=12,
                        bgcolor="rgba(0,0,0,0)")
        )
        if future_weeks:
            fig.add_vrect(
                x0=future_weeks[0], x1=future_weeks[-1],
                fillcolor=AMBER, opacity=0.06,
                layer="below", line_width=0
            )
        st.plotly_chart(fig, use_container_width=True)

        # pivot table
        future_only = drill[drill["period"] == "Future"]
        if not future_only.empty:
            pivot = (
                future_only.groupby(["city_name", "meal_name", "week_number"])
                ["num_orders"].sum().unstack(level=2)
                .fillna(0).astype(int).reset_index()
            )
            st.markdown('<div class="sec-tag">Export-ready table</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">Forecasted orders by week</div>', unsafe_allow_html=True)
            st.dataframe(
                pivot.rename(columns={"city_name": "City", "meal_name": "Meal"}),
                hide_index=True, use_container_width=True
            )

# ── footer ───────────────────────────────────────────────────────
st.markdown("""
<div class="dash-footer">
    <div class="dash-footer-title">Meal Demand Forecasting System</div>
    <div class="dash-footer-sub">
        XGBoost · Time-series features · 528K rows · 76 cities · 51 meals ·
        Built by <a href="https://github.com/faheem-afk">Faheem Bashir Bhat</a>
    </div>
</div>
""", unsafe_allow_html=True)