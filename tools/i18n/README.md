# English edition build

`/en/` is generated from the Japanese pages, not written by hand. Markup, classes,
images and layout are copied through untouched; only text nodes, translatable
attributes (`title`, `alt`, `content`, `placeholder`) and shared asset paths change.

Keeping it generated is the point: when a Japanese page changes, the English one is
rebuilt from it, so the two cannot drift apart without anyone noticing.

## Rebuilding

The Japanese pages are not committed here. Mirror them first:

```bash
cd tools/i18n && mkdir -p site
curl -sSL https://www.timelessliving.jp/ -o site/home.html
# …and each path under about/ interview/ service/ portfolio/ corp/ policy/
```

Then:

```bash
python3 tools/i18n/build.py en
```

It prints every page it writes and, at the end, any Japanese text that no entry
covers — an empty list is the pass condition. A single section can be rebuilt by
passing a path prefix, e.g. `python3 tools/i18n/build.py en portfolio`.

## The translation tables

- `common.json` — every string that appears on more than one page: navigation,
  buttons, form labels, specification terms, the seminar template, dates.
- `pages/<section>_<page>.json` — strings belonging to one page. `text` is matched
  literally; `raw` holds HTML snippets replaced whole, used where a sentence is split
  across inline tags and English needs a different word order.

Longer keys are applied first, so a specific phrase always wins over a shorter one
inside it.

## Things the build is careful about

- **Form plumbing is masked.** `name="…"` on every field and `value="…"` on every
  radio are posted to `/corp/mail.php`, which reads them in Japanese, so they are
  protected before translation and restored after. Only the visible labels change.
- **Pages are normalised to NFC.** Some news pages were saved with a decomposed
  voiced-sound mark, which no dictionary key would otherwise match.
- **Asset paths become root-relative.** `/en/` sits one directory deeper than the
  Japanese tree, so `../css/`, `./images/` and `../about/images/` are rewritten to
  `/css/`, `/<section>/images/`. Page-to-page links stay relative and resolve
  inside `/en/`.
- **`hreflang` and the language switch** are added to every page; the switch is the
  only new element on the page.

## What the Japanese site still needs

Add the mirror link to each Japanese page, so the English edition can be found:

```html
<link rel="alternate" hreflang="en" href="https://www.timelessliving.jp/en/<path>">
<link rel="alternate" hreflang="x-default" href="https://www.timelessliving.jp/<path>">
```

and an `English` link in the header utility row, beside the telephone number.
