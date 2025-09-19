import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Page config
st.set_page_config(
    page_title="Forex Trading Log",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS to match the exact HTML UI
st.markdown("""
<style>
    body {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: none;
    }
    .card-header {
        background-color: #2c3e50;
        color: white;
        border-radius: 10px 10px 0 0 !important;
        font-weight: 600;
        padding: 12px 20px;
    }
    .table thead th {
        background-color: #34495e;
        color: white;
        padding: 12px 8px;
        font-weight: 600;
    }
    .table td {
        padding: 10px 8px;
        vertical-align: middle;
    }
    .btn-primary {
        background-color: #3498db;
        border: none;
    }
    .btn-primary:hover {
        background-color: #2980b9;
    }
    .btn-success {
        background-color: #2ecc71;
        border: none;
    }
    .btn-success:hover {
        background-color: #27ae60;
    }
    .btn-danger {
        background-color: #e74c3c;
        border: none;
    }
    .btn-danger:hover {
        background-color: #c0392b;
    }
    .btn-outline-danger {
        border: 1px solid #e74c3c;
        color: #e74c3c;
        background: transparent;
    }
    .btn-outline-danger:hover {
        background-color: #e74c3c;
        color: white;
    }
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
    .win-row {
        background-color: rgba(46, 204, 113, 0.1) !important;
    }
    .loss-row {
        background-color: rgba(231, 76, 60, 0.1) !important;
    }
    .chart-container {
        position: relative;
        height: 250px;
        margin-bottom: 20px;
    }
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
    .navbar-brand {
        font-weight: 700;
        color: #2c3e50 !important;
    }
    /* Custom navbar */
    .navbar {
        background-color: #343a40 !important;
        padding: 0.5rem 1rem;
    }
    .navbar-dark .navbar-nav .nav-link {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    .navbar-dark .navbar-nav .nav-link:hover {
        color: white !important;
    }
    /* Badge styles */
    .badge.bg-success {
        background-color: #28a745 !important;
        color: white;
        padding: 0.4em 0.6em;
        border-radius: 0.25rem;
        font-size: 0.85em;
        font-weight: 600;
    }
    .badge.bg-danger {
        background-color: #dc3545 !important;
        color: white;
        padding: 0.4em 0.6em;
        border-radius: 0.25rem;
        font-size: 0.85em;
        font-weight: 600;
    }
    /* Action buttons */
    .action-btn {
        padding: 0.25rem 0.5rem;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets setup
def setup_google_sheets():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        if 'gcp_service_account' in st.secrets:
            creds_dict = dict(st.secrets['gcp_service_account'])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            client = gspread.authorize(creds)
            
            try:
                spreadsheet = client.open("ForexTradingLog")
            except gspread.SpreadsheetNotFound:
                spreadsheet = client.create("ForexTradingLog")
                worksheet = spreadsheet.sheet1
                worksheet.update_title("Trades")
                headers = ["ID", "Date", "Trader", "Instrument", "Entry", "SL", "Target", "Risk", "Reward", "R/R Ratio", "Outcome", "Result"]
                worksheet.append_row(headers)
            
            return spreadsheet
        else:
            st.warning("Google Sheets credentials not found. Using local storage.")
            return None
    except Exception as e:
        st.warning(f"Google Sheets setup failed: {e}. Using local storage.")
        return None

# Load data from Google Sheets
def load_data_from_sheets(spreadsheet):
    try:
        worksheet = spreadsheet.worksheet("Trades")
        records = worksheet.get_all_records()
        trades = []
        for record in records:
            if record.get('ID') and record.get('ID') != 'ID':
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
        st.warning(f"Error loading data: {e}")
        return []

# Save data to Google Sheets
def save_data_to_sheets(spreadsheet, trades):
    try:
        worksheet = spreadsheet.worksheet("Trades")
        worksheet.clear()
        headers = ["ID", "Date", "Trader", "Instrument", "Entry", "SL", "Target", "Risk", "Reward", "R/R Ratio", "Outcome", "Result"]
        worksheet.append_row(headers)
        
        for trade in trades:
            row = [
                trade.get('id', ''), trade.get('date', ''), trade.get('trader', ''),
                trade.get('instrument', ''), trade.get('entry', ''), trade.get('sl', ''),
                trade.get('target', ''), trade.get('risk', ''), trade.get('reward', ''),
                trade.get('rr_ratio', ''), trade.get('outcome', ''), trade.get('result', '')
            ]
            worksheet.append_row(row)
        return True
    except Exception as e:
        st.warning(f"Error saving data: {e}")
        return False

# Initialize session state with sample data if empty
if 'trades' not in st.session_state:
    st.session_state.trades = [
        {
            'id': 1,
            'date': '2023-10-05',
            'trader': 'Waithaka',
            'instrument': 'XAUUSD',
            'entry': 1820.50,
            'sl': 1815.00,
            'target': 1830.00,
            'risk': 5.50,
            'reward': 9.50,
            'rr_ratio': 1.73,
            'outcome': 'Target Hit',
            'result': 'Win'
        },
        {
            'id': 2,
            'date': '2023-10-04',
            'trader': 'Wallace',
            'instrument': 'USOIL',
            'entry': 89.30,
            'sl': 88.50,
            'target': 91.00,
            'risk': 0.80,
            'reward': 1.70,
            'rr_ratio': 2.13,
            'outcome': 'SL Hit',
            'result': 'Loss'
        },
        {
            'id': 3,
            'date': '2023-10-03',
            'trader': 'Max',
            'instrument': 'BTCUSD',
            'entry': 27450.00,
            'sl': 27200.00,
            'target': 27800.00,
            'risk': 250.00,
            'reward': 350.00,
            'rr_ratio': 1.40,
            'outcome': 'Target Hit',
            'result': 'Win'
        }
    ]

if 'spreadsheet' not in st.session_state:
    st.session_state.spreadsheet = setup_google_sheets()
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Load data
if st.session_state.spreadsheet and not st.session_state.initialized:
    with st.spinner("Loading data..."):
        trades = load_data_from_sheets(st.session_state.spreadsheet)
        if trades:
            st.session_state.trades = trades
        st.session_state.initialized = True

# Function to delete a trade
def delete_trade(trade_id):
    st.session_state.trades = [trade for trade in st.session_state.trades if trade['id'] != trade_id]
    if st.session_state.spreadsheet:
        if save_data_to_sheets(st.session_state.spreadsheet, st.session_state.trades):
            st.success("Trade deleted successfully!")
        else:
            st.error("Error saving to Google Sheets")
    else:
        st.success("Trade deleted from local storage!")
    st.rerun()

# Navbar
st.markdown("""
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="#">
            <i class="fas fa-chart-line me-2"></i>Forex Trading Log
        </a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link active" href="#"><i class="fas fa-home me-1"></i> Dashboard</a>
            <a class="nav-link" href="#"><i class="fas fa-history me-1"></i> History</a>
            <a class="nav-link" href="#"><i class="fas fa-cog me-1"></i> Settings</a>
        </div>
    </div>
</nav>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="container mt-4">', unsafe_allow_html=True)

# Add New Trade Card
with st.container():
    st.markdown("""
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <span><i class="fas fa-plus-circle me-2"></i>Add New Trade</span>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    with st.form("trade_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trader = st.selectbox("Trader", ["Select Trader", "Waithaka", "Wallace", "Max"])
            entry = st.number_input("Entry Price", value=0.0, step=0.00001, format="%.5f")
        
        with col2:
            instrument = st.selectbox("Instrument", ["Select Instrument", "XAUUSD", "USOIL", "US30", "BTCUSD", "USTECH", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF"])
            sl = st.number_input("Stop Loss (SL)", value=0.0, step=0.00001, format="%.5f")
        
        with col3:
            date = st.date_input("Date", datetime.now())
            target = st.number_input("Target Price", value=0.0, step=0.00001, format="%.5f")
        
        with col4:
            outcome = st.selectbox("Outcome", ["Select Outcome", "Target Hit", "SL Hit"])
            st.write("")
            submitted = st.form_submit_button("Add Trade", use_container_width=True)
        
        if submitted:
            if not all([trader != "Select Trader", instrument != "Select Instrument", outcome != "Select Outcome", entry, sl, target]):
                st.error("Please fill all fields")
            else:
                risk = abs(entry - sl)
                reward = abs(target - entry)
                rr_ratio = round(reward / risk, 2) if risk > 0 else 0
                result = "Win" if outcome == "Target Hit" else "Loss"
                
                new_id = max([t['id'] for t in st.session_state.trades]) + 1 if st.session_state.trades else 1
                
                new_trade = {
                    'id': new_id, 'date': date.strftime("%Y-%m-%d"), 'trader': trader,
                    'instrument': instrument, 'entry': entry, 'sl': sl, 'target': target,
                    'risk': risk, 'reward': reward, 'rr_ratio': rr_ratio,
                    'outcome': outcome, 'result': result
                }
                
                st.session_state.trades.append(new_trade)
                
                if st.session_state.spreadsheet:
                    if save_data_to_sheets(st.session_state.spreadsheet, st.session_state.trades):
                        st.success("Trade added successfully!")
                    else:
                        st.error("Error saving to Google Sheets")
                else:
                    st.success("Trade added to local storage!")
                
                st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

# Main content columns
col1, col2 = st.columns([3, 1])

with col1:
    # Trading History Card
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-table me-2"></i>Trading History
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if st.session_state.trades:
        # Create HTML table with exact structure
        table_html = """
        <div class="table-responsive">
            <table class="table table-hover" style="width:100%">
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
            row_class = "win-row" if trade['result'] == 'Win' else "loss-row"
            badge_class = "bg-success" if trade['result'] == 'Win' else "bg-danger"
            
            table_html += f"""
            <tr class="{row_class}">
                <td>{trade['date']}</td>
                <td>{trade['trader']}</td>
                <td>{trade['instrument']}</td>
                <td>{trade['entry']:.2f}</td>
                <td>{trade['sl']:.2f}</td>
                <td>{trade['target']:.2f}</td>
                <td>{trade['risk']:.2f}</td>
                <td>{trade['reward']:.2f}</td>
                <td>{trade['rr_ratio']:.2f}</td>
                <td>{trade['outcome']}</td>
                <td><span class="badge {badge_class}">{trade['result']}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-danger action-btn" onclick="deleteTrade({trade['id']})" title="Delete Trade">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
            """
        
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No trades to display. Add your first trade above.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

with col2:
    # Performance Summary Card
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-chart-pie me-2"></i>Performance Summary
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    if st.session_state.trades:
        total_trades = len(st.session_state.trades)
        winning_trades = len([t for t in st.session_state.trades if t['result'] == 'Win'])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_rr = sum([t['rr_ratio'] for t in st.session_state.trades]) / total_trades if total_trades > 0 else 0
        
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
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Instrument Suggestions Card
    st.markdown("""
    <div class="card mt-4">
        <div class="card-header">
            <i class="fas fa-lightbulb me-2"></i>Instrument Suggestions
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    instruments = ["XAUUSD", "USOIL", "US30", "BTCUSD", "USTECH", "EURUSD", "GBPUSD"]
    suggestions_html = "".join([f'<div class="suggestion-pill">{inst}</div>' for inst in instruments])
    st.markdown(suggestions_html, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<footer class="bg-dark text-white text-center py-3 mt-4">
    <p class="mb-0">© 2023 Forex Trading Log. All rights reserved.</p>
</footer>
</div>
""", unsafe_allow_html=True)

# JavaScript for delete functionality
st.markdown("""
<script>
function deleteTrade(tradeId) {
    if (confirm('Are you sure you want to delete trade ' + tradeId + '?')) {
        // This would communicate with Streamlit in a real implementation
        window.location.href = window.location.href + '?delete_trade=' + tradeId;
    }
}
</script>
""", unsafe_allow_html=True)

# Handle trade deletion from URL parameter
query_params = st.experimental_get_query_params()
if 'delete_trade' in query_params:
    trade_id = int(query_params['delete_trade'][0])
    delete_trade(trade_id)

# Add Font Awesome
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
