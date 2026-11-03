# LaRojaFan.com
1. Edit config.json: amazon_tag, adsense_id (when approved), kit_uid + kit_src (Kit form embed).
2. Push this folder to a GitHub repo. Host the /docs folder (GitHub Pages, or Cloudflare Pages / Netlify with output dir `docs`).
3. The included GitHub Action refreshes results daily and rebuilds, so every new Spain match gets a page automatically.
4. Highlights: add "YYYY-MM-DD-opponent": "YOUTUBE_VIDEO_ID" to highlights.json (example key: 2026-07-19-argentina). Use official FIFA/UEFA/RFEF channel videos, embed only.
Local build: python3 build.py
