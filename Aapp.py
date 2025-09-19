import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Forex Trading Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Main styles */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Section */
    .header {
        background-color: #475569;
        color: white;
        padding: 15px 0;
        margin-bottom: 20px;
    }
    
    .header-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    
    .nav-buttons {
        display: flex;
        gap: 15px;
        float: right;
    }
    
    .nav-btn {
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.8);
        font-size: 16px;
        cursor: pointer;
        padding: 8px 15px;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .nav-btn:hover {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Card styles */
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: none;
    }
    
    .card-header {
        background-color: #475569;
        color: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .dropdown-arrow {
        cursor: pointer;
        transition: transform 0.3s;
    }
    
    /* Form styles */
    .form-container {
        padding: 20px;
    }
    
    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
        align-items: end;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
    }
    
    .form-label {
        display: block;
        margin-bottom: 8px;
        font-weight: 600;
        color: #2c3e50;
        font-size: 14px;
    }
    
    .suggestion-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    
    .suggestion-pill {
        background-color: #3498db;
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        cursor: pointer;
        transition: background-color 0.3s;
        font-weight: 500;
        border: none;
    }
    
    .suggestion-pill:hover {
        background-color: #2980b9;
    }
    
    /* Trader rankings */
    .trader-rank {
        display: flex;
        align-items: center;
        padding: 15px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .rank-badge {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 15px;
    }
    
    .rank-1 { background-color: #ffd700; color: black; }
    .rank-2 { background-color: #c0c0c0; color: black; }
    .rank-3 { background-color: #cd7f32; color: black; }
    
    .progress-bar {
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        margin: 5px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background-color: #28a745;
        border-radius: 4px;
    }
    
    /* Badge styles */
    .badge-win {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge-loss {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Stats box */
    .stats-box {
        text-align: center;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        background-color: rgba(46, 204, 113, 0.15);
    }
    
    .stats-box h6 {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin: 0;
    }
    
    .stats-box h3 {
        font-weight: 700;
        color: #2c3e50;
        margin: 5px 0 0 0;
    }
    
    /* Trophy */
    .trophy {
        font-size: 48px;
        margin-bottom: 10px;
    }
    
    /* Performance grid */
    .performance-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 2px;
        margin-top: 15px;
    }
    
    .performance-cell {
        background-color: #f8f9fa;
        padding: 10px;
        text-align: center;
        font-size: 12px;
    }
    
    .performance-header {
        background-color: #475569;
        color: white;
        font-weight: bold;
        padding: 12px 10px;
    }
    
    .performance-value {
        padding: 8px;
        margin: 2px;
        border-radius: 4px;
        font-weight: bold;
        color: white;
        font-size: 11px;
    }
    
    .perf-green { background-color: #28a745; }
    .perf-yellow { background-color: #ffc107; }
    .perf-red { background-color: #dc3545; }
    .perf-gray { background-color: #6c757d; }
    
    /* Delete button */
    .delete-btn {
        background: none;
        border: none;
        color: #dc3545;
        cursor: pointer;
        font-size: 16px;
        padding: 4px;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    
    .delete-btn:hover {
        background-color: rgba(220, 53, 69, 0.1);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .form-row {
            grid-template-columns: 1fr;
            gap: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = [
        {'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50, 'rr_ratio': 1.73, 'outcome': 'Target Hit', 'result': 'Win'},
        {'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70, 'rr_ratio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss'},
        {'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00, 'rr_ratio': 1.40, 'outcome': 'Target Hit', 'result': 'Win'},
        {'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450, 'rr_ratio': 1.80, 'outcome': 'Target Hit', 'result': 'Win'}
    ]

if 'selected_instrument' not in st.session_state:
    st.session_state.selected_instrument = ''

# Instrument pairs
instrument_pairs = ['XAUUSD', 'USDOIL', 'BTCUSD', 'USTECH', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD', 'NZDUSD']

# Functions
def delete_trade(trade_id):
    st.session_state.trades = [trade for trade in st.session_state.trades if trade['id'] != trade_id]

def select_instrument(instrument):
    st.session_state.selected_instrument = instrument

# Header Section
st.markdown("""
<div class="header">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; align-items: center;">
            <h1 class="header-title">📊 Forex Trading Analytics</h1>
        </div>
        <div class="nav-buttons">
            <button class="nav-btn">🏠 Dashboard</button>
            <button class="nav-btn">🕐 History</button>
            <button class="nav-btn">⚙️ Settings</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">', unsafe_allow_html=True)

# Add New Trade Section
st.markdown("""
<div class="card">
    <div class="card-header">
        <div>
            <span style="background-color: #14b8a6; padding: 4px; border-radius: 50%; margin-right: 8px;">+</span>
            Add New Trade
        </div>
        <span class="dropdown-arrow">▼</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Form in columns
with st.container():
    st.markdown('<div style="background: white; padding: 20px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">', unsafe_allow_html=True)
    
    # First row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<label class="form-label">Trader</label>', unsafe_allow_html=True)
        trader = st.selectbox('', ['Select Trader', 'Waithaka', 'Wallace', 'Max'], key='trader_select', label_visibility='collapsed')
    
    with col2:
        st.markdown('<label class="form-label">Instrument</label>', unsafe_allow_html=True)
        instrument = st.text_input('', value=st.session_state.selected_instrument, placeholder='Enter Instrument', key='instrument_input', label_visibility='collapsed')
        
        # Clickable suggestion pills
        pill_html = '<div class="suggestion-pills">'
        for pair in instrument_pairs:
            pill_html += f'<button class="suggestion-pill" onclick="document.querySelector(\'input[data-testid=\\\'stTextInput-instrument_input\\\']\').value=\'{pair}\'">{pair}</button>'
        pill_html += '</div>'
        st.markdown(pill_html, unsafe_allow_html=True)
    
    with col3:
        st.markdown('<label class="form-label">Date</label>', unsafe_allow_html=True)
        date = st.date_input('', value=datetime(2025, 9, 19), key='date_input', label_visibility='collapsed')
    
    with col4:
        st.markdown('<label class="form-label">Outcome</label>', unsafe_allow_html=True)
        outcome = st.selectbox('', ['Select Outcome', 'Target Hit', 'SL Hit'], key='outcome_select', label_visibility='collapsed')
    
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # Second row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown('<label class="form-label">Entry Price</label>', unsafe_allow_html=True)
        entry_price = st.number_input('', placeholder=0.00, key='entry_input', label_visibility='collapsed')
    
    with col6:
        st.markdown('<label class="form-label">Stop Loss (SL)</label>', unsafe_allow_html=True)
        sl = st.number_input('', placeholder=0.00, key='sl_input', label_visibility='collapsed')
    
    with col7:
        st.markdown('<label class="form-label">Target Price</label>', unsafe_allow_html=True)
        target = st.number_input('', placeholder=0.00, key='target_input', label_visibility='collapsed')
    
    with col8:
        st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
        if st.button('➕ Add Trade', key='add_trade_btn', type='primary'):
            st.success('Trade added successfully!')
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area
col_left, col_right = st.columns([2, 1])

with col_left:
    # Trader Performance Rankings
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span>🏆 Trader Performance Rankings</span>
        </div>
        <div>
            <div class="trader-rank">
                <div class="rank-badge rank-1">1</div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
                        <span style="font-weight: 600; color: #2c3e50;">Waithaka</span>
                        <span style="font-size: 14px; font-weight: 500;">Win Rate: 72.5%</span>
                    </div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 8px;">Total Trades: 18</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 72.5%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">Wins: 13 | Losses: 5</div>
                </div>
            </div>
            
            <div class="trader-rank">
                <div class="rank-badge rank-2">2</div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
                        <span style="font-weight: 600; color: #2c3e50;">Max</span>
                        <span style="font-size: 14px; font-weight: 500;">Win Rate: 65.3%</span>
                    </div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 8px;">Total Trades: 15</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 65.3%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">Wins: 10 | Losses: 5</div>
                </div>
            </div>
            
            <div class="trader-rank">
                <div class="rank-badge rank-3">3</div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 4px;">
                        <span style="font-weight: 600; color: #2c3e50;">Wallace</span>
                        <span style="font-size: 14px; font-weight: 500;">Win Rate: 58.7%</span>
                    </div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 8px;">Total Trades: 16</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 58.7%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">Wins: 9 | Losses: 7</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Trading History
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span>📋 Trading History</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create DataFrame for trades
    df = pd.DataFrame(st.session_state.trades)
    
    if not df.empty:
        # Display table with delete functionality
        for idx, trade in df.iterrows():
            col_del1, col_del2, col_del3, col_del4, col_del5, col_del6, col_del7, col_del8, col_del9, col_del10, col_del11, col_del12 = st.columns([1,1,1,1,1,1,1,1,1,1,1,0.5])
            
            if idx == 0:  # Header row
                with col_del1:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Date</div>', unsafe_allow_html=True)
                with col_del2:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Trader</div>', unsafe_allow_html=True)
                with col_del3:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Instrument</div>', unsafe_allow_html=True)
                with col_del4:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Entry</div>', unsafe_allow_html=True)
                with col_del5:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">SL</div>', unsafe_allow_html=True)
                with col_del6:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Target</div>', unsafe_allow_html=True)
                with col_del7:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Risk</div>', unsafe_allow_html=True)
                with col_del8:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Reward</div>', unsafe_allow_html=True)
                with col_del9:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">R/R Ratio</div>', unsafe_allow_html=True)
                with col_del10:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Outcome</div>', unsafe_allow_html=True)
                with col_del11:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Result</div>', unsafe_allow_html=True)
                with col_del12:
                    st.markdown('<div style="font-weight: bold; font-size: 12px; padding: 8px 4px; background-color: #475569; color: white; text-align: center;">Actions</div>', unsafe_allow_html=True)
            
            # Data rows
            with col_del1:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["date"]}</div>', unsafe_allow_html=True)
            with col_del2:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["trader"]}</div>', unsafe_allow_html=True)
            with col_del3:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["instrument"]}</div>', unsafe_allow_html=True)
            with col_del4:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["entry"]}</div>', unsafe_allow_html=True)
            with col_del5:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["sl"]}</div>', unsafe_allow_html=True)
            with col_del6:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["target"]}</div>', unsafe_allow_html=True)
            with col_del7:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["risk"]}</div>', unsafe_allow_html=True)
            with col_del8:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["reward"]}</div>', unsafe_allow_html=True)
            with col_del9:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["rr_ratio"]}</div>', unsafe_allow_html=True)
            with col_del10:
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;">{trade["outcome"]}</div>', unsafe_allow_html=True)
            with col_del11:
                badge_class = "badge-win" if trade["result"] == "Win" else "badge-loss"
                st.markdown(f'<div style="font-size: 12px; padding: 8px 4px; text-align: center; border-bottom: 1px solid #e9ecef;"><span class="{badge_class}">{trade["result"]}</span></div>', unsafe_allow_html=True)
            with col_del12:
                if st.button('🗑️', key=f'delete_{trade["id"]}', help='Delete trade'):
                    delete_trade(trade["id"])
                    st.experimental_rerun()

with col_right:
    # Performance Metrics - Pie Chart
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span>📊 Performance Metrics</span>
        </div>
        <div style="background-color: #475569; color: white; padding: 8px 16px; margin: 0; font-size: 14px; font-weight: 500;">
            Overall Win Rate Distribution
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create pie chart with Plotly
    traders = ['Waithaka', 'Max', 'Wallace']
    win_rates = [72.5, 65.3, 56.7]
    colors = ['#3b82f6', '#000000', '#eab308']  # Blue, Black, Yellow
    
    fig = go.Figure(data=[go.Pie(
        labels=traders,
        values=win_rates,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
        textfont=dict(color='white', size=14),
        showlegend=True
    )])
    
    fig.update_layout(
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        font=dict(size=12),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    # Add center text
    fig.add_annotation(
        text="65.5%<br>Avg Rate",
        showarrow=False,
        font=dict(size=16, color="gray"),
        x=0.5, y=0.5
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trader of the Month
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span>🏆 Trader of the Month</span>
        </div>
        <div style="padding: 20px; text-align: center;">
            <div class="trophy">🏆</div>
            <h3 style="color: #2c3e50; margin-bottom: 5px; font-size: 20px;">Waithaka</h3>
            <p style="color: #6c757d; margin-bottom: 15px; font-size: 14px;">Best performance with 72.5% win rate</p>
            <div class="stats-box">
                <h6>WIN RATE THIS MONTH</h6>
                <h3>72.5%</h3>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Instrument Performance by Trader
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <span>📈 Instrument Performance by Trader</span>
        </div>
        <div style="padding: 15px;">
            <div class="performance-grid">
                <div class="performance-header">Instrument</div>
                <div class="performance-header">Waithaka</div>
                <div class="performance-header">Wallace</div>
                <div class="performance-header">Max</div>
                
                <div class="performance-cell" style="font-weight: bold; background-color: #f8f9fa;">BTCUSD</div>
                <div class="performance-cell"><div class="performance-value perf-yellow">55%</div></div>
                <div class="performance-cell"><div class="performance-value perf-gray">-</div></div>
                <div class="performance-cell"><div class="performance-value perf-green">65%</div></div>
                
                <div class="performance-cell" style="font-weight: bold; background-color: #f8f9fa;">USTECH</div>
                <div class="performance-cell"><div class="performance-value perf-green">70%</div></div>
                <div class="performance-cell"><div class="performance-value perf-red">40%</div></div>
                <div class="performance-cell"><div class="performance-value perf-gray">-</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# JavaScript for instrument selection (optional enhancement)
st.markdown("""
<script>
function selectInstrument(instrument) {
    const input = document.querySelector('input[aria-label="Instrument"]');
    if (input) {
        input.value = instrument;
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
}
</script>
""", unsafe_allow_html=True)-weight: bold; background-color: #f8f9fa;">XAUUSD</div>
                <div class="performance-cell"><div class="performance-value perf-green">75%</div></div>
                <div class="performance-cell"><div class="performance-value perf-green">60%</div></div>
                <div class="performance-cell"><div class="performance-value perf-gray">-</div></div>
                
                <div class="performance-cell" style="font-weight: bold; background-color: #f8f9fa;">USOIL</div>
                <div class="performance-cell"><div class="performance-value perf-green">80%</div></div>
                <div class="performance-cell"><div class="performance-value perf-yellow">50%</div></div>
                <div class="performance-cell"><div class="performance-value perf-gray">-</div></div>
                
                <div class="performance-cell" style="font
