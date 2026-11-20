/* Neon Heat Arcade – gemeinsame Helfer: Hintergrund, Topbar, Sound, Cash-Bank, Overlay */
(() => {
  const PREFIX = 'neonheat_';
  const store = {
    get(k) { try { return localStorage.getItem(PREFIX + k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(PREFIX + k, v); } catch (e) {} },
  };

  let soundOn = store.get('sound') !== 'off';
  let ac;
  const ctx = () => (ac = ac || new (window.AudioContext || window.webkitAudioContext)());

  function beep(freq, dur = .08, type = 'square', vol = .05, slide = 0) {
    if (!soundOn) return;
    try {
      const a = ctx(), o = a.createOscillator(), g = a.createGain();
      o.type = type; o.frequency.setValueAtTime(freq, a.currentTime);
      if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(30, freq + slide), a.currentTime + dur);
      g.gain.setValueAtTime(vol, a.currentTime);
      g.gain.exponentialRampToValueAtTime(.0001, a.currentTime + dur);
      o.connect(g).connect(a.destination); o.start(); o.stop(a.currentTime + dur);
    } catch (e) {}
  }
  function noise(dur = .9, cutoff = 700, vol = .5) {
    if (!soundOn) return;
    try {
      const a = ctx(), len = a.sampleRate * dur, buf = a.createBuffer(1, len, a.sampleRate), d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.5);
      const s = a.createBufferSource(), f = a.createBiquadFilter(), g = a.createGain();
      f.type = 'lowpass'; f.frequency.value = cutoff; g.gain.value = vol;
      s.buffer = buf; s.connect(f).connect(g).connect(a.destination); s.start();
    } catch (e) {}
  }
  const jingle = () => [523, 659, 784, 1046, 784, 1046].forEach((f, i) => setTimeout(() => beep(f, .16, 'sawtooth', .05), i * 110));
  const sad = () => [392, 330, 262, 196].forEach((f, i) => setTimeout(() => beep(f, .22, 'sawtooth', .05), i * 160));

  const money = n => '$' + Math.round(n).toLocaleString('de-DE');

  const bank = {
    get() { return +(store.get('bank') || 0); },
    add(n) {
      const v = Math.max(0, bank.get() + Math.round(n));
      store.set('bank', v); renderBank(); return v;
    },
    set(v) { store.set('bank', Math.max(0, Math.round(v))); renderBank(); },
  };
  function renderBank() {
    const el = document.getElementById('nhBank');
    if (el) el.innerHTML = '<small>BANK</small>' + money(bank.get());
  }

  function best(key, value, lowerIsBetter = false) {
    const cur = store.get('best_' + key);
    if (value === undefined) return cur === null ? null : +cur;
    if (cur === null || (lowerIsBetter ? value < +cur : value > +cur)) { store.set('best_' + key, value); return true; }
    return false;
  }

  const SKYLINE = `<svg class="nh-skyline" viewBox="0 0 1200 300" preserveAspectRatio="none" aria-hidden="true">
  <g fill="#12052a"><rect x="0" y="180" width="70" height="120"/><rect x="60" y="130" width="50" height="170"/><rect x="120" y="160" width="80" height="140"/><rect x="210" y="90" width="45" height="210"/><rect x="260" y="150" width="70" height="150"/><rect x="340" y="110" width="60" height="190"/><rect x="760" y="120" width="55" height="180"/><rect x="820" y="160" width="80" height="140"/><rect x="905" y="70" width="50" height="230"/><rect x="960" y="140" width="70" height="160"/><rect x="1040" y="100" width="55" height="200"/><rect x="1100" y="170" width="100" height="130"/></g>
  <g fill="#0a0218"><path d="M470 300 C476 230 478 190 470 140 L476 140 C486 190 484 240 480 300Z"/><path d="M473 142 C440 120 410 125 390 140 C420 128 445 132 473 146Z M473 142 C500 112 535 112 560 128 C530 120 500 128 475 146Z M473 142 C455 105 430 95 405 98 C432 104 452 118 471 145Z M473 142 C492 100 520 88 545 92 C518 100 495 118 476 146Z"/><path d="M700 300 C704 250 708 215 718 175 L724 176 C716 215 712 255 710 300Z"/><path d="M720 178 C690 160 662 164 645 176 C672 166 696 170 720 182Z M720 178 C745 152 775 152 798 166 C770 160 745 166 722 182Z M720 178 C705 145 682 136 660 140 C684 145 702 158 718 181Z"/></g>
  <g fill="#ff2e93" opacity=".8"><rect x="218" y="100" width="6" height="6"/><rect x="350" y="125" width="6" height="6"/><rect x="915" y="85" width="6" height="6"/><rect x="1052" y="115" width="6" height="6"/></g>
  <g fill="#2ef2ff" opacity=".8"><rect x="75" y="150" width="6" height="6"/><rect x="835" y="180" width="6" height="6"/><rect x="1120" y="190" width="6" height="6"/></g></svg>`;

  function init({ hub = false } = {}) {
    const b = document.body;
    b.insertAdjacentHTML('afterbegin',
      `<div class="nh-sky"></div><div class="nh-sun"></div>${SKYLINE}<div class="nh-floor"></div>
       <div class="nh-top">
         ${hub ? '<span class="nh-top-l" style="font-family:Bungee;color:var(--pink);text-shadow:0 0 8px var(--pink)">NEON HEAT ARCADE</span>' : '<a href="index.html">◀ ARCADE</a>'}
         <span class="row" style="gap:6px"><span class="nh-bank" id="nhBank"></span><button class="nh-snd" id="nhSnd" title="Sound an/aus">${soundOn ? '🔊' : '🔇'}</button></span>
       </div>`);
    b.insertAdjacentHTML('beforeend',
      `<div class="nh-flash" id="nhFlash"></div>
       <div class="nh-overlay" id="nhOverlay"><div class="nh-banner"><h2 id="nhOvT"></h2><p id="nhOvP"></p><div class="row"><button class="btn hot big" id="nhOvB">Nochmal</button><a class="btn big" href="index.html" style="text-decoration:none">Arcade</a></div></div></div>`);
    document.getElementById('nhSnd').onclick = e => {
      soundOn = !soundOn; store.set('sound', soundOn ? 'on' : 'off');
      e.currentTarget.textContent = soundOn ? '🔊' : '🔇';
    };
    renderBank();
    window.addEventListener('storage', renderBank);
  }

  let ovCb = null;
  function overlay(kind, title, text, onAgain) {
    const o = document.getElementById('nhOverlay');
    document.getElementById('nhOvT').textContent = title;
    document.getElementById('nhOvP').textContent = text;
    o.className = 'nh-overlay show ' + kind;
    ovCb = onAgain;
    document.getElementById('nhOvB').onclick = () => { hideOverlay(); ovCb && ovCb(); };
  }
  const hideOverlay = () => { const o = document.getElementById('nhOverlay'); if (o) o.className = 'nh-overlay'; };

  function restartAnim(el, cls) { el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); }
  const flash = () => restartAnim(document.getElementById('nhFlash'), 'go');
  const shake = el => restartAnim(el, 'shake');
  const vibrate = p => { try { navigator.vibrate && navigator.vibrate(p); } catch (e) {} };

  window.NH = { init, beep, noise, jingle, sad, money, bank, best, store, overlay, hideOverlay, flash, shake, vibrate };
})();
