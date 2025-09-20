 # Create dynamic donut chart based on current data
if rankings and len(rankings) > 0:
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

# You can also try these common worksheet names if "Trades" doesn't work:
# WORKSHEET_NAME = "Sheet1"  # Default Google Sheets name
# WORKSHEET_NAME = "Trading Data"
# WORKSHEET_NAME = "Forex Trades"

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
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Get all records
        records = sheet.get_all_records()
        
        if not records:
            return load_fallback_data()
        
        # Convert string values back to appropriate types
        processed_records = []
        for record in records:
            try:
                processed_record = {
                    'id': int(record.get('id', 0)),
                    'date': str(record.get('date', '')),
                    'trader': str(record.get('trader', '')),
                    'instrument': str(record.get('instrument', '')),
                    'entry': float(record.get('entry', 0)),
                    'sl': float(record.get('sl', 0)),
                    'target': float(record.get('target', 0)),
                    'risk': float(record.get('risk', 0)),
                    'reward': float(record.get('reward', 0)),
                    'rrRatio': float(record.get('rrRatio', 0)),
                    'outcome': str(record.get('outcome', '')),
                    'result': str(record.get('result', ''))
                }
                processed_records.append(processed_record)
            except (ValueError, TypeError) as e:
                st.warning(f"Skipped malformed record: {record}. Error: {e}")
                continue
        
        return processed_records
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.warning(f"Spreadsheet '{SHEET_NAME}' not found. Using fallback data.")
        return load_fallback_data()
    except gspread.exceptions.WorksheetNotFound:
        st.warning(f"Worksheet '{WORKSHEET_NAME}' not found. Using fallback data.")
        return load_fallback_data()
    except gspread.exceptions.APIError as e:
        st.warning(f"Google Sheets API Error: {e}. Using fallback data.")
        return load_fallback_data()
    except Exception as e:
        st.warning(f"Error loading from Google Sheets: {e}. Using fallback data.")
        return load_fallback_data()

def save_trade_to_sheets(trade_data):
    """Save a single trade to Google Sheets"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        # Open the spreadsheet and worksheet
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Prepare row data in the same order as headers
        row_data = [
            str(trade_data['id']),
            str(trade_data['date']),
            str(trade_data['trader']),
            str(trade_data['instrument']),
            float(trade_data['entry']),
            float(trade_data['sl']),
            float(trade_data['target']),
            float(trade_data['risk']),
            float(trade_data['reward']),
            float(trade_data['rrRatio']),
            str(trade_data['outcome']),
            str(trade_data['result'])
        ]
        
        # Add the row and verify it was added
        response = sheet.append_row(row_data, value_input_option='RAW')
        
        # Check if the response indicates success
        if response and 'updates' in response:
            return True
        else:
            # Even if response format is different, try to verify the row was added
            time.sleep(1)  # Brief delay to allow for propagation
            all_records = sheet.get_all_records()
            # Check if our trade was added (look for matching ID)
            for record in all_records:
                if str(record.get('id', '')) == str(trade_data['id']):
                    return True
            return False
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Spreadsheet not found. Please check the SHEET_NAME or create the spreadsheet.")
        return False
    except gspread.exceptions.WorksheetNotFound:
        st.error("Worksheet not found. Please check the WORKSHEET_NAME or create the worksheet.")
        return False
    except gspread.exceptions.APIError as e:
        st.error(f"Google Sheets API Error: {e}")
        return False
    except Exception as e:
        st.error(f"Unexpected error saving to Google Sheets: {e}")
        return False

def delete_trade_from_sheets(trade_id):
    """Delete a trade from Google Sheets"""
    try:
        gc = init_connection()
        if gc is None:
            return False
        
        spreadsheet = gc.open(SHEET_NAME)
        sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Find the row with the trade ID
        try:
            cell = sheet.find(str(trade_id))
            if cell and cell.col == 1:  # Make sure it's in the ID column
                sheet.delete_rows(cell.row)
                return True
            else:
                st.error(f"Trade ID {trade_id} not found in spreadsheet.")
                return False
        except gspread.exceptions.CellNotFound:
            st.error(f"Trade ID {trade_id} not found in spreadsheet.")
            return False
        
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Spreadsheet not found. Please check the SHEET_NAME.")
        return False
    except gspread.exceptions.WorksheetNotFound:
        st.error("Worksheet not found. Please check the WORKSHEET_NAME.")
        return False
    except gspread.exceptions.APIError as e:
        st.error(f"Google Sheets API Error: {e}")
        return False
    except Exception as e:
        st.error(f"Unexpected error deleting from Google Sheets: {e}")
        return False

def setup_google_sheet():
    """Set up the Google Sheet with proper headers if it doesn't exist"""
    try:
        gc = init_connection()
        if gc is None:
            st.error("Cannot setup Google Sheets - connection failed.")
            return False
        
        # Step 1: Handle the spreadsheet
        st.info("🔍 Step 1: Checking for spreadsheet...")
        try:
            spreadsheet = gc.open(SHEET_NAME)
            st.success(f"✅ Found existing spreadsheet: '{SHEET_NAME}'")
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet
            st.info(f"📝 Creating new spreadsheet: '{SHEET_NAME}'")
            spreadsheet = gc.create(SHEET_NAME)
            st.success(f"✅ Created new spreadsheet: '{SHEET_NAME}'")
        
        # Step 2: Handle the worksheet
        st.info("🔍 Step 2: Checking for 'Trades' worksheet...")
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            st.success(f"✅ Found existing worksheet: '{WORKSHEET_NAME}'")
        except gspread.WorksheetNotFound:
            # Create new worksheet named "Trades"
            st.info(f"📝 Creating new worksheet: '{WORKSHEET_NAME}'")
            worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=12)
            st.success(f"✅ Created new worksheet: '{WORKSHEET_NAME}'")
        
        # Step 3: Setup headers
        st.info("🔍 Step 3: Checking worksheet headers...")
        try:
            headers = worksheet.row_values(1)
            expected_headers = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 'risk', 'reward', 'rrRatio', 'outcome', 'result']
            
            if not headers or len(headers) == 0 or headers != expected_headers:
                # Clear first row and set proper headers
                st.info("📝 Setting up column headers...")
                worksheet.clear()  # Clear the worksheet first
                worksheet.append_row(expected_headers)
                st.success("✅ Added column headers to worksheet")
            else:
                st.success("✅ Headers already exist and are correct")
        except Exception as e:
            st.warning(f"⚠️ Could not check/set headers: {e}")
            # Try to add headers anyway
            try:
                headers = ['id', 'date', 'trader', 'instrument', 'entry', 'sl', 'target', 'risk', 'reward', 'rrRatio', 'outcome', 'result']
                worksheet.append_row(headers)
                st.success("✅ Added column headers")
            except:
                st.error("❌ Failed to add headers")
        
        # Step 4: Provide user information
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        st.success("🎉 Setup Complete!")
        
        # Show final summary
        st.markdown("""
        ### ✅ Setup Summary:
        - **Spreadsheet**: Ready ✅
        - **Worksheet 'Trades'**: Ready ✅  
        - **Column Headers**: Ready ✅
        - **Ready for Trading Data**: Yes ✅
        """)
        
        st.info(f"🔗 **Your Google Sheet**: [Click here to open]({spreadsheet_url})")
        st.info("💡 **Next Steps**: You can now add trades and they will automatically sync to Google Sheets!")
        
        # Test the setup by trying to add a sample row (then remove it)
        try:
            # Add a test row to verify everything works
            test_row = ['TEST', 'TEST', 'TEST', 'TEST', 0, 0, 0, 0, 0, 0, 'TEST', 'TEST']
            worksheet.append_row(test_row)
            # Immediately delete the test row
            worksheet.delete_rows(2, 2)  # Delete row 2 (the test row)
            st.success("✅ Connection test passed - ready to sync trades!")
        except Exception as e:
            st.warning(f"⚠️ Setup complete but sync test failed: {e}")
        
        return True
        
    except gspread.exceptions.APIError as e:
        st.error(f"❌ Google Sheets API Error during setup: {e}")
        st.info("💡 This might be due to API limits or permissions. Please wait a moment and try again.")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error during Google Sheets setup: {e}")
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
    
    # Make the setup button more prominent
    st.markdown("""
    <div style="background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
        <h4 style="color: #92400e; margin: 0 0 0.5rem 0;">🚀 Ready to Enable Cloud Sync?</h4>
        <p style="color: #92400e; margin: 0; font-size: 0.875rem;">
            Click the button below to automatically create your "Trades" worksheet and enable real-time synchronization across all your devices!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_setup1, col_setup2, col_setup3 = st.columns([1, 2, 1])
    with col_setup2:
        if st.button("🔧 Setup Google Sheets Integration", use_container_width=True, type="primary"):
            with st.spinner("🔄 Setting up your Google Sheets integration..."):
                if setup_google_sheet():
                    st.session_state.sheets_connected = True
                    st.cache_data.clear()  # Clear cache to reload data
                    st.balloons()  # Celebration animation!
                    time.sleep(3)  # Give user time to see all the success messages
                    st.rerun()
                else:
                    st.error("❌ Setup failed. Please check the error messages above and try again.")
else:
    # Show connection info when connected
    st.markdown("""
    <div style="background-color: #dcfce7; border: 1px solid #16a34a; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 0.75rem;">✅</span>
            <div>
                <h4 style="color: #15803d; margin: 0 0 0.25rem 0;">Google Sheets Connected!</h4>
                <p style="color: #15803d; margin: 0; font-size: 0.875rem;">
                    Your trades are now syncing automatically across all devices. Add a trade below to test it!
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_info1, col_info2, col_info3 = st.columns([1, 2, 1])
    with col_info2:        
        # Add a test connection button
        if st.button("🔍 Test Connection & View Sheet", use_container_width=True):
            try:
                gc = init_connection()
                if gc:
                    try:
                        spreadsheet = gc.open(SHEET_NAME)
                        st.success(f"✅ Successfully connected to spreadsheet: '{SHEET_NAME}'")
                        
                        # List all available worksheets
                        worksheets = spreadsheet.worksheets()
                        worksheet_names = [ws.title for ws in worksheets]
                        st.info(f"📋 Available worksheets: {', '.join(worksheet_names)}")
                        
                        # Try to access the target worksheet
                        try:
                            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
                            st.success(f"✅ Successfully accessed worksheet: '{WORKSHEET_NAME}'")
                            
                            # Try to get records
                            try:
                                records = worksheet.get_all_records()
                                record_count = len(records)
                                st.success(f"✅ Found {record_count} trades in the worksheet")
                                
                                # Show first few column headers to verify structure
                                if records:
                                    headers = list(records[0].keys()) if records else worksheet.row_values(1)
                                    st.info(f"📊 Column headers: {', '.join(headers[:6])}{'...' if len(headers) > 6 else ''}")
                                else:
                                    headers = worksheet.row_values(1)
                                    if headers:
                                        st.info(f"📊 Column headers: {', '.join(headers[:6])}{'...' if len(headers) > 6 else ''}")
                                    else:
                                        st.warning("⚠️ No headers found - worksheet may be empty")
                                
                            except Exception as e:
                                st.warning(f"⚠️ Could not read worksheet data: {str(e)}")
                                
                        except gspread.WorksheetNotFound:
                            st.error(f"❌ Worksheet '{WORKSHEET_NAME}' not found!")
                            st.info(f"💡 Available worksheets: {', '.join(worksheet_names)}")
                            st.info("💡 Click 'Setup Google Sheets Integration' to create the missing worksheet.")
                        except Exception as ws_error:
                            st.error(f"❌ Error accessing worksheet: {str(ws_error)}")
                        
                        # Always show the spreadsheet URL
                        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
                        st.markdown(f"🔗 **[Open your Google Sheet in browser]({spreadsheet_url})**")
                        
                    except gspread.SpreadsheetNotFound:
                        st.error(f"❌ Spreadsheet '{SHEET_NAME}' not found!")
                        st.info("💡 Click 'Setup Google Sheets Integration' to create the spreadsheet.")
                    except Exception as sheet_error:
                        st.error(f"❌ Error accessing spreadsheet: {str(sheet_error)}")
                else:
                    st.error("❌ Google Sheets connection failed!")
                    st.info("💡 Check your credentials in secrets.toml")
                    
            except Exception as e:
                # Don't show the raw response object, parse it better
                error_msg = str(e)
                if "Response [200]" in error_msg:
                    st.success("✅ Connection successful! (Response 200 indicates success)")
                    st.info("💡 The connection is working - you can try adding trades now!")
                else:
                    st.error(f"❌ Connection test error: {error_msg}")
                st.info("💡 If you see 'Response [200]', that actually means success!")

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
                    try:
                        success = save_trade_to_sheets(new_trade)
                        st.session_state.trades.append(new_trade)
                        
                        if success:
                            st.success("✅ Trade added successfully and synced to Google Sheets!")
                            # Force immediate refresh and clear form
                            force_refresh_data()
                            time.sleep(0.5)  # Brief delay to ensure sync propagation
                        else:
                            st.warning("⚠️ Trade added locally but Google Sheets sync may have failed.")
                            
                        # Always rerun to update the UI with new trade
                        st.rerun()
                        
                    except Exception as e:
                        st.session_state.trades.append(new_trade)
                        error_msg = str(e)
                        if "Response [200]" in error_msg:
                            st.success("✅ Trade added and synced successfully!")
                            force_refresh_data()
                        else:
                            st.error(f"❌ Error syncing to Google Sheets: {error_msg}")
                            st.warning("⚠️ Trade added locally only")
                        st.rerun()
            else:
                st.session_state.trades.append(new_trade)
                st.warning("⚠️ Trade added locally only (Google Sheets not connected)")
            
        else:
            st.error("Please fill in all fields to add a trade.")

st.markdown('</div></div>', unsafe_allow_html=True)

# Real-time sync status and manual refresh
sync_col1, sync_col2, sync_col3, sync_col4 = st.columns([2, 1, 1, 6])

with sync_col1:
    if st.session_state.sheets_connected:
        current_time = datetime.now().strftime('%H:%M:%S')
        st.markdown(f"<small>🔄 <span style='color: #10b981;'>Live sync active</span> • Last check: {current_time}</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small>⚠️ <span style='color: #f59e0b;'>Local mode only</span></small>", unsafe_allow_html=True)

with sync_col2:
    if st.button("🔄", help="Force refresh data from Google Sheets", key="manual_refresh"):
        with st.spinner("Refreshing..."):
            if force_refresh_data():
                st.success("Data refreshed!")
            else:
                st.warning("Refresh completed (local data)")
            time.sleep(1)  # Show the message briefly
            st.rerun()

with sync_col3:
    # Auto-refresh toggle
    auto_refresh_enabled = st.checkbox("⚡", value=True, help="Enable/disable auto-refresh (every 3 seconds)", key="auto_refresh_toggle")
    if not auto_refresh_enabled:
        st.session_state.last_auto_refresh = 0  # Disable auto-refresh

# Main Content Grid
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    # Calculate dynamic rankings based on current data
    if st.session_state.trades and len(st.session_state.trades) > 0:
        trader_stats = {}
        for trade in st.session_state.trades:
            trader = trade.get('trader', '')
            if trader and trader != '':
                if trader not in trader_stats:
                    trader_stats[trader] = {'wins': 0, 'total': 0}
                trader_stats[trader]['total'] += 1
                if trade.get('result', '') == 'Win':
                    trader_stats[trader]['wins'] += 1
        
        # Calculate win rates and sort
        rankings = []
        for trader, stats in trader_stats.items():
            if stats['total'] > 0:  # Only include traders with trades
                win_rate = (stats['wins'] / stats['total']) * 100
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
    
    if rankings and len(rankings) > 0:
        for ranking in rankings:
            rank_class = f"rank-{min(ranking['rank'], 3)}"  # Cap at 3 for styling
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
        st.info("No trades available for rankings. Add some trades to see performance metrics!")
    
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
    if not st.session_state.trades or len(st.session_state.trades) == 0:
        st.info("No trades recorded yet. Add a trade using the form above.")
    else:
        # Header row
        header_cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.8, 1.5, 1])
        headers = ['Date', 'Trader', 'Instrument', 'Entry', 'SL', 'Target', 'Risk', 'Reward', 'R/R Ratio', 'Outcome', 'Result', 'Actions']
        
        for i, header in enumerate(headers):
            with header_cols[i]:
                st.markdown(f'<div style="font-weight: bold; color: #000000; padding: 0.5rem 0; border-bottom: 2px solid #e5e7eb; font-size: 0.875rem;">{header}</div>', unsafe_allow_html=True)
        
        # Create columns for each trade row (sort by ID descending to show newest first)
        sorted_trades = sorted(st.session_state.trades, key=lambda x: x.get('id', 0), reverse=True)
        for i, trade in enumerate(sorted_trades):
            cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.8, 1.5, 1])
            
            with cols[0]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("date", "N/A")}</div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("trader", "N/A")}</div>', unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("instrument", "N/A")}</div>', unsafe_allow_html=True)
            with cols[3]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("entry", 0)}</div>', unsafe_allow_html=True)
            with cols[4]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("sl", 0)}</div>', unsafe_allow_html=True)
            with cols[5]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("target", 0)}</div>', unsafe_allow_html=True)
            with cols[6]:
                risk_val = trade.get("risk", 0)
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{risk_val:.4f}</div>', unsafe_allow_html=True)
            with cols[7]:
                reward_val = trade.get("reward", 0)
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{reward_val:.4f}</div>', unsafe_allow_html=True)
            with cols[8]:
                rr_val = trade.get("rrRatio", 0)
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{rr_val}</div>', unsafe_allow_html=True)
            with cols[9]:
                st.markdown(f'<div style="color: #000000; padding: 0.25rem 0; font-size: 0.875rem;">{trade.get("outcome", "N/A")}</div>', unsafe_allow_html=True)
            with cols[10]:
                result = trade.get('result', 'Unknown')
                if result == 'Win':
                    st.markdown('<span style="background-color: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 12px; font-weight: 500; font-size: 0.75rem;">Win</span>', unsafe_allow_html=True)
                elif result == 'Loss':
                    st.markdown('<span style="background-color: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 12px; font-weight: 500; font-size: 0.75rem;">Loss</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="background-color: #f3f4f6; color: #6b7280; padding: 4px 8px; border-radius: 12px; font-weight: 500; font-size: 0.75rem;">Unknown</span>', unsafe_allow_html=True)
            with cols[11]:
                if st.button("🗑️", key=f"delete_{trade.get('id', i)}_{i}", help="Delete this trade", type="secondary"):
                    # Delete from Google Sheets first
                    if st.session_state.sheets_connected:
                        try:
                            success = delete_trade_from_sheets(trade['id'])
                            st.session_state.trades = [t for t in st.session_state.trades if t.get('id') != trade.get('id')]
                            
                            if success:
                                st.success("✅ Trade deleted and synced!")
                                # Force immediate refresh for real-time sync
                                force_refresh_data()
                            else:
                                st.warning("⚠️ Trade deleted locally, but Google Sheets sync may have failed")
                                
                            st.rerun()
                            
                        except Exception as e:
                            st.session_state.trades = [t for t in st.session_state.trades if t.get('id') != trade.get('id')]
                            error_msg = str(e)
                            if "Response [200]" in error_msg:
                                st.success("✅ Trade deleted and synced successfully!")
                                force_refresh_data()
                            else:
                                st.warning(f"⚠️ Trade deleted locally, sync error: {error_msg}")
                            st.rerun()
                    else:
                        st.session_state.trades = [t for t in st.session_state.trades if t.get('id') != trade.get('id')]
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
    if rankings and len(rankings) > 0:
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
        if len(rankings) >= 1:
            legend_cols = st.columns(min(3, len(rankings)))
            
            for i, ranking in enumerate(rankings[:3]):
                if i < len(legend_cols):
                    with legend_cols[i]:
                        color = colors[i] if i < len(colors) else '#6b7280'
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
        st.info("No data available for performance metrics. Add some trades to see analytics!")
    
    # Trader of the Month (dynamic based on highest win rate)
    if rankings and len(rankings) > 0:
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
    else:
        # Show placeholder when no data
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
            <div style="text-align: center; padding: 1.5rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">🏆</div>
                <h4 style="font-size: 1.25rem; font-weight: bold; color: #6b7280; margin: 0 0 0.5rem 0;">No Data Yet</h4>
                <p style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">Add trades to see top performer</p>
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
    if st.session_state.trades and len(st.session_state.trades) > 0:
        # Get all unique instruments and traders
        instruments = list(set(trade.get('instrument', '') for trade in st.session_state.trades if trade.get('instrument')))
        traders = list(set(trade.get('trader', '') for trade in st.session_state.trades if trade.get('trader')))
        
        if instruments and traders:
            # Calculate performance for each trader-instrument combination
            performance_data = {'Instrument': instruments}
            
            for trader in traders:
                trader_performance = []
                for instrument in instruments:
                    # Get trades for this trader-instrument combination
                    trades = [t for t in st.session_state.trades 
                             if t.get('trader') == trader and t.get('instrument') == instrument]
                    if trades:
                        wins = sum(1 for t in trades if t.get('result') == 'Win')
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
                    try:
                        rate = int(val.replace('%', ''))
                        if rate >= 70:
                            return 'background-color: #10b981; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
                        elif rate >= 50:
                            return 'background-color: #f59e0b; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
                        else:
                            return 'background-color: #ef4444; color: white; text-align: center; font-weight: bold; padding: 8px; border-radius: 4px;'
                    except:
                        pass
                return 'background-color: #f3f4f6; text-align: center; font-weight: 500; padding: 12px; color: #000000;'
            
            # Display the styled dataframe
            if len(traders) > 0:
                styled_df = perf_df.style.applymap(style_performance, subset=traders)
                styled_df = styled_df.applymap(lambda x: 'background-color: #f3f4f6; text-align: center; font-weight: 500; padding: 12px; color: #000000;', subset=['Instrument'])
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.info("No trader data available for instrument performance analysis.")
        else:
            st.info("No complete trading data available for instrument performance analysis.")
    else:
        st.info("No trades available for instrument performance analysis. Add some trades to see detailed analytics!")

    with st.expander("🔧 Worksheet Configuration", expanded=False):
        st.markdown("""
        ### Current Configuration:
        - **Spreadsheet Name**: `Forex Trading Analytics`
        - **Worksheet Name**: `Trades`
        
        ### If you're getting "Worksheet not found" errors:
        
        **Option 1: Create the correct worksheet**
        1. Open your Google Sheet
        2. Create a new worksheet named exactly `Trades`
        3. Or rename your existing worksheet to `Trades`
        
        **Option 2: Use your existing worksheet**
        If your worksheet has a different name (like `Sheet1`), you can:
        1. Find the worksheet name in your Google Sheet
        2. Update the `WORKSHEET_NAME` variable in the code
        3. Common names: `Sheet1`, `Trading Data`, `Forex Trades`
        
        **Option 3: Let the app create it for you**
        1. Use the "Setup Google Sheets Integration" button
        2. The app will automatically create the `Trades` worksheet
        """)
        
        # Add a dynamic worksheet selector
        if st.session_state.sheets_connected:
            if st.button("🔍 Detect Available Worksheets", use_container_width=True):
                try:
                    gc = init_connection()
                    spreadsheet = gc.open(SHEET_NAME)
                    worksheets = spreadsheet.worksheets()
                    worksheet_names = [ws.title for ws in worksheets]
                    
                    st.success("📋 Found these worksheets in your spreadsheet:")
                    for name in worksheet_names:
                        if name == WORKSHEET_NAME:
                            st.write(f"✅ **{name}** (Currently configured)")
                        else:
                            st.write(f"📄 {name}")
                    
                    if WORKSHEET_NAME not in worksheet_names:
                        st.warning(f"⚠️ The configured worksheet '{WORKSHEET_NAME}' was not found!")
                        st.info("💡 You can either:")
                        st.info("1. Rename one of your existing worksheets to 'Trades'")
                        st.info("2. Or modify the WORKSHEET_NAME in the code to match an existing worksheet")
                        
                except Exception as e:
                    st.error(f"Error detecting worksheets: {e}")
    
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

# Footer with real-time sync status
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if st.session_state.sheets_connected:
    sync_status = "🔄 Real-time sync enabled (updates every 3 seconds)"
    if st.session_state.get('auto_refresh_toggle', True):
        next_refresh = REAL_TIME_UPDATE_INTERVAL - (time.time() - st.session_state.get('last_auto_refresh', 0))
        if next_refresh > 0:
            sync_status += f" • Next auto-refresh in {int(next_refresh)}s"
else:
    sync_status = "📱 Local mode - Enable Google Sheets for multi-device sync"

st.markdown(f"""
<div style="text-align: center; padding: 2rem 0; color: #6b7280; font-size: 0.875rem; border-top: 1px solid #e5e7eb; margin-top: 2rem;">
    <p>📊 Forex Trading Analytics - {sync_status}</p>
    <p>Last updated: {current_time}</p>
</div>
""", unsafe_allow_html=True)



