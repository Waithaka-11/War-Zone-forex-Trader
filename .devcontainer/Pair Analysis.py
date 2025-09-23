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
        border-left: 4px solid #10b981;
    }
    .instrument-card {
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8fafc;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
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
    <h1 style="color: white; margin: 0; text-align: center;">📊 Instrument Pair Analysis</h1>
    <p style="color: #e2e8f0; text-align: center; margin: 0.5rem 0 0 0;">Analyze performance by trading instrument, compare pairs, and identify opportunities</p>
</div>
""", unsafe_allow_html=True)

# Load data
trades_data = load_trades_data()
df = pd.DataFrame(trades_data)

# Convert date column
df['date'] = pd.to_datetime(df['date'])

# Date and instrument filter
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
with col3:
    selected_instruments = st.multiselect("Filter Instruments", 
                                        options=df['instrument'].unique(), 
                                        default=df['instrument'].unique())

# Filter data
filtered_df = df[
    (df['date'].dt.date >= start_date) & 
    (df['date'].dt.date <= end_date) &
    (df['instrument'].isin(selected_instruments))
]

# Overall metrics
st.markdown("### 📈 Instrument Performance Overview")

if len(filtered_df) > 0:
    # Calculate instrument statistics
    instrument_stats = []
    for instrument in selected_instruments:
        inst_trades = filtered_df[filtered_df['instrument'] == instrument]
        inst_closed = inst_trades[inst_trades['outcome'].isin(['Target Hit', 'SL Hit'])]
        inst_wins = inst_closed[inst_closed['result'] == 'Win']
        
        stats = {
            'Instrument': instrument,
            'Total Trades': len(inst_trades),
            'Closed Trades': len(inst_closed),
            'Wins': len(inst_wins),
            'Losses': len(inst_closed) - len(inst_wins),
            'Win Rate': (len(inst_wins) / len(inst_closed) * 100) if len(inst_closed) > 0 else 0,
            'Avg R:R': inst_closed['rrRatio'].mean() if len(inst_closed) > 0 else 0,
            'Total P&L': (inst_wins['reward'].sum() - 
                         inst_closed[inst_closed['result'] == 'Loss']['risk'].sum()),
            'Avg Risk': inst_trades['risk'].mean(),
            'Avg Reward': inst_trades['reward'].mean()
        }
        instrument_stats.append(stats)
    
    stats_df = pd.DataFrame(instrument_stats).sort_values('Win Rate', ascending=False)
    
    # Display top metrics
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        total_inst_trades = stats_df['Total Trades'].sum()
        st.metric("Total Trades", total_inst_trades)
    with mcol2:
        avg_win_rate = stats_df['Win Rate'].mean()
        st.metric("Avg Win Rate", f"{avg_win_rate:.1f}%")
    with mcol3:
        best_instrument = stats_df.iloc[0]['Instrument'] if len(stats_df) > 0 else "N/A"
        st.metric("Best Performer", best_instrument)
    with mcol4:
        total_pnl = stats_df['Total P&L'].sum()
        st.metric("Total P&L", f"{total_pnl:+.2f}")

    # Instrument Leaderboard
    st.markdown("### 🏆 Instrument Performance Ranking")
    
    for i, (_, instrument) in enumerate(stats_df.iterrows()):
        win_rate_color = "#10b981" if instrument['Win Rate'] >= 50 else "#ef4444"
        pnl_color = "#10b981" if instrument['Total P&L'] >= 0 else "#ef4444"
        
        st.markdown(f"""
        <div class="instrument-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center;">
                    <div style="background: {'#fbbf24' if i == 0 else '#9ca3af' if i == 1 else '#fb923c' if i == 2 else '#3b82f6'}; 
                                color: white; width: 30px; height: 30px; border-radius: 50%; 
                                display: flex; align-items: center; justify-content: center; 
                                font-weight: bold; margin-right: 1rem;">
                        {i+1}
                    </div>
                    <div>
                        <strong style="font-size: 1.1rem;">{instrument['Instrument']}</strong>
                        <div style="font-size: 0.9rem; color: #666;">
                            {instrument['Total Trades']} trades • {instrument['Closed Trades']} closed
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <strong style="color: {win_rate_color}; font-size: 1.1rem;">
                        {instrument['Win Rate']:.1f}% Win Rate
                    </strong>
                    <div style="font-size: 0.9rem; color: {pnl_color};">
                        P&L: {instrument['Total P&L']:+.2f} • R:R: {instrument['Avg R:R']:.2f}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Charts section
    st.markdown("### 📊 Performance Visualization")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Win Rate by Instrument
        fig = px.bar(stats_df, x='Instrument', y='Win Rate', 
                    title='Win Rate by Instrument', color='Win Rate',
                    color_continuous_scale='Viridis')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_col2:
        # P&L by Instrument
        fig = px.bar(stats_df, x='Instrument', y='Total P&L', 
                    title='Total P&L by Instrument', color='Total P&L',
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)

    # Trader vs Instrument Heatmap
    st.markdown("### 🔥 Trader Performance Heatmap")
    
    # Create pivot table for heatmap
    heatmap_data = filtered_df.pivot_table(
        index='trader', 
        columns='instrument', 
        values='rrRatio', 
        aggfunc='mean',
        fill_value=0
    )
    
    if not heatmap_data.empty:
        fig = px.imshow(heatmap_data, 
                       title='Average R:R Ratio by Trader and Instrument',
                       color_continuous_scale='RdYlGn',
                       aspect='auto')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for heatmap visualization")

    # Detailed Trade Comparison
    st.markdown("### 🔍 Detailed Trade Analysis")
    
    # Comparison filters
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        compare_instruments = st.multiselect("Compare Instruments", 
                                           options=selected_instruments, 
                                           default=selected_instruments[:min(3, len(selected_instruments))])
    with fcol2:
        compare_traders = st.multiselect("Filter by Traders", 
                                       options=filtered_df['trader'].unique(), 
                                       default=filtered_df['trader'].unique())
    with fcol3:
        sort_by = st.selectbox("Sort Trades By", 
                             options=['date', 'rrRatio', 'risk', 'reward'], 
                             format_func=lambda x: x.replace('rrRatio', 'R:R Ratio').title())

    # Filter comparison data
    detailed_df = filtered_df[
        (filtered_df['instrument'].isin(compare_instruments)) &
        (filtered_df['trader'].isin(compare_traders))
    ].sort_values(sort_by, ascending=False)

    # Display detailed table
    if len(detailed_df) > 0:
        display_cols = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                       'rrRatio', 'outcome', 'result']
        st.dataframe(detailed_df[display_cols], use_container_width=True)
        
        # Additional visualizations
        st.markdown("#### Trade Distribution Analysis")
        dist_col1, dist_col2 = st.columns(2)
        
        with dist_col1:
            fig = px.pie(detailed_df, names='instrument', title='Trade Distribution by Instrument')
            st.plotly_chart(fig, use_container_width=True)
        
        with dist_col2:
            # Risk-Reward scatter plot
            fig = px.scatter(detailed_df, x='risk', y='reward', color='instrument',
                           size='rrRatio', hover_data=['trader', 'outcome'],
                           title='Risk vs Reward Analysis')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trades match the selected filters.")

    # Performance Over Time
    st.markdown("### 📅 Performance Timeline")
    
    # Weekly performance
    weekly_data = filtered_df.copy()
    weekly_data['week'] = weekly_data['date'].dt.to_period('W').dt.start_time
    weekly_stats = weekly_data.groupby('week').agg({
        'rrRatio': 'mean',
        'outcome': lambda x: (x == 'Target Hit').mean() * 100
    }).reset_index()

    if len(weekly_stats) > 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weekly_stats['week'], y=weekly_stats['rrRatio'],
                               name='Avg R:R Ratio', line=dict(color='#3b82f6')))
        fig.add_trace(go.Scatter(x=weekly_stats['week'], y=weekly_stats['outcome'],
                               name='Win Rate %', yaxis='y2', line=dict(color='#10b981')))
        
        fig.update_layout(
            title='Weekly Performance Trends',
            xaxis_title='Week',
            yaxis_title='Average R:R Ratio',
            yaxis2=dict(title='Win Rate %', overlaying='y', side='right'),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No trade data available for the selected filters.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <strong>The War Zone</strong> • Instrument Pair Analysis • Real-time market insights
</div>
""", unsafe_allow_html=True)
