'use strict';
/* THE ESCAPE HATCH — not registered by anything, and deliberately so.
   ==========================================================================
   A broken page is fixed by pushing a new one. A broken SERVICE WORKER is not:
   it is resident, it survives reloads, and if it is serving bad code from its
   own cache it can keep doing so. This file is the way out.

   TO USE IT:
     cp sw-kill.js sw.js && git commit -am "Kill the service worker" && git push

   Browsers re-fetch sw.js on navigation (bypassing the HTTP cache for it, and
   at most 24h stale), so within a reload or two every installed copy runs this
   instead: it deletes this app's caches, uninstalls itself, and force-reloads
   any open window so nobody is left sitting on the dead worker. The app goes
   back to being an ordinary online-only page — which is exactly what it was
   before offline was added, so the fallback is a known-good state.

   Keep it in the repo even while it is unused. The moment it is needed is the
   moment you do not want to be writing it from memory. It is also tested:
   tests.html asserts it stays a pure uninstaller and never grows a cache. */

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    /* Same origin-wide caution as the real worker: delete only this app's
       caches, never a sibling's. */
    for (const k of await caches.keys()) {
      if (k.startsWith('fin-shell-')) await caches.delete(k);
    }
    await self.registration.unregister();
    for (const c of await self.clients.matchAll({ type: 'window' })) c.navigate(c.url);
  })());
});

/* No fetch handler. Every request goes to the network untouched, which is the
   whole point — from the moment this installs, the worker is inert. */
