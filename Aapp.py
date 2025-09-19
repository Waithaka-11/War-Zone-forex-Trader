import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Page config
st.set_page_config(
    page_title="Forex Trading Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - IMPROVED VERSION
st.markdown("""
<style>
    /* Main styles */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Section - Dark Blue Background */
    .header {
        background-color: #2c3e50;
        color: white;
        padding: 15px 0;
        margin-bottom: 20px;
    }
    
    .header-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
        margin: 0;
    }
    
    .nav-buttons {
        display: flex;
        gap: 15px;
    }
    
    .nav-btn {
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.8);
        font-size: 16px;
        cursor: pointer;
        padding: 8px 15px;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .nav-btn:hover {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Card styles */
    .card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border: none;
    }
    
    .card-header {
        background-color: #2c3e50;
        color: white;
        border-radius: 10px 10px 0 0;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .dropdown-arrow {
        cursor: pointer;
        transition: transform 0.3s;
    }
    
    /* IMPROVED FORM LAYOUT */
    .form-container {
        padding: 20px;
    }
    
    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
        align-items: end;
    }
    
    .form-row:last-child {
        margin-bottom: 0;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
    }
    
    .form-label {
        display: block;
        margin-bottom: 8px;
        font-weight: 600;
        color: #2c3e50;
        font-size: 14px;
    }
    
    .form-select, .form-input {
        width: 100%;
        padding: 12px;
        border: 1px solid #ced4da;
        border-radius: 6px;
        font-size: 14px;
        background-color: white;
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    
    .form-select:focus, .form-input:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    /* Suggestion pills - IMPROVED */
    .suggestions-container {
        position: relative;
    }
    
    .suggestion-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    
    .suggestion-pill {
        background-color: #3498db;
        color: white;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        cursor: pointer;
        transition: background-color 0.3s;
        font-weight: 500;
    }
    
    .suggestion-pill:hover {
        background-color: #2980b9;
    }
    
    /* IMPROVED BUTTON */
    .btn-add-trade {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(52, 152, 219, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .btn-add-trade:hover {
        background: linear-gradient(135deg, #2980b9 0%, #1c5a85 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.4);
    }
    
    .btn-add-trade:active {
        transform: translateY(0);
    }
    
    /* Table styles */
    .trading-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .trading-table th {
        background-color: #34495e;
        color: white;
        padding: 12px 8px;
        font-weight: 600;
        text-align: left;
    }
    
    .trading-table td {
        padding: 10px 8px;
        border-bottom: 1px solid #e9ecef;
    }
    
    /* Badge styles */
    .badge-win {
        background-color: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge-loss {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Trader rankings */
    .trader-rank {
        display: flex;
        align-items: center;
        padding: 15px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .rank-badge {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 15px;
    }
    
    .rank-1 { background-color: #ffd700; color: black; }
    .rank-2 { background-color: #c0c0c0; color: black; }
    .rank-3 { background-color: #cd7f32; color: black; }
    
    .progress-bar {
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        margin: 5px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background-color: #28a745;
        border-radius: 4px;
    }
    
    /* Stats boxes */
    .stats-box {
        text-align: center;
        padding: 20px;
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
    
    /* Trader of the month */
    .trader-of-month {
        text-align: center;
        padding: 20px;
    }
    
    .trophy {
        font-size: 48px;
        color: #ffd700;
        margin-bottom: 10px;
    }
    
    /* Delete button */
    .delete-btn {
        background: none;
        border: none;
        color: #dc3545;
        cursor: pointer;
        font-size: 16px;
        padding: 4px;
        border-radius: 4px;
        transition: background-color 0.3s;
    }
    
    .delete-btn:hover {
        background-color: rgba(220, 53, 69, 0.1);
    }
    
    /* Chart placeholder */
    .chart-placeholder {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 250px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
    }
    
    /* Performance grid */
    .performance-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 15px;
    }
    
    .performance-cell {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    
    .performance-bar {
        height: 6px;
        background-color: #e9ecef;
        border-radius: 3px;
        margin-top: 5px;
        overflow: hidden;
    }
    
    .bar-fill {
        height: 100%;
        border-radius: 3px;
    }
    
    .good { background-color: #28a745; }
    .medium { background-color: #ffc107; }
    .poor { background-color: #dc3545; }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .form-row {
            grid-template-columns: 1fr;
            gap: 15px;
        }
        
        .header-title {
            font-size: 18px;
        }
        
        .nav-buttons {
            flex-direction: column;
            gap: 8px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with sample data
if 'trades' not in st.session_state:
    st.session_state.trades = [
        {
            'id': 1, 'date': '2023-10-05', 'trader': 'Waithaka', 'instrument': 'XAUUSD',
            'entry': 1820.50, 'sl': 1815.00, 'target': 1830.00, 'risk': 5.50, 'reward': 9.50,
            'rr_ratio': 1.73, 'outcome': 'Target Hit', 'result': 'Win'
        },
        {
            'id': 2, 'date': '2023-10-04', 'trader': 'Wallace', 'instrument': 'USOIL',
            'entry': 89.30, 'sl': 88.50, 'target': 91.00, 'risk': 0.80, 'reward': 1.70,
            'rr_ratio': 2.13, 'outcome': 'SL Hit', 'result': 'Loss'
        },
        {
            'id': 3, 'date': '2023-10-03', 'trader': 'Max', 'instrument': 'BTCUSD',
            'entry': 27450.00, 'sl': 27200.00, 'target': 27800.00, 'risk': 250.00, 'reward': 350.00,
            'rr_ratio': 1.40, 'outcome': 'Target Hit', 'result': 'Win'
        },
        {
            'id': 4, 'date': '2023-10-02', 'trader': 'Waithaka', 'instrument': 'EURUSD',
            'entry': 1.06250, 'sl': 1.06000, 'target': 1.06700, 'risk': 0.00250, 'reward': 0.00450,
            'rr_ratio': 1.80, 'outcome': 'Target Hit', 'result': 'Win'
        }
    ]

# Header Section
st.markdown("""
<div class="header">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div style="display: flex; align-items: center;">
            <h1 class="header-title"><i class="fas fa-chart-line" style="margin-right: 10px;"></i>Forex Trading Analytics</h1>
        </div>
        <div class="nav-buttons">
            <button class="nav-btn"><i class="fas fa-home" style="margin-right: 5px;"></i>Dashboard</button>
            <button class="nav-btn"><i class="fas fa-history" style="margin-right: 5px;"></i>History</button>
            <button class="nav-btn"><i class="fas fa-cog" style="margin-right: 5px;"></i>Settings</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">', unsafe_allow_html=True)

# IMPROVED Add New Trade Section
st.markdown("""
<div class="card">
    <div class="card-header">
        <div>
            <i class="fas fa-plus-circle" style="margin-right: 8px;"></i>Add New Trade
        </div>
        <span class="dropdown-arrow">▼</span>
    </div>
    <div class="form-container">
        <!-- First Row: Trader, Instrument, Date, Outcome -->
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Trader</label>
                <select class="form-select">
                    <option>Select Trader</option>
                    <option>Waithaka</option>
                    <option>Wallace</option>
                    <option>Max</option>
                </select>
            </div>
            
            <div class="form-group">
                <label class="form-label">Instrument</label>
                <div class="suggestions-container">
                    <input type="text" class="form-input" placeholder="Enter Instrument">
                    <div class="suggestion-pills">
                        <span class="suggestion-pill">XAUUSD</span>
                        <span class="suggestion-pill">USDOIL</span>
                        <span class="suggestion-pill">BTCUSD</span>
                        <span class="suggestion-pill">USTECH</span>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Date</label>
                <input type="date" class="form-input" value="2025-09-19">
            </div>
            
            <div class="form-group">
                <label class="form-label">Outcome</label>
                <select class="form-select">
                    <option>Select Outcome</option>
                    <option>Target Hit</option>
                    <option>SL Hit</option>
                </select>
            </div>
        </div>
        
        <!-- Second Row: Entry Price, Stop Loss, Target Price, Add Button -->
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Entry Price</label>
                <input type="number" class="form-input" placeholder="0.00" step="0.01">
            </div>
            
            <div class="form-group">
                <label class="form-label">Stop Loss (SL)</label>
                <input type="number" class="form-input" placeholder="0.00" step="0.01">
            </div>
            
            <div class="form-group">
                <label class="form-label">Target Price</label>
                <input type="number" class="form-input" placeholder="0.00" step="0.01">
            </div>
            
            <div class="form-group">
                <button class="btn-add-trade">
                    <i class="fas fa-plus"></i>
                    Add Trade
                </button>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Rest of your existing code continues here...
# (Main Content Area with columns, trader rankings, trading history table, etc.)

# Add Font Awesome
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
