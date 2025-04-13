// public/service-worker.js
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
  });
  
  self.addEventListener('activate', (event) => {
    console.log('Service Worker activated');
  });
  
  self.addEventListener('fetch', function(event) {
    event.respondWith(fetch(event.request));
  });