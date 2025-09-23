import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Trader Analysis - The War Zone",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .leaderboard-item {
        padding: 0.75rem;
        margin: 0.5rem 0;
        background: #f8fafc;
        border-radius: 0.5rem;
        border-left: 4px solid;
    }
</style>
""", unsafe_allow_html=True)

# Load data function (same as main app)
@st.cache_data(ttl=30)
def load_trades_data():
    """Load trades data - same function as main app"""
    try:
        # Import the same function from your main app
        from Aapp import load_trades_from_sheets
        return load_trades_from_sheets()
    except:
        # Fallback data
        return [
            {'id': 1, 'date': '2024-01-15', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.5, 'sl': 1815.0, 'target': 1830.0, 'risk': 5.5, 'reward': 9.5, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 2, 'date': '2024-01-14', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.3, 'sl': 88.5, 'target': 91.0, 'risk': 0.8, 'reward': 1.7, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss'},
            {'id': 3, 'date': '2024-01-13', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.0, 'sl': 27200.0, 'target': 27800.0, 'risk': 250.0, 'reward': 350.0, 'rrRatio': 1.4, 'outcome': 'Open', 'result': 'Open'},
            {'id': 4, 'date': '2024-01-12', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.0625, 'sl': 1.06, 'target': 1.067, 'risk': 0.0025, 'reward': 0.0045, 'rrRatio': 1.8, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 5, 'date': '2024-01-11', 'trader': 'Wallace', 'instrument': 'US30', 'entry': 34500.0, 'sl': 34200.0, 'target': 34900.0, 'risk': 300.0, 'reward': 400.0, 'rrRatio': 1.33, 'outcome': 'Open', 'result': 'Open'},
            {'id': 6, 'date': '2024-01-10', 'trader': 'Max', 'instrument': 'XAUUSD', 'entry': 1835.0, 'sl': 1828.0, 'target': 1845.0, 'risk': 7.0, 'reward': 10.0, 'rrRatio': 1.43, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 7, 'date': '2024-01-09', 'trader': 'Waithaka', 'instrument': 'BTCUSD', 'entry': 42000.0, 'sl': 41500.0, 'target': 43000.0, 'risk': 500.0, 'reward': 1000.0, 'rrRatio': 2.0, 'outcome': 'SL Hit', 'result': 'Loss'}
        ]

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 2rem; border-radius: 0.5rem; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0; text-align: center;">👤 Trader Performance Analysis</h1>
    <p style="color: #e2e8f0; text-align: center; margin: 0.5rem 0 0 0;">Compare trader performance, track records, and individual trade analysis</p>
</div>
""", unsafe_allow_html=True)

# Load data
trades_data = load_trades_data()
df = pd.DataFrame(trades_data)

# Convert date column
df['date'] = pd.to_datetime(df['date'])

# Date filter
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
with col3:
    selected_traders = st.multiselect("Filter Traders", options=df['trader'].unique(), default=df['trader'].unique())

# Filter data
filtered_df = df[
    (df['date'].dt.date >= start_date) & 
    (df['date'].dt.date <= end_date) &
    (df['trader'].isin(selected_traders))
]

# Overall metrics
st.markdown("### 📊 Overall Performance Metrics")

if len(filtered_df) > 0:
    # Calculate metrics
    total_trades = len(filtered_df)
    closed_trades = filtered_df[filtered_df['outcome'].isin(['Target Hit', 'SL Hit'])]
    open_trades = filtered_df[filtered_df['outcome'] == 'Open']
    winning_trades = closed_trades[closed_trades['result'] == 'Win']
    
    win_rate = (len(winning_trades) / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
    avg_rr = closed_trades['rrRatio'].mean() if len(closed_trades) > 0 else 0
    
    # Display metrics
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Total Trades", total_trades, f"{len(open_trades)} open")
    with mcol2:
        st.metric("Win Rate", f"{win_rate:.1f}%", f"{len(winning_trades)}/{len(closed_trades)}")
    with mcol3:
        st.metric("Avg R:R Ratio", f"{avg_rr:.2f}")
    with mcol4:
        total_pnl = (winning_trades['reward'].sum() - 
                    closed_trades[closed_trades['result'] == 'Loss']['risk'].sum())
        st.metric("Total P&L", f"{total_pnl:+.2f}")

    # Trader Leaderboard
    st.markdown("### 🏆 Trader Leaderboard")
    
    # Calculate trader statistics
    trader_stats = []
    for trader in selected_traders:
        trader_trades = filtered_df[filtered_df['trader'] == trader]
        trader_closed = trader_trades[trader_trades['outcome'].isin(['Target Hit', 'SL Hit'])]
        trader_wins = trader_closed[trader_closed['result'] == 'Win']
        
        stats = {
            'Trader': trader,
            'Total Trades': len(trader_trades),
            'Closed Trades': len(trader_closed),
            'Wins': len(trader_wins),
            'Losses': len(trader_closed) - len(trader_wins),
            'Win Rate': (len(trader_wins) / len(trader_closed) * 100) if len(trader_closed) > 0 else 0,
            'Avg R:R': trader_closed['rrRatio'].mean() if len(trader_closed) > 0 else 0,
            'Total P&L': (trader_wins['reward'].sum() - 
                         trader_closed[trader_closed['result'] == 'Loss']['risk'].sum())
        }
        trader_stats.append(stats)
    
    leaderboard_df = pd.DataFrame(trader_stats).sort_values('Win Rate', ascending=False)
    
    # Display leaderboard
    for i, (_, trader) in enumerate(leaderboard_df.iterrows()):
        win_rate_color = "#10b981" if trader['Win Rate'] >= 50 else "#ef4444"
        pnl_color = "#10b981" if trader['Total P&L'] >= 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="leaderboard-item" style="border-left-color: {'#fbbf24' if i == 0 else '#9ca3af' if i == 1 else '#fb923c' if i == 2 else '#3b82f6'}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center;">
                    <div style="background: {'#fbbf24' if i == 0 else '#9ca3af' if i == 1 else '#fb923c' if i == 2 else '#3b82f6'}; 
                                color: white; width: 30px; height: 30px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; 
                                font-weight: bold; margin-right: 1rem;">
                        {i+1}
                    </div>
                    <div>
                        <strong style="font-size: 1.1rem;">{trader['Trader']}</strong>
                        <div style="font-size: 0.9rem; color: #666;">
                            {trader['Total Trades']} trades ({trader['Total Trades'] - trader['Closed Trades']} open)
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <strong style="color: {win_rate_color}; font-size: 1.1rem;">
                        {trader['Win Rate']:.1f}% Win Rate
                    </strong>
                    <div style="font-size: 0.9rem; color: {pnl_color};">
                        P&L: {trader['Total P&L']:+.2f}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Charts section
    st.markdown("### 📈 Performance Charts")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Win Rate Comparison
        fig = px.bar(leaderboard_df, x='Trader', y='Win Rate', 
                    title='Win Rate by Trader', color='Win Rate',
                    color_continuous_scale='Viridis')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # P&L Comparison
        fig = px.bar(leaderboard_df, x='Trader', y='Total P&L', 
                    title='Total P&L by Trader', color='Total P&L',
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)

    # Individual Trade Comparison
    st.markdown("### 🔍 Individual Trade Comparison")
    
    # Trade filtering options
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        compare_traders = st.multiselect("Compare Trades for Traders", 
                                       options=selected_traders, 
                                       default=selected_traders[:min(2, len(selected_traders))])
    with fcol2:
        outcome_filter = st.multiselect("Outcome Filter", 
                                      options=['Open', 'Target Hit', 'SL Hit'],
                                      default=['Open', 'Target Hit', 'SL Hit'])
    with fcol3:
        sort_by = st.selectbox("Sort By", 
                             options=['date', 'rrRatio', 'risk', 'reward'], 
                             format_func=lambda x: x.replace('rrRatio', 'R:R Ratio').title())

    # Filter comparison data
    compare_df = filtered_df[
        (filtered_df['trader'].isin(compare_traders)) &
        (filtered_df['outcome'].isin(outcome_filter))
    ].sort_values(sort_by, ascending=False)

    # Display comparison table
    if len(compare_df) > 0:
        display_cols = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                       'rrRatio', 'outcome', 'result']
        st.dataframe(compare_df[display_cols], use_container_width=True)
        
        # Trade distribution chart
        st.markdown("#### Trade Distribution")
        dist_col1, dist_col2 = st.columns(2)
        
        with dist_col1:
            fig = px.pie(compare_df, names='trader', title='Trade Distribution by Trader')
            st.plotly_chart(fig, use_container_width=True)
        
        with dist_col2:
            fig = px.pie(compare_df, names='outcome', title='Trade Distribution by Outcome')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trades match the selected filters.")

else:
    st.warning("No trade data available for the selected filters.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>The War Zone</strong> • Trader Performance Analysis • Updated automatically
</div>
""", unsafe_allow_html=True)