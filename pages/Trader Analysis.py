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
        # Enhanced fallback data with more time points for better charts
        return [
            # Week 1
            {'id': 1, 'date': '2024-01-15', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.5, 'sl': 1815.0, 'target': 1830.0, 'risk': 5.5, 'reward': 9.5, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 2, 'date': '2024-01-14', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.3, 'sl': 88.5, 'target': 91.0, 'risk': 0.8, 'reward': 1.7, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss'},
            {'id': 3, 'date': '2024-01-13', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.0, 'sl': 27200.0, 'target': 27800.0, 'risk': 250.0, 'reward': 350.0, 'rrRatio': 1.4, 'outcome': 'Open', 'result': 'Open'},
            
            # Week 2
            {'id': 4, 'date': '2024-01-08', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.0625, 'sl': 1.06, 'target': 1.067, 'risk': 0.0025, 'reward': 0.0045, 'rrRatio': 1.8, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 5, 'date': '2024-01-07', 'trader': 'Wallace', 'instrument': 'US30', 'entry': 34500.0, 'sl': 34200.0, 'target': 34900.0, 'risk': 300.0, 'reward': 400.0, 'rrRatio': 1.33, 'outcome': 'Open', 'result': 'Open'},
            {'id': 6, 'date': '2024-01-06', 'trader': 'Max', 'instrument': 'XAUUSD', 'entry': 1835.0, 'sl': 1828.0, 'target': 1845.0, 'risk': 7.0, 'reward': 10.0, 'rrRatio': 1.43, 'outcome': 'Target Hit', 'result': 'Win'},
            
            # Week 3
            {'id': 7, 'date': '2024-01-01', 'trader': 'Waithaka', 'instrument': 'BTCUSD', 'entry': 42000.0, 'sl': 41500.0, 'target': 43000.0, 'risk': 500.0, 'reward': 1000.0, 'rrRatio': 2.0, 'outcome': 'SL Hit', 'result': 'Loss'},
            {'id': 8, 'date': '2023-12-28', 'trader': 'Wallace', 'instrument': 'EURUSD', 'entry': 1.0750, 'sl': 1.0720, 'target': 1.0800, 'risk': 0.0030, 'reward': 0.0050, 'rrRatio': 1.67, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 9, 'date': '2023-12-25', 'trader': 'Max', 'instrument': 'USOIL', 'entry': 92.5, 'sl': 91.5, 'target': 94.5, 'risk': 1.0, 'reward': 2.0, 'rrRatio': 2.0, 'outcome': 'SL Hit', 'result': 'Loss'},
            
            # Week 4
            {'id': 10, 'date': '2023-12-20', 'trader': 'Waithaka', 'instrument': 'US30', 'entry': 34800.0, 'sl': 34600.0, 'target': 35200.0, 'risk': 200.0, 'reward': 400.0, 'rrRatio': 2.0, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 11, 'date': '2023-12-18', 'trader': 'Wallace', 'instrument': 'XAUUSD', 'entry': 1850.0, 'sl': 1840.0, 'target': 1870.0, 'risk': 10.0, 'reward': 20.0, 'rrRatio': 2.0, 'outcome': 'Target Hit', 'result': 'Win'},
            {'id': 12, 'date': '2023-12-15', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 41000.0, 'sl': 40500.0, 'target': 42000.0, 'risk': 500.0, 'reward': 1000.0, 'rrRatio': 2.0, 'outcome': 'Target Hit', 'result': 'Win'}
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
df = pd.DataFrame(trades_data)

# Convert date column
df['date'] = pd.to_datetime(df['date'])

# Sidebar Filters
st.sidebar.markdown("### 🔧 Analysis Filters")

# Trader selection
available_traders = sorted(df['trader'].unique())
selected_traders = st.sidebar.multiselect(
    "👥 Select Traders to Compare",
    options=available_traders,
    default=available_traders,
    help="Choose 1, 2, or all 3 traders to compare"
)

# Date range selection
min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Time aggregation
time_grouping = st.sidebar.selectbox(
    "📊 Time Aggregation",
    options=['Daily', 'Weekly', 'Monthly'],
    index=1,
    help="Group data by day, week, or month for trends"
)

# Chart type selection
chart_types = st.sidebar.multiselect(
    "📈 Show Charts",
    options=['Target Hits vs Stop Losses', 'Number of Trades', 'Win Rate Trend', 'R:R Ratio Trend'],
    default=['Target Hits vs Stop Losses', 'Number of Trades'],
    help="Select which charts to display"
)

# Apply filters
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter data based on selections
filtered_df = df[
    (df['trader'].isin(selected_traders)) &
    (df['date'].dt.date >= start_date) &
    (df['date'].dt.date <= end_date)
]

# Main content
if len(filtered_df) == 0:
    st.warning("No trade data available for the selected filters. Please adjust your selection.")
else:
    # Overview metrics
    st.markdown("### 📊 Overall Performance Summary")
    
    # Calculate overall stats
    total_trades = len(filtered_df)
    closed_trades = filtered_df[filtered_df['outcome'].isin(['Target Hit', 'SL Hit'])]
    target_hits = closed_trades[closed_trades['outcome'] == 'Target Hit']
    stop_losses = closed_trades[closed_trades['outcome'] == 'SL Hit']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Target Hits", len(target_hits))
    with col3:
        st.metric("Stop Losses", len(stop_losses))
    with col4:
        win_rate = (len(target_hits) / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")

    # Trader Leaderboard
    st.markdown("### 🏆 Trader Performance Leaderboard")
    
    trader_stats = []
    for trader in selected_traders:
        trader_data = filtered_df[filtered_df['trader'] == trader]
        trader_closed = trader_data[trader_data['outcome'].isin(['Target Hit', 'SL Hit'])]
        trader_targets = trader_closed[trader_closed['outcome'] == 'Target Hit']
        trader_stops = trader_closed[trader_closed['outcome'] == 'SL Hit']
        
        stats = {
            'Trader': trader,
            'Total Trades': len(trader_data),
            'Target Hits': len(trader_targets),
            'Stop Losses': len(trader_stops),
            'Win Rate %': (len(trader_targets) / len(trader_closed) * 100) if len(trader_closed) > 0 else 0,
            'Avg R:R Ratio': trader_closed['rrRatio'].mean() if len(trader_closed) > 0 else 0,
            'Success Ratio': (len(trader_targets) / len(trader_stops)) if len(trader_stops) > 0 else len(trader_targets)
        }
        trader_stats.append(stats)
    
    leaderboard_df = pd.DataFrame(trader_stats).sort_values('Win Rate %', ascending=False)
    
    # Display leaderboard with progress bars
    for i, (_, trader) in enumerate(leaderboard_df.iterrows()):
        win_rate = trader['Win Rate %']
        target_hits = trader['Target Hits']
        stop_losses = trader['Stop Losses']
        total_closed = target_hits + stop_losses
        
        win_rate_color = "#10b981" if win_rate >= 50 else "#ef4444"
        
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
                    <strong style="color: {win_rate_color}; font-size: 1.2rem;">
                        {win_rate:.1f}% Win Rate
                    </strong>
                    <div style="font-size: 0.9rem; color: #666;">
                        🎯 {target_hits} Targets • ⚠️ {stop_losses} Stops
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
        # Prepare time-based data
        time_data = filtered_df.copy()
        
        # Set time grouping
        if time_grouping == 'Daily':
            time_data['time_period'] = time_data['date'].dt.date
            time_label = 'Day'
        elif time_grouping == 'Weekly':
            time_data['time_period'] = time_data['date'].dt.to_period('W').dt.start_time
            time_label = 'Week'
        else:  # Monthly
            time_data['time_period'] = time_data['date'].dt.to_period('M').dt.start_time
            time_label = 'Month'
        
        # Create aggregated data for charts
        chart_data = []
        for trader in selected_traders:
            trader_data = time_data[time_data['trader'] == trader]
            
            for period in sorted(trader_data['time_period'].unique()):
                period_data = trader_data[trader_data['time_period'] == period]
                closed_trades_period = period_data[period_data['outcome'].isin(['Target Hit', 'SL Hit'])]
                
                stats = {
                    'Trader': trader,
                    'Time Period': period,
                    'Total Trades': len(period_data),
                    'Target Hits': len(closed_trades_period[closed_trades_period['outcome'] == 'Target Hit']),
                    'Stop Losses': len(closed_trades_period[closed_trades_period['outcome'] == 'SL Hit']),
                    'Win Rate': (len(closed_trades_period[closed_trades_period['outcome'] == 'Target Hit']) / len(closed_trades_period) * 100) if len(closed_trades_period) > 0 else 0,
                    'Avg R:R': closed_trades_period['rrRatio'].mean() if len(closed_trades_period) > 0 else 0
                }
                chart_data.append(stats)
        
        chart_df = pd.DataFrame(chart_data)
        
        # Display selected charts
        if 'Target Hits vs Stop Losses' in chart_types and not chart_df.empty:
            st.markdown(f"#### 🎯 Target Hits vs Stop Losses Over Time ({time_label}ly)")
            
            # Create line chart for targets vs stops
            fig_targets_stops = go.Figure()
            
            for trader in selected_traders:
                trader_data = chart_df[chart_df['Trader'] == trader]
                
                # Target hits line
                fig_targets_stops.add_trace(go.Scatter(
                    x=trader_data['Time Period'],
                    y=trader_data['Target Hits'],
                    name=f'{trader} - Targets',
                    mode='lines+markers',
                    line=dict(width=3)
                ))
                
                # Stop losses line (dashed)
                fig_targets_stops.add_trace(go.Scatter(
                    x=trader_data['Time Period'],
                    y=trader_data['Stop Losses'],
                    name=f'{trader} - Stops',
                    mode='lines+markers',
                    line=dict(dash='dash', width=2)
                ))
            
            fig_targets_stops.update_layout(
                title=f'Target Hits vs Stop Losses by {time_label}',
                xaxis_title=time_label,
                yaxis_title='Number of Trades',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_targets_stops, use_container_width=True)
        
        if 'Number of Trades' in chart_types and not chart_df.empty:
            st.markdown(f"#### 📊 Trading Activity ({time_label}ly)")
            
            # Bar chart for number of trades
            fig_activity = px.bar(chart_df, x='Time Period', y='Total Trades', color='Trader',
                                 title=f'Trading Activity by {time_label}',
                                 labels={'Total Trades': 'Number of Trades', 'Time Period': time_label},
                                 barmode='group')
            fig_activity.update_layout(height=400)
            st.plotly_chart(fig_activity, use_container_width=True)
        
        if 'Win Rate Trend' in chart_types and not chart_df.empty:
            st.markdown(f"#### 📈 Win Rate Trend ({time_label}ly)")
            
            # Line chart for win rate
            fig_winrate = px.line(chart_df, x='Time Period', y='Win Rate', color='Trader',
                                 title=f'Win Rate Trend by {time_label}',
                                 labels={'Win Rate': 'Win Rate %', 'Time Period': time_label},
                                 markers=True)
            fig_winrate.update_layout(height=400)
            st.plotly_chart(fig_winrate, use_container_width=True)
        
        if 'R:R Ratio Trend' in chart_types and not chart_df.empty:
            st.markdown(f"#### ⚖️ Risk-Reward Ratio Trend ({time_label}ly)")
            
            # Line chart for R:R ratio
            fig_rr = px.line(chart_df, x='Time Period', y='Avg R:R', color='Trader',
                            title=f'Risk-Reward Ratio Trend by {time_label}',
                            labels={'Avg R:R': 'Average R:R Ratio', 'Time Period': time_label},
                            markers=True)
            fig_rr.update_layout(height=400)
            st.plotly_chart(fig_rr, use_container_width=True)
    
    # Detailed Trade View
    st.markdown("### 🔍 Detailed Trade Analysis")
    
    # Additional filters for detailed view
    detail_col1, detail_col2, detail_col3 = st.columns(3)
    with detail_col1:
        show_instruments = st.multiselect("Filter by Instrument", 
                                        options=filtered_df['instrument'].unique(),
                                        default=filtered_df['instrument'].unique())
    with detail_col2:
        show_outcomes = st.multiselect("Filter by Outcome", 
                                     options=['Open', 'Target Hit', 'SL Hit'],
                                     default=['Open', 'Target Hit', 'SL Hit'])
    with detail_col3:
        sort_by = st.selectbox("Sort Trades By", 
                             options=['date', 'rrRatio', 'risk', 'reward'], 
                             format_func=lambda x: x.replace('rrRatio', 'R:R Ratio').title())
    
    # Apply detailed filters
    detailed_view = filtered_df[
        (filtered_df['instrument'].isin(show_instruments)) &
        (filtered_df['outcome'].isin(show_outcomes))
    ].sort_values(sort_by, ascending=False)
    
    if len(detailed_view) > 0:
        # Display detailed trades
        display_columns = ['date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                         'rrRatio', 'outcome', 'result']
        st.dataframe(detailed_view[display_columns], use_container_width=True)
    else:
        st.info("No trades match the detailed view filters")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>The War Zone</strong> • Trader Performance Analysis • Track progress and compare performance over time
</div>
""", unsafe_allow_html=True)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("""
**📊 Chart Guide:**

- **Target Hits vs Stop Losses**: Line chart comparing successful vs unsuccessful trades
- **Number of Trades**: Bar chart showing trading activity
- **Win Rate Trend**: How win percentage changes over time
- **R:R Ratio Trend**: Risk-reward ratio evolution

**💡 Tip**: Use different time aggregations (Daily/Weekly/Monthly) to see different patterns!
""")
