// Tests the shared ad layer web/ads.js against a mock SDK for each portal: node tools/test_ads.js
// Per portal: load ads.js as the game does, mock the SDK, then check showAd calls done(ok) at the right time with the right value. Prints 1 line; exits 1 on failure.
const fs = require('fs');
const path = require('path');
const SRC = fs.readFileSync(path.join(__dirname, '..', 'web', 'ads.js'), 'utf8');
const bad = [];
const check = (name, got, want) => { if (got !== want) bad.push(`${name}: ra ${got}, can ${want}`); };

// -> { api: ads.js functions, window, scripts: injected script tags, tick(ms): advances the fake clock }
function load(portal, id, host) {
  let now = 1e6;
  const timers = [], scripts = [];
  const window = {};
  const env = {
    window, location: { hostname: host || 'games.example' },
    document: { createElement: () => ({}), head: { appendChild: s => scripts.push(s) } },
    setTimeout: (f, ms) => { timers.push({ f, at: now + ms }); return timers.length; },
    clearTimeout: i => { if (timers[i - 1]) timers[i - 1].f = null; },
    Date: { now: () => now }
  };
  const code = SRC.replace('/*PORTAL*/', portal).replace('/*GAME_ID*/', id) +
    '\nreturn { showAd, gameplay, happy, playing: () => adPlaying, ready: f => { onPortalReady = f; } };';
  env.Storage = function () {}; env.Storage.prototype.setItem = function () {};   // fake storage: ads.js wraps setItem to mirror saves to the portal
  const store = new env.Storage(); store.getItem = () => null;
  env.localStorage = store; env.sessionStorage = { getItem: () => null, setItem() {} };
  const api = new Function(...Object.keys(env), 'let onPortalReady; const SAVE_KEY = "t.save";' + code)(...Object.values(env));
  const tick = ms => { now += ms; timers.forEach(t => { if (t.f && t.at <= now) { const f = t.f; t.f = null; f(); } }); };
  return { api, window, scripts, tick, store };
}
const result = (api, type) => { const r = { v: 'chua goi' }; api.showAd(type, ok => { r.v = ok; }); return r; };

(async () => {
  // no SDK: local machine, portal 'none', or missing game id
  for (const [portal, id, host] of [['none', '', ''], ['gamemonetize', 'abc', 'localhost'], ['gamemonetize', '', ''], ['gamedistribution', '', '']]) {
    const t = load(portal, id, host);
    check(`${portal}/${host || 'web'} khong nap SDK`, t.scripts.length, 0);
    check(`${portal}/${host || 'web'} rewarded`, result(t.api, 'rewarded').v, true);
    check(`${portal}/${host || 'web'} midgame`, result(t.api, 'midgame').v, true);
  }

  // GameMonetize: a single ad type; the SDK signals PAUSE then START
  let t = load('gamemonetize', 'abc');
  check('gm nap SDK', t.scripts[0] && t.scripts[0].src, 'https://api.gamemonetize.com/sdk.js');
  check('gm ma game', t.window.SDK_OPTIONS.gameId, 'abc');
  let shown = 0;
  t.window.sdk = { showBanner: () => { shown++; } };
  let r = result(t.api, 'midgame');
  t.window.SDK_OPTIONS.onEvent({ name: 'SDK_GAME_PAUSE' });
  check('gm dang chieu', t.api.playing(), true);
  t.tick(30000);
  check('gm chua xong thi chua goi', r.v, 'chua goi');
  t.window.SDK_OPTIONS.onEvent({ name: 'SDK_GAME_START' });
  check('gm xong', r.v, true);
  check('gm het chieu', t.api.playing(), false);
  r = result(t.api, 'midgame');
  check('gm midgame sat nhau bi bo qua', shown + ':' + r.v, '1:true');
  r = result(t.api, 'rewarded');
  check('gm rewarded khong bi giu lai', shown, 2);
  t.tick(4000);
  check('gm khong co quang cao thi choi tiep sau 4 giay', r.v, true);
  t.tick(60000);
  result(t.api, 'midgame');
  check('gm midgame sau 60 giay', shown, 3);

  // GameDistribution: reward only on SDK_REWARDED_WATCH_COMPLETE
  t = load('gamedistribution', 'gd1');
  check('gd nap SDK', t.scripts[0] && t.scripts[0].src, 'https://html5.api.gamedistribution.com/main.min.js');
  const asked = [];
  let fail = null;
  t.window.gdsdk = { showAd: type => { asked.push(type); return new Promise((ok, no) => { fail = no; }); } };
  const ev = name => t.window.GD_OPTIONS.onEvent({ name });
  r = result(t.api, 'rewarded');
  ev('SDK_GAME_PAUSE'); ev('SDK_REWARDED_WATCH_COMPLETE'); ev('SDK_GAME_START');
  check('gd xem het thi thuong', asked[0] + ':' + r.v, 'rewarded:true');
  r = result(t.api, 'rewarded');
  ev('SDK_GAME_PAUSE'); ev('SDK_GAME_START');
  check('gd bo ngang thi khong thuong', r.v, false);
  r = result(t.api, 'rewarded');
  fail(new Error('no fill'));
  await new Promise(f => setImmediate(f));
  check('gd khong co quang cao thi khong thuong', r.v, false);
  r = result(t.api, 'rewarded');
  t.tick(4000);
  check('gd SDK im lang thi khong thuong sau 4 giay', r.v, false);
  t.tick(60000);
  r = result(t.api, 'midgame');
  ev('SDK_GAME_PAUSE'); ev('SDK_GAME_START');
  check('gd midgame', asked[asked.length - 1] + ':' + r.v, 'undefined:true');

  // CrazyGames: SDK v3; only an ad blocker withholds the reward
  t = load('crazygames', '');
  check('cg nap SDK', t.scripts[0] && t.scripts[0].src, 'https://sdk.crazygames.com/crazygames-sdk-v3.js');
  const calls = [];
  let cb = null, ready = 0;
  t.window.CrazyGames = { SDK: {
    init: () => Promise.resolve(),
    ad: { requestAd: (type, c) => { calls.push(type); cb = c; } },
    game: { gameplayStart: () => calls.push('start'), gameplayStop: () => calls.push('stop'), happytime: () => calls.push('happy') }
  } };
  t.api.ready(() => { ready++; });
  t.scripts[0].onload();
  await new Promise(f => setImmediate(f));
  check('cg goi onPortalReady', ready, 1);
  t.api.gameplay(true); t.api.gameplay(false); t.api.happy();
  check('cg bao luc choi', calls.join(','), 'start,stop,happy');
  r = result(t.api, 'rewarded');
  cb.adStarted();
  check('cg dang chieu', t.api.playing(), true);
  cb.adFinished();
  check('cg xem xong thi thuong', r.v, true);
  r = result(t.api, 'rewarded');
  cb.adError({ code: 'adblock' });
  check('cg chan quang cao thi khong thuong', r.v, false);
  r = result(t.api, 'rewarded');
  cb.adError({ code: 'adsDisabledBasicLaunch' });
  check('cg Basic Launch (chua co quang cao) van cho goi y', r.v, true);

  // Playgama Bridge: reward only on state 'rewarded'; pause follows PAUSE_STATE_CHANGED; reports game_ready; saves progress through the bridge
  t = load('playgama', '');
  check('pg nap SDK', t.scripts[0] && t.scripts[0].src, 'https://bridge.playgama.com/v2/stable/playgama-bridge.js');
  const on = {}, sent = [], shownPg = [], saved = [];
  t.window.bridge = {
    EVENT_NAME: { INTERSTITIAL_STATE_CHANGED: 'i', REWARDED_STATE_CHANGED: 'r', PAUSE_STATE_CHANGED: 'p' },
    initialize: () => Promise.resolve(),
    advertisement: { on: (e, f) => { on[e] = f; }, isInterstitialSupported: true, isRewardedSupported: true,
      showInterstitial: id => shownPg.push('i:' + id), showRewarded: id => shownPg.push('r:' + id) },
    platform: { on: (e, f) => { on[e] = f; }, sendMessage: m => sent.push(m) },
    storage: { get: () => Promise.resolve([null]), set: (k, v) => { saved.push(k[0] + '=' + v[0]); return Promise.resolve(); } }
  };
  ready = 0; t.api.ready(() => { ready++; });
  t.scripts[0].onload();
  await new Promise(f => setImmediate(f)); await new Promise(f => setImmediate(f));
  check('pg bao game_ready', sent.join(','), 'game_ready');
  check('pg goi onPortalReady', ready, 1);
  r = result(t.api, 'rewarded');
  on.r('loading'); on.r('opened');
  check('pg dang chieu', t.api.playing(), true);
  on.r('rewarded'); on.r('closed');
  check('pg xem het thi thuong', shownPg[0] + ':' + r.v, 'r:reward:true');
  check('pg het chieu', t.api.playing(), false);
  r = result(t.api, 'rewarded');
  on.r('opened'); on.r('closed');
  check('pg bo ngang thi khong thuong', r.v, false);
  r = result(t.api, 'rewarded');
  t.tick(4000);
  check('pg SDK im lang thi khong thuong sau 4 giay', r.v, false);
  t.tick(60000);
  r = result(t.api, 'midgame');
  on.i('opened'); on.i('closed');
  check('pg midgame', shownPg[shownPg.length - 1] + ':' + r.v, 'i:level_completed:true');
  on.p(true);
  check('pg tam dung khi cong bao', t.api.playing(), true);
  on.p(false);
  check('pg choi tiep', t.api.playing(), false);
  t.store.setItem('t.save', '{"a":1}'); t.store.setItem('khac', 'x');
  check('pg luu tien trinh qua bridge', saved.join(','), 't.save={"a":1}');
  t.window.bridge.advertisement.isRewardedSupported = false;
  check('pg cong khong co quang cao thuong thi khong thuong', result(t.api, 'rewarded').v, false);

  console.log(bad.length ? 'LOI ' + bad.join(' | ') : 'ads.js: dat (gamemonetize, gamedistribution, crazygames, playgama, none)');
  process.exit(bad.length ? 1 : 0);
})();
