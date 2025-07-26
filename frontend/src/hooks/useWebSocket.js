import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import { useLanguage } from '../contexts/LanguageContext';

export function useWebSocket(url, token) {
  const ws = useRef(null);
  const queryClient = useQueryClient();
  const { t } = useLanguage();
  const reconnectTimeout = useRef(null);
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    ws.current = new WebSocket(`${url}?token=${token}`);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      reconnectAttempts.current = 0;
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'room_update':
          queryClient.invalidateQueries(['rooms']);
          if (data.action === 'update') {
            toast.success(t('roomUpdated'));
          }
          break;

        case 'booking_update':
          queryClient.invalidateQueries(['rooms']);
          queryClient.invalidateQueries(['bookings']);
          if (data.action === 'create') {
            toast.success(t('bookingCreated'));
          } else if (data.action === 'delete') {
            toast.success(t('bookingDeleted'));
          }
          break;

        case 'pong':
          // Keep-alive response
          break;

        default:
          console.log('Unknown message type:', data.type);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');

      // Exponential backoff for reconnection
      const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
      reconnectAttempts.current++;

      reconnectTimeout.current = setTimeout(() => {
        connect();
      }, timeout);
    };
  }, [url, token, queryClient, t]);

  useEffect(() => {
    connect();

    // Keep-alive ping every 30 seconds
    const pingInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    return () => {
      clearInterval(pingInterval);
      clearTimeout(reconnectTimeout.current);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  return { sendMessage };
}