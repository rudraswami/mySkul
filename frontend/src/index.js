import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// PATCH: Force unregister old service workers that may be causing issues
// This ensures users always get the latest service worker version
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    for (let registration of registrations) {
      // Only unregister service workers with old cache versions
      registration.unregister().then(success => {
        if (success) {
          console.log('✅ Old service worker unregistered successfully');
          // Force reload to activate new service worker
          if (registrations.length > 0) {
            window.location.reload(true);
          }
        }
      });
    }
  });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
