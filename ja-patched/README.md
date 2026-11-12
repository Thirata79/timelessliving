# Patched Japanese pages

Copies of the live Japanese pages with the two additions the English edition needs,
and **nothing else changed**. Upload them over the existing files at the site root —
`index.html` here replaces `/index.html`, `about/index.html` replaces `/about/index.html`,
and so on. This folder is not served at `/ja-patched/`.

## What was added, on all 102 pages

1. Three `hreflang` links in `<head>`, pointing at the page's English twin and back at
   itself:
   ```html
   <link rel="alternate" hreflang="ja" href="https://www.timelessliving.jp/about/index.html">
   <link rel="alternate" hreflang="en" href="https://www.timelessliving.jp/en/about/index.html">
   <link rel="alternate" hreflang="x-default" href="https://www.timelessliving.jp/about/index.html">
   ```
   Without these, Google has no way to know the two editions are the same page, and the
   English edition competes with the Japanese one instead of serving a different reader.

2. An **English** link in the header beside the telephone number, and in the slide-out
   menu on mobile. It uses `class="header-link lang-switch"` — the same class the
   telephone link already has, so it introduces no new style and no new CSS is needed.

The diff for any page is exactly three insertions. Classes, images, scripts, copy and
whitespace are untouched.

## Before you upload

These are copies taken from the live site on **2026-11-12**. If a Japanese page has been
edited since, uploading its copy from here would undo that edit. If in doubt, re-mirror
the site and re-run the patch rather than uploading these files as they stand:

```bash
python3 tools/i18n/patch_ja.py ja-patched
```

It reports any page it could not patch; a clean run says so explicitly. The script is
deliberately dumb — it inserts text at two anchors and leaves everything else alone — so
it is safe to run again against fresher copies.

## Upload order

Put `/en/` up first, then these. That way the `hreflang="en"` links never point at a
page that does not exist yet.
