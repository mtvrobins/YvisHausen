/* Yvis Hausen — language switching (English, French, Italian).
   Each page carries its own translations (see tools/i18n.py). The visitor's
   choice is remembered on their device; on a first visit the browser's
   language is used when it is French or Italian. */
(function(){
  var KEY = 'yh_lang', LANGS = ['en', 'fr', 'it'];
  var COMMON = /*common*/{"ACCEPT ALL":{"fr":"TOUT ACCEPTER","it":"ACCETTA TUTTI"},"ALWAYS ON":{"fr":"TOUJOURS ACTIFS","it":"SEMPRE ATTIVI"},"Analytics":{"fr":"Analyse","it":"Analitici"},"COOKIE SETTINGS":{"fr":"PARAMÈTRES DES COOKIES","it":"IMPOSTAZIONI COOKIE"},"Close":{"fr":"Fermer","it":"Chiudi"},"Cookie Settings":{"fr":"Paramètres des cookies","it":"Impostazioni cookie"},"Cookie consent":{"fr":"Consentement aux cookies","it":"Consenso ai cookie"},"Marketing":{"fr":"Marketing","it":"Marketing"},"Measuring or personalising advertising. Not currently in use.":{"fr":"Mesurer ou personnaliser la publicité. Non utilisés actuellement.","it":"Misurare o personalizzare la pubblicità. Attualmente non in uso."},"REJECT ALL":{"fr":"TOUT REFUSER","it":"RIFIUTA TUTTI"},"Required for the site to function. Always on.":{"fr":"Indispensables au fonctionnement du site. Toujours actifs.","it":"Indispensabili al funzionamento del sito. Sempre attivi."},"SAVE SETTINGS":{"fr":"ENREGISTRER","it":"SALVA IMPOSTAZIONI"},"Strictly necessary":{"fr":"Strictement nécessaires","it":"Strettamente necessari"},"Understanding how the site is used. Not currently in use.":{"fr":"Comprendre comment le site est utilisé. Non utilisés actuellement.","it":"Capire come viene utilizzato il sito. Attualmente non in uso."},"We use only what is needed for this website to work. Optional categories stay off unless you choose otherwise. <a href=\"cookies.html\">Cookie Policy</a>":{"fr":"Nous n’utilisons que ce qui est nécessaire au fonctionnement de ce site. Les catégories facultatives restent désactivées, sauf choix contraire de votre part. <a href=\"cookies.html\">Politique relative aux cookies</a>","it":"Utilizziamo solo ciò che serve al funzionamento di questo sito. Le categorie facoltative restano disattivate, salvo vostra diversa scelta. <a href=\"cookies.html\">Cookie policy</a>"},"We use only what this website needs to work. Optional cookies stay off unless you choose otherwise. &nbsp;<a href=\"cookies.html\">Cookie Policy</a>":{"fr":"Nous n’utilisons que ce dont ce site a besoin pour fonctionner. Les cookies facultatifs restent désactivés, sauf choix contraire de votre part. &nbsp;<a href=\"cookies.html\">Politique relative aux cookies</a>","it":"Utilizziamo solo ciò di cui questo sito ha bisogno per funzionare. I cookie facoltativi restano disattivati, salvo vostra diversa scelta. &nbsp;<a href=\"cookies.html\">Cookie policy</a>"}}/*/common*/;
  var dict = {};
  try { dict = JSON.parse(document.getElementById('yh-i18n').textContent); } catch(e){}
  var listeners = [];

  function stored(){ try { return localStorage.getItem(KEY); } catch(e){ return null; } }
  function store(l){ try { localStorage.setItem(KEY, l); } catch(e){} }
  function initial(){
    var s = stored();
    if(LANGS.indexOf(s) > -1) return s;
    var n = (navigator.language || '').slice(0, 2).toLowerCase();
    return (n === 'fr' || n === 'it') ? n : 'en';
  }

  // keep the English original the first time an element is translated
  function orig(el, name, value){
    var k = '_yhEn_' + name;
    if(el[k] === undefined) el[k] = value;
    return el[k];
  }
  function setHTML(el, en, tr){
    var lead = /^\s*/.exec(en)[0], trail = /\s*$/.exec(en)[0];
    el.innerHTML = tr === null ? en : lead + tr + trail;
  }

  function apply(lang, root){
    root = root || document;
    var d = dict[lang] || {};
    each(root, '[data-t]', function(el){
      var en = orig(el, 'html', el.innerHTML);
      var tr = lang === 'en' ? null : d[el.getAttribute('data-t')];
      setHTML(el, en, tr === undefined ? null : tr);
    });
    each(root, '[data-ta]', function(el){
      el.getAttribute('data-ta').split(' ').forEach(function(pair){
        var i = pair.indexOf(':'), name = pair.slice(0, i), id = pair.slice(i + 1);
        var en = orig(el, name, el.getAttribute(name));
        var tr = lang === 'en' ? undefined : d[id];
        el.setAttribute(name, tr === undefined ? en : tr);
      });
    });
    each(root, '[data-k]', function(el){
      var en = orig(el, 'html', el.innerHTML);
      var row = COMMON[en.replace(/\s+/g, ' ').trim()];
      setHTML(el, en, lang !== 'en' && row && row[lang] ? row[lang] : null);
    });
    each(root, '[data-ka]', function(el){
      el.getAttribute('data-ka').split(' ').forEach(function(name){
        var en = orig(el, name, el.getAttribute(name));
        el.setAttribute(name, t(en, lang));
      });
    });
  }
  function each(root, sel, fn){
    if(root.nodeType === 1 && root.matches(sel)) fn(root);
    Array.prototype.forEach.call(root.querySelectorAll(sel), fn);
  }
  function t(en, lang){
    var row = COMMON[en];
    lang = lang || api.lang;
    return lang !== 'en' && row && row[lang] ? row[lang] : en;
  }

  function mark(lang){
    document.documentElement.setAttribute('lang', lang);
    Array.prototype.forEach.call(document.querySelectorAll('.lang-option'), function(o){
      o.classList.toggle('active', o.getAttribute('data-lang') === lang);
    });
  }

  function set(lang){
    if(LANGS.indexOf(lang) < 0 || lang === api.lang) return;
    store(lang);
    // pages that animate their text word by word are simply redrawn
    if(document.querySelector('[data-split], [data-letters]')){ location.reload(); return; }
    api.lang = lang;
    apply(lang);
    mark(lang);
    listeners.forEach(function(fn){ fn(lang); });
  }

  var api = window.YHi18n = {
    lang: initial(),
    set: set,
    t: t,
    apply: function(root){ apply(api.lang, root); },
    on: function(fn){ listeners.push(fn); }
  };
  if(api.lang !== 'en') apply(api.lang);
  mark(api.lang);

  // the LANGUAGE menu in the header
  document.addEventListener('click', function(e){
    var opt = e.target.closest && e.target.closest('.lang-option');
    var toggle = e.target.closest && e.target.closest('.lang-toggle');
    if(opt){
      e.stopPropagation();
      var dd = opt.closest('.lang-dropdown');
      if(dd) dd.classList.remove('open');
      set(opt.getAttribute('data-lang'));
      return;
    }
    if(toggle){
      toggle.closest('.lang-dropdown').classList.toggle('open');
      return;
    }
    Array.prototype.forEach.call(document.querySelectorAll('.lang-dropdown.open'), function(d){ d.classList.remove('open'); });
  });
})();
