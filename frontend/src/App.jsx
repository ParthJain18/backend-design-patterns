import React from 'react';
import { useSimulation } from './hooks/useSimulation';
import JobCard from './components/JobCard';
import ControlPanel from './components/ControlPanel';
import StatsPanel from './components/StatsPanel';

function App() {
  const { clients, addClients, clearClients } = useSimulation();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Backend Patterns Playground</h1>
          <p className="text-gray-600 mt-2">Simulate and compare Request-Response, Polling, SSE, and WebSocket patterns.</p>
        </header>

        <ControlPanel onAddClients={addClients} onClear={clearClients} />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
             <div className="bg-white p-4 rounded-xl shadow-md border border-gray-100 min-h-[500px]">
               <h3 className="text-lg font-semibold text-gray-800 mb-4 flex justify-between">
                 <span>Active Clients</span>
                 <span className="text-sm font-normal text-gray-500">{clients.length} total</span>
               </h3>
               
               <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 max-h-[600px] overflow-y-auto p-2">
                 {clients.map(client => (
                   <JobCard key={client.id} client={client} />
                 ))}
                 {clients.length === 0 && (
                   <div className="col-span-full text-center py-20 text-gray-400">
                     No active simulations. Use the control panel to add clients.
                   </div>
                 )}
               </div>
             </div>
          </div>
          
          <div>
            <StatsPanel clients={clients} />
            
            {/* Legend / Info */}
            <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 mt-6">
              <h4 className="font-semibold mb-3">Pattern Guide</h4>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="px-2 py-0.5 bg-gray-200 rounded text-xs font-mono">Req/Resp</span>
                  <span>Blocks until finished. Good for simple tasks, bad for long-running ones (timeouts).</span>
                </li>
                <li className="flex items-start gap-2">
                   <span className="px-2 py-0.5 bg-gray-200 rounded text-xs font-mono">Short Poll</span>
                   <span>Spams server with checks. High overhead, high latency.</span>
                </li>
                <li className="flex items-start gap-2">
                   <span className="px-2 py-0.5 bg-gray-200 rounded text-xs font-mono">Long Poll</span>
                   <span>Server holds connection. Better than short poll, but ties up connections.</span>
                </li>
                <li className="flex items-start gap-2">
                   <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-mono">SSE</span>
                   <span>One-way real-time stream. Great for status updates. Lightweight.</span>
                </li>
                <li className="flex items-start gap-2">
                   <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-mono">WebSocket</span>
                   <span>Full bi-directional channel. Lowest latency, most complex to scale.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;