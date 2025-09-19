import streamlit as st
import pandas as pd
from datetime import datetime

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
    .section-header {
        font-size: 1.8rem;
        color: #88C0D0;
        border-bottom: 2px solid #4C566A;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .positive-value {
        color: #A3BE8C;
        font-weight: bold;
    }
    .negative-value {
        color: #BF616A;
        font-weight: bold;
    }
    .win-rate-bar {
        height: 20px;
        background: linear-gradient(90deg, #BF616A 0%, #A3BE8C 100%);
        border-radius: 10px;
        margin: 10px 0;
        position: relative;
    }
    .win-rate-fill {
        height: 100%;
        background-color: #A3BE8C;
        border-radius: 10px;
    }
    .win-rate-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Sample data for demo mode
def get_sample_data():
    return [
        {
            'id': 1,
            'trader': 'Waithaka',
            'instrument': 'EUR/USD',
            'direction': 'Long',
            'entry_price': 1.0850,
            'exit_price': 1.0920,
            'profit_loss': 700,
            'rr_ratio': 2.1,
            'outcome': 'Win',
            'date': '2025-09-15'
        },
        {
            'id': 2,
            'trader': 'Wallace',
            'instrument': 'GBP/USD',
            'direction': 'Short',
            'entry_price': 1.2650,
            'exit_price': 1.2580,
            'profit_loss': 700,
            'rr_ratio': 1.8,
            'outcome': 'Win',
            'date': '2025-09-16'
        },
        {
            'id': 3,
            'trader': 'Waithaka',
            'instrument': 'USD/JPY',
            'direction': 'Long',
            'entry_price': 147.50,
            'exit_price': 148.20,
            'profit_loss': 700,
            'rr_ratio': 2.4,
            'outcome': 'Win',
            'date': '2025-09-17'
        },
        {
            'id': 4,
            'trader': 'Wallace',
            'instrument': 'AUD/USD',
            'direction': 'Short',
            'entry_price': 0.6450,
            'exit_price': 0.6480,
            'profit_loss': -300,
            'rr_ratio': 0.9,
            'outcome': 'Loss',
            'date': '2025-09-18'
        }
    ]

# Load data
def load_data():
    return get_sample_data()

# Load data if not initialized
if not st.session_state.initialized:
    with st.spinner("Loading data..."):
        data = load_data()
        if data:
            st.session_state.trades = data
        st.session_state.initialized = True

# App title
st.markdown('<h1 class="main-header">War Zone Forex Trader Dashboard</h1>', unsafe_allow_html=True)

# Function to delete a trade
def delete_trade(trade_id):
    st.session_state.trades = [trade for trade in st.session_state.trades if trade.get('id') != trade_id]
    st.success("Trade deleted successfully!")
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
                # Delete button
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
                # FIXED: Proper handling of None values
                try:
                    pl_value = float(pl) if pl is not None else 0
                    pl_class = "positive-value" if pl_value >= 0 else "negative-value"
                    st.markdown(f'<span class="{pl_class}">{pl_value}</span>', unsafe_allow_html=True)
                except (TypeError, ValueError):
                    st.markdown(f'<span class="negative-value">N/A</span>', unsafe_allow_html=True)
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
        
        # Win rate distribution using custom bar visualization
        st.markdown("---")
        st.subheader("Overall Win Rate Distribution")
        
        if trader_performance:
            for trader, rate in trader_performance.items():
                st.markdown(f"**{trader}**")
                st.markdown(f"""
                <div class="win-rate-bar">
                    <div class="win-rate-fill" style="width: {rate}%;"></div>
                    <div class="win-rate-text">{rate:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No trader data available.")
        
        # Instrument performance table
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
            
            # Display as a table
            st.dataframe(instrument_counts, use_container_width=True)
        else:
            st.info("No instrument data available.")
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
        st.success("Trade added successfully!")
        st.rerun()

# Information about Google Sheets issue
st.markdown("---")
st.warning("""
**Note:** Google Sheets integration is currently disabled due to storage quota limitations. 
All data is stored locally in this session and will be lost when you refresh the page.
""")
