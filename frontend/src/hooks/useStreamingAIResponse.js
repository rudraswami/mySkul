import { useCallback, useRef, useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const STREAM_ENDPOINT = `${BACKEND_URL}/api/ai/dual-response?stream=true`;

const parseSseEvent = (rawEvent) => {
  const lines = rawEvent.split('\n');
  let event = 'message';
  const dataLines = [];

  lines.forEach((line) => {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim() || 'message';
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim());
    }
  });

  const dataPayload = dataLines.join('\n');
  let parsedData = null;

  if (dataPayload) {
    try {
      parsedData = JSON.parse(dataPayload);
    } catch {
      parsedData = dataPayload;
    }
  }

  return { event, data: parsedData };
};

const useStreamingAIResponse = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState(null);
  const abortControllerRef = useRef(null);

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const startStream = useCallback(async ({ payload, token, onEvent }) => {
    cancelStream();

    const controller = new AbortController();
    abortControllerRef.current = controller;
    setIsStreaming(true);
    setStreamError(null);

    try {
      const response = await fetch(STREAM_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
        credentials: 'include',
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error(`Stream failed with status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        buffer = buffer.replace(/\r\n/g, '\n');

        let boundary = buffer.indexOf('\n\n');
        while (boundary !== -1) {
          const rawEvent = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);

          if (rawEvent.trim()) {
            const parsedEvent = parseSseEvent(rawEvent);
            if (onEvent) {
              await onEvent(parsedEvent);
            }
          }

          boundary = buffer.indexOf('\n\n');
        }
      }

      buffer += decoder.decode();
      buffer = buffer.replace(/\r\n/g, '\n');
      if (buffer.trim()) {
        const parsedEvent = parseSseEvent(buffer.trim());
        if (onEvent) {
          await onEvent(parsedEvent);
        }
      }
    } catch (error) {
      if (controller.signal.aborted) {
        return;
      }

      setStreamError(error);
      if (onEvent) {
        await onEvent({
          event: 'error',
          data: { message: error.message },
        });
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [cancelStream]);

  return {
    startStream,
    cancelStream,
    isStreaming,
    streamError,
  };
};

export default useStreamingAIResponse;
