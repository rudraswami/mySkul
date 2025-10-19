/**
 * PHASE 4: Service Worker for Auto-Note Mentor PWA
 * Provides offline recording capabilities, caching, and background sync
 */

const CACHE_NAME = 'dhruv-ai-auto-notes-v5';
const AUDIO_CACHE_NAME = 'dhruv-ai-audio-cache-v5';
const API_CACHE_NAME = 'dhruv-ai-api-cache-v5-NEVER-USE'; // Marking as NEVER-USE since we bypass all API caching

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/auto-notes',
  // Add other critical assets
];

// API endpoints that can be cached
const CACHEABLE_APIS = [
  '/api/auto-notes/sessions',
  '/api/subscription/current',
  '/api/subscription/usage'
];

// Audio processing queue for offline uploads
let audioUploadQueue = [];
let isOnline = navigator.onLine;

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Install event');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Initialize audio cache
      caches.open(AUDIO_CACHE_NAME),
      
      // Initialize API cache
      caches.open(API_CACHE_NAME)
    ]).then(() => {
      console.log('Service Worker: Installation complete');
      self.skipWaiting(); // Force activation of new service worker
    })
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activate event');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Delete ALL old cache versions including API cache
          // This ensures no stale 404/422 responses are served
          if (cacheName !== CACHE_NAME && 
              cacheName !== AUDIO_CACHE_NAME) {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
          // CRITICAL: Also delete API_CACHE_NAME to clear all API responses
          if (cacheName === API_CACHE_NAME) {
            console.log('Service Worker: Clearing API cache to prevent stale responses');
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Activation complete, all old caches cleared');
      return self.clients.claim(); // Take control of all clients immediately
    })
  );
});

// Fetch event - handle network requests with caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // CRITICAL FIX: For ALL /api/ routes, ALWAYS go directly to network
  // NEVER cache API responses to prevent stale data
  if (url.pathname.startsWith('/api/') || url.href.includes('/api/')) {
    // Bypass service worker completely for ALL API requests
    event.respondWith(
      fetch(request).catch(error => {
        console.error('Service Worker: API request failed', url.pathname, error);
        return new Response(
          JSON.stringify({ 
            error: 'Network unavailable', 
            offline: true,
            message: 'This request requires internet connection.' 
          }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );
    return;
  }
  
  // Handle audio file requests
  if (request.url.includes('audio') || request.url.includes('.wav') || 
      request.url.includes('.mp3') || request.url.includes('.webm')) {
    event.respondWith(handleAudioRequest(request));
    return;
  }
  
  // Handle static assets (cache-first strategy)
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        console.log('Service Worker: Serving from cache', request.url);
        return response;
      }
      
      // Network fallback
      return fetch(request).then((response) => {
        // Cache successful responses
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseClone);
          });
        }
        return response;
      }).catch(() => {
        // Return offline fallback page
        if (request.destination === 'document') {
          return caches.match('/offline.html') || 
                 new Response('App is offline. Please check your connection.', {
                   status: 200,
                   headers: { 'Content-Type': 'text/plain' }
                 });
        }
      });
    })
  );
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  // CRITICAL FIX: Never cache non-GET requests (POST, PUT, DELETE, PATCH)
  // These methods cannot be cached as per Cache API specification
  if (request.method !== 'GET') {
    try {
      return await fetch(request);
    } catch (error) {
      // Handle offline POST requests specially
      if (request.method === 'POST' && url.pathname.includes('/upload-audio')) {
        return handleOfflineAudioUpload(request);
      }
      
      // For other non-GET requests, return offline response
      return new Response(
        JSON.stringify({ 
          error: 'Network unavailable', 
          offline: true,
          message: 'This request requires internet connection.' 
        }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
  }
  
  // For GET requests, use network-first with cache fallback
  try {
    // Try network first
    const response = await fetch(request);
    
    // Cache successful GET requests (only 200 OK responses)
    if (response.status === 200) {
      const cache = await caches.open(API_CACHE_NAME);
      // Clone response before caching
      cache.put(request, response.clone()).catch(err => {
        console.log('Service Worker: Cache put failed', err);
      });
    }
    
    return response;
    
  } catch (error) {
    console.log('Service Worker: API request failed, checking cache', url.pathname);
    
    // Fallback to cache for GET requests only
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('Service Worker: Serving API from cache', url.pathname);
      return cachedResponse;
    }
    
    // Return offline response
    return new Response(
      JSON.stringify({ 
        error: 'Network unavailable', 
        offline: true,
        message: 'This request will be processed when you\'re back online.' 
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle audio file requests
async function handleAudioRequest(request) {
  try {
    // Try network first for audio files
    const response = await fetch(request);
    
    // Cache audio files for offline playback
    if (response.status === 200) {
      const cache = await caches.open(AUDIO_CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
    
  } catch (error) {
    // Fallback to cached audio
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('Service Worker: Serving audio from cache', request.url);
      return cachedResponse;
    }
    
    // Return audio unavailable response
    return new Response('Audio file not available offline', {
      status: 404,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Handle offline audio upload - store for later sync
async function handleOfflineAudioUpload(request) {
  console.log('Service Worker: Queuing audio upload for offline processing');
  
  try {
    // Clone and store request data
    const formData = await request.formData();
    const audioFile = formData.get('file');
    const sessionId = formData.get('session_id');
    
    // Store in IndexedDB for later upload
    const uploadData = {
      id: generateUploadId(),
      sessionId: sessionId,
      audioBlob: audioFile,
      timestamp: Date.now(),
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries())
    };
    
    await storeOfflineUpload(uploadData);
    
    // Add to queue
    audioUploadQueue.push(uploadData.id);
    
    // Notify client
    notifyClients({
      type: 'AUDIO_QUEUED_OFFLINE',
      uploadId: uploadData.id,
      message: 'Audio queued for upload when online'
    });
    
    return new Response(
      JSON.stringify({
        success: true,
        offline: true,
        uploadId: uploadData.id,
        message: 'Audio saved offline. Will upload when connection is restored.'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
  } catch (error) {
    console.error('Service Worker: Failed to queue offline upload', error);
    
    return new Response(
      JSON.stringify({
        error: 'Failed to save audio offline',
        message: 'Please try again when online'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Online/offline event handlers
self.addEventListener('online', () => {
  console.log('Service Worker: Online event detected');
  isOnline = true;
  
  // Process queued uploads
  processOfflineUploads();
  
  notifyClients({
    type: 'ONLINE',
    message: 'Connection restored. Processing queued uploads...'
  });
});

self.addEventListener('offline', () => {
  console.log('Service Worker: Offline event detected');
  isOnline = false;
  
  notifyClients({
    type: 'OFFLINE',
    message: 'You\'re offline. Recordings will be saved locally.'
  });
});

// Background sync for queued uploads
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync event', event.tag);
  
  if (event.tag === 'audio-upload-sync') {
    event.waitUntil(processOfflineUploads());
  }
});

// Process queued offline uploads
async function processOfflineUploads() {
  console.log('Service Worker: Processing offline uploads', audioUploadQueue.length);
  
  if (!isOnline || audioUploadQueue.length === 0) {
    return;
  }
  
  const uploads = await getOfflineUploads();
  
  for (const upload of uploads) {
    try {
      console.log('Service Worker: Uploading queued audio', upload.id);
      
      // Reconstruct FormData
      const formData = new FormData();
      formData.append('file', upload.audioBlob);
      formData.append('session_id', upload.sessionId);
      
      // Make upload request
      const response = await fetch(upload.url, {
        method: upload.method,
        body: formData,
        headers: {
          'Authorization': upload.headers.authorization // Preserve auth header
        }
      });
      
      if (response.ok) {
        console.log('Service Worker: Upload successful', upload.id);
        
        // Remove from queue and storage
        await removeOfflineUpload(upload.id);
        audioUploadQueue = audioUploadQueue.filter(id => id !== upload.id);
        
        // Notify client
        notifyClients({
          type: 'UPLOAD_SUCCESS',
          uploadId: upload.id,
          message: 'Offline audio uploaded successfully'
        });
      } else {
        console.error('Service Worker: Upload failed', upload.id, response.status);
      }
      
    } catch (error) {
      console.error('Service Worker: Upload error', upload.id, error);
    }
  }
}

// IndexedDB helpers for offline storage
async function storeOfflineUpload(uploadData) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('DhruvAI-OfflineUploads', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['uploads'], 'readwrite');
      const store = transaction.objectStore('uploads');
      
      const addRequest = store.add(uploadData);
      addRequest.onsuccess = () => resolve(uploadData.id);
      addRequest.onerror = () => reject(addRequest.error);
    };
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      const store = db.createObjectStore('uploads', { keyPath: 'id' });
      store.createIndex('timestamp', 'timestamp');
    };
  });
}

async function getOfflineUploads() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('DhruvAI-OfflineUploads', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['uploads'], 'readonly');
      const store = transaction.objectStore('uploads');
      
      const getAllRequest = store.getAll();
      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
  });
}

async function removeOfflineUpload(uploadId) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('DhruvAI-OfflineUploads', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(['uploads'], 'readwrite');
      const store = transaction.objectStore('uploads');
      
      const deleteRequest = store.delete(uploadId);
      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
  });
}

// Utility functions
function generateUploadId() {
  return 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function notifyClients(message) {
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage(message);
    });
  });
}

// Handle messages from the main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'CACHE_AUDIO_CHUNK':
      // Cache audio chunks for better performance
      cacheAudioChunk(data.chunkData, data.sessionId);
      break;
      
    case 'CLEAR_AUDIO_CACHE':
      // Clear audio cache when storage is full
      clearAudioCache();
      break;
      
    case 'GET_CACHE_STATUS':
      // Return cache size information
      getCacheStatus().then((status) => {
        event.ports[0].postMessage(status);
      });
      break;
  }
});

// Cache audio chunks for live recording
async function cacheAudioChunk(chunkData, sessionId) {
  try {
    const cache = await caches.open(AUDIO_CACHE_NAME);
    const chunkKey = `/audio-chunks/${sessionId}/${Date.now()}`;
    
    const response = new Response(chunkData, {
      headers: { 'Content-Type': 'audio/webm' }
    });
    
    await cache.put(chunkKey, response);
    console.log('Service Worker: Audio chunk cached', chunkKey);
    
  } catch (error) {
    console.error('Service Worker: Failed to cache audio chunk', error);
  }
}

// Clear audio cache when storage is full
async function clearAudioCache() {
  try {
    const cache = await caches.open(AUDIO_CACHE_NAME);
    const keys = await cache.keys();
    
    // Keep only the 10 most recent audio files
    const sortedKeys = keys.sort((a, b) => {
      const timeA = new Date(a.url.split('/').pop()).getTime();
      const timeB = new Date(b.url.split('/').pop()).getTime();
      return timeB - timeA;
    });
    
    const keysToDelete = sortedKeys.slice(10);
    
    for (const key of keysToDelete) {
      await cache.delete(key);
    }
    
    console.log('Service Worker: Audio cache cleared', keysToDelete.length, 'items');
    
  } catch (error) {
    console.error('Service Worker: Failed to clear audio cache', error);
  }
}

// Get cache status information
async function getCacheStatus() {
  try {
    const [staticCache, audioCache, apiCache] = await Promise.all([
      caches.open(CACHE_NAME),
      caches.open(AUDIO_CACHE_NAME),
      caches.open(API_CACHE_NAME)
    ]);
    
    const [staticKeys, audioKeys, apiKeys] = await Promise.all([
      staticCache.keys(),
      audioCache.keys(),
      apiCache.keys()
    ]);
    
    return {
      static: staticKeys.length,
      audio: audioKeys.length,
      api: apiKeys.length,
      queuedUploads: audioUploadQueue.length,
      isOnline: isOnline
    };
    
  } catch (error) {
    console.error('Service Worker: Failed to get cache status', error);
    return { error: error.message };
  }
}

console.log('Service Worker: Auto-Note Mentor PWA Service Worker loaded');