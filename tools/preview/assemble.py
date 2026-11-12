#!/usr/bin/env python3
"""Assemble the shareable preview: both editions, switching between each other.

The deliverables point at https://www.timelessliving.jp — which is right for the
real server and wrong for a preview, where following the switch would jump to
the live site. Here, and only here, those absolute links are made site-relative
so the two editions switch between each other inside the preview.

Nothing in en/ or ja-patched/ is modified; the rewrite happens on the copy.
"""
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 'https://www.timelessliving.jp'


def copy_tree(src, dst):
    for d, _, files in os.walk(src):
        rel = os.path.relpath(d, src)
        out = os.path.join(dst, rel) if rel != '.' else dst
        os.makedirs(out, exist_ok=True)
        for f in files:
            if f == 'README.md':
                continue              # the folder's own note, not a page
            shutil.copy2(os.path.join(d, f), os.path.join(out, f))


def localise(root):
    """Point the switch and the hreflang pair at this preview, not the live site."""
    n = 0
    for d, _, files in os.walk(root):
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(d, f)
            s = open(p, encoding='utf-8').read()
            before = s
            # only the two links that are about the other edition
            s = re.sub(r'(<(?:a|link)[^>]*?(?:lang-switch|rel="alternate")[^>]*?href=")'
                       + re.escape(BASE), r'\1', s)
            # og:url and the Facebook widget stay on the real domain: they are
            # about the published page, not about navigating the preview
            if s != before:
                open(p, 'w', encoding='utf-8').write(s)
                n += 1
    return n


def main(out):
    if os.path.exists(out):
        shutil.rmtree(out)
    copy_tree(os.path.join(ROOT, 'ja-patched'), out)          # Japanese at the root
    copy_tree(os.path.join(ROOT, 'en'), os.path.join(out, 'en'))
    pages = sum(len([f for f in fs if f.endswith('.html')]) for _, _, fs in os.walk(out))
    print('preview assembled: %d pages, %d rewritten for local switching'
          % (pages, localise(out)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '_preview')
