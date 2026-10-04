# Yvis Hausen — how the site is built

The site is plain HTML, CSS and JavaScript. There is no server code and no
database. One command keeps everything in step:

    python3 tools/build.py            # shared pieces, translations, private pages
    python3 tools/build.py --sp       # also rebuild the System Page
    python3 tools/build.py --ill      # also redraw the section-page illustrations

Requires Python 3 and Node.js (used for encryption).

## Folders

| Path | What it is | Public? |
|---|---|---|
| `*.html`, `styles.css`, `script.js`, `access.js`, `i18n.js`, `images/`, `fonts/`, `favicon.ico` | the website | yes |
| `partials/` | header, section menu, footer and icon links, shared by every page | no |
| `src/protected/` | readable source of the private pages (Engine + 7 database folders) | **never** |
| `tools/` | build scripts, System Page template, access codes, translations | **never** |
| `misc/` | archived files kept for reference (the original 1024px coin, the old Creative House image, the Vilaka and Rosie Brown demo fonts) | no |

When deploying, publish only the public files. `src/`, `tools/`, `partials/`,
`misc/`, `.claude/` and `.mcp.json` must not be uploaded.

## Shared pieces
Edit `partials/header.html`, `nav.html`, `footer.html` or `head-icons.html`,
then run the build. Every page is updated between its
`<!-- partial:NAME -->` markers. Don't edit inside those markers on a page.

## Private pages and access codes
- Edit the readable page in `src/protected/` (the System Page is generated
  from `tools/sp_template.html` with `--sp`).
- Codes live in `tools/access-codes.json`, one per page.
- The build encrypts each page with its code (AES-256-GCM, PBKDF2 key) and
  writes a small locked page to the site root. No code is ever shipped.
- 4-character codes submit as soon as they're typed; longer codes submit
  with Enter. Longer codes are much harder to guess.

## Translations (English, French, Italian)
- English is written in the pages as normal. The build tags every piece of
  text and gives each page its French and Italian versions.
- Translations live in `tools/i18n/fr.json` and `tools/i18n/it.json` as
  `"English": "translation"` pairs. Change a translation there, run the build.
- If English text is added or changed, the build lists what still needs
  translating in `tools/i18n/missing.json` (that page shows English until then).
- `translate="no"` on an element keeps it as written (the YVIS HAUSEN wordmark).
- The visitor's choice is remembered on their device (`yh_lang`); on a first
  visit, a French or Italian browser opens the site in that language.
- Private-page translations are encrypted with the page, so they stay private.
