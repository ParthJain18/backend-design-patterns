import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const StatsPanel = ({ clients }) => {
  const completed = clients.filter(c => c.status === 'completed');
  
  // Calculate average duration per type
  const stats = ['req_resp', 'short_polling', 'long_polling', 'sse', 'websocket'].map(type => {
    const typeClients = completed.filter(c => c.type === type);
    const avgDuration = typeClients.length 
      ? typeClients.reduce((acc, c) => acc + c.duration, 0) / typeClients.length 
      : 0;
    
    return {
      name: type,
      avgDuration: avgDuration / 1000, // seconds
      count: typeClients.length
    };
  });

  return (
    <div className="bg-white p-4 rounded-xl shadow-md border border-gray-100 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Performance Metrics (Avg Duration)</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={stats}>
            <XAxis dataKey="name" />
            <YAxis label={{ value: 'Seconds', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="avgDuration" fill="#3b82f6">
               {stats.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={['#94a3b8', '#94a3b8', '#94a3b8', '#3b82f6', '#8b5cf6'][index]} />
                ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default StatsPanel;
