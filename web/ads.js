// ============================================================================
// Ads: one source for every game (web/ads.js). tools/build.py pastes this file into each game
// in place of its ADS marker and fills in PORTAL and GAME_ID for the portal being packaged:
//   'gamemonetize'      GameMonetize HTML5 SDK (GAME_ID = game hash from their dashboard)
//   'gamedistribution'  GameDistribution HTML5 SDK (GAME_ID from their dashboard)
//   'crazygames'        CrazyGames SDK v3 (no id; only works on their domain)
//   'playgama'          Playgama Bridge v2 (no id; needs playgama-bridge-config.json next to index.html)
//   'none'              no SDK, no ads (itch.io, self-hosting, local testing)
// A game calls showAd(type, done), gameplay(on) and happy(), reads adPlaying to freeze and mute
// while an ad is on screen, and may define onPortalReady() to run once the SDK is up.
// SDK calls follow the pages listed in NGHIEN-CUU.md (checked 2026-10-12) and, for Playgama, CONG.md (checked 2026-10-13).
// ============================================================================
const PORTAL = '/*PORTAL*/';
const GAME_ID = '/*GAME_ID*/';
// No SDK and no ads when opened from disk or a local test server.
const LOCAL = /^(localhost|127\.0\.0\.1|)$/.test(location.hostname);
// Rewarded ads come first: the player asked for them, so they are never held back. Midgame ads
// are skipped when any ad ended less than this many ms ago.
const MIDGAME_GAP = 60000;

let adPlaying = false, adDone = null, adType = '', adTimer = 0, adEnd = 0, rewardSeen = false, cg = null, pg = null, pgPaused = false, pgAd = false;
function finishAd(ok) {
  clearTimeout(adTimer); adPlaying = false; adEnd = Date.now();
  const f = adDone; adDone = null;
  if (f) f(ok !== false);
}
function loadScript(src, id, onload) {
  const s = document.createElement('script');
  s.id = id; s.src = src; s.onload = onload || null;
  document.head.appendChild(s);
}
// GameMonetize and GameDistribution report ads through the same event names.
function portalEvent(e) {
  if (e.name === 'SDK_GAME_PAUSE') { clearTimeout(adTimer); adPlaying = true; }            // ad on screen: freeze + mute
  else if (e.name === 'SDK_REWARDED_WATCH_COMPLETE') rewardSeen = true;
  else if (e.name === 'SDK_GAME_START') finishAd(PORTAL !== 'gamedistribution' || adType !== 'rewarded' || rewardSeen);
  else if (e.name === 'SDK_READY' && typeof onPortalReady === 'function') onPortalReady();
}
if (!LOCAL && PORTAL === 'gamemonetize' && GAME_ID) {
  window.SDK_OPTIONS = { gameId: GAME_ID, onEvent: portalEvent };
  loadScript('https://api.gamemonetize.com/sdk.js', 'gamemonetize-sdk');
}
if (!LOCAL && PORTAL === 'gamedistribution' && GAME_ID) {
  window.GD_OPTIONS = { gameId: GAME_ID, onEvent: portalEvent };
  loadScript('https://html5.api.gamedistribution.com/main.min.js', 'gamedistribution-jssdk');
}
// Cloud saves (CrazyGames Data module, Playgama Bridge storage): every write to localStorage under the game's
// key also goes to the portal; on a fresh device the portal copy is restored once and the page reloads so the
// game starts from it. get(key) resolves to the portal's copy, put(key, value) stores one.
function mirrorSave(get, put, ready) {
  const key = typeof SAVE_KEY === 'string' ? SAVE_KEY : '';
  if (!key) return ready();
  try {
    const set = Storage.prototype.setItem;
    Storage.prototype.setItem = function (k, v) { set.call(this, k, v); if (k === key) { try { put(k, v); } catch (e) {} } };
  } catch (e) {}
  Promise.resolve().then(() => get(key)).then(data => {
    const cloud = data ? (typeof data === 'string' ? data : JSON.stringify(data)) : '';
    let local = '', again = '';
    try { local = localStorage.getItem(key) || ''; again = sessionStorage.getItem(key + '.restored') || ''; } catch (e) {}
    if (cloud && !local && !again) {
      try { sessionStorage.setItem(key + '.restored', '1'); localStorage.setItem(key, cloud); location.reload(); return; } catch (e) {}
    }
    if (local && !cloud) { try { put(key, local); } catch (e) {} }
    ready();
  }).catch(ready);
}
if (!LOCAL && PORTAL === 'crazygames') {
  loadScript('https://sdk.crazygames.com/crazygames-sdk-v3.js', 'crazygames-sdk', () => {
    window.CrazyGames.SDK.init().then(() => {
      cg = window.CrazyGames.SDK;
      mirrorSave(k => cg.data.getItem(k), (k, v) => cg.data.setItem(k, v), () => { if (typeof onPortalReady === 'function') onPortalReady(); });
    }).catch(() => {});
  });
}
// Playgama Bridge: one SDK for Playgama and its partner portals. The bridge tells us when to pause and mute
// (an ad is open, the tab is hidden); progress is mirrored to the bridge storage (mirrorSave) because some of
// its portals wipe localStorage; 'game_ready' hides the portal's loading screen.
function pgState(state) {
  if (state === 'opened') { clearTimeout(adTimer); pgAd = true; adPlaying = true; }
  else if (state === 'rewarded') rewardSeen = true;
  else if (state === 'closed' || state === 'failed') { pgAd = false; adPlaying = pgPaused; finishAd(adType !== 'rewarded' || rewardSeen); }
}
function pgSave(key, value) { if (pg) { try { pg.storage.set([key], [value]).catch(() => {}); } catch (e) {} } }
if (!LOCAL && PORTAL === 'playgama') {
  loadScript('https://bridge.playgama.com/v2/stable/playgama-bridge.js', 'playgama-bridge', () => {
    const b = window.bridge;
    b.initialize().then(() => {
      pg = b;
      b.advertisement.on(b.EVENT_NAME.INTERSTITIAL_STATE_CHANGED, pgState);
      b.advertisement.on(b.EVENT_NAME.REWARDED_STATE_CHANGED, pgState);
      b.platform.on(b.EVENT_NAME.PAUSE_STATE_CHANGED, paused => { pgPaused = !!paused; adPlaying = pgPaused || pgAd; });
      mirrorSave(k => b.storage.get([k]).then(d => d && d[0]), pgSave,
        () => { b.platform.sendMessage('game_ready'); if (typeof onPortalReady === 'function') onPortalReady(); });
    }).catch(() => {});
  });
}
// type: 'midgame' | 'rewarded'. Calls done(ok) afterwards. ok is false only for a rewarded ad
// whose reward must not be given: blocked by an adblocker (CrazyGames) or not watched to the
// end (GameDistribution). With no SDK, or no ad to show, the game simply carries on.
function showAd(type, done) {
  if (adDone) return;
  if (type !== 'rewarded' && Date.now() - adEnd < MIDGAME_GAP) return done(true);
  adType = type; rewardSeen = false;
  if (pg) {
    // Carry on after 4s if no ad opens (unsupported, cooldown, no fill); a rewarded ad that never ran pays nothing.
    const ok = type === 'rewarded' ? pg.advertisement.isRewardedSupported : pg.advertisement.isInterstitialSupported;
    if (!ok) return done(type !== 'rewarded');
    adDone = done; adTimer = setTimeout(() => finishAd(type !== 'rewarded'), 4000);
    try { if (type === 'rewarded') pg.advertisement.showRewarded('reward'); else pg.advertisement.showInterstitial('level_completed'); } catch (e) { finishAd(type !== 'rewarded'); }
  } else if (cg) {
    adDone = done;
    cg.ad.requestAd(type, {
      adStarted: () => { adPlaying = true; },
      adFinished: () => finishAd(true),
      adError: e => finishAd(!(type === 'rewarded' && e && e.code === 'adblock'))
    });
  } else if (window.gdsdk && window.gdsdk.showAd) {
    // Carry on after 4s if no ad starts (no fill / blocked); a rewarded ad that never ran pays nothing.
    adDone = done; adTimer = setTimeout(() => finishAd(type !== 'rewarded'), 4000);
    const p = type === 'rewarded' ? window.gdsdk.showAd('rewarded') : window.gdsdk.showAd();
    if (p && p.catch) p.catch(() => { if (!adPlaying) finishAd(type !== 'rewarded'); });
  } else if (window.sdk && window.sdk.showBanner) {
    // GameMonetize has one ad format; carry on after 4s if no ad starts.
    adDone = done; adTimer = setTimeout(finishAd, 4000);
    window.sdk.showBanner();
  } else done(true);
}
// Tells the portal when real gameplay starts and stops (CrazyGames requirement).
function gameplay(on) {
  if (!cg) return;
  try { if (on) cg.game.gameplayStart(); else cg.game.gameplayStop(); } catch (e) {}
}
// A big moment (three stars, a new best): CrazyGames may celebrate it.
function happy() {
  if (cg) { try { cg.game.happytime(); } catch (e) {} }
}
