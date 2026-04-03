# ShopClawMart Skills Scanner

Automated daily scan of [ShopClawMart](https://www.shopclawmart.com) for new/updated free downloadable skills.

## Quick Start

```bash
# Install dependency
pip install scrapling

# Quick scan
python scan_shopclawmart.py

# Deep scan (fetch individual listing pages for descriptions)
python scan_shopclawmart.py --deep

# Show only changes since last scan
python scan_shopclawmart.py --diff
```

## Output Files

- `current_listings.json` - All listings from last scan
- `prev_listings.json` - Listings from previous scan (for diff)
- `scan_log.md` - Markdown report with new/changed listings
- `scan_log.md` - Human-readable change report

## How It Works

1. Fetches `/listings` page using Scrapling Fetcher (HTTP-based SSR parsing)
2. Extracts listing data from article card HTML: slug, title, category, price, creator
3. Detects free items (no price badge = free, `$0` = free)
4. Compares against previous scan to find new/changed listings
5. Generates markdown report

## Technical Notes

**Findings (2026-04-03):**

| Method | Status | Notes |
|--------|--------|-------|
| curl + User-Agent | WORKS | Next.js SSR embeds all data in HTML |
| Scrapling Fetcher | WORKS | Same as curl, better Python API |
| Scrapling DynamicFetcher | FAILS | Playwright browser timeout on Windows |
| API `/api/v1/listings` | FAILS | Requires API key |
| Sitemap `/sitemap.xml` | Partial | Only main pages, no listing URLs |

**Architecture:** ShopClawMart uses Next.js with React Server Components (RSC). The listing data is embedded in `self.__next_f.push([N,"..."])` calls in the HTML, and also in the article card HTML directly.

**Pagination:** The `/listings` page initially shows ~11 listings. A "Load more" button reveals more (requires client-side JS). For daily scans of free items, page 1 coverage is typically sufficient.

## Current Free Skills (as of 2026-04-03)

1. YouTube Access for Agents (Research)
2. Agent Ops Playbook (Ops)
3. Twitter Growth Playbook by Shelly (Marketing, free for first 5)
4. AI Agent Quick Start Template (Persona)
5. Content Idea Generator (Marketing)
6. De-AI-ify (Marketing) ⚠️ We already have this locally
7. Forge — Staff Engineer + Release Captain (Persona)
8. Free Agent Upgrade Kit (Persona)
9. Token Optimizer (Ops) ⚠️ We already have this locally
10. 25 AI Prompts for Small Business by Shelly (Productivity, free for first 5)

**1 Paid listing:** Coding Agent Loops ($9, by Felix Craft)
