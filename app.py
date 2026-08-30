from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from investready.database import (
    SECTORS, STAGES, add_followup, add_investor, delete_investor, export_csv,
    get_followups, get_investors, initialize, seed_demo_data, toggle_followup,
    update_stage,
)
from investready.scoring import WEIGHTS, calculate_score


st.set_page_config(page_title="InvestReady", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');
:root { --navy:#0b1f33; --green:#13a67a; --gold:#d5a843; --paper:#f4f7f8; }
.stApp { background: var(--paper); color:#183042; font-family:'DM Sans',sans-serif; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#071a2d,#0d2b3f); }
[data-testid="stSidebar"] * { color:#eef8f5 !important; }
h1,h2,h3 { font-family:'DM Sans',sans-serif; letter-spacing:-.03em; }
.brand { font-family:'Playfair Display',serif; font-size:2rem; color:white; margin:.25rem 0 0; }
.eyebrow { text-transform:uppercase; letter-spacing:.14em; color:#13a67a; font-weight:700; font-size:.72rem; }
.hero { background:linear-gradient(120deg,#092238,#12485b); color:white; padding:1.7rem 2rem; border-radius:18px; margin-bottom:1.2rem; box-shadow:0 14px 35px rgba(11,31,51,.13); }
.hero h1 { margin:0; color:white; font-size:2.2rem; }
.hero p { margin:.35rem 0 0; color:#bdd7d8; }
[data-testid="stMetric"] { background:white; padding:1rem 1.15rem; border-radius:14px; border:1px solid #e1e9e9; box-shadow:0 5px 18px rgba(18,46,61,.05); }
[data-testid="stMetricValue"] { color:#0b3850; }
.priority { padding:.65rem .8rem; border-left:4px solid #13a67a; background:white; border-radius:0 10px 10px 0; margin:.4rem 0; }
.small-note { color:#607684; font-size:.85rem; }
.stButton>button { border-radius:9px; font-weight:600; }
div[data-testid="stDataFrame"] { border:1px solid #e1e9e9; border-radius:12px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def setup_database():
    initialize()
    seed_demo_data()
    return True


setup_database()


def load_frame() -> pd.DataFrame:
    return pd.DataFrame(get_investors())


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><div class="eyebrow">Investment intelligence</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown('<div class="brand">InvestReady</div>', unsafe_allow_html=True)
    st.caption("Investment Attraction Intelligence")
    page = st.radio("Workspace", ["Executive Dashboard", "Investor Pipeline", "Add Investor", "Compare Opportunities", "Follow-up Tracker", "Reports & Data"], label_visibility="collapsed")
    st.divider()
    st.caption("Transparent decisions • Stronger pipelines")


df = load_frame()

if page == "Executive Dashboard":
    hero("Executive Dashboard", "A single view of pipeline value, priority investors, and conversion momentum.")
    total_value = df["investment_usd_m"].sum() if not df.empty else 0
    jobs = int(df["jobs"].sum()) if not df.empty else 0
    strategic = int((df["category"] == "Strategic Priority").sum()) if not df.empty else 0
    committed = int((df["stage"] == "Committed").sum()) if not df.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pipeline value", f"${total_value:,.1f}M")
    c2.metric("Potential jobs", f"{jobs:,}")
    c3.metric("Strategic priorities", strategic)
    c4.metric("Committed investors", committed)

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Pipeline by stage")
        stage_data = df.groupby("stage", as_index=False)["investment_usd_m"].sum()
        stage_data["stage"] = pd.Categorical(stage_data["stage"], categories=STAGES, ordered=True)
        stage_data = stage_data.sort_values("stage")
        fig = px.bar(stage_data, x="stage", y="investment_usd_m", color="investment_usd_m", color_continuous_scale=["#b9ddd5", "#13a67a", "#0b3850"], labels={"investment_usd_m":"USD millions", "stage":""})
        fig.update_layout(coloraxis_showscale=False, height=340, margin=dict(l=10,r=10,t=10,b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Sector composition")
        sectors = df.groupby("sector", as_index=False)["investment_usd_m"].sum()
        fig = px.pie(sectors, names="sector", values="investment_usd_m", hole=.62, color_discrete_sequence=["#0b3850","#13a67a","#d5a843","#477b88","#84b9ad","#8d6d3e"])
        fig.update_layout(height=340, margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation="h", y=-.1))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top opportunities")
    for _, row in df.head(4).iterrows():
        st.markdown(f'<div class="priority"><b>{row.company}</b> · {row.country}<br><span class="small-note">{row.category} · Score {row.total_score:.1f} · ${row.investment_usd_m:.1f}M · {row.stage}</span></div>', unsafe_allow_html=True)

elif page == "Investor Pipeline":
    hero("Investor Pipeline", "Filter, inspect, and advance every opportunity from prospect to commitment.")
    f1, f2, f3 = st.columns(3)
    sector = f1.multiselect("Sector", sorted(df.sector.unique()))
    stage = f2.multiselect("Stage", STAGES)
    search = f3.text_input("Search company or country")
    view = df.copy()
    if sector: view = view[view.sector.isin(sector)]
    if stage: view = view[view.stage.isin(stage)]
    if search: view = view[view.company.str.contains(search, case=False) | view.country.str.contains(search, case=False)]
    columns = ["company","country","sector","investment_usd_m","jobs","total_score","category","stage","owner"]
    st.dataframe(view[columns], use_container_width=True, hide_index=True, column_config={"investment_usd_m":st.column_config.NumberColumn("Investment",format="$%.1fM"),"total_score":st.column_config.ProgressColumn("Score",min_value=0,max_value=100,format="%.1f")})
    if not view.empty:
        st.subheader("Update opportunity")
        c1, c2, c3 = st.columns([2,1,1])
        selected_company = c1.selectbox("Investor", view.company.tolist())
        current = view[view.company == selected_company].iloc[0]
        new_stage = c2.selectbox("Pipeline stage", STAGES, index=STAGES.index(current.stage))
        if c3.button("Save stage", use_container_width=True):
            update_stage(int(current.id), new_stage); st.success("Pipeline stage updated."); st.rerun()
        with st.expander("Investor details"):
            st.write(current.notes or "No notes added.")
            st.write(f"Contact: {current.contact_name} · {current.contact_email}")
        with st.expander("Delete investor", expanded=False):
            st.warning("This also deletes related follow-ups.")
            if st.button("Permanently delete", type="primary"):
                delete_investor(int(current.id)); st.rerun()

elif page == "Add Investor":
    hero("Add Investment Opportunity", "Capture the commercial case and produce an immediate, explainable priority score.")
    with st.form("investor_form", clear_on_submit=True):
        a, b, c = st.columns(3)
        company = a.text_input("Company name *")
        country = b.text_input("Country *")
        sector = c.selectbox("Sector", SECTORS)
        a, b, c = st.columns(3)
        investment = a.number_input("Investment (USD millions)", min_value=0.0, step=1.0)
        jobs = b.number_input("Potential jobs", min_value=0, step=10)
        export = c.slider("Export potential (%)", 0, 100, 50)
        st.markdown("#### Qualitative assessment")
        q1, q2, q3, q4 = st.columns(4)
        environmental = q1.slider("Environmental", 0, 10, 5)
        financial = q2.slider("Financial strength", 0, 10, 5)
        technology = q3.slider("Technology transfer", 0, 10, 5)
        readiness = q4.slider("Readiness", 0, 10, 5)
        a, b, c = st.columns(3)
        contact = a.text_input("Contact name")
        email = b.text_input("Contact email")
        owner = c.text_input("Opportunity owner")
        stage = st.selectbox("Initial stage", STAGES)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Score and save investor", type="primary", use_container_width=True)
        if submitted:
            if len(company.strip()) < 2 or len(country.strip()) < 2:
                st.error("Company and country are required.")
            else:
                try:
                    investor_id = add_investor({"company":company,"country":country,"sector":sector,"contact_name":contact,"contact_email":email,"investment_usd_m":investment,"jobs":jobs,"export_percent":export,"environmental_score":environmental,"financial_score":financial,"technology_score":technology,"readiness_score":readiness,"stage":stage,"status":"Active","owner":owner,"notes":notes})
                    result = calculate_score(investment,jobs,export,environmental,financial,technology,readiness)
                    st.success(f"Saved investor #{investor_id}: {result.category} ({result.total}/100).")
                    st.balloons()
                except Exception as exc:
                    st.error(f"Could not save investor: {exc}")

elif page == "Compare Opportunities":
    hero("Compare Opportunities", "Place investment cases side by side and understand what drives each score.")
    chosen = st.multiselect("Choose 2–4 investors", df.company.tolist(), default=df.company.head(3).tolist(), max_selections=4)
    if len(chosen) < 2:
        st.info("Select at least two investors.")
    else:
        compare = df[df.company.isin(chosen)]
        chart = go.Figure()
        axes = ["Investment","Jobs","Export","Environmental","Financial","Technology","Readiness"]
        for _, row in compare.iterrows():
            score = calculate_score(row.investment_usd_m,row.jobs,row.export_percent,row.environmental_score,row.financial_score,row.technology_score,row.readiness_score)
            values = list(score.components.values())
            chart.add_trace(go.Scatterpolar(r=values+[values[0]], theta=axes+[axes[0]], fill="toself", name=row.company))
        chart.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),height=500,margin=dict(l=30,r=30,t=30,b=30),paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart,use_container_width=True)
        st.dataframe(compare[["company","investment_usd_m","jobs","export_percent","total_score","category"]],hide_index=True,use_container_width=True)
        st.caption("Scoring weights: " + " · ".join(f"{key.title()} {value:.0%}" for key,value in WEIGHTS.items()))

elif page == "Follow-up Tracker":
    hero("Follow-up Tracker", "Keep every commitment visible and every investor conversation moving.")
    with st.form("followup"):
        c1,c2 = st.columns(2)
        company = c1.selectbox("Investor",df.company.tolist())
        due = c2.date_input("Due date",min_value=date.today())
        action = st.text_input("Next action")
        owner = st.text_input("Owner")
        if st.form_submit_button("Add follow-up",type="primary"):
            if not action.strip() or not owner.strip(): st.error("Action and owner are required.")
            else:
                investor_id=int(df[df.company==company].iloc[0].id)
                add_followup(investor_id,due.isoformat(),action,owner); st.success("Follow-up added."); st.rerun()
    followups = get_followups()
    st.subheader("Action queue")
    for item in followups:
        cols=st.columns([.5,2,3,2,1])
        done=cols[0].checkbox("Done",value=bool(item["completed"]),key=f'f{item["id"]}',label_visibility="collapsed")
        if done != bool(item["completed"]): toggle_followup(item["id"],done); st.rerun()
        cols[1].write(item["due_date"])
        cols[2].write(f'**{item["company"]}** — {item["action"]}')
        cols[3].write(item["owner"])
        if not item["completed"] and item["due_date"] < date.today().isoformat(): cols[4].error("Overdue")

else:
    hero("Reports & Data", "Export management-ready pipeline data and inspect the scoring methodology.")
    c1,c2,c3=st.columns(3)
    c1.metric("Investors",len(df)); c2.metric("Countries",df.country.nunique()); c3.metric("Average score",f'{df.total_score.mean():.1f}')
    st.download_button("Download complete investor register",export_csv(),"investready-investors.csv","text/csv",type="primary")
    st.subheader("Management summary")
    summary=df.groupby("sector").agg(Investors=("id","count"),Investment_USD_M=("investment_usd_m","sum"),Potential_Jobs=("jobs","sum"),Average_Score=("total_score","mean")).round(1).reset_index()
    st.dataframe(summary,use_container_width=True,hide_index=True)
    st.subheader("Scoring methodology")
    methodology=pd.DataFrame({"Criterion":[k.title() for k in WEIGHTS],"Weight":[f"{v:.0%}" for v in WEIGHTS.values()]})
    st.dataframe(methodology,use_container_width=True,hide_index=True)
    st.info("The scoring model is a decision-support tool. Adjust weights and thresholds to match the organization's approved investment strategy.")
