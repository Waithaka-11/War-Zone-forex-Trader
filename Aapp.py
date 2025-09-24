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
import requests
from streamlit_autorefresh import st_autorefresh

# Google Sheets Configuration
SHEET_NAME = "Forex Trading Analytics"
WORKSHEET_NAME = "Trades"

# Real-time update configuration
REAL_TIME_UPDATE_INTERVAL = 10  # Update every 10 seconds (reduced frequency)
CACHE_TTL = 30  # Cache data for 30 seconds (longer cache)

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
        return None

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def load_trades_from_sheets():
    """Load trades from Google Sheets with optimized caching"""
    try:
        gc = init_connection()
        if gc is None:
            return load_fallback_data()
        
        # Single API call to get all data
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            return load_fallback_data()
        
        # DATA CLEANING: Fix instrument names
        for i, row in enumerate(all_values):
            if len(row) > 3:  # Make sure instrument column exists
                instrument = str(row[3]).strip().upper()
                # Fix USTECH to US30 for Wallace
                if instrument == 'USTECH':
                    all_values[i][3] = 'US30'
                # Fix other common typos if needed
                elif instrument == 'NAS100':
                    all_values[i][3] = 'NAS100'
                elif instrument == 'SPX500':
                    all_values[i][3] = 'SPX500'
        
        # Continue with existing processing code...
        processed_records = []
        for i, row in enumerate(all_values[1:], 1):  # Skip headers
            if not any(str(cell).strip() for cell in row):
                continue
                
            try:
                while len(row) < 12:
                    row.append('')
                
                # Only process rows with complete valid data (no outcome required for new trades)
                if (row[2] and row[3] and row[4] and row[5] and row[6] and 
                    str(row[2]).strip() not in ['', 'trader'] and 
                    str(row[3]).strip() not in ['', 'instrument'] and
                    str(row[4]).strip() not in ['', '0.0', '0']):
                    
                    try:
                        entry_val = float(row[4])
                        sl_val = float(row[5]) 
                        target_val = float(row[6])
                        
                        # Skip if all prices are zero
                        if entry_val == 0.0 and sl_val == 0.0 and target_val == 0.0:
                            continue
                            
                        # Handle outcome and result - default to "Open" if not set
                        outcome = str(row[10]).strip() if row[10] and str(row[10]).strip() not in ['', 'outcome'] else "Open"
                        result = str(row[11]).strip() if row[11] and str(row[11]).strip() not in ['', 'result'] else "Open"
                        
                        processed_record = {
                            'id': int(row[0]) if row[0] and str(row[0]).strip().isdigit() else i,
                            'date': str(row[1]).strip() if row[1] else '',
                            'trader': str(row[2]).strip(),
                            'instrument': str(row[3]).strip(),
                            'entry': entry_val,
                            'sl': sl_val,
                            'target': target_val,
                            'risk': float(row[7]) if row[7] and str(row[7]).replace('.', '').replace('-', '').isdigit() else abs(entry_val - sl_val),
                            'reward': float(row[8]) if row[8] and str(row[8]).replace('.', '').replace('-', '').isdigit() else abs(target_val - entry_val),
                            'rrRatio': float(row[9]) if row[9] and str(row[9]).replace('.', '').replace('-', '').isdigit() else 0.0,
                            'outcome': outcome,
                            'result': result
                        }
                        processed_records.append(processed_record)
                    except (ValueError, TypeError):
                        continue
                    
            except (ValueError, TypeError, IndexError):
                continue
        
        return processed_records if processed_records else load_fallback_data()
        
    except:
        return load_fallback_data()

def save_trade_to_sheets(trade_data):
    """Save a single trade to Google Sheets - optimized for speed"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Prepare row data efficiently
        row_data = [
            str(trade_data['id']), str(trade_data['date']), str(trade_data['trader']),
            str(trade_data['instrument']), float(trade_data['entry']), float(trade_data['sl']),
            float(trade_data['target']), float(trade_data['risk']), float(trade_data['reward']),
            float(trade_data['rrRatio']), str(trade_data['outcome']), str(trade_data['result'])
        ]
        
        # Single API call
        sheet.append_row(row_data, value_input_option='RAW')
        return True
        
    except:
        return False

def update_trade_in_sheets(trade_data):
    """Update an existing trade in Google Sheets"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Find the trade by ID
        cell = sheet.find(str(trade_data['id']))
        if cell and cell.col == 1:  # Found in ID column
            # Update the entire row
            row_data = [
                str(trade_data['id']), str(trade_data['date']), str(trade_data['trader']),
                str(trade_data['instrument']), float(trade_data['entry']), float(trade_data['sl']),
                float(trade_data['target']), float(trade_data['risk']), float(trade_data['reward']),
                float(trade_data['rrRatio']), str(trade_data['outcome']), str(trade_data['result'])
            ]
            
            # Update the row
            for col, value in enumerate(row_data, 1):
                sheet.update_cell(cell.row, col, value)
            return True
        return False
        
    except:
        return False

def delete_trade_from_sheets(trade_id):
    """Delete a trade from Google Sheets - optimized for speed"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Find and delete in single operation
        cell = sheet.find(str(trade_id))
        if cell and cell.col == 1:
            sheet.delete_rows(cell.row)
            return True
        return False
        
    except:
        return False

def setup_google_sheet_silently():
    """Set up the Google Sheet with proper headers if it doesn't exist - runs silently in background"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        # Step 1: Handle the spreadsheet
        try:
            spreadsheet = gc.open(SHEET_NAME)
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet
            spreadsheet = gc.create(SHEET_NAME)
        
        # Step 2: Handle the worksheet
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            # Create new worksheet named "Trades"
            worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=12)
        
        # Step 3: Setup headers
        try:
            headers = worksheet.row_values(1)
            expected_headers = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 'risk', 'reward', 'rrRatio', 'outcome', 'result']
            
            if not headers or len(headers) == 0 or headers != expected_headers:
                # Clear first row and set proper headers
                worksheet.clear()  # Clear the worksheet first
                worksheet.append_row(expected_headers)
            
        except Exception as e:
            # Try to add headers anyway
            try:
                headers = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 'risk', 'reward', 'rrRatio', 'outcome', 'result']
                worksheet.append_row(headers)
            except:
                pass
        
        return True
        
    except:
        return False

def load_fallback_data():
    """Load fallback data when Google Sheets is not available"""
    return [
        { 'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss' },
        { 'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00, 'rrRatio': 1.40, 'outcome': 'Open', 'result': 'Open' },
        { 'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450, 'rrRatio': 1.80, 'outcome': 'Open', 'result': 'Open' },
        { 'id': 5, 'date': '2023-10-04', 'trader': 'Wallace', 'instrument': 'US30', 'entry': 34500.00, 'sl': 34200.00, 'target': 34900.00, 'risk': 300.00, 'reward': 400.00, 'rrRatio': 1.33, 'outcome': 'Open', 'result': 'Open' }
    ]

# Real-time update functions
def force_refresh_data():
    """Force refresh data from Google Sheets and update session state - optimized"""
    try:
        # Clear cache and get fresh data
        st.cache_data.clear()
        fresh_data = load_trades_from_sheets()
        st.session_state.trades = fresh_data
        st.session_state.last_data_hash = hash(str(fresh_data))  # Track changes
        return True
    except:
        return False

def auto_refresh_trades():
    """Auto-refresh trades data - optimized to reduce unnecessary updates"""
    if 'last_auto_refresh' not in st.session_state:
        st.session_state.last_auto_refresh = time.time()
    if 'last_data_hash' not in st.session_state:
        st.session_state.last_data_hash = None
        
    # Check if enough time has passed and we're connected
    if (st.session_state.sheets_connected and 
        time.time() - st.session_state.last_auto_refresh > REAL_TIME_UPDATE_INTERVAL):
        
        st.session_state.last_auto_refresh = time.time()
        
        try:
            # Get fresh data without clearing cache immediately
            fresh_data = load_trades_from_sheets()
            current_hash = hash(str(fresh_data))
            
            # Only update if data actually changed
            if st.session_state.last_data_hash != current_hash:
                st.session_state.trades = fresh_data
                st.session_state.last_data_hash = current_hash
                st.rerun()
        except:
            pass

def normalize_symbol(pair: str) -> str:
    """Convert pair formats (EURUSD or BTCUSD) => 'EUR/USD' or 'BTC/USD'"""
    pair = pair.strip().upper()
    if "/" in pair:
        return pair
    if len(pair) >= 6:
        return f"{pair[:3]}/{pair[3:]}"
    return pair

def get_live_price(pair: str) -> float:
    """Get live price from Twelve Data API"""
    symbol = normalize_symbol(pair)
    
    try:
        api_key = st.secrets.get("twelvedata", {}).get("api_key")
    except:
        return None
    
    if not api_key:
        return None

    url = "https://api.twelvedata.com/price"
    try:
        resp = requests.get(
            url, 
            params={"symbol": symbol, "apikey": api_key}, 
            timeout=10
        )
        data = resp.json()
        
        if "price" in data:
            return float(data["price"])
        return None
    except:
        return None

def check_and_update_trades():
    """Check live prices and update trade outcomes"""
    if not st.session_state.trades:
        return 0
    
    updates_made = 0
    
    for trade in st.session_state.trades:
        # Skip already closed trades
        if trade.get("outcome") in ("Target Hit", "SL Hit"):
            continue
        
        symbol = trade.get("instrument", "")
        if not symbol:
            continue
        
        # Get live price
        live_price = get_live_price(symbol)
        if live_price is None:
            continue
        
        # Get trade parameters
        entry_price = float(trade.get("entry", 0))
        sl_price = float(trade.get("sl", 0))
        target_price = float(trade.get("target", 0))
        
        if entry_price == 0 or (sl_price == 0 and target_price == 0):
            continue
        
        # Determine trade direction and check for hits
        is_long_trade = target_price > entry_price
        trade_updated = False
        
        if is_long_trade:
            # Long trade
            if target_price > 0 and live_price >= target_price:
                trade["outcome"] = "Target Hit"
                trade["result"] = "Win"
                trade_updated = True
            elif sl_price > 0 and live_price <= sl_price:
                trade["outcome"] = "SL Hit"
                trade["result"] = "Loss"
                trade_updated = True
        else:
            # Short trade
            if target_price > 0 and live_price <= target_price:
                trade["outcome"] = "Target Hit"
                trade["result"] = "Win"
                trade_updated = True
            elif sl_price > 0 and live_price >= sl_price:
                trade["outcome"] = "SL Hit"
                trade["result"] = "Loss"
                trade_updated = True
        
        if trade_updated:
            updates_made += 1
            # Try to update in sheets if connected
            if st.session_state.sheets_connected:
                try:
                    update_trade_in_sheets(trade)
                except:
                    pass
    
    return updates_made

def close_trade(trade_id):
    """Close a trade manually - sets outcome to 'Manual Close'"""
    try:
        # Force complete data refresh
        st.cache_data.clear()
        fresh_data = load_trades_from_sheets()
        st.session_state.trades = fresh_data
        
        # Find and update the trade
        trade_updated = False
        for i, trade in enumerate(st.session_state.trades):
            if trade['id'] == trade_id:
                # Always set to Manual Close for manual closures
                st.session_state.trades[i]['outcome'] = 'Manual Close'
                st.session_state.trades[i]['result'] = 'Closed'  # Neutral result
                trade_updated = True
                
                # Update Google Sheets
                if st.session_state.sheets_connected:
                    update_trade_in_sheets(st.session_state.trades[i])
                break
        
        if trade_updated:
            st.success(f"✅ Trade #{trade_id} manually closed!")
            return True
        else:
            st.error(f"❌ Trade #{trade_id} not found")
            return False
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

def adjust_trade_sl_tp(trade_id, new_sl, new_tp):
    """Adjust Stop Loss and Take Profit for a trade"""
    try:
        # Validate inputs
        if new_sl <= 0 or new_tp <= 0:
            st.error("SL and TP must be positive values")
            return False
            
        # Find the trade in session state
        for trade in st.session_state.trades:
            if trade['id'] == trade_id:
                # Update the trade values
                trade['sl'] = float(new_sl)
                trade['target'] = float(new_tp)
                trade['risk'] = abs(trade['entry'] - trade['sl'])
                trade['reward'] = abs(trade['target'] - trade['entry'])
                trade['rrRatio'] = trade['reward'] / trade['risk'] if trade['risk'] > 0 else 0
                
                # Update in Google Sheets if connected
                if st.session_state.sheets_connected:
                    return update_trade_in_sheets(trade)
                else:
                    return True  # Success for local mode
        
        return False  # Trade not found
    except Exception as e:
        st.error(f"Error adjusting trade: {e}")
        return False

# Page configuration
st.set_page_config(
    page_title="The War Zone - Forex Trading Analytics",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f3f4f6;
    }
    
    .war-zone-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 3rem 1.5rem 2rem 1.5rem;
        border-radius: 0;
        margin: -1rem -1rem 0 -1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .war-zone-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") repeat;
        pointer-events: none;
    }
    
    .war-zone-title {
        font-size: 4rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        letter-spacing: 2px;
        position: relative;
        z-index: 1;
    }
    
    .war-zone-subtitle {
        font-size: 1.2rem;
        font-style: italic;
        margin: 1rem 0 0.5rem 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .war-zone-author {
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        opacity: 0.8;
        position: relative;
        z-index: 1;
    }
    
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
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stDeployButton {display: none;}
    
    .main-content {
        padding: 1.5rem;
        max-width: 90rem;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with optimized data loading
if 'trades' not in st.session_state:
    st.session_state.trades = load_trades_from_sheets()
    st.session_state.last_data_hash = hash(str(st.session_state.trades))
    
if 'sheets_connected' not in st.session_state:
    connection = init_connection()
    st.session_state.sheets_connected = connection is not None
    # Silently setup Google Sheets if connected (non-blocking)
    if st.session_state.sheets_connected:
        try:
            setup_google_sheet_silently()
        except:
            pass

# Optimized real-time updates
if st.session_state.sheets_connected:
    auto_refresh_trades()

# Header - The War Zone
st.markdown("""
<div class="war-zone-header">
    <h1 class="war-zone-title">THE WAR ZONE</h1>
    <p class="war-zone-subtitle">"Don't be afraid to give up the good to go for the great."</p>
    <p class="war-zone-author">— John D. Rockefeller</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Refresh Controls at the top
refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 2, 1])

with refresh_col2:
    refresh_container = st.container()
    with refresh_container:
        button_col, timer_col = st.columns([1, 2])
        
        with button_col:
            if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
                with st.spinner("Refreshing..."):
                    force_refresh_data()
                    st.success("Data refreshed!")
                    time.sleep(1)
                    st.rerun()
        
        with timer_col:
            if st.session_state.sheets_connected:
                # Calculate time until next auto-refresh
                time_since_last = time.time() - st.session_state.get('last_auto_refresh', 0)
                time_until_next = max(0, REAL_TIME_UPDATE_INTERVAL - time_since_last)
                
                if time_until_next > 0:
                    minutes = int(time_until_next // 60)
                    seconds = int(time_until_next % 60)
                    if minutes > 0:
                        next_refresh_text = f"Next auto-refresh in {minutes}m {seconds}s"
                    else:
                        next_refresh_text = f"Next auto-refresh in {seconds}s"
                else:
                    next_refresh_text = "Auto-refreshing now..."
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; height: 2.5rem; padding-left: 1rem;">
                    <span style="color: #10b981; font-size: 0.875rem; font-weight: 500;">
                        ⚡ {next_refresh_text}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="display: flex; align-items: center; height: 2.5rem; padding-left: 1rem;">
                    <span style="color: #6b7280; font-size: 0.875rem;">
                        📱 Local mode - Manual refresh only
                    </span>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# Live Price Monitoring
st.markdown("### 📊 Live Price Monitor")

monitor_col1, monitor_col2, monitor_col3 = st.columns([1, 1, 1])

with monitor_col1:
    try:
        api_key_available = bool(st.secrets.get("twelvedata", {}).get("api_key"))
    except:
        api_key_available = False
    
    if api_key_available:
        if st.button("🔍 Check Live Prices", type="secondary", use_container_width=True):
            with st.spinner("Checking market prices..."):
                updates = check_and_update_trades()
                if updates > 0:
                    st.success(f"✅ Updated {updates} trade(s)!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("ℹ️ No trades updated")
    else:
        st.button("🔑 API Key Required", disabled=True, use_container_width=True)
        with st.expander("Setup Instructions"):
            st.markdown("""
            **To enable live price monitoring:**
            1. Sign up at [twelvedata.com](https://twelvedata.com) 
            2. Get your free API key
            3. Add to Streamlit secrets:
            ```toml
            [twelvedata]
            api_key = "your_key_here"
            ```
            """)

with monitor_col2:
    if api_key_available:
        auto_monitor = st.checkbox("🔄 Auto-monitor trades")
        if auto_monitor:
            check_interval = st.selectbox("Check every:", [15, 30, 60, 120], format_func=lambda x: f"{x} seconds")
            
            # Initialize session state for auto-refresh counter
            if 'auto_refresh_count' not in st.session_state:
                st.session_state.auto_refresh_count = 0
            
            # Auto-refresh component
            count = st_autorefresh(
                interval=check_interval * 1000, 
                key="live_monitor",
                limit=None
            )
            
            # Perform automatic check
            if count > 0:
                updates = check_and_update_trades()
                if updates > 0:
                    st.success(f"🔔 Auto-updated {updates} trade(s)!")
                    st.session_state.auto_refresh_count += updates

with monitor_col3:
    # Show monitoring status
    open_trades = [t for t in st.session_state.trades if t.get("outcome", "") not in ("Target Hit", "SL Hit")]
    total_open = len(open_trades)
    
    st.metric("📈 Open Trades", total_open)
    
    if total_open > 0 and api_key_available:
        unique_instruments = len(set(t.get('instrument', '') for t in open_trades))
        unique_traders = len(set(t.get('trader', '') for t in open_trades))
        
        st.markdown(f"""
        <div style="font-size: 0.8rem; color: #666; text-align: center; margin-top: 0.5rem;">
            📊 {unique_instruments} instruments<br>
            👥 {unique_traders} traders
        </div>
        """, unsafe_allow_html=True)
    elif total_open == 0:
        st.markdown("""
        <div style="font-size: 0.8rem; color: #999; text-align: center; margin-top: 0.5rem;">
            All trades closed
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

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
            <span style="font-weight: 600;">Add New Trade Setup</span>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6,9 12,15 18,9"></polyline>
        </svg>
    </div>
    <div class="card-body">
""", unsafe_allow_html=True)

# Information box
st.info("💡 Enter your trade setup details below. The system will automatically monitor live prices and update outcomes when your target or stop loss is hit.")

# First Row of Form
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="form-group"><label>Trader</label></div>', unsafe_allow_html=True)
    trader = st.selectbox("", ["Select Trader", "Waithaka", "Wallace", "Max"], key="trader_select", label_visibility="collapsed")

with col2:
    st.markdown('<div class="form-group"><label>Instrument</label></div>', unsafe_allow_html=True)
    instrument = st.selectbox("", [
        "Select Instrument", 
        "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
        "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "AUDJPY", "CADJPY",
        "USOIL", "BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD",
        "US30", "NAS100", "SPX500", "FTSE100", "DAX30",
        "NGAS", "COPPER", "SILVER", "XAGUSD", "USTECH"
    ], key="instrument_select", label_visibility="collapsed")

with col3:
    st.markdown('<div class="form-group"><label>Entry Price</label></div>', unsafe_allow_html=True)
    entry_price = st.number_input("", min_value=0.0, format="%.5f", key="entry_input", label_visibility="collapsed")

with col4:
    st.markdown('<div class="form-group"><label>Date</label></div>', unsafe_allow_html=True)
    trade_date = st.date_input("", value=date.today(), key="date_input", label_visibility="collapsed")

# Second Row of Form
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown('<div class="form-group"><label>Stop Loss (SL)</label></div>', unsafe_allow_html=True)
    sl_price = st.number_input("", min_value=0.0, format="%.5f", key="sl_input", label_visibility="collapsed")

with col6:
    st.markdown('<div class="form-group"><label>Target Price</label></div>', unsafe_allow_html=True)
    target_price = st.number_input("", min_value=0.0, format="%.5f", key="target_input", label_visibility="collapsed")

with col7:
    # Calculate and display risk automatically
    if entry_price > 0 and sl_price > 0:
        risk = abs(entry_price - sl_price)
        st.markdown(f'<div class="form-group"><label>Risk</label><div style="padding: 0.5rem; background: #f8f9fa; border-radius: 0.25rem; margin-top: 0.5rem;">{risk:.5f}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="form-group"><label>Risk</label><div style="padding: 0.5rem; background: #f8f9fa; border-radius: 0.25rem; margin-top: 0.5rem;">0.00000</div></div>', unsafe_allow_html=True)

with col8:
    # Calculate and display reward automatically
    if entry_price > 0 and target_price > 0:
        reward = abs(target_price - entry_price)
        rr_ratio = reward / risk if risk > 0 else 0
        st.markdown(f'<div class="form-group"><label>Reward/Risk</label><div style="padding: 0.5rem; background: #f8f9fa; border-radius: 0.25rem; margin-top: 0.5rem;">{rr_ratio:.2f}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="form-group"><label>Reward/Risk</label><div style="padding: 0.5rem; background: #f8f9fa; border-radius: 0.25rem; margin-top: 0.5rem;">0.00</div></div>', unsafe_allow_html=True)

# Submit Button
submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])

with submit_col2:
    if st.button("🎯 Submit Trade Setup", type="primary", use_container_width=True):
        # Validation
        if trader == "Select Trader":
            st.error("Please select a trader")
        elif instrument == "Select Instrument":
            st.error("Please select an instrument")
        elif entry_price <= 0:
            st.error("Please enter a valid entry price")
        elif sl_price <= 0:
            st.error("Please enter a valid stop loss")
        elif target_price <= 0:
            st.error("Please enter a valid target price")
        elif sl_price == target_price:
            st.error("Stop loss and target cannot be the same")
        else:
            # Create new trade
            new_trade = {
                'id': max([t['id'] for t in st.session_state.trades], default=0) + 1,
                'date': trade_date.strftime("%Y-%m-%d"),
                'trader': trader,
                'instrument': instrument,
                'entry': float(entry_price),
                'sl': float(sl_price),
                'target': float(target_price),
                'risk': abs(float(entry_price) - float(sl_price)),
                'reward': abs(float(target_price) - float(entry_price)),
                'rrRatio': round(abs(float(target_price) - float(entry_price)) / abs(float(entry_price) - float(sl_price)), 2) if abs(float(entry_price) - float(sl_price)) > 0 else 0,
                'outcome': "Open",
                'result': "Open"
            }
            
            # Save to Google Sheets if connected, otherwise to session state
            if st.session_state.sheets_connected:
                success = save_trade_to_sheets(new_trade)
                if success:
                    st.session_state.trades.append(new_trade)
                    st.success("Trade setup saved successfully!")
                    # Clear form by rerunning
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to save trade to Google Sheets")
            else:
                st.session_state.trades.append(new_trade)
                st.success("Trade setup saved locally!")
                # Clear form by rerunning
                time.sleep(1)
                st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("---")

# Trading Analytics Dashboard
st.markdown("### 📈 Trading Analytics Dashboard")

# Calculate metrics
total_trades = len(st.session_state.trades)
closed_trades = [t for t in st.session_state.trades if t['outcome'] in ['Target Hit', 'SL Hit']]
open_trades = [t for t in st.session_state.trades if t['outcome'] == 'Open']
manual_closures = [t for t in st.session_state.trades if t['outcome'] == 'Manual Close']
winning_trades = [t for t in closed_trades if t['result'] == 'Win']

# Calculate win rate AFTER defining the variables
win_rate = len(winning_trades) / len(closed_trades) * 100 if closed_trades else 0
avg_rr = np.mean([t['rrRatio'] for t in closed_trades]) if closed_trades else 0
total_pnl = sum([t['reward'] if t['result'] == 'Win' else -t['risk'] for t in closed_trades])

# Display metrics
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Total Trades", total_trades, f"{len(open_trades)} open")

with metric_col2:
    st.metric("Market Closures", len(closed_trades), f"{len(manual_closures)} manual")

with metric_col3:
    st.metric("Win Rate", f"{win_rate:.1f}%", f"{len(winning_trades)}/{len(closed_trades)}" if closed_trades else "0/0")

with metric_col4:
    st.metric("Total P&L", f"{total_pnl:+.2f}", "Market trades")

st.markdown("---")
# DEBUG FUNCTION - ADD THIS RIGHT HERE
def debug_close_trade(trade_id):
    """Debug version to see what's happening"""
    try:
        st.write("🔍 DEBUG: Starting close_trade function")
        st.write(f"🔍 DEBUG: Looking for trade ID: {trade_id}")
        
        # Show current trades
        st.write("🔍 DEBUG: Current trades in session state:")
        for i, trade in enumerate(st.session_state.trades):
            st.write(f"  Trade {i}: ID={trade['id']}, Outcome={trade['outcome']}")
            if trade['id'] == trade_id:
                st.write(f"  ✅ FOUND TRADE TO CLOSE: {trade}")
        
        # Try to close the trade
        for i, trade in enumerate(st.session_state.trades):
            if trade['id'] == trade_id:
                st.write("🔍 DEBUG: Updating trade outcome...")
                st.session_state.trades[i]['outcome'] = 'Manual Close'
                st.session_state.trades[i]['result'] = 'Closed'
                
                st.write("🔍 DEBUG: After update:")
                st.write(f"  Trade now: {st.session_state.trades[i]}")
                
                # Try to update Google Sheets
                if st.session_state.sheets_connected:
                    st.write("🔍 DEBUG: Updating Google Sheets...")
                    success = update_trade_in_sheets(st.session_state.trades[i])
                    st.write(f"🔍 DEBUG: Google Sheets update result: {success}")
                
                st.success("✅ Trade closed successfully!")
                return True
        
        st.error("❌ Trade not found")
        return False
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

# Recent Trades Section
st.markdown("### 📋 Recent Trade Setups")

if st.session_state.trades:
    # Display trades in reverse chronological order (newest first)
    recent_trades = sorted(st.session_state.trades, key=lambda x: x['date'], reverse=True)[:10]
    
    for trade in recent_trades:
        # Determine card color based on outcome
        if trade['outcome'] == 'Target Hit':
            border_color = "#10b981"  # Green
            status_emoji = "✅"
            show_buttons = False
        elif trade['outcome'] == 'SL Hit':
            border_color = "#ef4444"  # Red
            status_emoji = "❌"
            show_buttons = False
        else:
            border_color = "#3b82f6"  # Blue
            status_emoji = "⏳"
            show_buttons = True  # Only show buttons for open trades
        
        st.markdown(f"""
        <div class="trade-card" style="border-left: 4px solid {border_color};">
            <div class="card-header">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: {border_color}; border-radius: 50%; padding: 0.25rem; margin-right: 0.75rem;">
                            {status_emoji}
                        </div>
                        <div>
                            <strong>{trade['instrument']}</strong> • {trade['trader']} • {trade['date']}
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <span>ID: {trade['id']}</span>
                        <span style="background-color: {'#10b981' if trade['rrRatio'] >= 1 else '#f59e0b'}; 
                                    color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;">
                            R:R {trade['rrRatio']:.2f}
                        </span>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                    <div>
                        <strong>Entry</strong><br>
                        {trade['entry']:.5f}
                    </div>
                    <div>
                        <strong>Stop Loss</strong><br>
                        {trade['sl']:.5f}
                    </div>
                    <div>
                        <strong>Target</strong><br>
                        {trade['target']:.5f}
                    </div>
                    <div>
                      <strong>Status</strong><br>
                      {trade['outcome']}
                      {" 🏁" if trade['outcome'] == 'Manual Close' else " ⚡" if trade['outcome'] in ['Target Hit', 'SL Hit'] else ""}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
                          # Add the actual Streamlit buttons (functional) - ONLY for open trades
        if show_buttons:
            st.markdown("**Trade Actions:**")
            
            # Create columns for the buttons
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                close_key = f"close_{trade['id']}_{trade['entry']}_{trade['sl']}"
                if st.button(f"❌ Close Trade #{trade['id']}", key=close_key, use_container_width=True):
                    if close_trade(trade['id']):
                        time.sleep(1)
                        st.rerun()
            
            with button_col2:
                adjust_key = f"adjust_{trade['id']}_{trade['entry']}_{trade['sl']}"
                if st.button(f"⚙️ Adjust SL/TP #{trade['id']}", key=adjust_key, use_container_width=True):
                    # Show adjustment form
                    st.session_state[f"adjusting_trade_{trade['id']}"] = True
            
            # Adjustment form (appears when Adjust button is clicked)
            if st.session_state.get(f"adjusting_trade_{trade['id']}"):
                st.markdown("---")
                st.markdown(f"#### ⚙️ Adjust Trade #{trade['id']}")
                
                # Current values display
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current SL", f"{trade['sl']:.5f}")
                with col2:
                    st.metric("Current TP", f"{trade['target']:.5f}")
                
                # Adjustment inputs
                adj_col1, adj_col2 = st.columns(2)
                with adj_col1:
                    new_sl = st.number_input("New Stop Loss", value=float(trade['sl']), key=f"sl_{trade['id']}")
                with adj_col2:
                    new_tp = st.number_input("New Take Profit", value=float(trade['target']), key=f"tp_{trade['id']}")
                
                # Calculate and display new risk/reward
                new_risk = abs(trade['entry'] - new_sl)
                new_reward = abs(new_tp - trade['entry'])
                new_rr = new_reward / new_risk if new_risk > 0 else 0
                
                st.info(f"**New R:R Ratio:** {new_rr:.2f} | **Risk:** {new_risk:.5f} | **Reward:** {new_reward:.5f}")
                
                # Action buttons
                adj_col3, adj_col4 = st.columns(2)
                with adj_col3:
                    if st.button("✅ Apply Changes", key=f"apply_{trade['id']}", use_container_width=True):
                        if adjust_trade_sl_tp(trade['id'], new_sl, new_tp):
                            st.session_state[f"adjusting_trade_{trade['id']}"] = False
                            st.rerun()
                with adj_col4:
                    if st.button("❌ Cancel", key=f"cancel_{trade['id']}", use_container_width=True):
                        st.session_state[f"adjusting_trade_{trade['id']}"] = False
                        st.rerun()
                
                st.markdown("---")
            
            st.markdown("---")
else:
    st.info("No trades recorded yet. Add your first trade setup above!")

# Trader Performance Rankings
st.markdown("### 🏆 Trader Performance Rankings")

if st.session_state.trades:
    # Calculate trader statistics
    trader_stats = {}
    
    for trade in st.session_state.trades:
        trader_name = trade['trader']
        if trader_name not in trader_stats:
            trader_stats[trader_name] = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'open_trades': 0,
                'total_pnl': 0,
                'total_risk': 0,
                'total_reward': 0
            }
        
        stats = trader_stats[trader_name]
        stats['total_trades'] += 1
        
        if trade['outcome'] == 'Open':
            stats['open_trades'] += 1
        elif trade['result'] == 'Win':
            stats['winning_trades'] += 1
            stats['total_pnl'] += trade['reward']
            stats['total_reward'] += trade['reward']
        elif trade['result'] == 'Loss':
            stats['losing_trades'] += 1
            stats['total_pnl'] -= trade['risk']
            stats['total_risk'] += trade['risk']
    
    # Convert to list and sort by P&L
    trader_ranking = []
    for trader, stats in trader_stats.items():
        closed_trades_count = stats['winning_trades'] + stats['losing_trades']
        win_rate = (stats['winning_trades'] / closed_trades_count * 100) if closed_trades_count > 0 else 0
        
        trader_ranking.append({
            'trader': trader,
            'total_pnl': stats['total_pnl'],
            'win_rate': win_rate,
            'total_trades': stats['total_trades'],
            'closed_trades': closed_trades_count,
            'open_trades': stats['open_trades']
        })
    
    trader_ranking.sort(key=lambda x: x['total_pnl'], reverse=True)
    
    # Display rankings
    for i, trader_data in enumerate(trader_ranking[:5]):  # Top 5 traders
        rank_class = "rank-1" if i == 0 else "rank-2" if i == 1 else "rank-3" if i == 2 else ""
        
        st.markdown(f"""
        <div class="rank-item">
            <div class="rank-number {rank_class}">{i+1}</div>
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 1.1rem;">{trader_data['trader']}</strong>
                        <div style="font-size: 0.875rem; color: #666;">
                            {trader_data['total_trades']} trades ({trader_data['open_trades']} open)
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <strong style="color: {'#10b981' if trader_data['total_pnl'] >= 0 else '#ef4444'}; font-size: 1.1rem;">
                            {trader_data['total_pnl']:+.2f}
                        </strong>
                        <div style="font-size: 0.875rem; color: #666;">
                            {trader_data['win_rate']:.1f}% win rate
                        </div>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {trader_data['win_rate']}%;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No trader data available yet. Add trades to see rankings.")

st.markdown("</div>", unsafe_allow_html=True)

# Navigation Section
st.markdown("---")
st.markdown("### 🚀 Quick Navigation")

col1, col2 = st.columns(2)

with col1:
    if st.button("👤 Trader Analysis", use_container_width=True):
        st.switch_page("pages/Trader Analysis.py")

with col2:
    if st.button("📊 Pair Analysis", use_container_width=True):
        st.switch_page("pages/Pair Analysis.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem; padding: 2rem 0;">
    <strong>The War Zone</strong> • Forex Trading Analytics Dashboard<br>
    Real-time monitoring • Risk management • Performance tracking
</div>
""", unsafe_allow_html=True)









