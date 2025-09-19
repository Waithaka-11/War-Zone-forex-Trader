import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from df2gspread import df2gspread as d2g
from gspread_dataframe import set_with_dataframe
import math

# Page config
st.set_page_config(
    page_title="Forex Trading Log",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the HTML UI
st.markdown("""
<style>
    /* Main styles */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Card styles */
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        border: none;
    }
    
    .card-header {
        background-color: #2c3e50;
        color: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 20px;
        margin: -20px -20px 20px -20px;
        font-weight: 600;
        font-size: 18px;
    }
    
    /* Table styles */
    .dataframe {
        width: 100%;
    }
    
    .dataframe thead th {
        background-color: #34495e !important;
        color: white !important;
    }
    
    /* Button styles */
    .stButton button {
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stButton button:hover {
        opacity: 0.9;
    }
    
    .btn-primary {
        background-color: #3498db;
    }
    
    .btn-success {
        background-color: #2ecc71;
    }
    
    .btn-danger {
        background-color: #e74c3c;
    }
    
    /* Stats boxes */
    .stats-box {
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
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
    
    .positive {
        background-color: rgba(46, 204, 113, 0.15);
    }
    
    .negative {
        background-color: rgba(231, 76, 60, 0.15);
    }
    
    .neutral {
        background-color: rgba(241, 196, 15, 0.15);
    }
    
    /* Badge styles */
    .badge-win {
        background-color: #2ecc71;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .badge-loss {
        background-color: #e74c3c;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Suggestion pills */
    .suggestion-pill {
        display: inline-block;
        padding: 5px 12px;
        margin: 3px;
        border-radius: 20px;
        background-color: #e3f2fd;
        color: #1976d2;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggestion-pill:hover {
        background-color: #bbdefb;
        transform: translateY(-2px);
    }
    
    /* Form styles */
    .stSelectbox, .stTextInput, .stDateInput, .stNumberInput {
        margin-bottom: 15px;
    }
    
    /* Header */
    .main-header {
        background-color: #343a40;
        color: white;
        padding: 15px 0;
        margin-bottom: 20px;
        border-radius: 0;
    }
    
    /* Footer */
    .footer {
        background-color: #343a40;
        color: white;
        text-align: center;
        padding: 15px 0;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets setup
def setup_google_sheets():
    try:
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Check if credentials are in secrets
        if 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        else:
            st.error("Google Sheets credentials not found. Please add them to Streamlit secrets.")
            return None
        
        # Authorize the client
        client = gspread.authorize(creds)
        
        # Try to open the existing spreadsheet or create a new one
        try:
            spreadsheet = client.open("ForexTradingLog")
        except gspread.SpreadsheetNotFound:
            # Create a new spreadsheet
            spreadsheet = client.create("ForexTradingLog")
            # Share with yourself (replace with your email)
            spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')
            
            # Set up the worksheet
            worksheet = spreadsheet.sheet1
            worksheet.update_title("Trades")
            
            # Add headers
            headers = ["ID", "Date", "Trader", "Instrument", "Entry", "SL", "Target", 
                      "Risk", "Reward", "R/R Ratio", "Outcome", "Result"]
            worksheet.append_row(headers)
            
            st.success("Created new Google Sheet: ForexTradingLog")
        
        return spreadsheet
    
    except Exception as e:
        st.error(f"Error setting up Google Sheets: {e}")
        return None

# Load data from Google Sheets
def load_data_from_sheets(spreadsheet):
    try:
        worksheet = spreadsheet.worksheet("Trades")
        records = worksheet.get_all_records()
        
        # Convert to list of dictionaries with proper data types
        trades = []
        for record in records:
            # Skip empty rows or header row if it appears in data
            if not record.get('ID') or record.get('ID') == 'ID':
                continue
                
            trades.append({
                'id': int(record.get('ID', 0)),
                'date': record.get('Date', ''),
                'trader': record.get('Trader', ''),
                'instrument': record.get('Instrument', ''),
                'entry': float(record.get('Entry', 0)),
                'sl': float(record.get('SL', 0)),
                'target': float(record.get('Target', 0)),
                'risk': float(record.get('Risk', 0)),
                'reward': float(record.get('Reward', 0)),
                'rr_ratio': float(record.get('R/R Ratio', 0)),
                'outcome': record.get('Outcome', ''),
                'result': record.get('Result', '')
            })
        
        return trades
    
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return []

# Save data to Google Sheets
def save_data_to_sheets(spreadsheet, trades):
    try:
        worksheet = spreadsheet.worksheet("Trades")
        
        # Clear existing data but keep headers
        worksheet.clear()
        headers = ["ID", "Date", "Trader", "Instrument", "Entry", "SL", "Target", 
                  "Risk", "Reward", "R/R Ratio", "Outcome", "Result"]
        worksheet.append_row(headers)
        
        # Add all trades
        for trade in trades:
            row = [
                trade.get('id', ''),
                trade.get('date', ''),
                trade.get('trader', ''),
                trade.get('instrument', ''),
                trade.get('entry', ''),
                trade.get('sl', ''),
                trade.get('target', ''),
                trade.get('risk', ''),
                trade.get('reward', ''),
                trade.get('rr_ratio', ''),
                trade.get('outcome', ''),
                trade.get('result', '')
            ]
            worksheet.append_row(row)
        
        return True
    
    except Exception as e:
        st.error(f"Error saving data to Google Sheets: {e}")
        return False

# Initialize session state and Google Sheets
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'spreadsheet' not in st.session_state:
    st.session_state.spreadsheet = setup_google_sheets()
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Load data from Google Sheets if available
if st.session_state.spreadsheet and not st.session_state.initialized:
    with st.spinner("Loading data from Google Sheets..."):
        trades = load_data_from_sheets(st.session_state.spreadsheet)
        if trades:
            st.session_state.trades = trades
        st.session_state.initialized = True

# Header
st.markdown("""
<div class="main-header">
    <div class="container">
        <h1><i class="fas fa-chart-line"></i> Forex Trading Log</h1>
    </div>
</div>
""", unsafe_allow_html=True)

# Function to delete a trade
def delete_trade(trade_id):
    st.session_state.trades = [trade for trade in st.session_state.trades if trade['id'] != trade_id]
    if st.session_state.spreadsheet:
        if save_data_to_sheets(st.session_state.spreadsheet, st.session_state.trades):
            st.success("Trade deleted successfully!")
        else:
            st.error("Error saving to Google Sheets")
    st.rerun()

# Main container
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Add New Trade Card
        st.markdown('<div class="card-header"><i class="fas fa-plus-circle me-2"></i>Add New Trade</div>', unsafe_allow_html=True)
        with st.form("trade_form"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                trader = st.selectbox("Trader", ["", "Waithaka", "Wallace", "Max"])
                entry = st.number_input("Entry Price", value=0.0, step=0.00001, format="%.5f")
            
            with col2:
                instrument = st.selectbox("Instrument", ["", "XAUUSD", "USOIL", "US30", "BTCUSD", "USTECH", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF"])
                sl = st.number_input("Stop Loss (SL)", value=0.0, step=0.00001, format="%.5f")
            
            with col3:
                date = st.date_input("Date", datetime.now())
                target = st.number_input("Target Price", value=0.0, step=0.00001, format="%.5f")
            
            with col4:
                outcome = st.selectbox("Outcome", ["", "Target Hit", "SL Hit"])
                st.write("")  # Spacer
                submitted = st.form_submit_button("Add Trade", use_container_width=True)
            
            if submitted:
                if not all([trader, instrument, outcome, entry, sl, target]):
                    st.error("Please fill all fields")
                else:
                    # Calculate risk, reward, and R/R ratio
                    risk = abs(entry - sl)
                    reward = abs(target - entry)
                    rr_ratio = round(reward / risk, 2) if risk > 0 else 0
                    
                    # Determine result
                    result = "Win" if outcome == "Target Hit" else "Loss"
                    
                    # Generate ID
                    if st.session_state.trades:
                        new_id = max([t['id'] for t in st.session_state.trades]) + 1
                    else:
                        new_id = 1
                    
                    # Add to trades
                    new_trade = {
                        'id': new_id,
                        'date': date.strftime("%Y-%m-%d"),
                        'trader': trader,
                        'instrument': instrument,
                        'entry': entry,
                        'sl': sl,
                        'target': target,
                        'risk': risk,
                        'reward': reward,
                        'rr_ratio': rr_ratio,
                        'outcome': outcome,
                        'result': result
                    }
                    
                    st.session_state.trades.append(new_trade)
                    
                    # Save to Google Sheets
                    if st.session_state.spreadsheet:
                        if save_data_to_sheets(st.session_state.spreadsheet, st.session_state.trades):
                            st.success("Trade added successfully!")
                        else:
                            st.error("Error saving to Google Sheets")
                    else:
                        st.success("Trade added to local session!")
                    
                    st.rerun()

        # Trading History Card
        st.markdown('<div class="card-header"><i class="fas fa-table me-2"></i>Trading History</div>', unsafe_allow_html=True)
        
        if st.session_state.trades:
            # Convert to DataFrame for display
            df = pd.DataFrame(st.session_state.trades)
            
            # Format the display
            display_df = df.copy()
            display_df['entry'] = display_df['entry'].apply(lambda x: f"{x:.5f}")
            display_df['sl'] = display_df['sl'].apply(lambda x: f"{x:.5f}")
            display_df['target'] = display_df['target'].apply(lambda x: f"{x:.5f}")
            display_df['risk'] = display_df['risk'].apply(lambda x: f"{x:.5f}")
            display_df['reward'] = display_df['reward'].apply(lambda x: f"{x:.5f}")
            display_df['rr_ratio'] = display_df['rr_ratio'].apply(lambda x: f"{x:.2f}")
            
            # Add actions column with delete buttons
            display_df['Actions'] = display_df['id'].apply(lambda x: f"""
                <button onclick="window.deleteTrade({x})" style="
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    cursor: pointer;
                ">
                    <i class="fas fa-trash"></i>
                </button>
            """)
            
            # Format result as badges
            display_df['result'] = display_df['result'].apply(
                lambda x: f'<span class="badge-{x.lower()}">{x}</span>'
            )
            
            # Reorder columns
            display_df = display_df[['date', 'trader', 'instrument', 'entry', 'sl', 'target', 
                                   'risk', 'reward', 'rr_ratio', 'outcome', 'result', 'Actions']]
            
            # Display the table
            st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
        else:
            st.info("No trades to display. Add your first trade above.")
    
    with col2:
        # Performance Summary Card
        st.markdown('<div class="card-header"><i class="fas fa-chart-pie me-2"></i>Performance Summary</div>', unsafe_allow_html=True)
        
        if st.session_state.trades:
            total_trades = len(st.session_state.trades)
            winning_trades = len([t for t in st.session_state.trades if t['result'] == 'Win'])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            avg_rr = sum([t['rr_ratio'] for t in st.session_state.trades]) / total_trades if total_trades > 0 else 0
            
            # Calculate loss streak
            loss_streak = 0
            current_streak = 0
            for trade in reversed(st.session_state.trades):
                if trade['result'] == 'Loss':
                    current_streak += 1
                    loss_streak = max(loss_streak, current_streak)
                else:
                    current_streak = 0
            
            st.markdown(f"""
            <div class="stats-box positive">
                <h6>TOTAL TRADES</h6>
                <h3>{total_trades}</h3>
            </div>
            <div class="stats-box positive">
                <h6>WIN RATE</h6>
                <h3>{win_rate:.1f}%</h3>
            </div>
            <div class="stats-box positive">
                <h6>AVG R/R RATIO</h6>
                <h3>{avg_rr:.2f}</h3>
            </div>
            <div class="stats-box negative">
                <h6>LOSS STREAK</h6>
                <h3>{loss_streak}</h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No performance data available")
        
        # Instrument Suggestions Card
        st.markdown('<div class="card-header"><i class="fas fa-lightbulb me-2"></i>Instrument Suggestions</div>', unsafe_allow_html=True)
        
        instruments = ["XAUUSD", "USOIL", "US30", "BTCUSD", "USTECH", "EURUSD", "GBPUSD"]
        suggestions_html = "".join([f'<div class="suggestion-pill">{inst}</div>' for inst in instruments])
        st.markdown(suggestions_html, unsafe_allow_html=True)
        
        # Refresh button
        if st.button("Refresh Data", use_container_width=True):
            if st.session_state.spreadsheet:
                with st.spinner("Refreshing data from Google Sheets..."):
                    trades = load_data_from_sheets(st.session_state.spreadsheet)
                    if trades:
                        st.session_state.trades = trades
                        st.success("Data refreshed from Google Sheets!")
                    else:
                        st.error("Error refreshing data")
            else:
                st.warning("Google Sheets not connected")

# Add JavaScript for delete functionality
st.markdown("""
<script>
// Create a global function for deleting trades
window.deleteTrade = function(tradeId) {
    // This would communicate with Streamlit via a custom component in a real app
    // For now, we'll show a confirmation and reload
    if (confirm('Are you sure you want to delete trade ' + tradeId + '?')) {
        // In a real implementation, this would call a Streamlit backend function
        alert('Trade deletion would be handled by the backend. Please implement proper deletion functionality.');
    }
};
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>© 2023 Forex Trading Log. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

# Add Font Awesome for icons
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# Instructions for setting up Google Sheets
with st.expander("Google Sheets Setup Instructions"):
    st.markdown("""
    ### To enable Google Sheets integration:
    
    1. **Create a Google Service Account**:
       - Go to the [Google Cloud Console](https://console.cloud.google.com/)
       - Create a new project or select an existing one
       - Enable the Google Sheets API and Google Drive API
       - Create a service account and download the JSON key file
    
    2. **Add credentials to Streamlit**:
       - In your Streamlit app, go to Settings → Secrets
       - Add your service account credentials as follows:
         
         ```toml
         [gcp_service_account]
         type = "service_account"
         project_id = "your-project-id"
         private_key_id = "your-private-key-id"
         private_key = "-----BEGIN PRIVATE KEY-----\\nyour-private-key\\n-----END PRIVATE KEY-----\\n"
         client_email = "your-service-account-email@your-project-id.iam.gserviceaccount.com"
         client_id = "your-client-id"
         auth_uri = "https://accounts.google.com/o/oauth2/auth"
         token_uri = "https://oauth2.googleapis.com/token"
         auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
         client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project-id.iam.gserviceaccount.com"
         ```
    
    3. **Share your Google Sheet**:
       - The app will automatically create a Google Sheet named "ForexTradingLog"
       - Share it with your service account email with editor permissions
    """)
