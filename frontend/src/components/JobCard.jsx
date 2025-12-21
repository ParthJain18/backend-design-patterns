import React from 'react';
import clsx from 'clsx';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

const JobCard = ({ client }) => {
  const getStatusColor = () => {
    switch (client.status) {
      case 'completed': return 'bg-green-100 border-green-200';
      case 'failed': return 'bg-red-100 border-red-200';
      case 'running': return 'bg-blue-50 border-blue-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const getIcon = () => {
    switch (client.status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'failed': return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'running': return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      default: return <div className="w-5 h-5" />;
    }
  };

  return (
    <div className={clsx("p-3 rounded-lg border shadow-sm transition-all", getStatusColor())}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-semibold uppercase text-gray-500">{client.type}</span>
        {getIcon()}
      </div>
      <div className="text-sm font-mono text-gray-700 truncate mb-2">{client.id}</div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
        <div 
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
          style={{ width: `${client.progress}%` }}
        ></div>
      </div>

      <div className="flex justify-between text-xs text-gray-600">
        <span>{client.status}</span>
        {client.duration && <span>{(client.duration / 1000).toFixed(2)}s</span>}
      </div>
    </div>
  );
};

export default JobCard;
