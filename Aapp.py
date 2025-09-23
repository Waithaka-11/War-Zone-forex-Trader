# ADD THESE IMPORTS TO YOUR EXISTING IMPORTS SECTION
import requests
from streamlit_autorefresh import st_autorefresh

# ADD THESE FUNCTIONS ANYWHERE IN YOUR CODE (before the UI sections)

def normalize_symbol(pair: str) -> str:
    """Convert pair formats (EURUSD or BTCUSD) => 'EUR/USD' or 'BTC/USD'"""
    pair = pair.strip().upper()
    if "/" in pair:
        return pair
    if len(pair) >= 6:
        return f"{pair[:3]}/{pair[3:]}"
    return pair

@st.cache_data(ttl=60, show_spinner=False)
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
        
        # Determine trade direction
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
            # Try to save to sheets if connected
            if st.session_state.sheets_connected:
                try:
                    # Update the specific trade in sheets
                    save_trade_to_sheets(trade)
                except:
                    pass
    
    return updates_made

# ADD THIS SECTION RIGHT AFTER YOUR EXISTING REFRESH CONTROLS
# (After the st.markdown("---") line but before "Add New Trade Section")

# Live Price Monitoring Section
live_col1, live_col2, live_col3 = st.columns([1, 1, 1])

with live_col1:
    try:
        api_key_available = bool(st.secrets.get("twelvedata", {}).get("api_key"))
    except:
        api_key_available = False
    
    if api_key_available:
        if st.button("Check Live Prices", type="secondary", use_container_width=True):
            with st.spinner("Checking prices..."):
                updates = check_and_update_trades()
                if updates > 0:
                    st.success(f"Updated {updates} trade(s)!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("No trades updated")
    else:
        st.button("API Key Required", disabled=True, use_container_width=True)
        if st.button("Setup Help", use_container_width=True):
            st.info("Add 'twelvedata.api_key' to Streamlit secrets")

with live_col2:
    if api_key_available:
        auto_check = st.checkbox("Auto-check trades")
        if auto_check:
            interval = st.selectbox("Interval", [15, 30, 60], format_func=lambda x: f"{x}s")
            
            # Auto-refresh component
            count = st_autorefresh(interval=interval * 1000, key="price_check")
            
            if count > 0:
                updates = check_and_update_trades()
                if updates > 0:
                    st.success(f"Auto-updated {updates} trade(s)!")

with live_col3:
    # Show open trades count
    open_trades = [t for t in st.session_state.trades if t.get("outcome", "") not in ("Target Hit", "SL Hit")]
    st.metric("Open Trades", len(open_trades))
    
    if open_trades and api_key_available:
        st.markdown(f"""
        <div style="font-size: 0.8rem; color: #666; text-align: center;">
            Monitoring {len(set(t.get('instrument', '') for t in open_trades))} instruments
        </div>
        """, unsafe_allow_html=True)
