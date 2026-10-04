"""Yvis Hausen site build.

    python3 tools/build.py              shared pieces + private pages
    python3 tools/build.py --sp         also rebuild the System Page from tools/sp_template.html
    python3 tools/build.py --ill        also redraw the section-page illustrations

1. Shared pieces: the header, section menu, footer and icon links live once in
   partials/ and are copied into every page between <!-- partial:NAME --> markers.
   Edit the partial, run the build, and every page updates.
2. Private pages: the readable pages in src/protected/ are encrypted with their
   access code (tools/access-codes.json) and published at the site root as small
   locked pages. Only the right code can open them; no code ships to the browser.
3. Translations: every page is tagged and given its French and Italian text from
   tools/i18n/fr.json and it.json (see tools/i18n.py). Text still waiting for a
   translation is listed in tools/i18n/missing.json.
"""
import glob, hashlib, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BLOCKS = {  # name: (opening of the block, its closing tag)
    'header': ('<header id="topbar">', '</header>'),
    'nav': ('<nav class="site-index"', '</nav>'),
    'footer': ('<footer class="site-footer">', '</footer>'),
}

def partial(name):
    return open(f'partials/{name}.html').read().rstrip('\n')

def apply_partials(s):
    for name, (start, end) in BLOCKS.items():
        body = partial(name)
        marked = re.compile(rf'<!-- partial:{name} -->.*?<!-- /partial:{name} -->', re.S)
        if marked.search(s):
            s = marked.sub(lambda m: f'<!-- partial:{name} -->\n  {body}\n  <!-- /partial:{name} -->', s)
        elif start in s:  # first run: wrap the existing copy in markers
            a = s.index(start); b = s.index(end, a) + len(end)
            s = s[:a] + f'<!-- partial:{name} -->\n  {body}\n  <!-- /partial:{name} -->' + s[b:]
    icons = '\n'.join(partial('head-icons').splitlines())
    marked = re.compile(r'<!-- partial:head-icons -->.*?<!-- /partial:head-icons -->', re.S)
    block = f'<!-- partial:head-icons -->\n{icons}\n<!-- /partial:head-icons -->'
    if marked.search(s):
        s = marked.sub(lambda m: block, s)
    else:
        m = re.search(r'<meta name="viewport"[^>]*>\n', s)
        s = s[:m.end()] + block + '\n' + s[m.end():]
    return s

def encrypt(text, code):
    # done in Node (tools/encrypt.mjs) with the same Web Crypto the browser uses
    out = subprocess.run(['node', 'tools/encrypt.mjs', code], input=text.encode(), capture_output=True, check=True)
    return out.stdout.decode()

ENGINE_NOTE = '''<div class="code-restricted code-note" id="gateNote">
        <p>THE SYSTEM CONTAINS PROPRIETARY YVIS HAUSEN METHODOLOGY AND IS AVAILABLE BY PRIVATE ACCESS ONLY. ACCESS DETAILS ARE PROVIDED TO PROSPECTIVE CLIENTS FOLLOWING A DISCOVERY CONVERSATION.</p>
        <div class="code-book-row"><a class="code-book" href="book.html">BOOK A CALL</a></div>
      </div>'''
FOLDER_NOTE = '<p class="code-restricted" id="gateNote">ACCESS RESTRICTED. ACCESS CODES ARE PROVIDED BY AUTHORISED AGENTS ONLY</p>'

def update(path, tm, missing):
    """Shared pieces, then translations; the file is written only if it changed."""
    src = open(path).read()
    out = apply_partials(src)
    if path != 'tools/protected_stub.html':
        out = i18n.localise(out, tm, missing)
    if out != src:
        open(path, 'w').write(out)
        return True
    return False

def protect(tm, missing):
    codes = {k: v for k, v in json.load(open('tools/access-codes.json')).items() if not k.startswith('_')}
    stub = open('tools/protected_stub.html').read()
    tm_stamp = json.dumps(tm, sort_keys=True)  # gate text translations
    for note in (ENGINE_NOTE, FOLDER_NOTE):  # list gate text still to translate
        i18n.localise(stub.replace('{{NOTE}}', note).replace('{{PAYLOAD}}', '{}'), tm, missing)
    for name, code in codes.items():
        src = f'src/protected/{name}'
        text = open(src).read()
        stamp = hashlib.sha256((str(code) + '\0' + text + stub + tm_stamp).encode()).hexdigest()[:16]
        if os.path.exists(name) and f'<!-- build:{stamp} -->' in open(name).read():
            continue  # unchanged since the last build
        payload = encrypt(text, str(code))
        engine = name == 'engine.html'
        page = (stub.replace('{{PAYLOAD}}', payload)
                    .replace('{{NOTE}}', ENGINE_NOTE if engine else FOLDER_NOTE)
                    .replace('{{AFTER}}', '1' if engine else '2')
                    .replace('{{BACK}}', 'marketing.html' if engine else 'index.html'))
        page = i18n.localise(page, tm, missing)
        open(name, 'w').write(page.replace('<head>', f'<head>\n<!-- build:{stamp} -->', 1))
        print(f'  locked  {name}')

if __name__ == '__main__':
    if '--sp' in sys.argv:
        subprocess.run([sys.executable, 'tools/sp_build.py'], check=True)
    if '--ill' in sys.argv:
        subprocess.run([sys.executable, 'tools/page_illustrations.py'], check=True)
    pages = sorted(glob.glob('*.html')) + sorted(glob.glob('src/protected/*.html')) + ['tools/protected_stub.html']
    locked = set(k for k in json.load(open('tools/access-codes.json')) if not k.startswith('_'))
    tm, missing = i18n.load_tm(), {}
    changed = [p for p in pages if p not in locked and update(p, tm, missing)]
    print(f'pages updated: {len(changed)}')
    i18n.write_common(tm, missing)
    protect(tm, missing)
    i18n.write_missing(missing)
    if missing:
        print(f'  {len(missing)} piece(s) of text still need translating: tools/i18n/missing.json')
