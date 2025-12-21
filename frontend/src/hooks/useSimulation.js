import { useState, useCallback, useRef } from 'react';
import axios from 'axios';

const API_BASE = '/api';

export const useSimulation = () => {
  const [clients, setClients] = useState([]);
  const [metrics, setMetrics] = useState({
    activeConnections: 0,
    completedJobs: 0,
    avgLatency: 0,
    requestsPerSecond: 0,
  });
  
  // Refs to keep track of active simulations without triggering re-renders for every small update
  // We will flush these to state periodically
  const clientsRef = useRef({});

  const updateClient = (clientId, updates) => {
    clientsRef.current[clientId] = { ...clientsRef.current[clientId], ...updates };
    setClients(Object.values(clientsRef.current));
  };

  const startReqResp = async (clientId) => {
    const start = performance.now();
    updateClient(clientId, { status: 'running', startTime: start, progress: 0 });

    try {
      const response = await axios.post(`${API_BASE}/req_resp/process`, { data: {} });
      const end = performance.now();
      updateClient(clientId, { 
        status: 'completed', 
        progress: 100, 
        endTime: end, 
        duration: end - start 
      });
    } catch (error) {
      updateClient(clientId, { status: 'failed', error: error.message });
    }
  };

  const startShortPolling = async (clientId) => {
    const start = performance.now();
    updateClient(clientId, { status: 'running', startTime: start, progress: 0 });

    try {
      // 1. Trigger Job
      const { data: jobId } = await axios.post(`${API_BASE}/polling/process`, { data: {} });
      
      // 2. Poll
      const poll = async () => {
        try {
          const pollStart = performance.now();
          const { data: status } = await axios.get(`${API_BASE}/polling/status/${jobId}`);
          const pollEnd = performance.now();
          
          updateClient(clientId, { 
            progress: status.progress || 0,
            latency: pollEnd - pollStart 
          });

          if (status.status === 'completed') {
             updateClient(clientId, { 
              status: 'completed', 
              progress: 100, 
              endTime: performance.now(),
              duration: performance.now() - start
            });
          } else {
            setTimeout(poll, 1000); // Poll every 1s
          }
        } catch (err) {
          updateClient(clientId, { status: 'failed', error: err.message });
        }
      };
      
      poll();
    } catch (error) {
      updateClient(clientId, { status: 'failed', error: error.message });
    }
  };

  const startLongPolling = async (clientId) => {
    const start = performance.now();
    updateClient(clientId, { status: 'running', startTime: start, progress: 0 });

    try {
      // 1. Trigger Job
      const { data: jobId } = await axios.post(`${API_BASE}/polling/process`, { data: {} });
      
      // 2. Long Poll (Waits on server)
      const lpStart = performance.now();
      const { data: result } = await axios.get(`${API_BASE}/polling/result/${jobId}`);
      const lpEnd = performance.now();

      updateClient(clientId, { 
        status: 'completed',
        progress: 100,
        endTime: lpEnd,
        duration: lpEnd - start,
        latency: lpEnd - lpStart
      });
    } catch (error) {
      updateClient(clientId, { status: 'failed', error: error.message });
    }
  };

  const startSSE = async (clientId) => {
    const start = performance.now();
    updateClient(clientId, { status: 'running', startTime: start, progress: 0 });

    try {
       // 1. Trigger Job
      const { data: jobId } = await axios.post(`${API_BASE}/polling/process`, { data: {} });
      
      // 2. Open EventSource
      const evtSource = new EventSource(`${API_BASE}/sse/stream/${jobId}`);
      
      evtSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const now = performance.now();
        
        updateClient(clientId, { 
          progress: data.progress,
          latency: now - start // Rough estimate of freshness
        });

        if (data.status === 'completed') {
          evtSource.close();
          updateClient(clientId, { 
            status: 'completed', 
            progress: 100,
            endTime: now,
            duration: now - start
          });
        }
      };

      evtSource.onerror = () => {
        evtSource.close();
        updateClient(clientId, { status: 'failed', error: "SSE Error" });
      };

    } catch (error) {
      updateClient(clientId, { status: 'failed', error: error.message });
    }
  };

  const startWebSocket = async (clientId) => {
    const start = performance.now();
    updateClient(clientId, { status: 'running', startTime: start, progress: 0 });

    try {
      // 1. Trigger Job
      const { data: jobId } = await axios.post(`${API_BASE}/polling/process`, { data: {} });
      
      // 2. Open WebSocket
      // Note: Vite proxy doesn't always handle WS well, might need full URL if it fails, 
      // but let's try relative first or construct absolute from window.location
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/websocket/ws/${jobId}`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const now = performance.now();

        updateClient(clientId, { 
          progress: data.progress,
          latency: now - start 
        });

        if (data.status === 'completed') {
          ws.close();
          updateClient(clientId, { 
            status: 'completed', 
            progress: 100,
            endTime: now,
            duration: now - start
          });
        }
      };

      ws.onerror = (err) => {
         console.error("WS Error", err);
         updateClient(clientId, { status: 'failed', error: "WebSocket Error" });
      };

    } catch (error) {
      updateClient(clientId, { status: 'failed', error: error.message });
    }
  };

  const addClients = (count, type) => {
    for (let i = 0; i < count; i++) {
      const id = `${type}-${Date.now()}-${i}`;
      clientsRef.current[id] = { 
        id, 
        type, 
        status: 'pending', 
        progress: 0,
        startTime: 0 
      };
      
      if (type === 'req_resp') startReqResp(id);
      if (type === 'short_polling') startShortPolling(id);
      if (type === 'long_polling') startLongPolling(id);
      if (type === 'sse') startSSE(id);
      if (type === 'websocket') startWebSocket(id);
    }
    setClients(Object.values(clientsRef.current));
  };

  const clearClients = () => {
    clientsRef.current = {};
    setClients([]);
  };

  return { clients, addClients, clearClients };
};
