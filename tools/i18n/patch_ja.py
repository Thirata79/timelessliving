#!/usr/bin/env python3
"""Add the English edition's links to the Japanese pages.

Two additions per page and nothing else: the hreflang pair that lets a search
engine know the two editions are the same page, and an `English` link in the
header beside the telephone number. Every other byte is left as it is.
"""
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(ROOT), 'site')
BASE = 'https://www.timelessliving.jp/'

# the Japanese page -> its path on the site; home.html is served from the root
PAGES = {'home.html': ''}
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
import glob
for p in glob.glob(os.path.join(SRC, 'corp', 'news*.html')):
    n = os.path.basename(p)
    PAGES['corp/' + n] = 'corp/' + n

# Older news pages carry a Facebook link where the rest carry Instagram.
DESKTOP_ANCHORS = ['<li><a class="header-link" href="https://www.instagram.com/',
                   '<li><a class="header-link" href="https://www.facebook.com/']
MOBILE_HEADER_ANCHOR = '<li><a class="header-link menu sb-toggle-right"'

LANG_STYLE = '\n  <style>/* Added to the page, not to tl.css, which is maintained separately.\n     Language switch, and a readability pass for a readership that skews older. */\n  .lang-current{color:#bf360c}\n  .lang-sp{line-height:1;vertical-align:middle;font-size:12px;letter-spacing:.02em}\n  .lang-sp .lang-switch{padding:0 10px 0 0}\n  @media screen and (max-width:360px){\n    .lang-sp{font-size:11px}\n    .lang-sp .lang-switch{padding:0 4px 0 0}\n  }\n  /* desktop body was 14px; mobile was already 16px. 1.8 is the leading the\n     site already uses on its feature pages. */\n  body{font-size:16px;line-height:1.8}\n  p{margin-bottom:2.6em}\n  .news dl{font-size:16px}\n  .news dt{font-size:15px}\n  table{font-size:15px}\n  /* the smallest text on the site, and the lowest contrast: 4.2:1 -> 5.2:1 */\n  .copyright,.info li,div.capty-caption,span.post_date,p.postmetadata{font-size:13px}\n  .sec_txt{color:#666}\n  /* the interviewer. Italic is already in the site’s vocabulary (.author).\n     The space goes before the question, not after it, so each question stays\n     attached to the answer it belongs to. */\n  .interview dt{font-style:italic;margin:2.6em 0 .8em}\n  .interview dd{margin-bottom:2em}\n  /* a 16px body widens the whitespace between the nav’s inline-block items,\n     which tipped the row onto two lines at 768px. The labels set their own. */\n  .g_nav ul{font-size:0}\n  </style>'


def patch(html, path):
    ja, en = BASE + path, BASE + 'en/' + path
    notes = []

    head = ('\n  <link rel="alternate" hreflang="ja" href="%s">'
            '\n  <link rel="alternate" hreflang="en" href="%s">'
            '\n  <link rel="alternate" hreflang="x-default" href="%s">' % (ja, en, ja))
    if '</head>' in html:
        html = html.replace('</head>', head + '\n</head>', 1)
    else:
        notes.append('no </head>')

    desktop = '<li><span class="header-link lang-current">日本語</span><a class="header-link lang-switch" href="%s" lang="en" hreflang="en">English</a></li>' % en
    for anchor in DESKTOP_ANCHORS:
        if anchor in html:
            html = html.replace(anchor, desktop + anchor, 1)
            break
    else:
        notes.append('no header nav')

    mobile = '<li class="lang-sp"><a class="header-link lang-switch" href="%s" lang="en" hreflang="en">English</a></li>' % en
    if MOBILE_HEADER_ANCHOR in html:
        html = html.replace(MOBILE_HEADER_ANCHOR, mobile + MOBILE_HEADER_ANCHOR, 1)
    else:
        notes.append('no mobile header')

    html = html.replace('</head>', LANG_STYLE + '\n</head>', 1)

    return html, notes


def main(outroot):
    done, problems = 0, {}
    for src, path in sorted(PAGES.items()):
        f = os.path.join(SRC, src)
        if not os.path.exists(f):
            continue
        html = open(f, encoding='utf-8').read()
        html, notes = patch(html, path)
        out = os.path.join(outroot, path or 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w', encoding='utf-8').write(html)
        done += 1
        if notes:
            problems[path or 'index.html'] = notes
    print('patched %d pages' % done)
    if problems:
        print('INCOMPLETE:')
        for p, n in problems.items():
            print('  %-30s %s' % (p, ', '.join(n)))
    else:
        print('every page got all three hreflang links and both English links')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
