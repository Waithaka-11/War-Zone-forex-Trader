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

# Custom CSS to match the exact UI description
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
    
    /* Form styles */
    .form-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        padding: 20px;
    }
    
    .form-group {
        margin-bottom: 15px;
    }
    
    .form-label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
        color: #2c3e50;
    }
    
    .form-select, .form-input {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #ced4da;
        border-radius: 5px;
        font-size: 14px;
    }
    
    .btn-primary {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: 600;
        cursor: pointer;
    }
    
    .btn-primary:hover {
        background-color: #2980b9;
    }
    
    /* Suggestion pills */
    .suggestion-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 5px;
    }
    
    .suggestion-pill {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        cursor: pointer;
    }
    
    /* Delete button */
    .delete-btn {
        background: none;
        border: none;
        color: #dc3545;
        cursor: pointer;
        font-size: 16px;
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

# Add New Trade Section
st.markdown("""
<div class="card">
    <div class="card-header">
        <i class="fas fa-plus-circle me-2"></i>Add New Trade
    </div>
    <div class="form-grid">
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
            <input type="text" class="form-input" placeholder="Enter instrument">
            <div class="suggestion-pills">
                <span class="suggestion-pill">XAUUSD</span>
                <span class="suggestion-pill">USOIL</span>
                <span class="suggestion-pill">BTCUSD</span>
                <span class="suggestion-pill">USTECH</span>
            </div>
        </div>
        
        <div class="form-group">
            <label class="form-label">Date</label>
            <input type="text" class="form-input" value="09/19/2025">
        </div>
        
        <div class="form-group">
            <label class="form-label">Outcome</label>
            <select class="form-select">
                <option>Select Outcome</option>
                <option>Target Hit</option>
                <option>SL Hit</option>
            </select>
        </div>
        
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
        
        <div class="form-group" style="display: flex; align-items: flex-end;">
            <button class="btn-primary"><i class="fas fa-plus" style="margin-right: 5px;"></i>Add Trade</button>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    # Trader Performance Rankings
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-trophy me-2"></i>Trader Performance Rankings
        </div>
        <div>
            <div class="trader-rank">
                <div class="rank-badge rank-1">1</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #2c3e50;">Waithaka</div>
                    <div style="font-size: 14px; color: #6c757d;">72.5% win rate</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 72.5%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">Wins: 13 | Losses: 5</div>
                </div>
            </div>
            
            <div class="trader-rank">
                <div class="rank-badge rank-2">2</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #2c3e50;">Max</div>
                    <div style="font-size: 14px; color: #6c757d;">65.3% win rate</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 65.3%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">Wins: 10 | Losses: 5</div>
                </div>
            </div>
            
            <div class="trader-rank">
                <div class="rank-badge rank-3">3</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #2c3e50;">Wallace</div>
                    <div style="font-size: 14px; color: #6c757d;">58.7% win rate</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 58.7%;"></div>
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">Wins: 9 | Losses: 7</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Trading History Table
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-table me-2"></i>Trading History
        </div>
        <div style="padding: 20px;">
            <table class="trading-table">
                <thead>
                    <tr>
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
                    <tr>
                        <td>XAUUSD</td>
                        <td>1820.50</td>
                        <td>1815.00</td>
                        <td>1830.00</td>
                        <td>5.50</td>
                        <td>9.50</td>
                        <td>1.73</td>
                        <td>Target Hit</td>
                        <td><span class="badge-win">Win</span></td>
                        <td><button class="delete-btn"><i class="fas fa-trash"></i></button></td>
                    </tr>
                    <tr>
                        <td>USOIL</td>
                        <td>89.30</td>
                        <td>88.50</td>
                        <td>91.00</td>
                        <td>0.80</td>
                        <td>1.70</td>
                        <td>2.13</td>
                        <td>SL Hit</td>
                        <td><span class="badge-loss">Loss</span></td>
                        <td><button class="delete-btn"><i class="fas fa-trash"></i></button></td>
                    </tr>
                    <tr>
                        <td>BTCUSD</td>
                        <td>27450.00</td>
                        <td>27200.00</td>
                        <td>27800.00</td>
                        <td>250.00</td>
                        <td>350.00</td>
                        <td>1.40</td>
                        <td>Target Hit</td>
                        <td><span class="badge-win">Win</span></td>
                        <td><button class="delete-btn"><i class="fas fa-trash"></i></button></td>
                    </tr>
                    <tr>
                        <td>EURUSD</td>
                        <td>1.06250</td>
                        <td>1.06000</td>
                        <td>1.06700</td>
                        <td>0.00250</td>
                        <td>0.00450</td>
                        <td>1.80</td>
                        <td>Target Hit</td>
                        <td><span class="badge-win">Win</span></td>
                        <td><button class="delete-btn"><i class="fas fa-trash"></i></button></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Performance Metrics - Win Rate Distribution
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-chart-pie me-2"></i>Overall Win Rate Distribution
        </div>
        <div style="padding: 20px;">
            <div class="chart-placeholder">
                Donut Chart: Waithaka (72.5%), Max (65.3%), Wallace (56.7%)
            </div>
            <div style="margin-top: 15px;">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 12px; height: 12px; background-color: #ff6384; border-radius: 2px; margin-right: 8px;"></div>
                    <span>Waithaka (72.5%)</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 12px; height: 12px; background-color: #36a2eb; border-radius: 2px; margin-right: 8px;"></div>
                    <span>Max (65.3%)</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background-color: #ffcd56; border-radius: 2px; margin-right: 8px;"></div>
                    <span>Wallace (56.7%)</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Trader of the Month
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-award me-2"></i>Trader of the Month
        </div>
        <div class="trader-of-month">
            <div class="trophy">🏆</div>
            <h3 style="color: #2c3e50; margin-bottom: 5px;">Waithaka</h3>
            <p style="color: #6c757d; margin-bottom: 15px;">Best performance with 72.5% win rate</p>
            <div class="stats-box positive">
                <h6>WIN RATE THIS MONTH</h6>
                <h3>72.5%</h3>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Instrument Performance by Trader
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <i class="fas fa-chart-bar me-2"></i>Instrument Performance by Trader
        </div>
        <div style="padding: 20px;">
            <div class="performance-grid">
                <div class="performance-cell">
                    <div style="font-size: 12px; color: #6c757d;">XAUUSD</div>
                    <div style="font-weight: 600;">Waithaka</div>
                    <div class="performance-bar">
                        <div class="bar-fill good" style="width: 85%;"></div>
                    </div>
                </div>
                <div class="performance-cell">
                    <div style="font-size: 12px; color: #6c757d;">USOIL</div>
                    <div style="font-weight: 600;">Wallace</div>
                    <div class="performance-bar">
                        <div class="bar-fill medium" style="width: 60%;"></div>
                    </div>
                </div>
                <div class="performance-cell">
                    <div style="font-size: 12px; color: #6c757d;">BTCUSD</div>
                    <div style="font-weight: 600;">Max</div>
                    <div class="performance-bar">
                        <div class="bar-fill good" style="width: 78%;"></div>
                    </div>
                </div>
                <div class="performance-cell">
                    <div style="font-size: 12px; color: #6c757d;">USTECH</div>
                    <div style="font-weight: 600;">Waithaka</div>
                    <div class="performance-bar">
                        <div class="bar-fill poor" style="width: 40%;"></div>
                    </div>
                </div>
                <div class="performance-cell">
                    <div style="font-size: 12px; color: #6c757d;">EURUSD</div>
                    <div style="font-weight: 600;">Max</div>
                    <div class="performance-bar">
                        <div class="bar-fill good" style="width: 82%;"></div>
                    </div>
                </div>
                <div class="performance-cell">
                    <div style="font-size: 12px; color: #6c757d;">GBPUSD</div>
                    <div style="font-weight: 600;">Wallace</div>
                    <div class="performance-bar">
                        <div class="bar-fill medium" style="width: 55%;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add Font Awesome
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
