import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import numpy as np
import json
import os
from google.oauth2.service_account import Credentials
import gspread
import time

# Google Sheets Configuration
SHEET_NAME = "Forex Trading Analytics"
WORKSHEET_NAME = "Trades"

# Initialize Google Sheets connection
@st.cache_resource
def init_connection():
    """Initialize connection to Google Sheets"""
    try:
        # Try to get credentials from Streamlit secrets
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return None

@st.cache_data(ttl=30)  # Cache for 30 seconds to allow real-time updates
def load_trades_from_sheets():
    """Load trades from Google Sheets"""
    try:
        gc = init_connection()
        if gc is None:
            return load_fallback_data()
        
        # Open the spreadsheet
        sheet = gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        
        # Get all records
        records = sheet.get_all_records()
        
        if not records:
            return load_fallback_data()
        
        return records
        
    except Exception as e:
        st.error(f"Error loading from Google Sheets: {e}")
        return load_fallback_data()

def save_trade_to_sheets(trade_data):
    """Save a single trade to Google Sheets"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        sheet = gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        
        # Prepare row data in the same order as headers
        row_data = [
            trade_data['id'],
            trade_data['date'],
            trade_data['trader'],
            trade_data['instrument'],
            trade_data['entry'],
            trade_data['sl'],
            trade_data['target'],
            trade_data['risk'],
            trade_data['reward'],
            trade_data['rrRatio'],
            trade_data['outcome'],
            trade_data['result']
        ]
        
        # Add the row
        sheet.append_row(row_data)
        return True
        
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def delete_trade_from_sheets(trade_id):
    """Delete a trade from Google Sheets"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        sheet = gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        
        # Find the row with the trade ID
        records = sheet.get_all_records()
        for i, record in enumerate(records):
            if record.get('id') == trade_id:
                # Delete row (add 2 because of header row and 0-based indexing)
                sheet.delete_rows(i + 2)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error deleting from Google Sheets: {e}")
        return False

def setup_google_sheet():
    """Set up the Google Sheet with proper headers if it doesn't exist"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        # Try to open existing sheet
        try:
            spreadsheet = gc.open(SHEET_NAME)
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet
            spreadsheet = gc.create(SHEET_NAME)
            # Share with your email (replace with your email)
            # spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')
        
        # Try to get the worksheet
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            # Create new worksheet
            worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=12)
        
        # Set headers if the sheet is empty
        if not worksheet.get_all_records():
            headers = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 'risk', 'reward', 'rrRatio', 'outcome', 'result']
            worksheet.append_row(headers)
        
        return True
        
    except Exception as e:
        st.error(f"Error setting up Google Sheet: {e}")
        return False

def load_fallback_data():
    """Load fallback data when Google Sheets is not available"""
    return [
        { 'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss' },
        { 'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00, 'rrRatio': 1.40, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450, 'rrRatio': 1.80, 'outcome': 'Target Hit', 'result': 'Win' }
    ]

# Auto-refresh functionality for real-time updates
def auto_refresh():
    """Auto-refresh data every 30 seconds"""
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # Refresh every 30 seconds
    if time.time() - st.session_state.last_refresh > 30:
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
        st.rerun()

# Page configuration
st.set_page_config(
    page_title="Forex Trading Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS (keeping the same as original)
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
    
    /* Connection status */
    .connection-status {
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 1000;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-connected {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-disconnected {
        background-color: #fee2e2;
        color: #dc2626;
        border: 1px solid #fecaca;
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

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = load_trades_from_sheets()
    
if 'sheets_connected' not in st.session_state:
    st.session_state.sheets_connected = init_connection() is not None

# Auto-refresh for real-time updates
auto_refresh()

# Connection status indicator
connection_class = "status-connected" if st.session_state.sheets_connected else "status-disconnected"
connection_text = "🟢 Google Sheets Connected" if st.session_state.sheets_connected else "🔴 Using Local Data"

st.markdown(f"""
<div class="connection-status {connection_class}">
    {connection_text}
</div>
""", unsafe_allow_html=True)

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
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Setup Google Sheets button (for first-time setup)
if not st.session_state.sheets_connected:
    st.warning("⚠️ Google Sheets not connected. Using local data only.")
    if st.button("🔧 Setup Google Sheets Integration"):
        if setup_google_sheet():
            st.success("✅ Google Sheets setup completed!")
            st.session_state.sheets_connected = True
            st.rerun()

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
    instrument_pairs = ['Select Instrument', 'XAUUSD', 'USDOIL', 'BTCUSD', 'USTECH', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD', 'NZDUSD']
    instrument = st.selectbox("", instrument_pairs, key="instrument_select", label_visibility="collapsed")

with col3:
    st.markdown('<div class="form-group"><label>Date</label></div>', unsafe_allow_html=True)
    trade_date = st.date_input("", value=date.today(), key="date_input", label_visibility="collapsed")

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
        if trader != "Select Trader" and instrument != "Select Instrument" and outcome != "Select Outcome" and entry and sl and target:
            risk = abs(entry - sl)
            reward = abs(target - entry)
            rr_ratio = reward / risk if risk != 0 else 0
            result = "Win" if outcome == "Target Hit" else "Loss"
            
            # Generate new ID
            max_id = max([trade.get('id', 0) for trade in st.session_state.trades], default=0)
            
            new_trade = {
                'id': max_id + 1,
                'date': trade_date.strftime('%Y-%m-%d'),
                'trader': trader,
                'instrument': instrument,
                'entry': entry,
                'sl': sl,
                'target': target,
                'risk': round(risk, 4),
                'reward': round(reward, 4),
                'rrRatio': round(rr_ratio, 2),
                'outcome': outcome,
                'result': result
            }
            
            # Save to Google Sheets first
            if st.session_state.sheets_connected:
                if save_trade_to_sheets(new_trade):
                    st.session_state.trades.append(new_trade)
                    st.success("✅ Trade added successfully and synced to Google Sheets!")
                    # Clear cache to refresh data
                    st.cache_data.clear()
                    time.sleep(1)  # Brief delay to ensure sync
                    st.rerun()
                else:
                    st.error("❌ Failed to sync to Google Sheets, but trade added locally.")
                    st.session_state.trades.append(new_trade)
            else:
                st.session_state.trades.append(new_trade)
                st.warning("⚠️ Trade added locally only (Google Sheets not connected)")
            
        else:
            st.error("Please fill in all fields to add a trade.")

st.markdown('</div></div>', unsafe_allow_html=True)

# Refresh button
col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 8])
with col_refresh2:
    if st.button("🔄 Refresh Data", help="Refresh data from Google Sheets"):
        st.cache_data.clear()
        st.session_state.trades = load_trades_from_sheets()
        st.success("Data refreshed!")
        st.rerun()

# Main Content Grid
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    # Calculate dynamic rankings based on current data
    if st.session_state.trades:
        trader_stats = {}
        for trade in st.session_state.trades:
            trader = trade['trader']
            if trader not in trader_stats:
                trader_stats[trader] = {'wins': 0, 'total': 0}
            trader_stats[trader]['total'] += 1
            if trade['result'] == 'Win':
                trader_stats[trader]['wins'] += 1
        
        # Calculate win rates and sort
        rankings = []
        for trader, stats in trader_stats.items():
            win_rate = (stats['wins'] / stats['total']) * 100 if stats['total'] > 0 else 0
            rankings.append({
                'name': trader,
                'win_rate': round(win_rate, 1),
                'wins': stats['wins'],
                'losses': stats['total'] - stats['wins'],
                'total': stats['total']
            })
        
        rankings.sort(key=lambda x: x['win_rate'], reverse=True)
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
    else:
        rankings = []

    # Trader Performance Rankings
    st.markdown("""
    <div class="trade-card">
        <div class="card-header">
            <h3 style="font-weight: 600; margin: 0;">Trader Performance Rankings</h3>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if rankings:
        for ranking in rankings:
            rank_class = f"rank-{ranking['rank']}" if ranking['rank'] <= 3 else "rank-other"
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
    else:
        st.info("No trades available for rankings.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Trading History
    st.markdown("""
    <div style="background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
        <div style="background-color: #334155; color: white; padding: 0.75rem 1rem; border-radius: 0.5rem 0.5rem 0 0; display: flex; align-items: center;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h4"></path>
            </svg>
            <h3 style="font-weight: 600; margin: 0; font-size: 1rem;">Trading History</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display trades with individual delete buttons
    if not st.session_state.trades:
        st.info("No trades recorded yet. Add a trade using the form above.")
    else:
        # Header row
        header_cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.8, 1.5, 1])
        headers = ['Date', 'Trader', 'Instrument', 'Entry', 'SL', 'Target', 'Risk', 'Reward', 'R/R Ratio', 'Outcome', 'Result', 'Actions']
        
        for i, header in enumerate(headers):
            with header_cols[i]:
                st.markdown(f'<div style="font-weight: bold; color: #000000; padding: 0.5rem 0; border-bottom: 2px solid #e5e7eb; font-size: 0.875rem;">{header}</div>', unsafe_allow_html=True)
        
        # Create columns for each trade row
        for i, trade in enumerate(st.session_state.trades):
            cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.8, 1.5, 1])
            
            with cols[0]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["date"]}</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["trader"]}</div>', unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["instrument"]}</div>', unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["entry"]}</div>', unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["sl"]}</div>', unsafe_allow_html=True)
            with cols[5]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["target"]}</div>', unsafe_allow_html=True)
            with cols[6]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["risk"]}</div>', unsafe_allow_html=True)
            with cols[7]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["reward"]}</div>', unsafe_allow_html=True)
            with cols[8]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["rrRatio"]}</div>', unsafe_allow_html=True)
            with cols[9]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0;">{trade["outcome"]}</div>', unsafe_allow_html=True)
            with cols[10]:
                if trade['result'] == 'Win':
                    st.markdown('<span style="background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 12px; font-weight: 500; font-size: 0.75rem;">Win</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="background-color: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 12px; font-weight: 500; font-size: 0.75rem;">Loss</span>', unsafe_allow_html=True)
            with cols[11]:
                if st.button("🗑️", key=f"delete_{trade['id']}", help="Delete this trade", type="secondary"):
                    # Delete from Google Sheets first
                    if st.session_state.sheets_connected:
                        if delete_trade_from_sheets(trade['id']):
                            st.session_state.trades = [t for t in st.session_state.trades if t['id'] != trade['id']]
                            st.success("✅ Trade deleted and synced!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete from Google Sheets")
                    else:
                        st.session_state.trades = [t for t in st.session_state.trades if t['id'] != trade['id']]
                        st.warning("⚠️ Trade deleted locally only (Google Sheets not connected)")
                        st.rerun()

with col_sidebar:
    # Performance Metrics
    st.markdown("""
    <div style="background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
        <div style="background-color: #334155; color: white; padding: 0.75rem 1rem; border-radius: 0.5rem 0.5rem 0 0; display: flex; align-items: center;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
            </svg>
            <h3 style="font-weight: 600; margin: 0; font-size: 1rem;">Performance Metrics</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #475569; color: white; padding: 0.75rem; font-size: 0.875rem; font-weight: 500; margin: -1.5rem -1rem 0 -1rem;">
        Overall Win Rate Distribution
    </div>
    """, unsafe_allow_html=True)
    
    # Create dynamic donut chart based on current data
    if rankings:
        labels = [r['name'] for r in rankings[:3]]  # Top 3 traders
        values = [r['win_rate'] for r in rankings[:3]]
        colors = ['#fb923c', '#3b82f6', '#9ca3af']
        
        # Calculate average win rate
        avg_win_rate = sum(values) / len(values) if values else 0
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.6,
            marker=dict(colors=colors[:len(labels)], line=dict(color='#FFFFFF', width=2)),
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>Win Rate: %{value}%<extra></extra>'
        )])
        
        fig_donut.update_layout(
            showlegend=False,
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[
                dict(
                    text=f'<b>{avg_win_rate:.1f}%</b><br><span style="font-size:12px; color:#6b7280;">Avg Rate</span>', 
                    x=0.5, y=0.5, 
                    font_size=20, 
                    showarrow=False,
                    font_color='#374151'
                )
            ]
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
        
        # Dynamic Legend
        if len(rankings) >= 3:
            col_legend1, col_legend2, col_legend3 = st.columns(3)
            
            for i, (col, ranking) in enumerate(zip([col_legend1, col_legend2, col_legend3], rankings[:3])):
                with col:
                    color = colors[i]
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center;">
                            <div style="width: 0.75rem; height: 0.75rem; background-color: {color}; border-radius: 0.125rem; margin-right: 0.5rem;"></div>
                            <span style="font-size: 0.875rem; color: #000000;">{ranking['name']}</span>
                        </div>
                        <span style="font-weight: 600; font-size: 0.875rem; color: #000000;">{ranking['win_rate']}%</span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No data available for performance metrics.")
    
    # Trader of the Month (dynamic based on highest win rate)
    if rankings:
        top_trader = rankings[0]
        st.markdown(f"""
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
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🏆</div>
                <h4 style="font-size: 1.25rem; font-weight: bold; color: #1f2937; margin: 0 0 0.5rem 0;">{top_trader['name']}</h4>
                <p style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">Best performance with {top_trader['win_rate']}% win rate</p>
                <div style="background-color: #dcfce7; border-radius: 0.5rem; padding: 1rem; margin-top: 1rem;">
                    <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">WIN RATE THIS MONTH</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #15803d;">{top_trader['win_rate']}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Dynamic Instrument Performance by Trader
    st.markdown("""
    <div style="background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
        <div style="background-color: #334155; color: white; padding: 0.75rem 1rem; border-radius: 0.5rem 0.5rem 0 0; display: flex; align-items: center;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 0.5rem;">
                <line x1="12" y1="20" x2="12" y2="10"></line>
                <line x1="18" y1="20" x2="18" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="16"></line>
            </svg>
            <h3 style="font-weight: 600; margin: 0; font-size: 1rem;">Instrument Performance by Trader</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate dynamic instrument performance
    if st.session_state.trades:
        # Get all unique instruments and traders
        instruments = list(set(trade['instrument'] for trade in st.session_state.trades))
        traders = list(set(trade['trader'] for trade in st.session_state.trades))
        
        # Calculate performance for each trader-instrument combination
        performance_data = {'Instrument': instruments}
        
        for trader in traders:
            trader_performance = []
            for instrument in instruments:
                # Get trades for this trader-instrument combination
                trades = [t for t in st.session_state.trades if t['trader'] == trader and t['instrument'] == instrument]
                if trades:
                    wins = sum(1 for t in trades if t['result'] == 'Win')
                    win_rate = (wins / len(trades)) * 100
                    trader_performance.append(f"{win_rate:.0f}%")
                else:
                    trader_performance.append("-")
            performance_data[trader] = trader_performance
        
        # Create DataFrame
        perf_df = pd.DataFrame(performance_data)
        
        # Style the dataframe
        def style_performance(val):
            if val == '-':
                return 'background-color: #6b7280; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
            elif val.replace('%', '').replace('-', '').isdigit():
                rate = int(val.replace('%', ''))
                if rate >= 70:
                    return 'background-color: #10b981; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
                elif rate >= 50:
                    return 'background-color: #f59e0b; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
                else:
                    return 'background-color: #ef4444; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
            else:
                return 'background-color: #f3f4f6; text-align: center; font-weight: 500; padding: 12px; color: #000000;'
        
        # Display the styled dataframe
        if len(traders) > 0:
            styled_df = perf_df.style.applymap(style_performance, subset=traders)
            styled_df = styled_df.applymap(lambda x: 'background-color: #f3f4f6; text-align: center; font-weight: 500; padding: 12px; color: #000000;', subset=['Instrument'])
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No instrument performance data available.")
    else:
        st.info("No trades available for instrument performance analysis.")

# Instructions for Google Sheets setup
with st.expander("📋 Google Sheets Setup Instructions", expanded=False):
    st.markdown("""
    ### Setting up Google Sheets Integration
    
    To enable real-time synchronization across devices, follow these steps:
    
    1. **Create a Google Cloud Project:**
       - Go to [Google Cloud Console](https://console.cloud.google.com/)
       - Create a new project or select existing one
    
    2. **Enable APIs:**
       - Enable Google Sheets API
       - Enable Google Drive API
    
    3. **Create Service Account:**
       - Go to IAM & Admin > Service Accounts
       - Create new service account
       - Download the JSON key file
    
    4. **Configure Streamlit Secrets:**
       - Create `.streamlit/secrets.toml` file in your project
       - Add the service account credentials:
       ```toml
       [gcp_service_account]
       type = "service_account"
       project_id = "your-project-id"
       private_key_id = "your-private-key-id"
       private_key = "your-private-key"
       client_email = "your-service-account-email"
       client_id = "your-client-id"
       auth_uri = "https://accounts.google.com/o/oauth2/auth"
       token_uri = "https://oauth2.googleapis.com/token"
       auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
       client_x509_cert_url = "your-cert-url"
       ```
    
    5. **Install Required Packages:**
       ```bash
       pip install gspread google-auth
       ```
    
    6. **Share the Spreadsheet:**
       - Share your Google Sheet with the service account email
       - Give "Editor" permissions
    
    **Benefits of Google Sheets Integration:**
    - ✅ Real-time synchronization across devices
    - ✅ Data persistence and backup
    - ✅ Collaborative access for team members
    - ✅ Easy data export and analysis
    - ✅ Automatic updates every 30 seconds
    """)

st.markdown('</div>', unsafe_allow_html=True)

# Footer with sync status
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #6b7280; font-size: 0.875rem; border-top: 1px solid #e5e7eb; margin-top: 2rem;">
    <p>📊 Forex Trading Analytics - Real-time data synchronization with Google Sheets</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)
