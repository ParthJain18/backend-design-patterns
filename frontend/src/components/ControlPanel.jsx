import React, { useState } from 'react';

const ControlPanel = ({ onAddClients, onClear }) => {
  const [count, setCount] = useState(1);

  const handleAdd = (type) => {
    onAddClients(count, type);
  };

  return (
    <div className="bg-white p-4 rounded-xl shadow-md border border-gray-100 mb-6">
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2 border-r pr-4">
          <label className="text-sm font-medium text-gray-700">Count:</label>
          <input 
            type="number" 
            min="1" 
            max="100" 
            value={count} 
            onChange={(e) => setCount(parseInt(e.target.value) || 1)}
            className="w-16 p-2 border rounded-md text-center"
          />
        </div>

        <button onClick={() => handleAdd('req_resp')} className="btn-secondary">
          + Req/Resp
        </button>
        <button onClick={() => handleAdd('short_polling')} className="btn-secondary">
          + Short Poll
        </button>
        <button onClick={() => handleAdd('long_polling')} className="btn-secondary">
          + Long Poll
        </button>
        <button onClick={() => handleAdd('sse')} className="btn-primary">
          + SSE
        </button>
        <button onClick={() => handleAdd('websocket')} className="btn-primary">
          + WebSocket
        </button>
        
        <div className="flex-grow"></div>

        <button onClick={onClear} className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors">
          Clear All
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;
