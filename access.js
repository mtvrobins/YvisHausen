/* Private pages: the Engine (System Page) and the seven database folders are
   published only in encrypted form (AES-256-GCM, key derived from the access
   code with PBKDF2). Nothing readable, and no code, is shipped to the browser:
   a page opens only when the right code decrypts it. Built by tools/build.py. */
(function(){
  const enc = new TextEncoder(), dec = new TextDecoder();
  const bytes = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

  async function decrypt(payload, code){
    const base = await crypto.subtle.importKey('raw', enc.encode(code), 'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey(
      { name:'PBKDF2', salt:bytes(payload.s), iterations:payload.n, hash:'SHA-256' },
      base, { name:'AES-GCM', length:256 }, false, ['decrypt']);
    const out = await crypto.subtle.decrypt({ name:'AES-GCM', iv:bytes(payload.i) }, key, bytes(payload.c));
    return dec.decode(out);
  }

  function readPayload(html){
    const m = html.match(/<script type="application\/json" id="yh-payload">([\s\S]*?)<\/script>/);
    return m ? JSON.parse(m[1]) : null;
  }

  // true: the code opens the page; false: it does not; null: could not check
  // from here (e.g. opened from disk), so the page itself will check.
  async function check(href, code){
    try{
      const res = await fetch(href, { cache:'no-store' });
      if(!res.ok) return null;
      const payload = readPayload(await res.text());
      if(!payload) return true;
      await decrypt(payload, code);
      return true;
    }catch(e){
      return (e && e.name === 'OperationError') ? false : null;
    }
  }

  const keyFor = (href) => 'yh-access:' + href.split('/').pop().split('#')[0];
  function remember(href, code){ try{ sessionStorage.setItem(keyFor(href), code); }catch(e){} }
  function recall(href){ try{ return sessionStorage.getItem(keyFor(href)); }catch(e){ return null; } }

  window.YHAccess = { decrypt, readPayload, check, remember, recall };
})();
