# AILA-Bench Demo Site

Static preview for the paper demo UI. Metrics use honest placeholders (`xxx`) until human-study data is available.

## Local development

```bash
npm install
npm run dev -- --port 5190 --host 127.0.0.1
```

Open http://127.0.0.1:5190

## Build

```bash
# Netlify Drop / root hosting (base path /)
npm run build

# GitHub Pages project site (repo name must match path)
npm run build:pages
npm run preview:pages
```

Output: `dist/`

## Share UI without code (Netlify Drop)

1. `npm run build`
2. Open https://app.netlify.com/drop
3. Drag the `dist/` folder onto the page
4. Share the generated `*.netlify.app` URL

Rebuild and re-upload when the UI changes.

## GitHub Pages (automatic)

**One-time setup (required before the first deploy):**

1. Open **Settings → Pages**:  
   https://github.com/jennifershao11/AILA-Bench/settings/pages
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Save — this enables Pages for the repo

Then push to `main` (or re-run the workflow from the Actions tab).

Live URL: `https://jennifershao11.github.io/AILA-Bench/`

If **build** passes but **deploy** fails, Pages is almost always not enabled yet — repeat step 2 above.
