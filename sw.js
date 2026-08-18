'use strict';
/* Financial Plan — the offline service worker.
   ==========================================================================
   This file is the most security-sensitive one in the repo, for two reasons
   that are easy to miss:

   1. THE PAGE'S CSP DOES NOT APPLY HERE. A worker takes its policy from the
      HTTP response headers of its own script, and GitHub Pages cannot set
      headers — so this code runs with NO Content-Security-Policy at all, and
      it runs resident, surviving reloads. That is why it is deliberately tiny,
      has no dynamic import, no eval, and never fetches anything cross-origin.
      Anything added here should be weighed as if it were running unsandboxed,
      because it is. Keep it short enough to read in one sitting.

   2. CACHE STORAGE IS ORIGIN-WIDE, NOT PER APP. Every app in the family shares
      eagleadams86.github.io, and `caches` is keyed by ORIGIN — so any page on
      that origin can read anything cached here, and a future Sprint Velocity
      or Flow Metrics worker could too. The answer is the rule below: only files
      that are ALREADY PUBLIC in this repo are ever cached. Nothing an attacker
      could read from the cache is anything they couldn't read from GitHub. The
      plan itself stays in localStorage, which every page on the origin could
      already reach — installing this changes that threat model not at all.
      The same cut goes the other way: any same-origin page can also WRITE
      into this cache, so an XSS hole in a sibling app could poison the
      offline shell, and the poison outlives the hole. No per-cache ACL
      exists; the defence is the origin policy itself — a CSP on every page
      and no third-party script anywhere.

   The scope is this file's own directory. Widening it past `/financial-plan/`
   would need a `Service-Worker-Allowed` header, which Pages cannot send, so
   this worker structurally cannot reach the sibling apps.

   STRATEGY: NETWORK-FIRST, ALWAYS — the cache is a fallback for a network that
   actually failed, never a first choice. That is the whole answer to the
   failure this repo can least afford: stale cached code reading a plan whose
   schema has since moved. You can only ever be served cached code if the
   network genuinely did not answer, so a schema change landing while you are
   online is impossible to miss. It costs the speed a cache-first worker would
   buy, which was never the point — offline was.

   The belt to this braces is in index.html: if a plan turns out to have been
   written by a NEWER schema than the running code knows, the app refuses to
   open it rather than guessing. See `haltForNewerData`.

   If this worker ever misbehaves, it is sticky in a way a broken page is not —
   it can keep serving itself. `sw-kill.js` is the escape hatch: copy it over
   this file, push, and every installed copy uninstalls itself on next load. */

/* Bump when the shell list changes, so old caches are purged on activate. It is
   NOT load-bearing for freshness — network-first means a forgotten bump cannot
   serve you stale code — it only stops dead entries accumulating. */
const CACHE = 'fin-shell-v1';
const PREFIX = 'fin-shell-';

/* THE ALLOWLIST, and the security boundary of this file. Every entry is a file
   that is already public in the GitHub repo. Nothing else is EVER cached — not
   the plan, not a Firestore reply, not a Twelve Data quote, not the gitignored
   real-data JSONs, not tests.html. A request that is not on this list is not
   intercepted at all: it goes to the network as if this worker did not exist.
   Adding a line here is a security decision, so justify it in the commit. */
const SHELL = [
  './',
  'chart.min.js',
  'theme.css',
  'manifest.webmanifest',
  'privacy.html',
  'favicon.ico',
  'apple-touch-icon.png',
  'icon-192.png',
  'icon-512.png',
  'icon-512-maskable.png'
];

/* Resolved against this file's own URL, so the same list works unchanged on
   localhost (where the app is at the root) and on Pages (where it is under
   /financial-plan/). The absolute-vs-relative trap that bites `scope` in the
   manifest bites here too — don't hard-code the directory. */
const ROOT = new URL('./', self.location).pathname;
const SHELL_PATHS = new Set(SHELL.map((p) => new URL(p, self.location).pathname));

/* The cache key for a request, or null if it isn't ours to touch. Returning a
   PATH rather than the request strips query strings: `favicon.ico?v=2` and the
   precached `favicon.ico` have to be one entry, or the fallback misses the
   moment the markup adds a cache-buster. `index.html` is folded onto './' for
   the same reason — both are the app, and a share link arriving at either one
   should work offline. */
function shellKey(url) {
  let p = url.pathname;
  if (p === ROOT + 'index.html') p = ROOT;
  return SHELL_PATHS.has(p) ? p : null;
}

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

/* Fill in whatever the cache is missing, and nothing it already has.
   Two bugs live here, both of which cost offline entirely and neither of which
   announces itself:

   • `cache.addAll` is ALL-OR-NOTHING. One 404 in the list — a file renamed, an
     icon not yet committed — rejects the whole call, install fails, and the app
     has no offline at all while looking perfectly healthy online. Fetching each
     entry on its own degrades instead: a missing icon costs that icon.

   • INSTALL FIRES ONCE PER SCRIPT VERSION. If the cache is later evicted (a
     browser reclaiming storage, or the user clearing part of their site data)
     the registration survives, no new install event ever runs, and the shell is
     never rebuilt — so offline quietly covers only whatever the last online
     visit happened to request. That is why the page pings this on every load
     (see the `message` handler): the repair has to be able to run without a new
     worker version to hang it on. */
async function topUp() {
  const cache = await caches.open(CACHE);
  await Promise.all(SHELL.map(async (p) => {
    const url = new URL(p, self.location);
    const key = self.location.origin + url.pathname;
    if (await cache.match(key)) return;
    try {
      /* `reload` so a top-up can't re-seed the cache from the HTTP cache's own
         stale copy — the one thing worse than an empty entry is a stale one. */
      const res = await fetch(url, { cache: 'reload' });
      if (res && res.ok && res.type === 'basic') await cache.put(key, res);
    } catch (_) { /* offline: nothing to top up with, try again next load */ }
  }));
}

self.addEventListener('install', (e) => {
  /* Precache up front so the FIRST offline open works, including for files this
     visit never happened to request. skipWaiting is safe here in a way it isn't
     under cache-first: the page already has its code, and all a new worker
     changes is where later fetches are answered from. */
  e.waitUntil(topUp().then(() => self.skipWaiting()));
});

/* The page asks for a shell check on every load, which is when it is most
   likely to be online and cheapest to repair. Nothing else is accepted, and
   nothing is read out of the message — the only thing a sender can do here is
   ask for files that are already public to be re-fetched. */
self.addEventListener('message', (e) => {
  if (!e.data || e.data.type !== 'shell-check') return;
  e.waitUntil(topUp());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    /* ONLY this app's caches. `caches.keys()` is origin-wide, so an unguarded
       "delete everything that isn't mine" here would wipe a future Sprint
       Velocity or Flow Metrics cache — the shared origin cutting the other way.
       The prefix check is what keeps this worker inside its own app. */
    for (const k of await caches.keys()) {
      if (k !== CACHE && k.startsWith(PREFIX)) await caches.delete(k);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  /* Cross-origin is never touched: Firestore, Google sign-in, Twelve Data and
     the GitHub changelog all go straight past. Sync is an online-only feature
     by definition and gets no help — and no interference — from here. */
  if (url.origin !== self.location.origin) return;
  const key = shellKey(url);
  if (!key) return;
  e.respondWith(networkFirst(req, key));
});

async function networkFirst(req, key) {
  const cache = await caches.open(CACHE);
  const cacheKey = self.location.origin + key;
  /* Read the cache BEFORE starting the fetch, so the handler below can consult
     it: a same-origin error page — a transient 404/500 from Pages mid-deploy —
     is a network that answered and still failed, and with a good copy in hand
     the shell should win. Only allowlisted shell files ever reach here, so no
     real missing page is being papered over. */
  const cached = await cache.match(cacheKey);
  const fresh = fetch(req).then((res) => {
    /* Only a real, same-origin 200 is worth keeping. `basic` excludes opaque
       cross-origin replies, which we should never see here anyway. */
    if (res && res.ok && res.type === 'basic') cache.put(cacheKey, res.clone());
    if (res && !res.ok && cached) return cached;
    return res;
  });
  /* Nothing to fall back to: let the network answer, or fail honestly. */
  if (!cached) return fresh;
  /* Offline rejects fast, but the case that actually matters is the slow, alive
     connection — hotel wifi — where a plain network-first would hang for a
     minute with a perfectly good copy sitting in the cache. Five seconds, then
     serve what we have; the in-flight fetch still refreshes the cache behind it
     (race() has already attached handlers, so a later rejection is not
     unhandled). */
  return Promise.race([fresh, wait(5000).then(() => cached)]).catch(() => cached);
}
