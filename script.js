// ---------- Loader (index page only) ----------
// The coin is a still PNG; on top of it a small WebGL pass sets it alight:
// liquid-metal fire catches at the tail, climbs up behind the body and is
// drawn up into the flame-shaped inflections above the wings, passing behind
// the raised relief and lettering. The bird's head turns gently.
const LOADER_MS = 4600;
let stopCoinFire = null;

window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if(!loader) return;
  stopCoinFire = startCoinFire(loader.querySelector('.loader-coin-fire'));
  setTimeout(() => {
    loader.classList.add('hide');
    setTimeout(() => { if(stopCoinFire) stopCoinFire(); }, 1000);
  }, LOADER_MS);
});

function startCoinFire(canvas){
  if(!canvas) return null;
  // with reduced motion, draw a single finished frame instead of animating
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gl = canvas.getContext('webgl', { premultipliedAlpha:true, alpha:true, antialias:false });
  if(!gl) return null;

  const vs = 'attribute vec2 p; varying vec2 uv; void main(){ uv = p * vec2(0.5, -0.5) + 0.5; gl_Position = vec4(p, 0.0, 1.0); }';
  const fs = `
    precision mediump float;
    varying vec2 uv;
    uniform sampler2D coin;    // the finished medal
    uniform sampler2D flames;  // r: where fire may burn, g: raised relief it passes behind, b: head weight
    uniform float t;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float noise(vec2 p){
      vec2 i = floor(p), f = fract(p);
      vec2 u = f * f * (3.0 - 2.0 * f);
      return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
                 mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
    }
    float fbm(vec2 p){ return 0.65 * noise(p) + 0.35 * noise(p * 2.07 + 5.3); }
    // liquid-metal flame: a slowly warping field whose ridges are drawn upward
    float flame(vec2 p){
      vec2 w = vec2(fbm(p * vec2(3.0, 2.0) + vec2(0.0, t * 0.5)),
                    fbm(p * vec2(3.0, 2.0) + vec2(4.7, t * 0.5 + 2.3)));
      vec2 q = vec2(p.x * 12.0 + (w.x - 0.5) * 3.2, p.y * 3.6 + t * 0.95 + (w.y - 0.5) * 1.4);
      float r = 1.0 - abs(fbm(q) * 2.0 - 1.0);
      return smoothstep(0.35, 1.0, r);
    }
    void main(){
      vec3 m = texture2D(flames, uv).rgb;
      vec2 st = uv;
      // the head turns gently about the middle of the neck
      if(m.b > 0.001){
        vec2 piv = vec2(0.5207, 0.2563);
        // ...and towards the end bows a little further down
        float dip = smoothstep(2.6, 3.9, t);
        float a = ((0.014 * sin(t * 0.9) + 0.005 * sin(t * 1.9 + 1.0)) * (1.0 - 0.5 * dip) - 0.035 * dip) * m.b;
        vec2 d = uv - piv;
        st = piv + vec2(d.x * cos(a) - d.y * sin(a), d.x * sin(a) + d.y * cos(a));
        st.y -= 0.004 * dip * m.b;
      }
      vec4 c = texture2D(coin, st);
      if(m.r > 0.001){
        // ignition: the fire catches at the bottom and climbs with a ragged,
        // flickering edge, then keeps being drawn up through the wings
        float yb = 1.0 - uv.y;
        float rag = (noise(vec2(uv.x * 9.0, t * 1.6)) - 0.5) * 0.14;
        float front = t * 0.42 + 0.02;
        float lit = 1.0 - smoothstep(front - 0.12, front + 0.02, yb + rag);
        // quieter and more transparent low down, fuller towards the wings
        float low = mix(0.28, 1.0, smoothstep(0.12, 0.55, yb));
        float k = m.r * lit * (1.0 - m.g) * low;
        if(k > 0.001){
          float e = 0.003;
          float h = flame(uv);
          float hx = flame(uv + vec2(e, 0.0)), hy = flame(uv + vec2(0.0, e));
          float s = 0.011 * k;
          vec3 n = normalize(vec3(-(hx - h) / e * s, -(hy - h) / e * s, 1.0));
          vec3 L = normalize(vec3(-0.5, -0.62, 0.6));
          vec3 H = normalize(L + vec3(0.0, 0.0, 1.0));
          float diff = dot(n, L) - L.z;
          float spec = max(pow(max(dot(n, H), 0.0), 32.0) - pow(H.z, 32.0), 0.0);
          // a soft bright seam where the fire is catching
          float seam = exp(-pow((yb + rag - front) / 0.035, 2.0)) * m.r * (1.0 - m.g) * low * step(front, 1.15);
          c.rgb *= 1.0 + diff * 1.0 + h * k * 0.12 + seam * 0.25;
          c.rgb += (c.rgb * 0.6 + 0.2) * spec * 1.4;
        }
      }
      gl_FragColor = vec4(c.rgb * c.a, c.a);
    }`;

  function shader(type, src){
    const sh = gl.createShader(type); gl.shaderSource(sh, src); gl.compileShader(sh);
    return gl.getShaderParameter(sh, gl.COMPILE_STATUS) ? sh : null;
  }
  const v = shader(gl.VERTEX_SHADER, vs), f = shader(gl.FRAGMENT_SHADER, fs);
  if(!v || !f) return null;
  const prog = gl.createProgram();
  gl.attachShader(prog, v); gl.attachShader(prog, f); gl.linkProgram(prog);
  if(!gl.getProgramParameter(prog, gl.LINK_STATUS)) return null;
  gl.useProgram(prog);

  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  function texture(unit, name, src){
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => { try {
        gl.activeTexture(gl.TEXTURE0 + unit);
        gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.uniform1i(gl.getUniformLocation(prog, name), unit);
        resolve();
      } catch(e){ reject(e); } };
      img.onerror = reject;
      img.src = src;
    });
  }

  const tLoc = gl.getUniformLocation(prog, 't');
  let raf = 0, running = true;
  const t0 = performance.now();
  function frame(now){
    if(!running) return;
    const size = Math.round(canvas.clientWidth * Math.min(window.devicePixelRatio || 1, 2));
    if(canvas.width !== size){ canvas.width = canvas.height = size; gl.viewport(0, 0, size, size); }
    gl.uniform1f(tLoc, still ? 6.0 : (now - t0) / 1000);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if(!still) raf = requestAnimationFrame(frame);
  }
  Promise.all([texture(0, 'coin', 'images/yvis-hausen-coin.webp'),
               texture(1, 'flames', 'images/coin-flames.png')])
    .then(() => { if(running) raf = requestAnimationFrame(frame); })
    .catch(() => {});
  return () => { running = false; cancelAnimationFrame(raf); };
}

// ---------- i18n ----------
const SUBTITLES = {
  en: ["International Creative House","Global Meta Acquisition","Private Art Office","Global Ideation Firm","Artist Agency","Brand Governance"],
  fr: ["Maison Créative Internationale","Acquisition Meta Mondiale","Bureau d'Art Privé","Cabinet d'Idéation Global","Agence d'Artistes","Gouvernance de Marque"],
  it: ["Casa Creativa Internazionale","Acquisizione Meta Globale","Ufficio d'Arte Privato","Studio di Ideazione Globale","Agenzia di Artisti","Governance del Brand"]
};

// Page text is translated by i18n.js; the header subtitle cycles here.
const LANG = () => (window.YHi18n ? YHi18n.lang : 'en');
let phraseIndex = 0;
if(window.YHi18n) YHi18n.on(lang => {
  const el = document.getElementById('subtitle');
  if(el){ phraseIndex = 0; el.textContent = SUBTITLES[lang][0]; }
});

// ---------- Cycling subtitle ----------
const subtitleEl = document.getElementById('subtitle');
if(subtitleEl){
  subtitleEl.textContent = SUBTITLES[LANG()][0];
  setInterval(() => {
    subtitleEl.classList.add('swipe');
    setTimeout(() => {
      const arr = SUBTITLES[LANG()];
      phraseIndex = (phraseIndex + 1) % arr.length;
      subtitleEl.textContent = arr[phraseIndex];
      subtitleEl.classList.remove('swipe');
    }, 700);
  }, 3400);
}

// ---------- Private-code gate (filing cabinet and the Engine) ----------
// No codes live in this file. Each private page is published encrypted
// (see access.js and tools/build.py); a code is right only if it unlocks
// the page. Codes of this length submit as soon as they are typed;
// longer codes submit with Enter.
const CODE_LENGTH = 4;

let pendingFolder = null;   // folder key, or a gate { key, href }
const codeModal = document.getElementById('codeModal');
const codeInput = document.getElementById('codeInput');
const codeError = document.getElementById('codeError');
const codeCancel = document.getElementById('codeCancel');
const codeRestricted = document.getElementById('codeRestricted');
let failedAttempts = 0;   // after enough wrong codes, explain how access works
// how many wrong codes before the note appears (the cabinet waits for two)
const restrictAfter = codeModal ? parseInt(codeModal.getAttribute('data-restrict-after') || '2', 10) : 2;

function openCodeModal(folderKey){
  pendingFolder = folderKey;
  if(!codeModal) return;
  codeError.classList.remove('show');
  if(codeRestricted) codeRestricted.classList.toggle('show', failedAttempts >= restrictAfter);
  codeInput.value = '';
  codeModal.classList.add('open');
  setTimeout(() => codeInput.focus(), 50);
}

function closeCodeModal(){
  if(!codeModal) return;
  codeModal.classList.remove('open');
  pendingFolder = null;
}

function goToDatabase(folderKey){
  // Single-file preview build has #route-database-<key> sections and uses hash routing.
  // The real multi-page site instead has a standalone database-<key>.html file.
  if(document.getElementById('route-database-' + folderKey)){
    window.location.hash = 'database-' + folderKey;
  }else{
    window.location.href = 'database-' + folderKey + '.html';
  }
}

function gateHref(target){
  return typeof target === 'string' ? 'database-' + target + '.html' : target.href;
}

let checking = false;
async function submitCode(){
  if(!pendingFolder || checking) return;
  const code = codeInput.value.trim();
  if(!code) return;
  const target = pendingFolder, href = gateHref(target);
  checking = true;
  const ok = window.YHAccess ? await window.YHAccess.check(href, code) : null;
  checking = false;
  if(ok === false){
    failedAttempts++;
    codeError.classList.add('show');
    if(codeRestricted && failedAttempts >= restrictAfter) codeRestricted.classList.add('show');
    codeInput.value = '';
    return;
  }
  // unlocked (or could not be checked from here, in which case the page asks again)
  if(window.YHAccess) window.YHAccess.remember(href, code);
  closeCodeModal();
  if(typeof target === 'string') goToDatabase(target);
  else window.location.href = href;
}

document.querySelectorAll('.folder').forEach(f => {
  f.addEventListener('click', () => openCodeModal(f.getAttribute('data-folder')));
});
document.querySelectorAll('[data-gate]').forEach(a => {
  a.addEventListener('click', (e) => {
    e.preventDefault();
    openCodeModal({ key: a.getAttribute('data-gate'), href: a.getAttribute('href') });
  });
});

if(codeCancel){ codeCancel.addEventListener('click', closeCodeModal); }
if(codeInput){
  codeInput.addEventListener('keydown', (e) => { if(e.key === 'Enter') submitCode(); });
  codeInput.addEventListener('input', () => {
    if(codeInput.value.length === CODE_LENGTH) submitCode();
  });
}
if(codeModal){
  codeModal.addEventListener('click', (e) => { if(e.target === codeModal) closeCodeModal(); });
}
document.addEventListener('keydown', (e) => {
  if(e.key === 'Escape' && codeModal && codeModal.classList.contains('open')) closeCodeModal();
});

// ---------- Filing cabinet: papers riffle as the cursor moves along a file ----------
// Each sheet eases towards a target on every frame (a soft spring), so the
// motion stays fluid however fast the cursor moves. Sheets in the file under
// the cursor lift in a wave that follows the pointer; the neighbouring files
// stir slightly; everything drifts back when the cursor leaves.
(function(){
  const cabinet = document.querySelector('.filing-cabinet');
  if(!cabinet || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const folders = Array.from(cabinet.querySelectorAll('.folder')).map(el => ({
    el, body: el.querySelector('.folder-body'),
    papers: Array.from(el.querySelectorAll('.paper')).map((p, i) => ({ el: p, n: i + 1, y: 0, r: 0, x: 0, vy: 0, vr: 0, vx: 0 }))
  }));
  let pointer = null, raf = 0;
  function targetFor(f, fi, p){
    if(!pointer) return [0, 0, 0];
    const d = Math.abs(fi - pointer.fi);
    if(d > 1) return [0, 0, 0];
    const r = f.el.getBoundingClientRect();
    const x = Math.min(Math.max((pointer.x - r.left) / r.width, 0), 1);
    const k = d === 0 ? 1 : 0.3;
    // back sheets rise a little more, with a gentle wave travelling across
    const wave = 0.75 + 0.25 * Math.sin(x * Math.PI * 2 + p.n * 0.9);
    return [-(1.5 + p.n * 1.2) * wave * k, (0.5 - x) * 0.35 * k, (x - 0.5) * 6 * k];
  }
  function step(){
    let moving = false;
    folders.forEach((f, fi) => {
      f.papers.forEach(p => {
        const [ty, tr, tx] = targetFor(f, fi, p);
        // critically-damped-ish spring; later sheets respond a touch later
        const stiff = 0.075 - p.n * 0.006, damp = 0.78;
        p.vy = (p.vy + (ty - p.y) * stiff) * damp; p.y += p.vy;
        p.vr = (p.vr + (tr - p.r) * stiff) * damp; p.r += p.vr;
        p.vx = (p.vx + (tx - p.x) * stiff) * damp; p.x += p.vx;
        if(Math.abs(ty - p.y) + Math.abs(p.vy) + Math.abs(tr - p.r) * 10 + Math.abs(tx - p.x) > 0.02) moving = true;
        p.el.style.transform = 'translate3d(' + p.x.toFixed(2) + 'px,' + p.y.toFixed(2) + 'px,0) rotate(' + p.r.toFixed(3) + 'deg)';
      });
    });
    raf = moving ? requestAnimationFrame(step) : 0;
  }
  function kick(){ if(!raf) raf = requestAnimationFrame(step); }
  cabinet.addEventListener('mousemove', e => {
    const el = e.target.closest('.folder');
    const fi = folders.findIndex(f => f.el === el);
    pointer = fi < 0 ? null : { x: e.clientX, fi };
    kick();
  });
  cabinet.addEventListener('mouseleave', () => {
    pointer = null;
    kick();
  });
})();

// ---------- Section index (inner pages): touch devices open a group on tap ----------
document.querySelectorAll('.site-index .idx-group > .idx-head').forEach(head => {
  head.addEventListener('click', e => {
    const g = head.parentElement;
    const open = !g.classList.contains('open');
    document.querySelectorAll('.site-index .idx-group.open').forEach(x => x.classList.remove('open'));
    g.classList.toggle('open', open);
    head.setAttribute('aria-expanded', open);
    e.stopPropagation();
  });
});
document.addEventListener('click', () => {
  document.querySelectorAll('.site-index .idx-group.open').forEach(g => { g.classList.remove('open'); g.querySelector('.idx-head').setAttribute('aria-expanded', 'false'); });
});

// ---------- Cookie consent: first-visit banner + settings panel ----------
// The site sets no analytics or advertising cookies today; these record the
// visitor's choices (on their own device) so any future categories only run
// with consent. The banner shows once, until a choice is made in either the
// banner or the panel; the panel opens from "Cookie Settings" in every footer.
(function(){
  const KEY = 'yh_cookie_prefs';
  function load(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){ return {}; } }
  function save(p){ try { localStorage.setItem(KEY, JSON.stringify(Object.assign(p, { updated: new Date().toISOString() }))); } catch(e){} }
  let panel = null;
  function build(){
    panel = document.createElement('div');
    panel.className = 'cookie-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'true');
    panel.setAttribute('aria-labelledby', 'cookieTitle');
    panel.innerHTML = `
      <div class="cookie-card">
        <p class="cookie-eyebrow">YVIS HAUSEN</p>
        <h2 class="cookie-title" data-k id="cookieTitle">Cookie Settings</h2>
        <p class="cookie-text" data-k>We use only what is needed for this website to work. Optional categories stay off unless you choose otherwise. <a href="cookies.html">Cookie Policy</a></p>
        <div class="cookie-row">
          <div><p class="cookie-name" data-k>Strictly necessary</p><p class="cookie-desc" data-k>Required for the site to function. Always on.</p></div>
          <span class="cookie-always" data-k>ALWAYS ON</span>
        </div>
        <label class="cookie-row">
          <div><p class="cookie-name" data-k>Analytics</p><p class="cookie-desc" data-k>Understanding how the site is used. Not currently in use.</p></div>
          <input type="checkbox" class="cookie-switch" data-cat="analytics">
        </label>
        <label class="cookie-row">
          <div><p class="cookie-name" data-k>Marketing</p><p class="cookie-desc" data-k>Measuring or personalising advertising. Not currently in use.</p></div>
          <input type="checkbox" class="cookie-switch" data-cat="marketing">
        </label>
        <div class="cookie-actions">
          <button type="button" class="cookie-btn" data-k data-act="reject">REJECT ALL</button>
          <button type="button" class="cookie-btn" data-k data-act="accept">ACCEPT ALL</button>
          <button type="button" class="cookie-btn cookie-btn--solid" data-k data-act="save">SAVE SETTINGS</button>
        </div>
        <button type="button" class="cookie-close" aria-label="Close" data-ka="aria-label">&times;</button>
      </div>`;
    if(window.YHi18n) YHi18n.apply(panel);
    document.body.appendChild(panel);
    panel.addEventListener('click', e => {
      if(e.target === panel || e.target.closest('.cookie-close')) return close();
      const act = e.target.closest('[data-act]'); if(!act) return;
      const boxes = panel.querySelectorAll('.cookie-switch');
      if(act.dataset.act === 'accept') boxes.forEach(b => b.checked = true);
      if(act.dataset.act === 'reject') boxes.forEach(b => b.checked = false);
      const prefs = { necessary: true };
      boxes.forEach(b => prefs[b.dataset.cat] = b.checked);
      save(prefs);
      hideBanner();
      close();
    });
    document.addEventListener('keydown', e => { if(e.key === 'Escape' && panel.classList.contains('open')) close(); });
  }
  let lastFocus = null;
  function open(){
    if(!panel) build();
    const prefs = load();
    panel.querySelectorAll('.cookie-switch').forEach(b => b.checked = !!prefs[b.dataset.cat]);
    lastFocus = document.activeElement;
    requestAnimationFrame(() => { panel.classList.add('open'); panel.querySelector('.cookie-btn--solid').focus(); });
  }
  function close(){ panel.classList.remove('open'); if(lastFocus) lastFocus.focus(); }
  document.addEventListener('click', e => {
    const t = e.target.closest('[data-cookie-settings]');
    if(t){ e.preventDefault(); open(); }
  });

  // first-visit banner
  let banner = null;
  function hideBanner(){
    if(!banner) return;
    banner.classList.remove('show');
    const b = banner; banner = null;
    setTimeout(() => b.remove(), 600);
  }
  function showBanner(){
    banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', window.YHi18n ? YHi18n.t('Cookie consent') : 'Cookie consent');
    banner.innerHTML = `
      <p class="cookie-banner-text" data-k>We use only what this website needs to work. Optional cookies stay off unless you choose otherwise. &nbsp;<a href="cookies.html">Cookie Policy</a></p>
      <div class="cookie-banner-actions">
        <button type="button" class="cookie-btn" data-k data-choice="settings">COOKIE SETTINGS</button>
        <button type="button" class="cookie-btn" data-k data-choice="reject">REJECT ALL</button>
        <button type="button" class="cookie-btn cookie-btn--solid" data-k data-choice="accept">ACCEPT ALL</button>
      </div>`;
    if(window.YHi18n) YHi18n.apply(banner);
    document.body.appendChild(banner);
    banner.addEventListener('click', e => {
      const b = e.target.closest('[data-choice]'); if(!b) return;
      if(b.dataset.choice === 'settings') return open();
      const all = b.dataset.choice === 'accept';
      save({ necessary: true, analytics: all, marketing: all });
      hideBanner();
    });
    requestAnimationFrame(() => requestAnimationFrame(() => banner && banner.classList.add('show')));
  }
  if(!load().updated){
    // on the homepage, wait for the coin loader to finish first
    const delay = document.getElementById('loader') ? LOADER_MS + 900 : 700;
    setTimeout(() => { if(!load().updated) showBanner(); }, delay);
  }
})();

// ---------- Legal pages: highlight the section being read in the contents ----------
(function(){
  const toc = document.querySelectorAll('.legal-toc a');
  if(!toc.length || !('IntersectionObserver' in window)) return;
  const map = new Map(Array.from(toc).map(a => [a.getAttribute('href').slice(1), a]));
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if(en.isIntersecting){
        toc.forEach(a => a.classList.remove('active'));
        const a = map.get(en.target.id); if(a) a.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  document.querySelectorAll('.legal-sec').forEach(s => io.observe(s));
})();

// ---------- Legal links always open at the top of the page ----------
// Pages load at the top rather than restoring an earlier scroll position,
// and clicking the link for the page you are already on glides back up.
if('scrollRestoration' in history) history.scrollRestoration = 'manual';
window.addEventListener('pageshow', () => { if(!location.hash) window.scrollTo(0, 0); });
document.querySelectorAll('.legal-links a[href$=".html"]').forEach(a => {
  a.addEventListener('click', e => {
    const here = location.pathname.split('/').pop() || 'index.html';
    if(a.getAttribute('href') === here){
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }
  });
});

// ---------- Section-page illustrations: play on scroll, rest when off screen ----------
(function(){
  const figs = document.querySelectorAll('.page-ill');
  if(!figs.length) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reveal = new IntersectionObserver((entries) => {
    entries.forEach(e => { if(e.isIntersecting){ e.target.classList.add('in'); reveal.unobserve(e.target); } });
  }, { threshold: 0.3 });
  const vis = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      const svg = e.target.querySelector('svg');
      e.target.classList.toggle('off', !e.isIntersecting);
      if(svg && svg.pauseAnimations){ e.isIntersecting && !reduce ? svg.unpauseAnimations() : svg.pauseAnimations(); }
    });
  }, { threshold: 0 });
  figs.forEach(f => {
    const svg = f.querySelector('svg');
    if(svg && svg.pauseAnimations) svg.pauseAnimations();
    reveal.observe(f); vis.observe(f);
  });
})();
