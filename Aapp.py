import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import numpy as np
import json
import os
import requests
import time
from google.oauth2.service_account import Credentials
import gspread
from streamlit_autorefresh import st_autorefresh

# Google Sheets Configuration
SHEET_NAME = "Forex Trading Analytics"
WORKSHEET_NAME = "Trades"

# Real-time update configuration
REAL_TIME_UPDATE_INTERVAL = 10  # Update every 10 seconds (reduced frequency)
CACHE_TTL = 30  # Cache data for 30 seconds (longer cache)

# Live price configuration
PRICE_CHECK_INTERVAL = 15  # Check prices every 15 seconds to avoid API limits

# --- LIVE PRICE INTEGRATION FUNCTIONS ---

def normalize_symbol(pair: str) -> str:
    """Convert pair formats (EURUSD or BTCUSD) => 'EUR/USD' or 'BTC/USD'"""
    pair = pair.strip().upper()
    if "/" in pair:
        return pair
    if len(pair) >= 6:
        return f"{pair[:3]}/{pair[3:]}"
    return pair

@st.cache_data(ttl=60, show_spinner=False)  # Cache prices for 1 minute
def get_live_price(pair: str) -> float:
    """
    Returns the latest price as float or None on failure.
    Works for currency pairs (EURUSD -> EUR/USD) and cryptos (BTCUSD -> BTC/USD).
    """
    symbol = normalize_symbol(pair)
    
    # Try to get API key from secrets
    try:
        api_key = st.secrets.get("twelvedata", {}).get("api_key")
    except:
        api_key = None
    
    if not api_key:
        # Return None silently - we'll show a warning in the UI
        return None

    url = "https://api.twelvedata.com/price"
    try:
        resp = requests.get(
            url, 
            params={"symbol": symbol, "apikey": api_key}, 
            timeout=10
        )
        data = resp.json()
        
        # Successful response: {"price":"YYYY.YY"}
        if "price" in data:
            return float(data["price"])
        else:
            # Error response (rate limit, invalid symbol, etc.)
            return None
    except Exception as e:
        # Network or JSON parse error
        return None

def update_trade_outcomes(trades: list, save_callback=None) -> tuple[list, int]:
    """
    Check each trade against live price and mark outcome if hit.
    Returns (updated_trades, number_of_updates)
    """
    if not trades:
        return trades, 0
    
    updates_made = 0
    updated_trades = []
    
    for trade in trades:
        # Only check open trades (no outcome yet or marked as open)
        current_outcome = trade.get("outcome", "")
        if current_outcome in ("Target Hit", "SL Hit"):
            updated_trades.append(trade)
            continue  # Already resolved
        
        symbol = trade.get("instrument", "")
        if not symbol:
            updated_trades.append(trade)
            continue
        
        # Get live price
        live_price = get_live_price(symbol)
        if live_price is None:
            updated_trades.append(trade)
            continue  # Skip if cannot fetch price
        
        # Get trade parameters
        entry_price = float(trade.get("entry", 0))
        sl_price = float(trade.get("sl", 0))
        target_price = float(trade.get("target", 0))
        
        if entry_price == 0 or (sl_price == 0 and target_price == 0):
            updated_trades.append(trade)
            continue
        
        # Create a copy of the trade for potential updates
        updated_trade = trade.copy()
        trade_updated = False
        
        # Determine if it's a long or short trade
        is_long_trade = target_price > entry_price
        
        if is_long_trade:
            # Long trade: price going up hits target, price going down hits SL
            if target_price > 0 and live_price >= target_price:
                updated_trade["outcome"] = "Target Hit"
                updated_trade["result"] = "Win"
                updated_trade["closed_price"] = live_price
                updated_trade["closed_time"] = datetime.now().isoformat()
                trade_updated = True
            elif sl_price > 0 and live_price <= sl_price:
                updated_trade["outcome"] = "SL Hit"
                updated_trade["result"] = "Loss"
                updated_trade["closed_price"] = live_price
                updated_trade["closed_time"] = datetime.now().isoformat()
                trade_updated = True
        else:
            # Short trade: price going down hits target, price going up hits SL
            if target_price > 0 and live_price <= target_price:
                updated_trade["outcome"] = "Target Hit"
                updated_trade["result"] = "Win"
                updated_trade["closed_price"] = live_price
                updated_trade["closed_time"] = datetime.now().isoformat()
                trade_updated = True
            elif sl_price > 0 and live_price >= sl_price:
                updated_trade["outcome"] = "SL Hit"
                updated_trade["result"] = "Loss"
                updated_trade["closed_price"] = live_price
                updated_trade["closed_time"] = datetime.now().isoformat()
                trade_updated = True
        
        if trade_updated:
            updates_made += 1
        
        updated_trades.append(updated_trade)
    
    # Save if changes were made and callback provided
    if updates_made > 0 and callable(save_callback):
        try:
            save_callback(updated_trades)
        except Exception as e:
            st.warning(f"Auto-save failed after updating outcomes: {e}")
    
    return updated_trades, updates_made

def get_open_trades_summary(trades: list) -> dict:
    """Get summary of open trades with live prices"""
    open_trades = [t for t in trades if t.get("outcome", "") not in ("Target Hit", "SL Hit")]
    
    summary = {
        "total_open": len(open_trades),
        "instruments": set(),
        "traders": set(),
        "total_risk": 0.0,
        "total_potential_reward": 0.0
    }
    
    for trade in open_trades:
        summary["instruments"].add(trade.get("instrument", ""))
        summary["traders"].add(trade.get("trader", ""))
        summary["total_risk"] += float(trade.get("risk", 0))
        summary["total_potential_reward"] += float(trade.get("reward", 0))
    
    return summary

# --- EXISTING FUNCTIONS (keep all your existing functions here) ---

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
        
        # Process data efficiently
        processed_records = []
        for i, row in enumerate(all_values[1:], 1):  # Skip headers
            if not any(str(cell).strip() for cell in row):
                continue
                
            try:
                while len(row) < 14:  # Extended to include closed_price and closed_time
                    row.append('')
                
                # Only process rows with complete valid data
                if (row[2] and row[3] and row[4] and row[5] and row[6] and 
                    str(row[2]).strip() not in ['', 'trader'] and 
                    str(row[3]).strip() not in ['', 'instrument'] and
                    str(row[4]).strip() not in ['', '0.0', '0'] and
                    str(row[10]).strip() not in ['', 'outcome'] and
                    str(row[11]).strip() not in ['', 'result']):
                    
                    try:
                        entry_val = float(row[4])
                        sl_val = float(row[5]) 
                        target_val = float(row[6])
                        
                        # Skip if all prices are zero
                        if entry_val == 0.0 and sl_val == 0.0 and target_val == 0.0:
                            continue
                            
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
                            'outcome': str(row[10]).strip(),
                            'result': str(row[11]).strip(),
                            'closed_price': float(row[12]) if row[12] and str(row[12]).replace('.', '').replace('-', '').isdigit() else None,
                            'closed_time': str(row[13]).strip() if row[13] else None
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
        
        # Prepare row data efficiently (extended with closed_price and closed_time)
        row_data = [
            str(trade_data['id']), str(trade_data['date']), str(trade_data['trader']),
            str(trade_data['instrument']), float(trade_data['entry']), float(trade_data['sl']),
            float(trade_data['target']), float(trade_data['risk']), float(trade_data['reward']),
            float(trade_data['rrRatio']), str(trade_data['outcome']), str(trade_data['result']),
            trade_data.get('closed_price', ''), trade_data.get('closed_time', '')
        ]
        
        # Single API call
        sheet.append_row(row_data, value_input_option='RAW')
        return True
        
    except:
        return False

def save_all_trades_to_sheets(trades):
    """Save all trades to Google Sheets (overwrites existing data)"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Clear existing data
        sheet.clear()
        
        # Add headers (extended with new fields)
        headers = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                  'risk', 'reward', 'rrRatio', 'outcome', 'result', 'closed_price', 'closed_time']
        sheet.append_row(headers)
        
        # Add all trades
        for trade in trades:
            row_data = [
                str(trade['id']), str(trade['date']), str(trade['trader']),
                str(trade['instrument']), float(trade['entry']), float(trade['sl']),
                float(trade['target']), float(trade['risk']), float(trade['reward']),
                float(trade['rrRatio']), str(trade['outcome']), str(trade['result']),
                trade.get('closed_price', ''), trade.get('closed_time', '')
            ]
            sheet.append_row(row_data, value_input_option='RAW')
        
        return True
        
    except Exception as e:
        st.error(f"Failed to save to sheets: {e}")
        return False

# [Keep all your other existing functions: delete_trade_from_sheets, setup_google_sheet_silently, 
#  load_fallback_data, force_refresh_data, auto_refresh_trades, etc.]

def load_fallback_data():
    """Load fallback data when Google Sheets is not available"""
    return [
        { 'id': 1, 'date': '2023-10-08', 'trader': 'Waithaka', 'instrument': 'XAUUSD', 'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50, 'rrRatio': 1.73, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 2, 'date': '2023-10-07', 'trader': 'Wallace', 'instrument': 'USOIL', 'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70, 'rrRatio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss' },
        { 'id': 3, 'date': '2023-10-06', 'trader': 'Max', 'instrument': 'BTCUSD', 'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00, 'rrRatio': 1.40, 'outcome': 'Target Hit', 'result': 'Win' },
        { 'id': 4, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'EURUSD', 'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450, 'rrRatio': 1.80, 'outcome': '', 'result': '' },  # Open trade
        { 'id': 5, 'date': '2023-10-04', 'trader': 'Wallace', 'instrument': 'US30', 'entry': 34500.00, 'sl': 34200.00, 'target': 34900.00, 'risk': 300.00, 'reward': 400.00, 'rrRatio': 1.33, 'outcome': '', 'result': '' }  # Open trade
    ]

# --- UI INTEGRATION (add this after your existing refresh controls) ---

def render_live_price_controls():
    """Render live price checking controls"""
    st.markdown("### 📊 Live Market Monitor")
    
    # Check API key availability
    try:
        api_key_available = bool(st.secrets.get("twelvedata", {}).get("api_key"))
    except:
        api_key_available = False
    
    if not api_key_available:
        st.warning("⚠️ Twelve Data API key not configured. Add `twelvedata.api_key` to your Streamlit secrets for live price monitoring.")
        return
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Check Live Prices Now", type="primary", use_container_width=True):
            with st.spinner("Checking live prices..."):
                # Define save callback
                def save_callback(updated_trades):
                    if st.session_state.sheets_connected:
                        save_all_trades_to_sheets(updated_trades)
                    # Always update session state
                    st.session_state.trades = updated_trades
                
                # Update trade outcomes
                updated_trades, updates_made = update_trade_outcomes(
                    st.session_state.trades, 
                    save_callback=save_callback
                )
                
                if updates_made > 0:
                    st.success(f"✅ Updated {updates_made} trade(s) based on live prices!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("ℹ️ No trades were updated (no TP/SL conditions met)")
    
    with col2:
        # Auto-refresh configuration
        auto_refresh_enabled = st.checkbox("Auto-check live prices", value=False)
        if auto_refresh_enabled:
            refresh_interval = st.selectbox(
                "Check interval", 
                [15, 30, 60, 120], 
                index=0,
                format_func=lambda x: f"{x} seconds"
            )
            
            # Auto-refresh component
            count = st_autorefresh(
                interval=refresh_interval * 1000, 
                key="live_price_refresh",
                limit=None  # No limit
            )
            
            # Perform update on auto-refresh
            if count > 0:  # Skip first render (count=0)
                def save_callback(updated_trades):
                    if st.session_state.sheets_connected:
                        save_all_trades_to_sheets(updated_trades)
                    st.session_state.trades = updated_trades
                
                updated_trades, updates_made = update_trade_outcomes(
                    st.session_state.trades, 
                    save_callback=save_callback
                )
                
                if updates_made > 0:
                    st.success(f"🔔 Auto-update: {updates_made} trade(s) closed!")
    
    with col3:
        # Open trades summary
        summary = get_open_trades_summary(st.session_state.trades)
        st.metric("Open Trades", summary["total_open"])
        
        if summary["total_open"] > 0:
            st.markdown(f"""
            <div style="font-size: 0.8rem; color: #666;">
                📈 {len(summary['instruments'])} instruments<br>
                👥 {len(summary['traders'])} traders<br>
                💰 Risk: ${summary['total_risk']:.2f}<br>
                🎯 Potential: ${summary['total_potential_reward']:.2f}
            </div>
            """, unsafe_allow_html=True)

# --- ADD THIS TO YOUR MAIN APP AFTER THE REFRESH CONTROLS ---
# Replace your existing refresh controls section with this:

# Page configuration (keep existing)
st.set_page_config(
    page_title="The War Zone - Forex Trading Analytics",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [Keep all your existing CSS and initialization code]

# Header - The War Zone (keep existing)
st.markdown("""
<div class="war-zone-header">
    <h1 class="war-zone-title">THE WAR ZONE</h1>
    <p class="war-zone-subtitle">"Don't be afraid to give up the good to go for the great."</p>
    <p class="war-zone-author">— John D. Rockefeller</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Enhanced refresh controls with live prices
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

# Add live price controls
render_live_price_controls()

st.markdown("---")

# [Continue with the rest of your existing app code...]
