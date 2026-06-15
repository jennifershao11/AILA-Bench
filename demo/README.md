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

The repo includes `.github/workflows/deploy-demo.yml`.

After pushing to GitHub:

1. Repo → **Settings** → **Pages**
2. **Build and deployment** → Source: **GitHub Actions** (not “Deploy from a branch”)
3. Push to `main` — workflow builds `demo/` and deploys

If **build** succeeds but **deploy** fails, check that step 2 is set to GitHub Actions, then re-run the workflow from the Actions tab.

Live URL: `https://<username>.github.io/<repo-name>/`

If you rename the repo, no config change is needed — CI sets `VITE_BASE_PATH` from the repo name automatically.
