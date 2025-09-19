import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    .stButton>button {
        background-color: #BF616A;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #A5424E;
        color: white;
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
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">War Zone Forex Trader Dashboard</h1>', unsafe_allow_html=True)

# Sample data (replace with your actual data loading logic)
@st.cache_data
def load_sample_data():
    trades = [
        {
            'id': 1,  # Added ID field to prevent KeyError
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
    return trades

# Load data
trades_data = load_sample_data()

# Initialize session state for trades if not exists
if 'trades' not in st.session_state:
    st.session_state.trades = trades_data

# Function to delete a trade
def delete_trade(trade_id):
    st.session_state.trades = [trade for trade in st.session_state.trades if trade['id'] != trade_id]
    st.success("Trade deleted successfully!")
    st.rerun()

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="section-header">Trade History</div>', unsafe_allow_html=True)
    
    # Create trade history table
    if st.session_state.trades:
        table_data = []
        for trade in st.session_state.trades:
            # Use .get() method to prevent KeyError if any field is missing
            row = {
                'Date': trade.get('date', 'N/A'),
                'Trader': trade.get('trader', 'N/A'),
                'Instrument': trade.get('instrument', 'N/A'),
                'Direction': trade.get('direction', 'N/A'),
                'Entry': trade.get('entry_price', 'N/A'),
                'Exit': trade.get('exit_price', 'N/A'),
                'P/L ($)': trade.get('profit_loss', 'N/A'),
                'R/R Ratio': trade.get('rr_ratio', 'N/A'),
                'Outcome': trade.get('outcome', 'N/A'),
                'Actions': trade.get('id', 'N/A')  # Using get to prevent KeyError
            }
            table_data.append(row)
        
        df = pd.DataFrame(table_data)
        
        # Display the table with delete buttons
        for i, trade in enumerate(st.session_state.trades):
            cols = st.columns([0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1])
            with cols[0]:
                # Delete button with white text
                if st.button("🗑️", key=f"delete_{trade['id']}", help="Delete trade"):
                    delete_trade(trade['id'])
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
        st.info("No trades to display.")

with col2:
    st.markdown('<div class="section-header">Performance Metrics</div>', unsafe_allow_html=True)
    
    # Calculate metrics
    if st.session_state.trades:
        total_trades = len(st.session_state.trades)
        winning_trades = len([t for t in st.session_state.trades if t.get('outcome') == 'Win'])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Trader performance
        traders = set(t.get('trader') for t in st.session_state.trades)
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
            st.markdown("""
            <div class="metric-card">
                <div class="metric-title">WIN RATE THIS MONTH</div>
                <div class="metric-value">{:.1f}%</div>
            </div>
            """.format(win_rate), unsafe_allow_html=True)
        
        with m2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-title">TOTAL TRADES</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(total_trades), unsafe_allow_html=True)
        
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
        
        win_rate_data = {
            'Trader': list(trader_performance.keys()),
            'Win Rate': list(trader_performance.values())
        }
        
        win_rate_df = pd.DataFrame(win_rate_data)
        
        fig = px.bar(win_rate_df, x='Trader', y='Win Rate', 
                     title="Win Rate by Trader",
                     color='Win Rate', color_continuous_scale='Teal')
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#D8DEE9'),
            title_font_size=20,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Instrument performance
        st.markdown("---")
        st.subheader("Instrument Performance by Trader")
        
        instrument_data = []
        for trade in st.session_state.trades:
            instrument_data.append({
                'Trader': trade.get('trader'),
                'Instrument': trade.get('instrument'),
                'Outcome': trade.get('outcome')
            })
        
        if instrument_data:
            instrument_df = pd.DataFrame(instrument_data)
            instrument_pivot = pd.crosstab(index=instrument_df['Trader'], 
                                         columns=instrument_df['Instrument'])
            
            fig2 = px.imshow(instrument_pivot, text_auto=True,
                            aspect="auto",
                            title="Trades by Instrument and Trader",
                            color_continuous_scale='Blues')
            
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#D8DEE9'),
                title_font_size=20
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available for performance metrics.")

# Add new trade form
st.markdown("---")
st.markdown('<div class="section-header">Add New Trade</div>', unsafe_allow_html=True)

with st.form("add_trade_form"):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        trader = st.selectbox("Trader", ["Waithaka", "Wallace"])
        instrument = st.selectbox("Instrument", ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"])
        direction = st.radio("Direction", ["Long", "Short"])
    
    with c2:
        entry_price = st.number_input("Entry Price", value=1.1000, step=0.0001, format="%.4f")
        exit_price = st.number_input("Exit Price", value=1.1050, step=0.0001, format="%.4f")
        rr_ratio = st.number_input("R/R Ratio", value=1.5, step=0.1)
    
    with c3:
        profit_loss = st.number_input("Profit/Loss ($)", value=500, step=10)
        outcome = st.selectbox("Outcome", ["Win", "Loss"])
        trade_date = st.date_input("Date", datetime.now())
    
    submitted = st.form_submit_button("Add Trade")
    
    if submitted:
        new_trade = {
            'id': max([t['id'] for t in st.session_state.trades], default=0) + 1,
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
