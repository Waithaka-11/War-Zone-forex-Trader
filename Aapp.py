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
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the exact design
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #f3f4f6;
    }
    
    /* Header styling */
    .main-header {
        background-color: #334155;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0;
        margin: -1rem -1rem 0 -1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .header-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-buttons {
        display: flex;
        gap: 1rem;
    }
    
    .nav-btn {
        background: transparent;
        border: none;
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 0.375rem;
        cursor: pointer;
        transition: background-color 0.2s;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
    }
    
    .nav-btn:hover {
        background-color: #475569;
    }
    
    /* Card styling */
    .trade-card {
        background: white;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        background-color: #334155;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem 0.5rem 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .card-body {
        padding: 1.5rem;
    }
    
    /* Form styling */
    .form-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .form-group label {
        display: block;
        font-size: 0.875rem;
        font-weight: 500;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    /* Instrument tags */
    .instrument-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .instrument-tag {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .instrument-tag:hover {
        background-color: #bfdbfe;
    }
    
    /* Rankings styling */
    .rank-item {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background-color: #f8fafc;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .rank-number {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
        color: black;
    }
    
    .rank-1 { background-color: #fbbf24; }
    .rank-2 { background-color: #9ca3af; }
    .rank-3 { background-color: #fb923c; }
    
    .progress-bar {
        background-color: #e5e7eb;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        background-color: #10b981;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* Table styling */
    .trading-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .trading-table th {
        background-color: #475569;
        color: white;
        padding: 0.75rem 1rem;
        text-align: left;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .trading-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e5e7eb;
        font-size: 0.875rem;
    }
    
    .trading-table tr:hover {
        background-color: #f9fafb;
    }
    
    .result-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .result-win {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .result-loss {
        background-color: #fee2e2;
        color: #dc2626;
    }
    
    /* Performance metrics styling */
    .donut-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .legend-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    
    .legend-color {
        width: 0.75rem;
        height: 0.75rem;
        border-radius: 0.125rem;
        margin-right: 0.5rem;
    }
    
    /* Trader of the month styling */
    .trader-month {
        text-align: center;
        padding: 1.5rem;
    }
    
    .trophy-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .month-card {
        background-color: #dcfce7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    /* Instrument performance grid */
    .perf-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.25rem;
        font-size: 0.75rem;
    }
    
    .perf-header {
        background-color: #475569;
        color: white;
        font-weight: 600;
        text-align: center;
        padding: 0.75rem;
        border-radius: 0.25rem;
    }
    
    .perf-cell {
        background-color: #f3f4f6;
        padding: 0.75rem;
        text-align: center;
        font-weight: 500;
        border-radius: 0.25rem;
    }
    
    .perf-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .perf-green { background-color: #10b981; }
    .perf-yellow { background-color: #f59e0b; }
    .perf-red { background-color: #ef4444; }
    .perf-gray { background-color: #6b7280; }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stDeployButton {display: none;}
    
    /* Custom spacing */
    .main-content {
        padding: 1.5rem;
        max-width: 90rem;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for trades
if 'trades' not in st.session_state:
    st.session_state.trades = [
        { 'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss' },
        { 'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00, 'rrRatio': 1.40, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450, 'rrRatio': 1.80, 'outcome': 'Target Hit', 'result': 'Win' }
    ]

if 'selected_instrument' not in st.session_state:
    st.session_state.selected_instrument = ''

if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'trader': '',
        'instrument': '',
        'outcome': '',
        'entry': 0.0,
        'sl': 0.0,
        'target': 0.0
    }

# Header
st.markdown("""
<div class="main-header">
    <div class="header-nav">
        <div style="display: flex; align-items: center;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.75rem;">
                <line x1="12" y1="20" x2="12" y2="10"></line>
                <line x1="18" y1="20" x2="18" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="16"></line>
            </svg>
            <h1 style="font-size: 1.25rem; font-weight: bold; margin: 0;">Forex Trading Analytics</h1>
        </div>
        <div class="nav-buttons">
            <button class="nav-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9,22 9,12 15,12 15,22"></polyline>
                </svg>
                Dashboard
            </button>
            <button class="nav-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12,6 12,12 16,14"></polyline>
                </svg>
                History
            </button>
            <button class="nav-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"></path>
                </svg>
                Settings
            </button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Add New Trade Section
st.markdown("""
<div class="trade-card">
    <div class="card-header">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #0d9488; border-radius: 50%; padding: 0.25rem; margin-right: 0.75rem;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </div>
            <span style="font-weight: 600;">Add New Trade</span>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6,9 12,15 18,9"></polyline>
        </svg>
    </div>
    <div class="card-body">
""", unsafe_allow_html=True)

# First Row of Form
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="form-group"><label>Trader</label></div>', unsafe_allow_html=True)
    trader = st.selectbox("", ["Select Trader", "Waithaka", "Wallace", "Max"], key="trader_select", label_visibility="collapsed")

with col2:
    st.markdown('<div class="form-group"><label>Instrument</label></div>', unsafe_allow_html=True)
    instrument = st.text_input("", placeholder="Enter Instrument", value=st.session_state.selected_instrument, key="instrument_input", label_visibility="collapsed")
    
    # Instrument pairs
    instrument_pairs = ['XAUUSD', 'USDOIL', 'BTCUSD', 'USTECH', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD', 'NZDUSD']
    
    tags_html = '<div class="instrument-tags">'
    for pair in instrument_pairs:
        tags_html += f'<span class="instrument-tag" onclick="document.querySelector(\'input[data-testid=\\\"stTextInput\\\"] input\').value=\'{pair}\'">{pair}</span>'
    tags_html += '</div>'
    
    st.markdown(tags_html, unsafe_allow_html=True)

with col3:
    st.markdown('<div class="form-group"><label>Date</label></div>', unsafe_allow_html=True)
    st.text_input("", value="09/19/2025", disabled=True, key="date_input", label_visibility="collapsed")

with col4:
    st.markdown('<div class="form-group"><label>Outcome</label></div>', unsafe_allow_html=True)
    outcome = st.selectbox("", ["Select Outcome", "Target Hit", "SL Hit"], key="outcome_select", label_visibility="collapsed")

# Second Row of Form
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown('<div class="form-group"><label>Entry Price</label></div>', unsafe_allow_html=True)
    entry = st.number_input("", value=0.0, step=0.01, format="%.4f", key="entry_input", label_visibility="collapsed")

with col6:
    st.markdown('<div class="form-group"><label>Stop Loss (SL)</label></div>', unsafe_allow_html=True)
    sl = st.number_input("", value=0.0, step=0.01, format="%.4f", key="sl_input", label_visibility="collapsed")

with col7:
    st.markdown('<div class="form-group"><label>Target Price</label></div>', unsafe_allow_html=True)
    target = st.number_input("", value=0.0, step=0.01, format="%.4f", key="target_input", label_visibility="collapsed")

with col8:
    st.markdown('<div style="padding-top: 1.5rem;"></div>', unsafe_allow_html=True)
    if st.button("➕ Add Trade", type="primary", use_container_width=True):
        if trader != "Select Trader" and instrument and outcome != "Select Outcome" and entry and sl and target:
            risk = abs(entry - sl)
            reward = abs(target - entry)
            rr_ratio = reward / risk if risk != 0 else 0
            result = "Win" if outcome == "Target Hit" else "Loss"
            
            new_trade = {
                'id': len(st.session_state.trades) + 1,
                'date': '2025-09-19',
                'trader': trader,
                'instrument': instrument,
                'entry': entry,
                'sl': sl,
                'target': target,
                'risk': risk,
                'reward': reward,
                'rrRatio': round(rr_ratio, 2),
                'outcome': outcome,
                'result': result
            }
            
            st.session_state.trades.append(new_trade)
            st.success("Trade added successfully!")
            st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True)

# Main Content Grid
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    # Trader Performance Rankings
    st.markdown("""
    <div class="trade-card">
        <div class="card-header">
            <h3 style="font-weight: 600; margin: 0;">Trader Performance Rankings</h3>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    # Rankings data (matching exact percentages from React)
    rankings = [
        {"name": "Waithaka", "win_rate": 72.5, "total": 18, "wins": 13, "losses": 5, "rank": 1},
        {"name": "Max", "win_rate": 65.3, "total": 15, "wins": 10, "losses": 5, "rank": 2},
        {"name": "Wallace", "win_rate": 58.7, "total": 16, "wins": 9, "losses": 7, "rank": 3}
    ]
    
    for ranking in rankings:
        rank_class = f"rank-{ranking['rank']}"
        st.markdown(f"""
        <div class="rank-item">
            <div class="rank-number {rank_class}">{ranking['rank']}</div>
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.25rem;">
                    <span style="font-weight: 600; color: #1f2937;">{ranking['name']}</span>
                    <span style="font-size: 0.875rem; font-weight: 500;">Win Rate: {ranking['win_rate']}%</span>
                </div>
                <div style="font-size: 0.75rem; color: #6b7280; margin-bottom: 0.5rem;">Total Trades: {ranking['total']}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {ranking['win_rate']}%;"></div>
                </div>
                <div style="font-size: 0.75rem; color: #6b7280;">Wins: {ranking['wins']} | Losses: {ranking['losses']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Trading History
    st.markdown("""
    <div class="trade-card">
        <div class="card-header">
            <div style="display: flex; align-items: center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                    <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h4"></path>
                </svg>
                <h3 style="font-weight: 600; margin: 0;">Trading History</h3>
            </div>
        </div>
        <div style="overflow-x: auto;">
    """, unsafe_allow_html=True)
    
    # Trading table
    table_html = """
    <table class="trading-table">
        <thead>
            <tr>
                <th>Date</th>
                <th>Trader</th>
                <th>Instrument</th>
                <th>Entry</th>
                <th>SL</th>
                <th>Target</th>
                <th>Risk</th>
                <th>Reward</th>
                <th>R/R Ratio</th>
                <th>Outcome</th>
                <th>Result</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for trade in st.session_state.trades:
        result_class = "result-win" if trade['result'] == 'Win' else "result-loss"
        table_html += f"""
        <tr>
            <td>{trade['date']}</td>
            <td>{trade['trader']}</td>
            <td>{trade['instrument']}</td>
            <td>{trade['entry']}</td>
            <td>{trade['sl']}</td>
            <td>{trade['target']}</td>
            <td>{trade['risk']}</td>
            <td>{trade['reward']}</td>
            <td>{trade['rrRatio']}</td>
            <td>{trade['outcome']}</td>
            <td><span class="result-badge {result_class}">{trade['result']}</span></td>
            <td>
                <button onclick="alert('Delete functionality would be here')" style="color: #ef4444; background: none; border: none; cursor: pointer; padding: 0.25rem; border-radius: 0.25rem;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            </td>
        </tr>
        """
    
    table_html += """
        </tbody>
    </table>
        </div>
    </div>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)

with col_sidebar:
    # Performance Metrics
    st.markdown("""
    <div class="trade-card">
        <div class="card-header">
            <div style="display: flex; align-items: center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                    <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                </svg>
                <h3 style="font-weight: 600; margin: 0;">Performance Metrics</h3>
            </div>
        </div>
        <div class="card-body" style="padding: 0;">
            <div style="background-color: #475569; color: white; padding: 0.75rem; font-size: 0.875rem; font-weight: 500;">
                Overall Win Rate Distribution
            </div>
            <div style="padding: 1rem; background-color: #f9fafb;">
    """, unsafe_allow_html=True)
    
    # SVG Donut Chart (matching exact React implementation)
    st.markdown("""
    <div class="donut-container">
        <div style="width: 12rem; height: 12rem; position: relative;">
            <svg viewBox="0 0 100 100" style="width: 100%; height: 100%; transform: rotate(-90deg);">
                <!-- Background circle -->
                <circle cx="50" cy="50" r="35" fill="none" stroke="#f3f4f6" stroke-width="12"/>
                
                <!-- Waithaka - 37.1% of total - Blue -->
                <circle cx="50" cy="50" r="35" fill="none" stroke="#3b82f6" stroke-width="12" 
                        stroke-dasharray="81.6 138.4" stroke-dashoffset="0" 
                        style="transition: all 0.5s;"/>
                
                <!-- Max - 33.5% of total - Black -->
                <circle cx="50" cy="50" r="35" fill="none" stroke="#000000" stroke-width="12" 
                        stroke-dasharray="73.7 146.3" stroke-dashoffset="-81.6" 
                        style="transition: all 0.5s;"/>
                
                <!-- Wallace - 29.4% of total - Yellow -->
                <circle cx="50" cy="50" r="35" fill="none" stroke="#eab308" stroke-width="12" 
                        stroke-dasharray="64.7 155.3" stroke-dashoffset="-155.3" 
                        style="transition: all 0.5s;"/>
            </svg>
            <!-- Center text -->
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center;">
                <div style="text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: bold; color: #374151;">65.5%</div>
                    <div style="font-size: 0.75rem; color: #6b7280;">Avg Rate</div>
                </div>
            </div>
        </div>
    </div>
    
    <div style="margin-top: 1rem;">
        <div class="legend-item">
            <div style="display: flex; align-items: center;">
                <div class="legend-color" style="background-color: #fb923c;"></div>
                <span>Waithaka</span>
            </div>
            <span style="font-weight: 600;">72.5%</span>
        </div>
        <div class="legend-item">
            <div style="display: flex; align-items: center;">
                <div class="legend-color" style="background-color: #3b82f6;"></div>
                <span>Max</span>
            </div>
            <span style="font-weight: 600;">65.3%</span>
        </div>
        <div class="legend-item">
            <div style="display: flex; align-items: center;">
                <div class="legend-color" style="background-color: #9ca3af;"></div>
                <span>Wallace</span>
            </div>
            <span style="font-weight: 600;">56.7%</span>
        </div>
    </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Trader of the Month
    st.markdown("""
    <div class="trade-card">
        <div class="card-header">
            <div style="display: flex; align-items: center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                    <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path>
                    <path d="M14 9h1.5a2.5 2.5 0 0 0 0-5H14"></path>
                    <path d="M6 9v12l6-3 6 3V9"></path>
                </svg>
                <h3 style="font-weight: 600; margin: 0;">Trader of the Month</h3>
            </div>
        </div>
        <div class="trader-month">
            <div class="trophy-icon">🏆</div>
            <h4 style="font-size: 1.25rem; font-weight: bold; color: #1f2937; margin: 0 0 0.5rem 0;">Waithaka</h4>
            <p style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">Best performance with 72.5% win rate</p>
            <div class="month-card">
                <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">WIN RATE THIS MONTH</div>
                <div style="font-size: 2rem; font-weight: bold; color: #15803d;">72.5%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Instrument Performance by Trader
    st.markdown("""
    <div class="trade-card">
        <div class="card-header">
            <div style="display: flex; align-items: center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                    <line x1="12" y1="20" x2="12" y2="10"></line>
                    <line x1="18" y1="20" x2="18" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="16"></line>
                </svg>
                <h3 style="font-weight: 600; margin: 0;">Instrument Performance by Trader</h3>
            </div>
        </div>
        <div style="padding: 1rem;">
            <div class="perf-grid">
                <!-- Header -->
                <div class="perf-header">Instrument</div>
                <div class="perf-header">Waithaka</div>
                <div class="perf-header">Wallace</div>
                <div class="perf-header">Max</div>
                
                <!-- XAUUSD -->
                <div class="perf-cell">XAUUSD</div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-green">75%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-green">60%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-gray">-</div>
                </div>
                
                <!-- USOIL -->
                <div class="perf-cell">USOIL</div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-green">80%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-yellow">50%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-gray">-</div>
                </div>
                
                <!-- BTCUSD -->
                <div class="perf-cell">BTCUSD</div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-yellow">55%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-gray">-</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-green">65%</div>
                </div>
                
                <!-- USTECH -->
                <div class="perf-cell">USTECH</div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-green">70%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-red">40%</div>
                </div>
                <div style="padding: 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <div class="perf-badge perf-gray">-</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
