#!/usr/bin/env python3
"""Generate the English edition of timelessliving.jp from the Japanese pages.

Markup, classes, image files and layout are untouched. Only text nodes,
translatable attributes and asset paths change.
"""
import glob, json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(ROOT), 'site')
CJK = re.compile(r'[぀-ゟ゠-ヿ㐀-䶿一-鿿]')

# source file -> path of the page on the site (Japanese)
PAGES = {'home.html': 'index.html'}
for d, names in (
    ('about', ['index', 'page1', 'page2', 'page3']),
    ('interview', ['index'] + ['page%d' % i for i in range(1, 7)]),
    ('service', ['index', 'page1', 'page2']),
    ('portfolio', ['index'] + ['page%d' % i for i in range(1, 16)]),
    ('corp', ['index', 'message', 'history', 'access', 'changes',
              'conceptroom', 'info', 'news', 'news261014']),
    ('policy', ['index']),
):
    for n in names:
        PAGES['%s/%s.html' % (d, n)] = '%s/%s.html' % (d, n)

# The dated news archive: same template, translated entirely from common.json.
for _p in glob.glob(os.path.join(SRC, 'corp', 'news*.html')):
    _n = os.path.basename(_p)
    PAGES['corp/' + _n] = 'corp/' + _n


def nfc(obj):
    if isinstance(obj, str):
        return unicodedata.normalize('NFC', obj)
    if isinstance(obj, dict):
        return {nfc(k): nfc(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [nfc(v) for v in obj]
    return obj


def load(name):
    p = os.path.join(ROOT, name)
    return nfc(json.load(open(p, encoding='utf-8'))) if os.path.exists(p) else {}


COMMON = load('common.json')

# Shared numeric patterns: floor-area, tsubo and the layout code separator.
REGEX = [
    (r'(\d(?:LDK|DK|K)(?:\+S)?|STUDIO)\u3000', '\\1 · '),
    (r'\u7d04(\d+)m', r'approx. \1 m'),
    (r'\u7d04(\d+)\u576a', r'approx. \1 tsubo'),
]


# Form plumbing that must stay exactly as the Japanese server expects it:
# radio inputs carry their posted value, and every field carries its posted name.
MASK = [re.compile(r'<input[^>]*type="radio"[^>]*>'), re.compile(r'name="[^"]*"')]


def protect(html):
    store = []

    def grab(m):
        store.append(m.group(0))
        return '\x00P%d\x00' % (len(store) - 1)

    for pat in MASK:
        html = pat.sub(grab, html)
    return html, store


def restore(html, store):
    for i, original in enumerate(store):
        html = html.replace('\x00P%d\x00' % i, original)
    return html


def translate(html, table, raws):
    for ja, en in raws:
        if ja not in html:
            print('    ! raw snippet not found: %s' % ja[:60].replace('\n', ' '))
        html = html.replace(ja, en)
    html, store = protect(html)
    for ja in sorted(table, key=len, reverse=True):
        html = html.replace(ja, table[ja])
    html = restore(html, store)
    for pat, rep in REGEX:
        html = re.sub(pat, rep, html)
    return html


def rewrite_urls(html, jadir):
    """Point shared assets at the site root; keep page links relative."""
    html = html.replace('https://www.timelessliving.jp/images/', '\x00IMG\x00')
    html = html.replace('https://www.timelessliving.jp', 'https://www.timelessliving.jp/en')
    html = html.replace('\x00IMG\x00', 'https://www.timelessliving.jp/images/')
    html = re.sub(r'(src|href|data)="\.\./(css|js|images|font)/', r'\1="/\2/', html)
    # images that live in another section's folder, e.g. ../about/images/x.jpg
    html = re.sub(r'(src|href|data)="\.\./([a-z]+)/images/', r'\1="/\2/images/', html)
    prefix = '/%s/' % jadir if jadir else '/'
    html = re.sub(r'(src|href|data)="\./(images|css|js)/',
                  lambda m: '%s="%s%s/' % (m.group(1), prefix, m.group(2)), html)
    html = re.sub(r'(src|href|data)="(images|css|js)/',
                  lambda m: '%s="%s%s/' % (m.group(1), prefix, m.group(2)), html)
    html = html.replace('connect.facebook.net/ja_JP/sdk.js',
                        'connect.facebook.net/en_US/sdk.js')
    return html


# The social link the switch sits beside. Older news pages carry Facebook
# where the rest carry Instagram, so each anchor is tried in turn.
DESKTOP_ANCHORS = [
    '<li><a class="header-link" href="https://www.instagram.com/',
    '<li><a class="header-link" href="https://www.facebook.com/',
]
MOBILE_HEADER_ANCHOR = '<li><a class="header-link menu sb-toggle-right"'

LANG_STYLE = '\n  <style>/* language switch: scoped to this page, tl.css untouched */\n  .lang-current{color:#bf360c}\n  .lang-sp{line-height:1;vertical-align:middle;font-size:12px;letter-spacing:.02em}\n  .lang-sp .lang-switch{padding:0 10px 0 0}\n  /* at 320px the logo, the switch and the burger are 1px too wide to\n     share a line, and the burger drops below the logo */\n  @media screen and (max-width:360px){\n    .lang-sp{font-size:11px}\n    .lang-sp .lang-switch{padding:0 4px 0 0}\n  }\n  </style>'


def canonical(japath):
    """The home page is served from the directory, not from index.html."""
    return '' if japath == 'index.html' else japath


def add_head_links(html, japath):
    japath = canonical(japath)
    ja = 'https://www.timelessliving.jp/' + japath
    en = 'https://www.timelessliving.jp/en/' + japath
    block = (
        '\n  <link rel="alternate" hreflang="ja" href="%s">'
        '\n  <link rel="alternate" hreflang="en" href="%s">'
        '\n  <link rel="alternate" hreflang="x-default" href="%s">' % (ja, en, ja)
    )
    return html.replace('</head>', block + '\n</head>', 1)


def add_language_switch(html, japath):
    """Both languages in the header of both layouts, the current one in accent.

    Mobile carries it beside the burger rather than inside the slide-out menu, so
    an English reader landing on a Japanese page sees the way out without opening
    anything; under 360px the current-language marker drops and only the tappable
    one remains, which is what fits beside the logo.

    The rules live in a style block on the page. tl.css is maintained by someone
    else and is never edited.
    """
    japath = canonical(japath)
    ja = 'https://www.timelessliving.jp/' + japath
    desktop = '<li><a class="header-link lang-switch" href="%s" lang="ja" hreflang="ja">日本語</a><span class="header-link lang-current">English</span></li>' % ja
    for anchor in DESKTOP_ANCHORS:
        if anchor in html:
            html = html.replace(anchor, desktop + anchor, 1)
            break
    else:
        print('    ! desktop language switch anchor not found')
    mobile = '<li class="lang-sp"><a class="header-link lang-switch" href="%s" lang="ja" hreflang="ja">日本語</a></li>' % ja
    if MOBILE_HEADER_ANCHOR in html:
        html = html.replace(MOBILE_HEADER_ANCHOR, mobile + MOBILE_HEADER_ANCHOR, 1)
    else:
        print('    ! mobile header anchor not found')
    return html.replace('</head>', LANG_STYLE + '\n</head>', 1)


def build(outroot, only=None):
    built, leftovers = 0, {}
    for src, japath in sorted(PAGES.items()):
        if only and not japath.startswith(only):
            continue
        srcfile = os.path.join(SRC, src)
        if not os.path.exists(srcfile):
            continue
        key = japath.replace('/', '_').replace('.html', '')
        page = load(os.path.join('pages', key + '.json'))
        # Some pages were saved in NFD (a separate voiced-sound mark), which no
        # dictionary key would match. Normalise to NFC before translating.
        html = unicodedata.normalize('NFC', open(srcfile, encoding='utf-8').read())
        table = dict(COMMON)
        table.update(page.get('text', {}))
        print('  %s' % japath)
        html = translate(html, table, page.get('raw', []))
        jadir = os.path.dirname(japath)
        html = rewrite_urls(html, jadir)
        desc = page.get('description')
        if desc:
            before = html
            html = html.replace('<meta name="description" content="">',
                                '<meta name="description" content="%s">' % desc, 1)
            if html == before:
                print('    ! no empty description tag to fill')
        html = add_head_links(html, japath)
        html = add_language_switch(html, japath)
        html = html.replace('<html lang="ja-JP"', '<html lang="en"', 1)
        out = os.path.join(outroot, japath)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(html)
        built += 1
        # anything still Japanese, outside the deliberate language switch
        check = re.sub(r'(?is)<script\b.*?</script>', '', html)
        check = check.replace('日本語', '')
        rest = sorted({t.strip() for t in re.split(r'<[^>]*>|\n', check)
                       if CJK.search(t or '')})
        if rest:
            leftovers[japath] = rest
    print('\nbuilt %d pages' % built)
    if leftovers:
        print('UNTRANSLATED RUNS REMAIN:')
        for p, rs in leftovers.items():
            print('  %s' % p)
            for r in rs:
                print('     |%s' % r[:110])
    else:
        print('no Japanese text left in the built pages')
    return 0 if not leftovers else 1


if __name__ == '__main__':
    outroot = sys.argv[1]
    only = sys.argv[2] if len(sys.argv) > 2 else None
    sys.exit(build(outroot, only))
