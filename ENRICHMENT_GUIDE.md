# Player photographs and match statistics

This release adds the presentation and validation hooks, but deliberately does **not** invent photographs, licenses, or match statistics. Until records are populated, player profiles display placeholders and match pages explain unavailable statistics.

## Add an approved Wikimedia Commons photo

Edit `player_photos.json` with a player slug (for example `david-villa`):

```json
{
  "david-villa": {
    "url": "https://upload.wikimedia.org/.../verified-image.jpg",
    "source_url": "https://commons.wikimedia.org/wiki/File:Verified_image.jpg",
    "credit": "Photographer name",
    "license": "CC BY-SA 4.0"
  }
}
```

These are illustrative placeholders, not real image links. Verify the image's identity, author, license, attribution requirements, and commercial reuse rights on its Commons file page before adding it. Some licenses require indicating modifications or other conditions.

## Add sourced match statistics

Edit `match_stats.json` with a match ID (matching the HTML filename without `.html`):

```json
{
  "spain-vs-netherlands-2010-07-11": {
    "source_name": "Verified match report publisher",
    "source_url": "https://example.org/verified-match-report",
    "possession": {"spain": 0, "opponent": 0},
    "shots": {"spain": 0, "opponent": 0}
  }
}
```

The numbers and URL above are examples ONLY; do not publish them as match statistics. Omit unverified fields entirely. `0` is a real zero and should only be used when verified. Supported fields: possession, shots, shots_on_target, corners, fouls.

Run `python3 build.py` then `python3 validate_site.py`. The generated `/docs` folder is the GitHub Pages output.

## Source candidates

* Wikimedia Commons image metadata: https://www.mediawiki.org/wiki/API:Imageinfo
* FIFA and UEFA match reports for official competition records
* StatsBomb open data for selected seasons only: https://github.com/hudl/open-data (check redistribution/attribution conditions)

2010 World Cup event data is **not assumed** to be present in StatsBomb's open-data release. Do not label source-derived stats as official unless they originate from the governing body's record.
