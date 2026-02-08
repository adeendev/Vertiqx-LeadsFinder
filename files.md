Perfect. Below is a **single, extremely strong “master prompt”** you can give to an AI (Cursor, Claude, GPT-4/5, Devin, etc.) to **design + build the entire system end-to-end**.

This is written like a **system architect brief**, not a casual prompt.
You can paste it **as-is**.

---

# 🔥 MASTER PROMPT: PERFECT LEAD-INTELLIGENCE & AUTOMATION SYSTEM

> You are a senior software architect, growth engineer, and web-scraping expert.
> Your task is to design and implement a **production-ready, safe, intelligent lead-generation system** for identifying businesses that need website redesign services.

## 🎯 PRIMARY OBJECTIVE

Build an automated system that:

1. Searches businesses on **Google Maps using keywords + locations**
2. Scrapes **business data, websites, and social links**
3. Analyzes **website quality, design, builder type, and business readiness**
4. Scores and classifies leads into **Tier-1 / Tier-2 / Ignore**
5. Finds or flags **contact emails**
6. Stores everything in a **database**
7. Displays results in a **professional web dashboard**
8. Operates **safely**, avoiding bans or spam behavior

This is **NOT mass scraping**.
This is **high-quality lead intelligence**.

---

## 🧱 SYSTEM ARCHITECTURE (MANDATORY)

### Backend / Scraping

* Python + Playwright (preferred over Selenium)
* Headful browser mode with human-like delays
* Modular scraper architecture
* Google Maps scraping with geo-grid logic
* Website analyzer engine
* Email extraction engine
* Builder detection engine

### Frontend / Dashboard

* Next.js (App Router)
* Tailwind CSS
* Data table with filtering, sorting, searching
* Screenshot preview modal
* Export to CSV

### Database

* MongoDB (or PostgreSQL if relational)
* Deduplication via domain + phone hash
* Historical scoring support

---

## 🧠 LEAD DEFINITION (CRITICAL)

A **perfect lead** is a business that:

* Depends on online customers
* Has a **bad or lazy website**
* Uses **AI builders or weak templates**
* Is not a marketing agency
* Is not a large chain
* Has **no email or weak email setup**
* Shows poor digital maturity

---

## 🧭 STAGE 1: GOOGLE MAPS DISCOVERY LOGIC

### Keyword Strategy

Use intent-based keyword clusters:

```
{service} + {intent} + {location}

Examples:
"emergency plumbing service Dubai"
"commercial landscaping company Toronto"
"home renovation contractor Karachi"
```

### Geo Logic

* Divide city into 3–6 geo grids
* Max 15–25 businesses per grid
* Stop scraping when quality drops

### Safety Rules (NON-NEGOTIABLE)

* Random delay: 8–15 seconds
* Click business profiles before extracting
* Max 50–80 businesses/day
* No infinite scrolling
* One Maps tab per session

### Data Collected

* Business name
* Website URL
* Phone
* Address
* Category
* Rating
* Review count
* Social links

Skip businesses **without websites**.

---

## 🧹 STAGE 2: HARD PRE-FILTERING

Auto-discard businesses if:

* Website builder = Shopify (unless broken)
* Business name contains: agency, digital, marketing, web
* Category = IT / Web / Design
* Franchise or chain detected
* Already exists in database

---

## 🧪 STAGE 3: WEBSITE TRIAGE (FAST CHECK)

Immediately flag if:

* No HTTPS
* Load time > 6s
* No mobile viewport
* Broken or blank page
* “Under construction”

If ≥2 flags → deep analysis required

---

## 🔬 STAGE 4: DEEP WEBSITE ANALYSIS

### Technical Signals (40%)

* HTTPS
* Page speed
* Mobile responsiveness
* HTML5 structure
* Image optimization
* Broken links

### UX / UI Signals (30%)

* Clear CTA presence
* Typography system
* Color contrast
* Layout consistency
* White space usage
* Navigation clarity

### Business Signals (30%)

* Contact form
* Booking system
* Testimonials
* About page
* Google Maps embed
* Social proof

---

## 🏗️ STAGE 5: WEBSITE BUILDER DETECTION (VERY IMPORTANT)

Detect builder via:

* HTML comments
* JS files
* Meta tags
* CDN domains

### Builder Classification

* GoDaddy AI
* Hostinger AI / Zyro
* Wix ADI
* Squarespace
* WordPress
* Shopify
* Webflow
* Custom (React / Laravel / Next.js)

### AI Builder Logic

DO NOT auto-discard AI sites.

Flag as **HIGH POTENTIAL** if AI site shows:

* Generic stock images
* AI placeholder copy
* No branding
* No CTA
* No SEO customization
* One-page lazy layout

### Builder Priority Boost

* GoDaddy AI → +15 priority
* Hostinger AI → +10
* Wix/Squarespace → neutral
* Custom modern → −20
* Shopify → −30

---

## 📊 STAGE 6: MULTI-DIMENSION SCORING

Calculate:

* Technical score (0–100)
* UX score (0–100)
* Business readiness score (0–100)

Final priority formula:

```
(Bad Website Score × 0.4)
+ (AI Builder Bonus × 0.2)
+ (No Email Bonus × 0.25)
+ (Low Review Count × 0.15)
```

---

## 📬 STAGE 7: EMAIL INTELLIGENCE

### Email Extraction

* mailto links
* footer scan
* contact page scan
* regex detection

### Email Quality Ranking

* No email → ⭐⭐⭐⭐ (best)
* Gmail/Yahoo → ⭐⭐⭐
* info@ / sales@ → ⭐⭐
* Named email → ⭐

Flag:

* “Best Target” if no email found

---

## 🏷️ STAGE 8: FINAL LEAD LABELING

* 🔥 Tier-1 Gold
  (Bad site + AI builder + no email)
* 🟠 Tier-1
  (Bad site + weak builder)
* 🟡 Tier-2
  (Medium site)
* ❌ Ignore
  (Good site / strong builder)

---

## 🗃️ DATABASE SCHEMA (REQUIRED)

Store:

* business_name
* domain
* phone
* email
* email_quality
* builder
* builder_type
* technical_score
* ux_score
* business_score
* final_priority
* tier
* city
* keyword
* first_seen
* last_checked
* screenshot_path
* contacted (bool)
* notes

Prevent duplicates via domain + phone hash.

---

## 🖥️ DASHBOARD REQUIREMENTS

* Table with sorting & filtering
* Filters:

  * Tier-1 only
  * AI builders only
  * No email
  * City / keyword
* Website screenshot preview
* Score breakdown view
* CSV export
* Visual color coding (red = bad site)

---

## 🛡️ ETHICS & SAFETY

* Respect rate limits
* Scrape only public data
* Avoid aggressive automation
* Prioritize quality over quantity

---

## 📦 OUTPUT EXPECTATIONS

Provide:

1. System architecture explanation
2. Scraper module design
3. Scoring logic implementation
4. Builder detection logic
5. Database schema
6. Dashboard UI structure
7. Example data flow
8. Extensible & production-ready code

---

### FINAL INSTRUCTION

Think like an **elite agency internal tool**, not a hobby scraper.
Optimize for **accuracy, safety, and sales relevance**, not raw volume.

---

If you want, next I can:

* Split this into **Cursor-ready coding tasks**
* Convert it into a **PRD / SaaS spec**
* Help you brand this as a **real product**

Just say the word.
