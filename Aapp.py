import React, { useState } from 'react';
import { ChevronDown, Home, Clock, Settings, Plus, Trophy, Award, BarChart3, Table, PieChart, Trash2 } from 'lucide-react';

const ForexTradingAnalytics = () => {
  const [selectedInstrument, setSelectedInstrument] = useState('');
  const [trades, setTrades] = useState([
    { id: 1, date: '2023-10-08', trader: 'Waithaka', instrument: 'XAUUSD', entry: 1820.50, sl: 1815.00, target: 1830.00, risk: 5.50, reward: 9.50, rrRatio: 1.73, outcome: 'Target Hit', result: 'Win' },
    { id: 2, date: '2023-10-07', trader: 'Wallace', instrument: 'USOIL', entry: 89.30, sl: 88.50, target: 91.00, risk: 0.80, reward: 1.70, rrRatio: 2.13, outcome: 'SL Hit', result: 'Loss' },
    { id: 3, date: '2023-10-06', trader: 'Max', instrument: 'BTCUSD', entry: 27450.00, sl: 27200.00, target: 27800.00, risk: 250.00, reward: 350.00, rrRatio: 1.40, outcome: 'Target Hit', result: 'Win' },
    { id: 4, date: '2023-10-05', trader: 'Waithaka', instrument: 'EURUSD', entry: 1.06250, sl: 1.06000, target: 1.06700, risk: 0.00250, reward: 0.00450, rrRatio: 1.80, outcome: 'Target Hit', result: 'Win' }
  ]);

  const instrumentPairs = ['XAUUSD', 'USDOIL', 'BTCUSD', 'USTECH', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY', 'USDCAD', 'NZDUSD'];

  const deleteTrade = (id) => {
    setTrades(trades.filter(trade => trade.id !== id));
  };

  const handleInstrumentSelect = (instrument) => {
    setSelectedInstrument(instrument);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-slate-700 text-white px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <BarChart3 className="mr-3 h-6 w-6" />
            <h1 className="text-xl font-bold">Forex Trading Analytics</h1>
          </div>
          <div className="flex space-x-4">
            <button className="flex items-center px-3 py-2 text-sm hover:bg-slate-600 rounded">
              <Home className="mr-2 h-4 w-4" />
              Dashboard
            </button>
            <button className="flex items-center px-3 py-2 text-sm hover:bg-slate-600 rounded">
              <Clock className="mr-2 h-4 w-4" />
              History
            </button>
            <button className="flex items-center px-3 py-2 text-sm hover:bg-slate-600 rounded">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </button>
          </div>
        </div>
      </div>

      <div className="p-6 max-w-7xl mx-auto">
        {/* Add New Trade Section */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="bg-slate-700 text-white px-4 py-3 rounded-t-lg flex justify-between items-center">
            <div className="flex items-center">
              <div className="bg-teal-600 rounded-full p-1 mr-3">
                <Plus className="h-4 w-4" />
              </div>
              <span className="font-semibold">Add New Trade</span>
            </div>
            <ChevronDown className="h-4 w-4" />
          </div>
          
          <div className="p-6">
            {/* First Row */}
            <div className="grid grid-cols-4 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Trader</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white">
                  <option>Select Trader</option>
                  <option>Waithaka</option>
                  <option>Wallace</option>
                  <option>Max</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Instrument</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="Enter Instrument"
                  value={selectedInstrument}
                  onChange={(e) => setSelectedInstrument(e.target.value)}
                />
                <div className="flex gap-2 mt-2 flex-wrap">
                  {instrumentPairs.map(pair => (
                    <span 
                      key={pair}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full cursor-pointer hover:bg-blue-200 transition-colors"
                      onClick={() => handleInstrumentSelect(pair)}
                    >
                      {pair}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value="09/19/2025"
                  readOnly
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Outcome</label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white">
                  <option>Select Outcome</option>
                  <option>Target Hit</option>
                  <option>SL Hit</option>
                </select>
              </div>
            </div>

            {/* Second Row */}
            <div className="grid grid-cols-4 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Entry Price</label>
                <input 
                  type="number" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="0.00"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Stop Loss (SL)</label>
                <input 
                  type="number" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="0.00"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Target Price</label>
                <input 
                  type="number" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="0.00"
                />
              </div>
              
              <div className="flex items-end">
                <button className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md flex items-center justify-center">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Trade
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-3 gap-6">
          {/* Left Column - 2/3 width */}
          <div className="col-span-2 space-y-6">
            {/* Trader Performance Rankings */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-slate-700 text-white px-4 py-3 rounded-t-lg">
                <h3 className="font-semibold">Trader Performance Rankings</h3>
              </div>
              <div className="p-6">
                {/* Waithaka - Rank 1 */}
                <div className="flex items-center mb-6">
                  <div className="bg-yellow-400 text-black font-bold w-8 h-8 rounded-full flex items-center justify-center mr-4">1</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-semibold text-gray-800">Waithaka</span>
                      <span className="text-sm font-medium">Win Rate: 72.5%</span>
                    </div>
                    <div className="text-xs text-gray-600 mb-2">Total Trades: 18</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '72.5%'}}></div>
                    </div>
                    <div className="text-xs text-gray-600">Wins: 13 | Losses: 5</div>
                  </div>
                </div>

                {/* Max - Rank 2 */}
                <div className="flex items-center mb-6">
                  <div className="bg-gray-400 text-black font-bold w-8 h-8 rounded-full flex items-center justify-center mr-4">2</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-semibold text-gray-800">Max</span>
                      <span className="text-sm font-medium">Win Rate: 65.3%</span>
                    </div>
                    <div className="text-xs text-gray-600 mb-2">Total Trades: 15</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '65.3%'}}></div>
                    </div>
                    <div className="text-xs text-gray-600">Wins: 10 | Losses: 5</div>
                  </div>
                </div>

                {/* Wallace - Rank 3 */}
                <div className="flex items-center">
                  <div className="bg-orange-400 text-black font-bold w-8 h-8 rounded-full flex items-center justify-center mr-4">3</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-semibold text-gray-800">Wallace</span>
                      <span className="text-sm font-medium">Win Rate: 58.7%</span>
                    </div>
                    <div className="text-xs text-gray-600 mb-2">Total Trades: 16</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '58.7%'}}></div>
                    </div>
                    <div className="text-xs text-gray-600">Wins: 9 | Losses: 7</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Trading History */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-slate-700 text-white px-4 py-3 rounded-t-lg flex items-center">
                <Table className="mr-2 h-4 w-4" />
                <h3 className="font-semibold">Trading History</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-600 text-white">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Trader</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Instrument</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Entry</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">SL</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Target</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Risk</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Reward</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">R/R Ratio</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Outcome</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Result</th>
                      <th className="px-4 py-3 text-left text-xs font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {trades.map((trade) => (
                      <tr key={trade.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm">{trade.date}</td>
                        <td className="px-4 py-3 text-sm">{trade.trader}</td>
                        <td className="px-4 py-3 text-sm">{trade.instrument}</td>
                        <td className="px-4 py-3 text-sm">{trade.entry}</td>
                        <td className="px-4 py-3 text-sm">{trade.sl}</td>
                        <td className="px-4 py-3 text-sm">{trade.target}</td>
                        <td className="px-4 py-3 text-sm">{trade.risk}</td>
                        <td className="px-4 py-3 text-sm">{trade.reward}</td>
                        <td className="px-4 py-3 text-sm">{trade.rrRatio}</td>
                        <td className="px-4 py-3 text-sm">{trade.outcome}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            trade.result === 'Win' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {trade.result}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <button 
                            onClick={() => deleteTrade(trade.id)}
                            className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded transition-colors"
                            title="Delete trade"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column - 1/3 width */}
          <div className="space-y-6">
            {/* Performance Metrics */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-slate-700 text-white px-4 py-3 rounded-t-lg flex items-center">
                <PieChart className="mr-2 h-4 w-4" />
                <h3 className="font-semibold">Performance Metrics</h3>
              </div>
              <div className="p-6">
                <div className="bg-slate-600 text-white px-3 py-2 rounded-t text-sm font-medium">
                  Overall Win Rate Distribution
                </div>
                <div className="p-4 bg-gray-50 rounded-b">
                  {/* Enhanced Donut Chart with 3 Distinctive Colors */}
                  <div className="w-48 h-48 mx-auto mb-4 relative">
                    <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                      {/* Background circle */}
                      <circle cx="50" cy="50" r="35" fill="none" stroke="#f3f4f6" strokeWidth="12"/>
                      
                      {/* Waithaka - 37.1% of total - Blue (largest individual segment) */}
                      <circle 
                        cx="50" 
                        cy="50" 
                        r="35" 
                        fill="none" 
                        stroke="#3b82f6" 
                        strokeWidth="12" 
                        strokeDasharray="81.6 138.4" 
                        strokeDashoffset="0"
                        className="transition-all duration-500"
                      />
                      
                      {/* Max - 33.5% of total - Black (middle segment) */}
                      <circle 
                        cx="50" 
                        cy="50" 
                        r="35" 
                        fill="none" 
                        stroke="#000000" 
                        strokeWidth="12" 
                        strokeDasharray="73.7 146.3" 
                        strokeDashoffset="-81.6"
                        className="transition-all duration-500"
                      />
                      
                      {/* Wallace - 29.4% of total - Yellow (smallest segment) */}
                      <circle 
                        cx="50" 
                        cy="50" 
                        r="35" 
                        fill="none" 
                        stroke="#eab308" 
                        strokeWidth="12" 
                        strokeDasharray="64.7 155.3" 
                        strokeDashoffset="-155.3"
                        className="transition-all duration-500"
                      />
                    </svg>
                    {/* Center text */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-xl font-bold text-gray-700">65.5%</div>
                        <div className="text-xs text-gray-500">Avg Rate</div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
                        <span>Waithaka</span>
                      </div>
                      <span className="font-semibold">72.5%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-black rounded mr-2"></div>
                        <span>Max</span>
                      </div>
                      <span className="font-semibold">65.3%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-yellow-500 rounded mr-2"></div>
                        <span>Wallace</span>
                      </div>
                      <span className="font-semibold">58.7%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Trader of the Month */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-slate-700 text-white px-4 py-3 rounded-t-lg flex items-center">
                <Award className="mr-2 h-4 w-4" />
                <h3 className="font-semibold">Trader of the Month</h3>
              </div>
              <div className="p-6 text-center">
                <div className="text-6xl mb-4">🏆</div>
                <h4 className="text-xl font-bold text-gray-800 mb-2">Waithaka</h4>
                <p className="text-gray-600 text-sm mb-4">Best performance with 72.5% win rate</p>
                <div className="bg-green-100 rounded-lg p-4">
                  <div className="text-xs text-gray-600 uppercase tracking-wide">WIN RATE THIS MONTH</div>
                  <div className="text-2xl font-bold text-green-700">72.5%</div>
                </div>
              </div>
            </div>

            {/* Instrument Performance by Trader */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="bg-slate-700 text-white px-4 py-3 rounded-t-lg flex items-center">
                <BarChart3 className="mr-2 h-4 w-4" />
                <h3 className="font-semibold">Instrument Performance by Trader</h3>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-4 gap-1 text-xs">
                  {/* Header */}
                  <div className="bg-slate-600 text-white font-semibold text-center p-3 rounded">Instrument</div>
                  <div className="bg-slate-600 text-white font-semibold text-center p-3 rounded">Waithaka</div>
                  <div className="bg-slate-600 text-white font-semibold text-center p-3 rounded">Wallace</div>
                  <div className="bg-slate-600 text-white font-semibold text-center p-3 rounded">Max</div>
                  
                  {/* XAUUSD */}
                  <div className="text-center p-3 font-medium bg-gray-100 rounded">XAUUSD</div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-semibold">75%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-semibold">60%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-gray-400 text-white px-2 py-1 rounded text-xs font-semibold">-</div>
                  </div>
                  
                  {/* USOIL */}
                  <div className="text-center p-3 font-medium bg-gray-100 rounded">USOIL</div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-semibold">80%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-yellow-500 text-white px-2 py-1 rounded text-xs font-semibold">50%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-gray-400 text-white px-2 py-1 rounded text-xs font-semibold">-</div>
                  </div>
                  
                  {/* BTCUSD */}
                  <div className="text-center p-3 font-medium bg-gray-100 rounded">BTCUSD</div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-yellow-500 text-white px-2 py-1 rounded text-xs font-semibold">55%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-gray-400 text-white px-2 py-1 rounded text-xs font-semibold">-</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-semibold">65%</div>
                  </div>
                  
                  {/* USTECH */}
                  <div className="text-center p-3 font-medium bg-gray-100 rounded">USTECH</div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-semibold">70%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-red-500 text-white px-2 py-1 rounded text-xs font-semibold">40%</div>
                  </div>
                  <div className="p-2 flex items-center justify-center">
                    <div className="bg-gray-400 text-white px-2 py-1 rounded text-xs font-semibold">-</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForexTradingAnalytics;
