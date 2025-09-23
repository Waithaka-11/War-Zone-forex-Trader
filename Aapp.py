# Trading History
st.markdown("""
<div class="trade-card">
    <div class="card-header">
        <h3 style="font-weight: 600; margin: 0;">Trading History</h3>
    </div>
    <div class="card-body">
""", unsafe_allow_html=True)

# Display trades table
if st.session_state.trades and len(st.session_state.trades) > 0:
    df = pd.DataFrame(st.session_state.trades)
    
    # Sort by date descending (most recent first)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Format the dataframe for display
    display_df = df.copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['entry'] = display_df['entry'].round(4)
    display_df['sl'] = display_df['sl'].round(4)
    display_df['target'] = display_df['target'].round(4)
    display_df['risk'] = display_df['risk'].round(4)
    display_df['reward'] = display_df['reward'].round(4)
    display_df['rrRatio'] = display_df['rrRatio'].round(2)
    
    # Rename columns for better display
    display_df = display_df.rename(columns={
        'id': 'ID',
        'date': 'Date',
        'trader': 'Trader',
        'instrument': 'Instrument',
        'entry': 'Entry',
        'sl': 'Stop Loss',
        'target': 'Target',
        'risk': 'Risk',
        'reward': 'Reward',
        'rrRatio': 'R:R Ratio',
        'outcome': 'Outcome',
        'result': 'Result'
    })
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Add delete functionality
    st.markdown("### Delete Trade")
    col_delete1, col_delete2 = st.columns([2, 1])
    
    with col_delete1:
        trade_ids = [trade['id'] for trade in st.session_state.trades]
        selected_id = st.selectbox("Select Trade ID to Delete", [None] + trade_ids)
    
    with col_delete2:
        st.markdown('<div style="padding-top: 1.5rem;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Delete Trade", type="secondary"):
            if selected_id:
                # Remove from session state
                st.session_state.trades = [trade for trade in st.session_state.trades if trade['id'] != selected_id]
                
                # Remove from Google Sheets if connected
                if st.session_state.sheets_connected:
                    try:
                        delete_trade_from_sheets(selected_id)
                        force_refresh_data()
                    except:
                        pass
                
                st.success(f"✅ Trade {selected_id} deleted successfully!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Please select a trade ID to delete.")

else:
    st.info("No trades available. Add your first trade above!")

st.markdown('</div></div>', unsafe_allow_html=True)

# Close the main content div
st.markdown('</div>', unsafe_allow_html=True)
