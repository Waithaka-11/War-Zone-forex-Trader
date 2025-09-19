import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Page config
st.set_page_config(
    page_title="War Zone Forex Trader",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background-color: #2E3440;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        height: 100%;
    }
    .metric-title {
        font-size: 1rem;
        color: #D8DEE9;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #88C0D0;
    }
    .delete-btn {
        background-color: #BF616A;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .delete-btn:hover {
        background-color: #A5424E;
        color: white;
        cursor: pointer;
    }
    .section-header {
        font-size: 1.8rem;
        color: #88C0D0;
        border-bottom: 2px solid #4C566A;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .trader-table {
        width: 100%;
    }
    .positive-value {
        color: #A3BE8C;
        font-weight: bold;
    }
    .negative-value {
        color: #BF616A;
        font-weight: bold;
    }
    .center-content {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets integration setup
def setup_google_sheets():
    try:
        # Create the connection to Google Sheets
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Load credentials from Streamlit secrets
        if 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        else:
            # For local development - you would need to set up your own service account
            st.error("Google Sheets credentials not found. Please configure them in Streamlit secrets.")
            return None
        
        client = gspread.authorize(creds)
        
        # Try to open the spreadsheet or create a new one
        try:
            spreadsheet = client.open("WarZoneForexTrader")
        except gspread.SpreadsheetNotFound:
            # Create a new spreadsheet if it doesn't exist
            spreadsheet = client.create("WarZoneForexTrader")
            # Share with yourself (replace with your email)
            spreadsheet.share('your-email@gmail.com', perm_type='user', role='writer')
            
            # Set up the worksheets
            worksheet = spreadsheet.sheet1
            worksheet.update_title("Trades")
            headers = ["ID", "Date", "Trader", "Instrument", "Direction", "Entry", "Exit", "P/L", "R/R Ratio", "Outcome"]
            worksheet.append_row(headers)
            
        return spreadsheet
    except Exception as e:
        st.error(f"Error setting up Google Sheets: {e}")
        return None

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'spreadsheet' not in st.session_state:
    st.session_state.spreadsheet = setup_google_sheets()
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Load data from Google Sheets
def load_data_from_sheets():
    if st.session_state.spreadsheet:
        try:
            worksheet = st.session_state.spreadsheet.worksheet("Trades")
            data = worksheet.get_all_records()
            
            # Convert to proper data types
            for trade in data:
                trade['ID'] = int(trade['ID']) if 'ID' in trade and trade['ID'] else 0
                trade['P/L'] = float(trade['P/L']) if 'P/L' in trade and trade['P/L'] else 0.0
                trade['R/R Ratio'] = float(trade['R/R Ratio']) if 'R/R Ratio' in trade and trade['R/R Ratio'] else 0.0
                trade['Entry'] = float(trade['Entry']) if 'Entry' in trade and trade['Entry'] else 0.0
                trade['Exit'] = float(trade['Exit']) if 'Exit' in trade and trade['Exit'] else 0.0
            
            return data
        except Exception as e:
            st.error(f"Error loading data from Google Sheets: {e}")
            return []
    return []

# Save data to Google Sheets
def save_data_to_sheets():
    if st.session_state.spreadsheet:
        try:
            worksheet = st.session_state.spreadsheet.worksheet("Trades")
            
            # Clear existing data (except headers)
            worksheet.clear()
            headers = ["ID", "Date", "Trader", "Instrument", "Direction", "Entry", "Exit", "P/L", "R/R Ratio", "Outcome"]
            worksheet.append_row(headers)
            
            # Add all trades
            for trade in st.session_state.trades:
                row = [
                    trade.get('id', ''),
                    trade.get('date', ''),
                    trade.get('trader', ''),
                    trade.get('instrument', ''),
                    trade.get('direction', ''),
                    trade.get('entry_price', ''),
                    trade.get('exit_price', ''),
                    trade.get('profit_loss', ''),
                    trade.get('rr_ratio', ''),
                    trade.get('outcome', '')
                ]
                worksheet.append_row(row)
                
            return True
        except Exception as e:
            st.error(f"Error saving data to Google Sheets: {e}")
            return False
    return False

# Load data if not initialized
if not st.session_state.initialized:
    with st.spinner("Loading data from Google Sheets..."):
        data = load_data_from_sheets()
        if data:
            # Convert to our format
            converted_data = []
            for item in data:
                converted_data.append({
                    'id': item.get('ID', ''),
                    'date': item.get('Date', ''),
                    'trader': item.get('Trader', ''),
                    'instrument': item.get('Instrument', ''),
                    'direction': item.get('Direction', ''),
                    'entry_price': item.get('Entry', ''),
                    'exit_price': item.get('Exit', ''),
                    'profit_loss': item.get('P/L', ''),
                    'rr_ratio': item.get('R/R Ratio', ''),
                    'outcome': item.get('Outcome', '')
                })
            st.session_state.trades = converted_data
        st.session_state.initialized = True

# App title
st.markdown('<h1 class="main-header">War Zone Forex Trader Dashboard</h1>', unsafe_allow_html=True)

# Function to delete a trade
def delete_trade(trade_id):
    st.session_state.trades = [trade for trade in st.session_state.trades if trade.get('id') != trade_id]
    if save_data_to_sheets():
        st.success("Trade deleted successfully!")
    else:
        st.error("Error saving to Google Sheets")
    st.rerun()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-header">Trade History</div>', unsafe_allow_html=True)
    
    # Create trade history table
    if st.session_state.trades:
        # Display the table with delete buttons
        for i, trade in enumerate(st.session_state.trades):
            cols = st.columns([0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            with cols[0]:
                # Delete button with white text
                if st.button("🗑️", key=f"delete_{trade.get('id', i)}", help="Delete trade"):
                    delete_trade(trade.get('id', i))
            with cols[1]:
                st.write(trade.get('date', 'N/A'))
            with cols[2]:
                st.write(trade.get('trader', 'N/A'))
            with cols[3]:
                st.write(trade.get('instrument', 'N/A'))
            with cols[4]:
                st.write(trade.get('direction', 'N/A'))
            with cols[5]:
                st.write(trade.get('entry_price', 'N/A'))
            with cols[6]:
                st.write(trade.get('exit_price', 'N/A'))
            with cols[7]:
                pl = trade.get('profit_loss', 0)
                pl_class = "positive-value" if pl >= 0 else "negative-value"
                st.markdown(f'<span class="{pl_class}">{pl}</span>', unsafe_allow_html=True)
            with cols[8]:
                st.write(trade.get('rr_ratio', 'N/A'))
            with cols[9]:
                outcome = trade.get('outcome', 'N/A')
                outcome_color = "#A3BE8C" if outcome == "Win" else "#BF616A"
                st.markdown(f'<span style="color: {outcome_color}; font-weight: bold">{outcome}</span>', unsafe_allow_html=True)
    else:
        st.info("No trades to display. Add your first trade below.")

with col2:
    st.markdown('<div class="section-header">Performance Metrics</div>', unsafe_allow_html=True)
    
    # Calculate metrics
    if st.session_state.trades:
        total_trades = len(st.session_state.trades)
        winning_trades = len([t for t in st.session_state.trades if t.get('outcome') == 'Win'])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Trader performance
        traders = set(t.get('trader') for t in st.session_state.trades if t.get('trader'))
        trader_performance = {}
        
        for trader in traders:
            trader_trades = [t for t in st.session_state.trades if t.get('trader') == trader]
            trader_wins = len([t for t in trader_trades if t.get('outcome') == 'Win'])
            trader_win_rate = (trader_wins / len(trader_trades)) * 100 if trader_trades else 0
            trader_performance[trader] = trader_win_rate
        
        best_trader = max(trader_performance, key=trader_performance.get) if trader_performance else "N/A"
        best_performance = trader_performance.get(best_trader, 0) if best_trader != "N/A" else 0
        
        # Display metrics in nice cards
        m1, m2 = st.columns(2)
        
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">WIN RATE THIS MONTH</div>
                <div class="metric-value">{win_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">TOTAL TRADES</div>
                <div class="metric-value">{total_trades}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Trader of the Month")
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: #3B4252; border-radius: 10px;">
            <h3 style="color: #88C0D0; margin-bottom: 0.5rem;">{best_trader}</h3>
            <p style="color: #D8DEE9; margin-bottom: 0.5rem;">Best performance with {best_performance:.1f}% win rate</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Win rate distribution chart
        st.markdown("---")
        st.subheader("Overall Win Rate Distribution")
        
        if trader_performance:
            fig, ax = plt.subplots(figsize=(8, 4))
            traders_list = list(trader_performance.keys())
            win_rates = list(trader_performance.values())
            
            bars = ax.bar(traders_list, win_rates, color=['#88C0D0', '#A3BE8C', '#EBCB8B', '#BF616A'])
            ax.set_ylabel('Win Rate (%)')
            ax.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("No trader data available for chart.")
        
        # Instrument performance
        st.markdown("---")
        st.subheader("Instrument Performance by Trader")
        
        instrument_data = []
        for trade in st.session_state.trades:
            if trade.get('trader') and trade.get('instrument'):
                instrument_data.append({
                    'Trader': trade.get('trader'),
                    'Instrument': trade.get('instrument'),
                    'Outcome': trade.get('outcome')
                })
        
        if instrument_data:
            instrument_df = pd.DataFrame(instrument_data)
            instrument_counts = instrument_df.groupby(['Trader', 'Instrument']).size().unstack(fill_value=0)
            
            fig, ax = plt.subplots(figsize=(8, 4))
            instrument_counts.plot(kind='bar', ax=ax, color=['#88C0D0', '#A3BE8C', '#EBCB8B', '#BF616A', '#B48EAD'])
            ax.set_ylabel('Number of Trades')
            ax.legend(title='Instrument', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("No instrument data available for chart.")
    else:
        st.info("No data available for performance metrics.")

# Add new trade form
st.markdown("---")
st.markdown('<div class="section-header">Add New Trade</div>', unsafe_allow_html=True)

with st.form("add_trade_form"):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        trader = st.selectbox("Trader", ["Waithaka", "Wallace", "Other"])
        instrument = st.selectbox("Instrument", ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "XAU/USD"])
        direction = st.radio("Direction", ["Long", "Short"])
    
    with c2:
        entry_price = st.number_input("Entry Price", value=1.1000, step=0.0001, format="%.4f")
        exit_price = st.number_input("Exit Price", value=1.1050, step=0.0001, format="%.4f")
        rr_ratio = st.number_input("R/R Ratio", value=1.5, step=0.1, min_value=0.1)
    
    with c3:
        profit_loss = st.number_input("Profit/Loss ($)", value=500, step=10)
        outcome = st.selectbox("Outcome", ["Win", "Loss"])
        trade_date = st.date_input("Date", datetime.now())
    
    submitted = st.form_submit_button("Add Trade")
    
    if submitted:
        # Generate a new ID
        if st.session_state.trades:
            max_id = max([t.get('id', 0) for t in st.session_state.trades])
            new_id = max_id + 1
        else:
            new_id = 1
            
        new_trade = {
            'id': new_id,
            'trader': trader,
            'instrument': instrument,
            'direction': direction,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'profit_loss': profit_loss,
            'rr_ratio': rr_ratio,
            'outcome': outcome,
            'date': trade_date.strftime("%Y-%m-%d")
        }
        
        st.session_state.trades.append(new_trade)
        if save_data_to_sheets():
            st.success("Trade added successfully!")
        else:
            st.error("Error saving to Google Sheets")
        st.rerun()

# Instructions for setting up Google Sheets integration
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
       - Create a Google Sheet named "WarZoneForexTrader"
       - Share it with your service account email with editor permissions
    """)

# Add a refresh button
if st.button("Refresh Data from Google Sheets"):
    with st.spinner("Refreshing data..."):
        data = load_data_from_sheets()
        if data:
            # Convert to our format
            converted_data = []
            for item in data:
                converted_data.append({
                    'id': item.get('ID', ''),
                    'date': item.get('Date', ''),
                    'trader': item.get('Trader', ''),
                    'instrument': item.get('Instrument', ''),
                    'direction': item.get('Direction', ''),
                    'entry_price': item.get('Entry', ''),
                    'exit_price': item.get('Exit', ''),
                    'profit_loss': item.get('P/L', ''),
                    'rr_ratio': item.get('R/R Ratio', ''),
                    'outcome': item.get('Outcome', '')
                })
            st.session_state.trades = converted_data
            st.success("Data refreshed successfully!")
        else:
            st.error("Error refreshing data from Google Sheets")
