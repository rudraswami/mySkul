/**
 * teachingAnalytics
 * Lightweight client-side event buffer for taps, responses, and learning path steps.
 * Persist to localStorage and expose a flush() hook to send later when backend is ready.
 */
const KEY = 'teaching_events_v1';

function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; }
}
function save(events) {
  try { localStorage.setItem(KEY, JSON.stringify(events.slice(-300))); } catch {}
}

export const teachingAnalytics = {
  track(event) {
    const now = Date.now();
    const row = { ...event, ts: now };
    const events = load();
    events.push(row);
    save(events);
  },
  getAll() { return load(); },
  clear() { save([]); },
  // Placeholder for future server sync
  async flush(sendFn) {
    const events = load();
    if (!events.length) return { sent: 0 };
    if (typeof sendFn === 'function') {
      await sendFn(events);
    }
    save([]);
    return { sent: events.length };
  },
};

