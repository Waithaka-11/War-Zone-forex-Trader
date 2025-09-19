import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Forex Trading Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: white;
        background-color: #334155;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .section-header {
        background-color: #334155;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem 0.5rem 0 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sample data
trades_data = [
    {'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.50, 
     'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50, 'rrRatio': 1.73, 
     'outcome': 'Target Hit', 'result': 'Win'},
    {'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.30, 
     'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70, 'rrRatio': 2.13, 
     'outcome': 'SL Hit', 'result': 'Loss'},
    {'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.00, 
     'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00, 'rrRatio': 1.40, 
     'outcome': 'Target Hit', 'result': 'Win'},
    {'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.06250, 
     'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450, 'rrRatio': 1.80, 
     'outcome': 'Target Hit', 'result': 'Win'}
]

instrument_pairs = ['XAUUSD', 'USDOIL', 'BTCUSD', 'USTECH', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD', 'NZDUSD']

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = trades_data

if 'selected_instrument' not in st.session_state:
    st.session_state.selected_instrument = ''

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown('<div class="main-header"><span style="margin-right:10px">📊</span>Forex Trading Analytics</div>', unsafe_allow_html=True)

with col3:
    st.write("")
    dashboard, history, settings = st.columns(3)
    with dashboard:
        st.button("Dashboard", use_container_width=True)
    with history:
        st.button("History", use_container_width=True)
    with settings:
        st.button("Settings", use_container_width=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Add New Trade Section
    with st.expander("Add New Trade", expanded=True):
        st.markdown('<div class="section-header">Add New Trade</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            trader = st.selectbox("Trader", ["Select Trader", "Waithaka", "Wallace", "Max"])
        with col2:
            st.session_state.selected_instrument = st.text_input("Instrument", st.session_state.selected_instrument, placeholder="Enter Instrument")
            st.write("Quick select:")
            cols = st.columns(5)
            for i, pair in enumerate(instrument_pairs):
                with cols[i % 5]:
                    if st.button(pair, key=f"btn_{pair}"):
                        st.session_state.selected_instrument = pair
                        st.rerun()
        with col3:
            trade_date = st.date_input("Date", datetime.now())
        with col4:
            outcome = st.selectbox("Outcome", ["Select Outcome", "Target Hit", "SL Hit"])
        
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            entry_price = st.number_input("Entry Price", value=0.0, format="%.2f")
        with col6:
            stop_loss = st.number_input("Stop Loss (SL)", value=0.0, format="%.2f")
        with col7:
            target_price = st.number_input("Target Price", value=0.0, format="%.2f")
        with col8:
            st.write("")
            if st.button("Add Trade", use_container_width=True):
                new_trade = {
                    'id': len(st.session_state.trades) + 1,
                    'date': trade_date.strftime('%Y-%m-%d'),
                    'trader': trader if trader != "Select Trader" else "Unknown",
                    'instrument': st.session_state.selected_instrument,
                    'entry': entry_price,
                    'sl': stop_loss,
                    'target': target_price,
                    'risk': abs(entry_price - stop_loss),
                    'reward': abs(target_price - entry_price),
                    'rrRatio': round(abs(target_price - entry_price) / abs(entry_price - stop_loss), 2) if entry_price != stop_loss else 0,
                    'outcome': outcome if outcome != "Select Outcome" else "Pending",
                    'result': "Win" if outcome == "Target Hit" else "Loss" if outcome == "SL Hit" else "Pending"
                }
                st.session_state.trades.append(new_trade)
                st.success("Trade added successfully!")
                st.rerun()

    # Trading History
    st.markdown('<div class="section-header">Trading History</div>', unsafe_allow_html=True)
    trades_df = pd.DataFrame(st.session_state.trades)
    
    # Add delete functionality
    if not trades_df.empty:
        trades_df['Delete'] = False
        edited_df = st.data_editor(
            trades_df,
            column_config={
                "Delete": st.column_config.CheckboxColumn(
                    "Delete?",
                    help="Select trades to delete",
                    default=False,
                ),
                "result": st.column_config.SelectboxColumn(
                    "Result",
                    options=["Win", "Loss", "Pending"],
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        if st.button("Delete Selected Trades"):
            # Get indices of rows to delete
            delete_indices = edited_df[edited_df['Delete']].index
            if not delete_indices.empty:
                # Remove from session state
                st.session_state.trades = [trade for i, trade in enumerate(st.session_state.trades) if i not in delete_indices]
                st.success(f"Deleted {len(delete_indices)} trades")
                st.rerun()

with col2:
    # Performance Metrics
    st.markdown('<div class="section-header">Performance Metrics</div>', unsafe_allow_html=True)
    
    # Calculate win rates
    if not trades_df.empty:
        win_rates = trades_df.groupby('trader')['result'].apply(
            lambda x: (x == 'Win').sum() / len(x) * 100 if len(x) > 0 else 0
        ).round(1)
        
        # Create donut chart
        fig = go.Figure(data=[go.Pie(
            labels=win_rates.index,
            values=win_rates.values,
            hole=0.6,
            marker_colors=['#3b82f6', '#000000', '#eab308']
        )])
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display win rates
        for trader, rate in win_rates.items():
            st.metric(f"{trader} Win Rate", f"{rate}%")
    else:
        st.info("No trades to display metrics")

    # Trader of the Month
    st.markdown('<div class="section-header">Trader of the Month</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background-color: white; border-radius: 0.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
        <div style='font-size: 3rem; margin-bottom: 1rem;'>🏆</div>
        <h3 style='margin-bottom: 0.5rem;'>Waithaka</h3>
        <p style='color: #6b7280; margin-bottom: 1rem;'>Best performance with 72.5% win rate</p>
        <div style='background-color: #dcfce7; padding: 1rem; border-radius: 0.5rem;'>
            <div style='font-size: 0.75rem; color: #6b7280;'>WIN RATE THIS MONTH</div>
            <div style='font-size: 1.5rem; font-weight: bold; color: #166534;'>72.5%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Trader Performance Rankings
st.markdown("---")
st.markdown('<div class="section-header">Trader Performance Rankings</div>', unsafe_allow_html=True)

if not trades_df.empty:
    # Calculate performance metrics
    performance_data = []
    for trader in trades_df['trader'].unique():
        trader_trades = trades_df[trades_df['trader'] == trader]
        win_rate = (trader_trades['result'] == 'Win').sum() / len(trader_trades) * 100
        performance_data.append({
            'Trader': trader,
            'Win Rate': win_rate,
            'Total Trades': len(trader_trades),
            'Wins': (trader_trades['result'] == 'Win').sum(),
            'Losses': (trader_trades['result'] == 'Loss').sum()
        })
    
    performance_df = pd.DataFrame(performance_data).sort_values('Win Rate', ascending=False)
    performance_df['Rank'] = range(1, len(performance_df) + 1)
    
    # Display rankings
    for _, row in performance_df.iterrows():
        with st.container():
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                rank_color = "#fbbf24" if row['Rank'] == 1 else "#9ca3af" if row['Rank'] == 2 else "#fb923c"
                st.markdown(f"<div style='background-color: {rank_color}; color: black; width: 2rem; height: 2rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;'>{row['Rank']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{row['Trader']}** - Win Rate: {row['Win Rate']:.1f}%")
                st.markdown(f"Total Trades: {row['Total Trades']} | Wins: {row['Wins']} | Losses: {row['Losses']}")
                st.progress(row['Win Rate'] / 100)
else:
    st.info("No trades data available for performance rankings")
