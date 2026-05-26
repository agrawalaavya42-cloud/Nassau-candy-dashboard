import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Nassau Candy - Factory Optimizer",
                   layout="wide", page_icon="🍬")

st.title("🍬 Nassau Candy Distributor — Factory Optimization Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True)
    df['Lead Time']  = (df['Ship Date'] - df['Order Date']).dt.days
    factory_map = {
        'Wonka Bar - Nutty Crunch Surprise' : "Lot's O' Nuts",
        'Wonka Bar - Fudge Mallows'         : "Lot's O' Nuts",
        'Wonka Bar -Scrumdiddlyumptious'    : "Lot's O' Nuts",
        'Wonka Bar - Milk Chocolate'        : "Wicked Choccy's",
        'Wonka Bar - Triple Dazzle Caramel' : "Wicked Choccy's",
        'Laffy Taffy'                        : 'Sugar Shack',
        'SweeTARTS'                          : 'Sugar Shack',
        'Nerds'                              : 'Sugar Shack',
        'Fun Dip'                            : 'Sugar Shack',
        'Fizzy Lifting Drinks'               : 'Sugar Shack',
        'Everlasting Gobstopper'             : 'Secret Factory',
        'Lickable Wallpaper'                 : 'Secret Factory',
        'Wonka Gum'                          : 'Secret Factory',
        'Hair Toffee'                        : 'The Other Factory',
        'Kazookles'                          : 'The Other Factory'
    }
    df['Factory'] = df['Product Name'].map(factory_map)
    return df

df = load_data()

st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"### 📦 Total Orders\n## **{len(df):,}**")
col2.markdown(f"### ⏱ Avg Lead Time\n## **{int(df['Lead Time'].mean())} days**")
col3.markdown(f"### 💰 Total Revenue\n## **${df['Sales'].sum():,.0f}**")
col4.markdown(f"### 📈 Profit Margin\n## **{df['Gross Profit'].sum()/df['Sales'].sum()*100:.1f}%**")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏭 Factory Simulator",
    "📈 What-If Analysis",
    "🎯 Recommendations",
    "⚠️ Risk Panel"
])

with tab1:
    st.subheader("Factory Optimization Simulator")
    product = st.selectbox("Select Product", sorted(df['Product Name'].unique()))
    region  = st.selectbox("Select Region",  sorted(df['Region'].unique()))
    filtered = df[(df['Product Name'] == product) & (df['Region'] == region)]
    if len(filtered) > 0:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                filtered.groupby('Factory')['Lead Time'].mean().reset_index(),
                x='Factory', y='Lead Time', color='Factory',
                title='Avg Lead Time by Factory')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(
                filtered.groupby('Factory')['Gross Profit'].mean().reset_index(),
                x='Factory', y='Gross Profit', color='Factory',
                title='Avg Profit by Factory')
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data for this combination.")

with tab2:
    st.subheader("What-If Scenario Analysis")
    ship_mode = st.selectbox("Ship Mode", sorted(df['Ship Mode'].unique()))
    st.write("**Optimization Priority (Speed vs Profit):** Use filters above to adjust")
    scenario = df[df['Ship Mode'] == ship_mode].groupby('Factory').agg(
        Avg_Lead_Time=('Lead Time',    'mean'),
        Avg_Profit   =('Gross Profit', 'mean'),
        Orders       =('Row ID',       'count')
    ).reset_index()
    fig = px.scatter(scenario, x='Avg_Lead_Time', y='Avg_Profit',
                     size='Orders', color='Factory', text='Factory',
                     title='Lead Time vs Profit by Factory')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🎯 Factory Reassignment Recommendations")
    factory_map_local = {
        'Wonka Bar - Nutty Crunch Surprise' : "Lot's O' Nuts",
        'Wonka Bar - Fudge Mallows'         : "Lot's O' Nuts",
        'Wonka Bar -Scrumdiddlyumptious'    : "Lot's O' Nuts",
        'Wonka Bar - Milk Chocolate'        : "Wicked Choccy's",
        'Wonka Bar - Triple Dazzle Caramel' : "Wicked Choccy's",
        'Laffy Taffy'                        : 'Sugar Shack',
        'SweeTARTS'                          : 'Sugar Shack',
        'Nerds'                              : 'Sugar Shack',
        'Fun Dip'                            : 'Sugar Shack',
        'Fizzy Lifting Drinks'               : 'Sugar Shack',
        'Everlasting Gobstopper'             : 'Secret Factory',
        'Lickable Wallpaper'                 : 'Secret Factory',
        'Wonka Gum'                          : 'Secret Factory',
        'Hair Toffee'                        : 'The Other Factory',
        'Kazookles'                          : 'The Other Factory'
    }
    recs = df.groupby('Product Name').agg(
        Avg_Lead_Time=('Lead Time',    'mean'),
        Avg_Profit   =('Gross Profit', 'mean'),
        Total_Orders =('Row ID',       'count')
    ).reset_index().sort_values('Avg_Lead_Time', ascending=False)
    recs['Current Factory'] = recs['Product Name'].map(factory_map_local)
    recs['Avg_Lead_Time']   = recs['Avg_Lead_Time'].round(1)
    recs['Avg_Profit']      = recs['Avg_Profit'].round(2)
    st.write(recs[['Product Name','Current Factory',
                   'Avg_Lead_Time','Avg_Profit',
                   'Total_Orders']].to_html(index=False),
             unsafe_allow_html=True)

with tab4:
    st.subheader("⚠️ Risk & Impact Panel")
    high_risk  = df[df['Lead Time'] > df['Lead Time'].quantile(0.75)]
    low_profit = df[df['Gross Profit'] < 2]
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"🔴 High Lead Time Orders: {len(high_risk):,}")
        fig = px.histogram(df, x='Lead Time', color='Factory',
                           title='Lead Time Distribution by Factory')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.warning(f"🟡 Low Profit Orders: {len(low_profit):,}")
        fig2 = px.box(df, x='Factory', y='Gross Profit', color='Factory',
                      title='Profit Distribution by Factory')
        st.plotly_chart(fig2, use_container_width=True)

