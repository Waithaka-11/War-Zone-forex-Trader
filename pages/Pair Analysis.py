import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Pair Analysis - The War Zone",
    page_icon="📊",
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
        margin: 0.5rem 0;
    }
    .trader-comparison {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data(ttl=30)
def load_trades_data():
    """Load trades data - same function as main app"""
    try:
        from Aapp import load_trades_from_sheets
        return load_trades_from_sheets()
    except:
        # Enhanced fallback data
        return [
            {'id': 1, 'date': '2024-01-15', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.5, 'sl': 1815.0, 'target': 1830.0, 'risk': 5.5, 'reward': 9.5, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 2, 'date': '2024-01-14', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.3, 'sl': 88.5, 'target': 91.0, 'risk': 0.8, 'reward': 1.7, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss'},
            {'id': 3, 'date': '2024-01-13', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.0, 'sl': 27200.0, 'target': 27800.0, 'risk': 250.0, 'reward': 350.0, 'rrRatio': 1.4, 'outcome': 'Open', 'result': 'Open'},
        ]

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 2rem; border-radius: 0.5rem; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0; text-align: center;">📊 Instrument Pair Analysis</h1>
    <p style="color: #e2e8f0; text-align: center; margin: 0.5rem 0 0 0;">Compare trader performance on specific trading pairs over time</p>
</div>
""", unsafe_allow_html=True)

# Load data
trades_data = load_trades_data()

# DATA CLEANING: Fix instrument names
cleaned_trades = []
for trade in trades_data:
    cleaned_trade = trade.copy()
    instrument = cleaned_trade.get('instrument', '').upper()
    
    if instrument == 'USTECH':
        cleaned_trade['instrument'] = 'US30'
    
    cleaned_trades.append(cleaned_trade)

df = pd.DataFrame(cleaned_trades)
df['date'] = pd.to_datetime(df['date'])

# Sidebar Filters
st.sidebar.markdown("### 🔧 Analysis Filters")

available_pairs = sorted(df['instrument'].unique())
selected_pair = st.sidebar.selectbox(
    "🎯 Select Trading Pair",
    options=available_pairs,
    index=0 if available_pairs else 0
)

available_traders = sorted(df['trader'].unique())
selected_traders = st.sidebar.multiselect(
    "👥 Select Traders to Compare",
    options=available_traders,
    default=available_traders
)

min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Quick date presets
st.sidebar.markdown("**Quick Presets:**")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    if st.button("1W"):
        end_date = max_date
        start_date = end_date - timedelta(days=7)
        st.session_state.date_range = (start_date, end_date)
with col2:
    if st.button("1M"):
        end_date = max_date
        start_date = end_date - timedelta(days=30)
        st.session_state.date_range = (start_date, end_date)
with col3:
    if st.button("All"):
        st.session_state.date_range = (min_date, max_date)

# Apply filters
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df['instrument'] == selected_pair) &
    (df['trader'].isin(selected_traders)) &
    (df['date'].dt.date >= start_date) &
    (df['date'].dt.date <= end_date)
]

# Main content
if len(filtered_df) == 0:
    st.warning("No trade data available for the selected filters. Please adjust your selection.")
else:
    # Overview metrics
    st.markdown(f"### 📈 Analysis for: **{selected_pair}**")
    
    # Calculate stats using result field
    total_trades = len(filtered_df)
    closed_trades = filtered_df[filtered_df['result'].isin(['Win', 'Loss', 'Breakeven'])]
    winning_trades = closed_trades[closed_trades['result'] == 'Win']
    losing_trades = closed_trades[closed_trades['result'] == 'Loss']
    
    # Calculate P&L
    total_pnl = 0
    for _, trade in closed_trades.iterrows():
        if trade['result'] == 'Win':
            total_pnl += trade['reward']
        elif trade['result'] == 'Loss':
            total_pnl -= trade['risk']
    
    win_rate = (len(winning_trades) / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Closed Trades", len(closed_trades))
    with col3:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col4:
        avg_rr = closed_trades['rrRatio'].mean() if len(closed_trades) > 0 else 0
        st.metric("Avg R:R", f"{avg_rr:.2f}")
    with col5:
        st.metric("Total P&L", f"{total_pnl:+.2f}")

    # Trader Comparison Table
    st.markdown("### 👥 Trader Performance Comparison")
    
    trader_stats = []
    for trader in selected_traders:
        trader_data = filtered_df[filtered_df['trader'] == trader]
        trader_closed = trader_data[trader_data['result'].isin(['Win', 'Loss', 'Breakeven'])]
        trader_wins = trader_closed[trader_closed['result'] == 'Win']
        trader_losses = trader_closed[trader_closed['result'] == 'Loss']
        
        # Calculate P&L for this trader
        trader_pnl = 0
        for _, trade in trader_closed.iterrows():
            if trade['result'] == 'Win':
                trader_pnl += trade['reward']
            elif trade['result'] == 'Loss':
                trader_pnl -= trade['risk']
        
        stats = {
            'Trader': trader,
            'Total Trades': len(trader_data),
            'Closed Trades': len(trader_closed),
            'Wins': len(trader_wins),
            'Losses': len(trader_losses),
            'Win Rate %': (len(trader_wins) / len(trader_closed) * 100) if len(trader_closed) > 0 else 0,
            'Avg R:R Ratio': trader_closed['rrRatio'].mean() if len(trader_closed) > 0 else 0,
            'Total P&L': trader_pnl
        }
        trader_stats.append(stats)
    
    comparison_df = pd.DataFrame(trader_stats)
    
    # Display comparison table
    if not comparison_df.empty:
        st.dataframe(comparison_df, use_container_width=True)
        
        # Visual performance summary
        st.markdown("#### 📊 Performance Summary")
        for _, trader in comparison_df.iterrows():
            win_rate = trader['Win Rate %']
            win_color = "#10b981" if win_rate >= 50 else "#ef4444"
            pnl_color = "#10b981" if trader['Total P&L'] >= 0 else "#ef4444"
            
            st.markdown(f"""
            <div class="trader-comparison">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{trader['Trader']}</strong>
                        <div style="font-size: 0.9rem; color: #666;">
                            {trader['Total Trades']} trades • {trader['Closed Trades']} closed
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <strong style="color: {win_color};">Win Rate: {win_rate:.1f}%</strong>
                        <div style="color: {pnl_color}; font-size: 1.1rem; font-weight: bold;">P&L: {trader['Total P&L']:+.2f}</div>
                    </div>
                </div>
                <div style="background: #e2e8f0; border-radius: 10px; height: 8px; margin-top: 0.5rem;">
                    <div style="background: {win_color}; width: {min(win_rate, 100)}%; height: 100%; border-radius: 10px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data available for comparison")

    # Performance Over Time Charts
    st.markdown("### 📅 Performance Over Time")
    
    if len(closed_trades) > 0:
        # Create weekly aggregated data
        weekly_data = closed_trades.copy()
        weekly_data['week'] = weekly_data['date'].dt.to_period('W').dt.start_time
        
        # Calculate weekly stats with P&L
        weekly_stats_list = []
        for week in weekly_data['week'].unique():
            week_trades = weekly_data[weekly_data['week'] == week]
            
            for trader in selected_traders:
                trader_week = week_trades[week_trades['trader'] == trader]
                
                if len(trader_week) > 0:
                    wins = len(trader_week[trader_week['result'] == 'Win'])
                    total = len(trader_week)
                    
                    # Calculate P&L for this week
                    week_pnl = 0
                    for _, trade in trader_week.iterrows():
                        if trade['result'] == 'Win':
                            week_pnl += trade['reward']
                        elif trade['result'] == 'Loss':
                            week_pnl -= trade['risk']
                    
                    weekly_stats_list.append({
                        'week': week,
                        'trader': trader,
                        'win_rate': (wins / total * 100) if total > 0 else 0,
                        'rrRatio': trader_week['rrRatio'].mean(),
                        'trade_count': total,
                        'pnl': week_pnl
                    })
        
        weekly_stats = pd.DataFrame(weekly_stats_list)
        
        # Chart 1: Win Rate Over Time
        st.markdown("#### 📊 Win Rate Trend")
        fig_winrate = px.line(weekly_stats, x='week', y='win_rate', color='trader',
                             title=f'Win Rate Over Time - {selected_pair}',
                             labels={'win_rate': 'Win Rate %', 'week': 'Week'},
                             markers=True)
        fig_winrate.update_layout(height=400)
        st.plotly_chart(fig_winrate, use_container_width=True)
        
        # Chart 2: P&L Over Time
        st.markdown("#### 💰 Profit & Loss Trend")
        fig_pnl = px.line(weekly_stats, x='week', y='pnl', color='trader',
                         title=f'P&L Over Time - {selected_pair}',
                         labels={'pnl': 'P&L', 'week': 'Week'},
                         markers=True)
        fig_pnl.update_layout(height=400)
        st.plotly_chart(fig_pnl, use_container_width=True)
        
        # Chart 3: R:R Ratio Over Time
        st.markdown("#### ⚖️ Risk-Reward Ratio Trend")
        fig_rr = px.line(weekly_stats, x='week', y='rrRatio', color='trader',
                        title=f'Risk-Reward Ratio Over Time - {selected_pair}',
                        labels={'rrRatio': 'R:R Ratio', 'week': 'Week'},
                        markers=True)
        fig_rr.update_layout(height=400)
        st.plotly_chart(fig_rr, use_container_width=True)
        
        # Chart 4: Trade Frequency
        st.markdown("#### 📈 Trading Activity")
        fig_activity = px.bar(weekly_stats, x='week', y='trade_count', color='trader',
                             title=f'Trading Activity - {selected_pair}',
                             labels={'trade_count': 'Number of Trades', 'week': 'Week'})
        fig_activity.update_layout(height=400, barmode='group')
        st.plotly_chart(fig_activity, use_container_width=True)

    # Individual Trade Analysis
    st.markdown("### 🔍 Individual Trade Analysis")
    
    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        show_results = st.multiselect("Filter by Result", 
                                     options=['Open', 'Win', 'Loss', 'Breakeven'],
                                     default=['Open', 'Win', 'Loss', 'Breakeven'])
    with detail_col2:
        sort_by = st.selectbox("Sort Trades By", 
                             options=['date', 'rrRatio', 'risk'], 
                             format_func=lambda x: x.replace('rrRatio', 'R:R Ratio').title())

    # Filter detailed view
    detailed_view = filtered_df[filtered_df['result'].isin(show_results)].sort_values(sort_by, ascending=False)
    
    if len(detailed_view) > 0:
        display_columns = ['date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                         'rrRatio', 'outcome', 'result']
        st.dataframe(detailed_view[display_columns], use_container_width=True)
        
        # Trade distribution
        st.markdown("#### 📋 Trade Distribution")
        dist_col1, dist_col2 = st.columns(2)
        
        with dist_col1:
            trader_dist = detailed_view['trader'].value_counts()
            fig_trader = px.pie(values=trader_dist.values, names=trader_dist.index,
                               title='Trade Distribution by Trader')
            st.plotly_chart(fig_trader, use_container_width=True)
        
        with dist_col2:
            result_dist = detailed_view['result'].value_counts()
            fig_result = px.pie(values=result_dist.values, names=result_dist.index,
                                title='Trade Distribution by Result',
                                color_discrete_map={'Win': '#10b981', 'Loss': '#ef4444', 'Open': '#3b82f6', 'Breakeven': '#6b7280'})
            st.plotly_chart(fig_result, use_container_width=True)
    else:
        st.info("No trades match the detailed view filters")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>The War Zone</strong> • Pair Analysis • Compare trader performance on specific instruments
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**📊 How to use this page:**

1. **Select a trading pair** to analyze
2. **Choose traders** to compare  
3. **Pick a time period** for analysis
4. **View performance metrics** and trends

Charts update automatically when filters change.
""")
