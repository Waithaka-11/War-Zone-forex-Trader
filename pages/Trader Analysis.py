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
        margin: 0.5rem 0;
    }
    .trader-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .progress-bar {
        background: #e2e8f0;
        border-radius: 10px;
        height: 8px;
        margin: 0.5rem 0;
    }
    .progress-fill {
        background: #10b981;
        height: 100%;
        border-radius: 10px;
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
    <h1 style="color: white; margin: 0; text-align: center;">👤 Trader Performance Analysis</h1>
    <p style="color: #e2e8f0; text-align: center; margin: 0.5rem 0 0 0;">Compare trader performance, track progress over time, and analyze trading patterns</p>
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

available_traders = sorted(df['trader'].unique())
selected_traders = st.sidebar.multiselect(
    "👥 Select Traders to Compare",
    options=available_traders,
    default=available_traders,
    help="Choose traders to compare"
)

min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

time_grouping = st.sidebar.selectbox(
    "📊 Time Aggregation",
    options=['Daily', 'Weekly', 'Monthly'],
    index=1,
    help="Group data by day, week, or month"
)

chart_types = st.sidebar.multiselect(
    "📈 Show Charts",
    options=['Wins vs Losses', 'Number of Trades', 'Win Rate Trend', 'P&L Trend', 'R:R Ratio Trend'],
    default=['Wins vs Losses', 'Number of Trades', 'P&L Trend'],
    help="Select which charts to display"
)

# Apply filters
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df['trader'].isin(selected_traders)) &
    (df['date'].dt.date >= start_date) &
    (df['date'].dt.date <= end_date)
]

# Main content
if len(filtered_df) == 0:
    st.warning("No trade data available for the selected filters.")
else:
    # Overview metrics
    st.markdown("### 📊 Overall Performance Summary")
    
    total_trades = len(filtered_df)
    closed_trades = filtered_df[filtered_df['result'].isin(['Win', 'Loss', 'Breakeven'])]
    winning_trades = closed_trades[closed_trades['result'] == 'Win']
    losing_trades = closed_trades[closed_trades['result'] == 'Loss']
    
    # Calculate total P&L
    total_pnl = 0
    for _, trade in closed_trades.iterrows():
        if trade['result'] == 'Win':
            total_pnl += trade['reward']
        elif trade['result'] == 'Loss':
            total_pnl -= trade['risk']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Winning Trades", len(winning_trades))
    with col3:
        st.metric("Losing Trades", len(losing_trades))
    with col4:
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col5:
        st.metric("Total P&L", f"{total_pnl:+.2f}", delta_color="normal")

    # Trader Leaderboard
    st.markdown("### 🏆 Trader Performance Leaderboard")
    
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
            'Wins': len(trader_wins),
            'Losses': len(trader_losses),
            'Win Rate %': (len(trader_wins) / len(trader_closed) * 100) if len(trader_closed) > 0 else 0,
            'P&L': trader_pnl,
            'Avg R:R Ratio': trader_closed['rrRatio'].mean() if len(trader_closed) > 0 else 0
        }
        trader_stats.append(stats)
    
    leaderboard_df = pd.DataFrame(trader_stats).sort_values('P&L', ascending=False)
    
    # Display leaderboard
    for i, (_, trader) in enumerate(leaderboard_df.iterrows()):
        win_rate = trader['Win Rate %']
        wins = trader['Wins']
        losses = trader['Losses']
        pnl = trader['P&L']
        total_closed = wins + losses
        
        win_rate_color = "#10b981" if win_rate >= 50 else "#ef4444"
        pnl_color = "#10b981" if pnl >= 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="trader-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center;">
                    <div style="background: {'#fbbf24' if i == 0 else '#9ca3af' if i == 1 else '#fb923c' if i == 2 else '#3b82f6'}; 
                                color: white; width: 35px; height: 35px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; 
                                font-weight: bold; margin-right: 1rem; font-size: 1.1rem;">
                        {i+1}
                    </div>
                    <div>
                        <strong style="font-size: 1.2rem;">{trader['Trader']}</strong>
                        <div style="font-size: 0.9rem; color: #666;">
                            {trader['Total Trades']} total trades • {total_closed} closed
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <strong style="color: {pnl_color}; font-size: 1.3rem;">
                        {pnl:+.2f}
                    </strong>
                    <div style="font-size: 0.9rem; color: {win_rate_color};">
                        {win_rate:.1f}% Win Rate • ✅ {wins} Wins • ❌ {losses} Losses
                    </div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {win_rate}%; background: {win_rate_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Progress Over Time Charts
    st.markdown("### 📈 Progress Over Time Analysis")
    
    if len(selected_traders) > 0 and len(chart_types) > 0:
        time_data = filtered_df.copy()
        
        if time_grouping == 'Daily':
            time_data['time_period'] = time_data['date'].dt.date
            time_label = 'Day'
        elif time_grouping == 'Weekly':
            time_data['time_period'] = time_data['date'].dt.to_period('W').dt.start_time
            time_label = 'Week'
        else:
            time_data['time_period'] = time_data['date'].dt.to_period('M').dt.start_time
            time_label = 'Month'
        
        chart_data = []
        for trader in selected_traders:
            trader_data = time_data[time_data['trader'] == trader]
            
            for period in sorted(trader_data['time_period'].unique()):
                period_data = trader_data[trader_data['time_period'] == period]
                closed_trades_period = period_data[period_data['result'].isin(['Win', 'Loss', 'Breakeven'])]
                
                # Calculate P&L for this period
                period_pnl = 0
                for _, trade in closed_trades_period.iterrows():
                    if trade['result'] == 'Win':
                        period_pnl += trade['reward']
                    elif trade['result'] == 'Loss':
                        period_pnl -= trade['risk']
                
                wins = len(closed_trades_period[closed_trades_period['result'] == 'Win'])
                losses = len(closed_trades_period[closed_trades_period['result'] == 'Loss'])
                
                stats = {
                    'Trader': trader,
                    'Time Period': period,
                    'Total Trades': len(period_data),
                    'Wins': wins,
                    'Losses': losses,
                    'Win Rate': (wins / len(closed_trades_period) * 100) if len(closed_trades_period) > 0 else 0,
                    'P&L': period_pnl,
                    'Avg R:R': closed_trades_period['rrRatio'].mean() if len(closed_trades_period) > 0 else 0
                }
                chart_data.append(stats)
        
        chart_df = pd.DataFrame(chart_data)
        
        # Display charts
        if 'Wins vs Losses' in chart_types and not chart_df.empty:
            st.markdown(f"#### ✅❌ Wins vs Losses Over Time ({time_label}ly)")
            
            fig_wins_losses = go.Figure()
            
            for trader in selected_traders:
                trader_data = chart_df[chart_df['Trader'] == trader]
                
                fig_wins_losses.add_trace(go.Scatter(
                    x=trader_data['Time Period'],
                    y=trader_data['Wins'],
                    name=f'{trader} - Wins',
                    mode='lines+markers',
                    line=dict(width=3)
                ))
                
                fig_wins_losses.add_trace(go.Scatter(
                    x=trader_data['Time Period'],
                    y=trader_data['Losses'],
                    name=f'{trader} - Losses',
                    mode='lines+markers',
                    line=dict(dash='dash', width=2)
                ))
            
            fig_wins_losses.update_layout(
                xaxis_title=time_label,
                yaxis_title='Number of Trades',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_wins_losses, use_container_width=True)
        
        if 'Number of Trades' in chart_types and not chart_df.empty:
            st.markdown(f"#### 📊 Trading Activity ({time_label}ly)")
            
            fig_activity = px.bar(chart_df, x='Time Period', y='Total Trades', color='Trader',
                                 title=f'Trading Activity by {time_label}',
                                 barmode='group')
            fig_activity.update_layout(height=400)
            st.plotly_chart(fig_activity, use_container_width=True)
        
        if 'Win Rate Trend' in chart_types and not chart_df.empty:
            st.markdown(f"#### 📈 Win Rate Trend ({time_label}ly)")
            
            fig_winrate = px.line(chart_df, x='Time Period', y='Win Rate', color='Trader',
                                 markers=True)
            fig_winrate.update_layout(height=400, yaxis_title='Win Rate %')
            st.plotly_chart(fig_winrate, use_container_width=True)
        
        if 'P&L Trend' in chart_types and not chart_df.empty:
            st.markdown(f"#### 💰 Profit & Loss Trend ({time_label}ly)")
            
            fig_pnl = px.line(chart_df, x='Time Period', y='P&L', color='Trader',
                             markers=True)
            fig_pnl.update_layout(height=400, yaxis_title='P&L')
            st.plotly_chart(fig_pnl, use_container_width=True)
        
        if 'R:R Ratio Trend' in chart_types and not chart_df.empty:
            st.markdown(f"#### ⚖️ Risk-Reward Ratio Trend ({time_label}ly)")
            
            fig_rr = px.line(chart_df, x='Time Period', y='Avg R:R', color='Trader',
                            markers=True)
            fig_rr.update_layout(height=400, yaxis_title='Average R:R Ratio')
            st.plotly_chart(fig_rr, use_container_width=True)
    
    # Detailed Trade View
    st.markdown("### 🔍 Detailed Trade Analysis")
    
    detail_col1, detail_col2, detail_col3 = st.columns(3)
    with detail_col1:
        show_instruments = st.multiselect("Filter by Instrument", 
                                        options=filtered_df['instrument'].unique(),
                                        default=filtered_df['instrument'].unique())
    with detail_col2:
        show_results = st.multiselect("Filter by Result", 
                                     options=['Open', 'Win', 'Loss', 'Breakeven'],
                                     default=['Open', 'Win', 'Loss', 'Breakeven'])
    with detail_col3:
        sort_by = st.selectbox("Sort Trades By", 
                             options=['date', 'rrRatio', 'risk', 'reward'], 
                             format_func=lambda x: x.replace('rrRatio', 'R:R Ratio').title())
    
    detailed_view = filtered_df[
        (filtered_df['instrument'].isin(show_instruments)) &
        (filtered_df['result'].isin(show_results))
    ].sort_values(sort_by, ascending=False)
    
    if len(detailed_view) > 0:
        display_columns = ['date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                         'rrRatio', 'outcome', 'result']
        st.dataframe(detailed_view[display_columns], use_container_width=True)
    else:
        st.info("No trades match the detailed view filters")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>The War Zone</strong> • Trader Performance Analysis • Track progress and compare performance
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**📊 Chart Guide:**

- **Wins vs Losses**: Compare successful vs unsuccessful trades
- **Number of Trades**: Trading activity over time
- **Win Rate Trend**: Win percentage changes
- **P&L Trend**: Profit and loss evolution
- **R:R Ratio Trend**: Risk-reward ratio changes
""")
