"""Translations (French and Italian) for every page.

How it works
------------
* The English text in each page is the source. The build finds each piece of
  readable text (a heading, a paragraph, a button, a link...) and tags it with
  data-t="<id>", where the id is taken from the English wording itself.
  Readable attributes (alt, aria-label, placeholder, title) are tagged with
  data-ta="attribute:<id> ...".
* The translations live in tools/i18n/fr.json and tools/i18n/it.json, as
  "English": "translation" pairs. Edit those files to change a translation.
* Each page then carries only its own translations, in a
  <script type="application/json" id="yh-i18n"> block, and i18n.js swaps the
  text when a visitor picks a language (remembered on their device). Private
  pages carry theirs inside the encrypted page, so nothing private is exposed.
* Text written by script.js (the cookie banner and settings) is marked with
  data-k; its translations are written into i18n.js.
* Anything that should never be translated gets translate="no" (the brand
  name, for example); anything script-driven gets data-t-skip.

If the English wording changes, its id changes too, and the build lists the
text that still needs translating in tools/i18n/missing.json.
"""
import hashlib, html, json, os, re
from html.parser import HTMLParser

LANGS = ('fr', 'it')
TM_DIR = 'tools/i18n'
INLINE = {'a', 'abbr', 'b', 'bdi', 'br', 'cite', 'code', 'em', 'i', 'mark', 'q', 's',
          'small', 'span', 'strong', 'sub', 'sup', 'time', 'u', 'wbr', 'tspan'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'source', 'track', 'wbr'}
SKIP = {'script', 'style', 'template', 'textarea', 'select'}
ATTRS = ('alt', 'aria-label', 'placeholder', 'title')
LETTER = re.compile(r'[A-Za-z]')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def key_id(text):
    return hashlib.sha1(text.encode()).hexdigest()[:8]


class Node:
    def __init__(self, tag, attrs, start, start_end, parent):
        self.tag, self.attrs, self.start, self.start_end = tag, dict(attrs), start, start_end
        self.end_start = None
        self.parent, self.children = parent, []


class Tree(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer('\n', src):
            self.lines.append(m.end())
        self.root = Node('#root', [], 0, 0, None)
        self.cur = self.root
        self.feed(src)
        self.close()

    def off(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        o = self.off()
        n = Node(tag, attrs, o, o + len(self.get_starttag_text()), self.cur)
        self.cur.children.append(n)
        if tag in VOID:
            n.end_start = n.start_end
        else:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        o = self.off()
        n = Node(tag, attrs, o, o + len(self.get_starttag_text()), self.cur)
        n.end_start = n.start_end
        self.cur.children.append(n)

    def handle_endtag(self, tag):
        o = self.off()
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is self.root:
            return  # stray end tag
        n.end_start = o
        self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)

    def handle_entityref(self, name):
        self.cur.children.append(f'&{name};')

    def handle_charref(self, name):
        self.cur.children.append(f'&#{name};')


def text_of(n):
    out = []
    for c in n.children:
        out.append(html.unescape(c) if isinstance(c, str) else text_of(c))
    return ''.join(out)


def inline_only(n):
    for c in n.children:
        if isinstance(c, str):
            continue
        if c.tag not in INLINE or 'data-t-skip' in c.attrs or c.attrs.get('translate') == 'no' \
                or 'data-i18n-block' in c.attrs or not inline_only(c):
            return False
    return True


def own_text(n):
    # a piece of text is the element itself when it holds words directly;
    # a row of separate links or labels is split into one piece per item
    return any(isinstance(c, str) and LETTER.search(html.unescape(c)) for c in n.children)


def skipped(n):
    return n.tag in SKIP or 'data-t-skip' in n.attrs or n.attrs.get('translate') == 'no'


def scan(src):
    """Return (segments, attrs, loose): segments are (node, english html);
    attrs are (node, attribute, english); loose lists text that sits next to
    block elements and so can't be tagged (fix those by wrapping in a span)."""
    tree = Tree(src)
    segs, attrs, loose = [], [], []

    def visit(n, in_svg):
        if n.tag != '#root' and skipped(n):
            return
        svg = in_svg or n.tag == 'svg'
        for a in ATTRS:
            v = n.attrs.get(a)
            if v and LETTER.search(v) and not (svg and a == 'title'):
                attrs.append((n, a, norm(html.unescape(v))))
        if n.tag != '#root' and n.end_start is not None and n.end_start > n.start_end \
                and (not svg or n.tag in ('text', 'title')) and inline_only(n) \
                and own_text(n):
            segs.append((n, norm(src[n.start_end:n.end_start])))
            return
        for c in n.children:
            if isinstance(c, str):
                if not svg and LETTER.search(html.unescape(c)) and n.tag not in ('#root', 'html', 'head'):
                    loose.append(norm(c))
            else:
                visit(c, svg)

    visit(tree.root, False)
    return segs, attrs, loose


def strip_tags(src):
    return re.sub(r' data-t(?:a)?="[^"]*"', '', src)


def annotate(src):
    """Tag every translatable piece; return (new html, {id: english}, loose)."""
    src = strip_tags(src)
    segs, attrs, loose = scan(src)
    inserts = {}  # offset just after the tag name -> text to insert
    found = {}
    for n, en in segs:
        k = key_id(en)
        found[k] = en
        inserts.setdefault(n.start + 1 + len(n.tag), []).append(f' data-t="{k}"')
    by_node = {}
    for n, a, en in attrs:
        k = key_id(en)
        found[k] = en
        by_node.setdefault(n, []).append(f'{a}:{k}')
    for n, parts in by_node.items():
        inserts.setdefault(n.start + 1 + len(n.tag), []).append(f' data-ta="{" ".join(parts)}"')
    out = src
    for at in sorted(inserts, reverse=True):
        out = out[:at] + ''.join(inserts[at]) + out[at:]
    return out, found, loose


def load_tm():
    tm = {}
    for lang in LANGS:
        p = f'{TM_DIR}/{lang}.json'
        tm[lang] = json.load(open(p)) if os.path.exists(p) else {}
    return tm


def page_dict(found, tm, missing):
    d = {lang: {} for lang in LANGS}
    for k, en in sorted(found.items()):
        for lang in LANGS:
            tr = tm[lang].get(en)
            if tr is None:
                missing.setdefault(en, set()).add(lang)
            elif tr != en:
                d[lang][k] = tr
    return d


BLOCK = re.compile(r'<!-- i18n -->.*?<!-- /i18n -->\n?', re.S)


def inject(src, d):
    src = BLOCK.sub('', src)
    data = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    block = (f'<!-- i18n -->\n<script type="application/json" id="yh-i18n">{data}</script>\n'
             f'<script src="i18n.js"></script>\n<!-- /i18n -->\n')
    body = src.index('<body')
    m = re.compile(r'^[ \t]*<script', re.M).search(src, body)
    at = m.start() if m else src.rindex('</body>')
    return src[:at] + block + src[at:]


def localise(src, tm, missing, report=None):
    """Annotate one page and embed its translations."""
    out, found, loose = annotate(BLOCK.sub('', src))
    if report is not None and loose:
        report.extend(loose)
    return inject(out, page_dict(found, tm, missing))


COMMON = re.compile(r'/\*common\*/.*?/\*/common\*/', re.S)


def script_strings(js):
    """English strings that script.js marks for translation."""
    keys = set()
    for m in re.finditer(r'<(\w+)\b([^>]*)\bdata-k\b([^>]*)>(.*?)</\1>', js, re.S):
        keys.add(norm(m.group(4)))
    for m in re.finditer(r'aria-label="([^"]*)" data-ka', js):
        keys.add(m.group(1))
    for m in re.finditer(r"YHi18n\.t\('((?:[^'\\]|\\.)*)'\)", js):
        keys.add(m.group(1).replace("\\'", "'"))
    return keys


def write_common(tm, missing):
    js = open('script.js').read()
    common = {}
    for en in sorted(script_strings(js)):
        row = {}
        for lang in LANGS:
            tr = tm[lang].get(en)
            if tr is None:
                missing.setdefault(en, set()).add(lang)
            else:
                row[lang] = tr
        common[en] = row
    data = json.dumps(common, ensure_ascii=False, separators=(',', ':'))
    src = open('i18n.js').read()
    new = COMMON.sub(lambda m: f'/*common*/{data}/*/common*/', src)
    if new != src:
        open('i18n.js', 'w').write(new)


def write_missing(missing):
    p = f'{TM_DIR}/missing.json'
    if missing:
        rows = {en: sorted(l) for en, l in sorted(missing.items())}
        json.dump(rows, open(p, 'w'), ensure_ascii=False, indent=1)
    elif os.path.exists(p):
        os.remove(p)
