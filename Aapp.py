import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Forex Trading Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background-color: #475569;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .trader-rank {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: #f8fafc;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for trades
if 'trades' not in st.session_state:
    st.session_state.trades = [
        {
            'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD',
            'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50,
            'reward': 9.50, 'rr_ratio': 1.73, 'outcome': 'Target Hit', 'result': 'Win'
        },
        {
            'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL',
            'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80,
            'reward': 1.70, 'rr_ratio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss'
        },
        {
            'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD',
            'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00,
            'reward': 350.00, 'rr_ratio': 1.40, 'outcome': 'Target Hit', 'result': 'Win'
        },
        {
            'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD',
            'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250,
            'reward': 0.00450, 'rr_ratio': 1.80, 'outcome': 'Target Hit', 'result': 'Win'
        }
    ]

# Header
st.markdown("""
<div class="main-header">
    <h1>📈 Forex Trading Analytics</h1>
    <p>Professional Trading Performance Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for adding new trades
st.sidebar.header("➕ Add New Trade")

with st.sidebar.form("add_trade_form"):
    trader = st.selectbox("Trader", ["", "Waithaka", "Wallace", "Max"])
    
    instrument_pairs = ['XAUUSD', 'USOIL', 'BTCUSD', 'USTECH', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD', 'NZDUSD']
    instrument = st.selectbox("Instrument", [""] + instrument_pairs)
    
    trade_date = st.date_input("Date", value=date.today())
    outcome = st.selectbox("Outcome", ["", "Target Hit", "SL Hit"])
    
    entry_price = st.number_input("Entry Price", value=0.0, step=0.001, format="%.4f")
    sl_price = st.number_input("Stop Loss (SL)", value=0.0, step=0.001, format="%.4f")
    target_price = st.number_input("Target Price", value=0.0, step=0.001, format="%.4f")
    
    submitted = st.form_submit_button("Add Trade")
    
    if submitted and trader and instrument and outcome and entry_price and sl_price and target_price:
        risk = abs(entry_price - sl_price)
        reward = abs(target_price - entry_price)
        rr_ratio = reward / risk if risk != 0 else 0
        result = "Win" if outcome == "Target Hit" else "Loss"
        
        new_trade = {
            'id': len(st.session_state.trades) + 1,
            'date': trade_date.strftime('%Y-%m-%d'),
            'trader': trader,
            'instrument': instrument,
            'entry': entry_price,
            'sl': sl_price,
            'target': target_price,
            'risk': risk,
            'reward': reward,
            'rr_ratio': round(rr_ratio, 2),
            'outcome': outcome,
            'result': result
        }
        
        st.session_state.trades.append(new_trade)
        st.success("Trade added successfully!")
        st.rerun()

# Convert trades to DataFrame
df = pd.DataFrame(st.session_state.trades)

# Calculate trader statistics
trader_stats = df.groupby('trader').agg({
    'result': ['count', lambda x: (x == 'Win').sum()],
    'rr_ratio': 'mean'
}).round(2)

trader_stats.columns = ['total_trades', 'wins', 'avg_rr']
trader_stats['losses'] = trader_stats['total_trades'] - trader_stats['wins']
trader_stats['win_rate'] = (trader_stats['wins'] / trader_stats['total_trades'] * 100).round(1)
trader_stats = trader_stats.sort_values('win_rate', ascending=False)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Trader Performance Rankings
    st.subheader("🏆 Trader Performance Rankings")
    
    rank_colors = ["🥇", "🥈", "🥉"]
    for i, (trader, stats) in enumerate(trader_stats.iterrows()):
        rank_icon = rank_colors[i] if i < 3 else f"{i+1}."
        
        with st.container():
            st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #3b82f6;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 1rem;">{rank_icon}</span>
                    <div>
                        <strong style="font-size: 1.2rem;">{trader}</strong>
                        <span style="margin-left: 2rem; color: #4ade80; font-weight: bold;">Win Rate: {stats['win_rate']}%</span>
                    </div>
                </div>
                <div style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    Total Trades: {stats['total_trades']} | Wins: {stats['wins']} | Losses: {stats['losses']}
                </div>
                <div style="background-color: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background-color: #10b981; height: 100%; width: {stats['win_rate']}%; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Trading History Table
    st.subheader("📊 Trading History")
    
    # Add delete functionality
    if st.button("🗑️ Delete Selected Trades"):
        st.session_state.show_delete = True
    
    if hasattr(st.session_state, 'show_delete') and st.session_state.show_delete:
        trades_to_delete = st.multiselect(
            "Select trades to delete:",
            options=range(len(st.session_state.trades)),
            format_func=lambda x: f"Trade {st.session_state.trades[x]['id']}: {st.session_state.trades[x]['trader']} - {st.session_state.trades[x]['instrument']}"
        )
        
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            if st.button("Confirm Delete", type="primary"):
                for idx in sorted(trades_to_delete, reverse=True):
                    st.session_state.trades.pop(idx)
                st.session_state.show_delete = False
                st.success("Selected trades deleted!")
                st.rerun()
        
        with col_del2:
            if st.button("Cancel"):
                st.session_state.show_delete = False
                st.rerun()
    
    # Display trades table
    if df.empty:
        st.info("No trades recorded yet. Add a trade using the sidebar.")
    else:
        # Format the dataframe for display
        display_df = df.copy()
        display_df['Result'] = display_df['result'].apply(
            lambda x: '✅ Win' if x == 'Win' else '❌ Loss'
        )
        
        st.dataframe(
            display_df[['date', 'trader', 'instrument', 'entry', 'sl', 'target', 'risk', 'reward', 'rr_ratio', 'outcome', 'Result']].rename(columns={
                'date': 'Date',
                'trader': 'Trader',
                'instrument': 'Instrument',
                'entry': 'Entry',
                'sl': 'SL',
                'target': 'Target',
                'risk': 'Risk',
                'reward': 'Reward',
                'rr_ratio': 'R/R Ratio',
                'outcome': 'Outcome'
            }),
            use_container_width=True,
            hide_index=True
        )

with col2:
    # Performance Metrics - Donut Chart
    st.subheader("📈 Performance Metrics")
    
    if not trader_stats.empty:
        # Create donut chart
        fig_donut = go.Figure(data=[go.Pie(
            labels=trader_stats.index,
            values=trader_stats['win_rate'],
            hole=0.4,
            marker_colors=['#f59e0b', '#3b82f6', '#6b7280']
        )])
        
        fig_donut.update_layout(
            title="Win Rate Distribution",
            height=300,
            showlegend=True,
            annotations=[dict(text=f'{trader_stats["win_rate"].mean():.1f}%<br>Avg Rate', 
                             x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
        
        # Win rate breakdown
        st.markdown("**Win Rate Breakdown:**")
        for trader, stats in trader_stats.iterrows():
            st.metric(
                label=trader,
                value=f"{stats['win_rate']}%",
                delta=f"{stats['total_trades']} trades"
            )
    
    # Trader of the Month
    st.subheader("🏆 Trader of the Month")
    if not trader_stats.empty:
        best_trader = trader_stats.index[0]
        best_rate = trader_stats.iloc[0]['win_rate']
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background-color: #f0fdf4; border-radius: 1rem; border: 2px solid #22c55e;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🏆</div>
            <h3 style="color: #15803d; margin-bottom: 0.5rem;">{best_trader}</h3>
            <p style="color: #6b7280; margin-bottom: 1rem;">Best performance this month</p>
            <div style="background-color: #dcfce7; padding: 1rem; border-radius: 0.5rem;">
                <div style="font-size: 0.8rem; color: #16a34a; font-weight: bold;">WIN RATE THIS MONTH</div>
                <div style="font-size: 2rem; font-weight: bold; color: #15803d;">{best_rate}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Instrument Performance
    st.subheader("📊 Instrument Performance")
    
    if not df.empty:
        instrument_performance = df.groupby(['instrument', 'trader']).agg({
            'result': lambda x: (x == 'Win').sum() / len(x) * 100
        }).round(1)
        
        # Create a pivot table for better display
        pivot_table = instrument_performance.unstack(fill_value=0)
        pivot_table.columns = pivot_table.columns.droplevel(0)
        
        if not pivot_table.empty:
            # Display as heatmap
            fig_heatmap = px.imshow(
                pivot_table.values,
                labels=dict(x="Trader", y="Instrument", color="Win Rate %"),
                x=pivot_table.columns,
                y=pivot_table.index,
                color_continuous_scale="RdYlGn",
                aspect="auto"
            )
            
            fig_heatmap.update_layout(
                title="Win Rate by Instrument & Trader",
                height=300
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)

# Additional Analytics Section
st.subheader("📈 Additional Analytics")

col3, col4, col5 = st.columns(3)

with col3:
    if not df.empty:
        total_trades = len(df)
        total_wins = len(df[df['result'] == 'Win'])
        overall_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        
        st.metric(
            label="Overall Statistics",
            value=f"{overall_win_rate:.1f}%",
            delta=f"{total_trades} total trades"
        )

with col4:
    if not df.empty:
        avg_rr = df['rr_ratio'].mean()
        best_rr = df['rr_ratio'].max()
        
        st.metric(
            label="Risk/Reward Ratio",
            value=f"{avg_rr:.2f}",
            delta=f"Best: {best_rr:.2f}"
        )

with col5:
    if not df.empty:
        recent_trades = df.tail(5)
        recent_wins = len(recent_trades[recent_trades['result'] == 'Win'])
        recent_win_rate = (recent_wins / len(recent_trades) * 100) if len(recent_trades) > 0 else 0
        
        st.metric(
            label="Recent Performance",
            value=f"{recent_win_rate:.1f}%",
            delta=f"Last 5 trades"
        )

# Footer
st.markdown("---")
st.markdown("*Forex Trading Analytics Dashboard - Built with Streamlit*")
