# Gabifit — DR Fitness Market Intelligence

Competitive intelligence dashboard for the Dominican Republic fitness coaching market.
Scrapes Instagram, TikTok, and coach websites via Apify and presents insights in a Streamlit dashboard.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your Apify token

```bash
cp .env.example .env
# Edit .env and set APIFY_TOKEN=apify_api_xxx
# Get your token at: https://console.apify.com/account/integrations
```

### 3. Add coaches to the seed list

Edit `seeds/coach_usernames.py` and add Dominican Republic fitness coaches:
- Search Instagram/TikTok for: `#fitnessrd`, `#coachrd`, `#nutricionrd`, `#entrenadorrd`
- Target 20–40 coaches for a solid dataset

```python
COACHES = [
    {
        "name": "Coach Name",
        "instagram": "ig_username",     # without @
        "tiktok": "tt_username",        # without @, or None
        "website": "https://...",       # or None
    },
    ...
]
```

## Running the Pipeline

### Step 1: Collect data (calls Apify APIs)

```bash
python run_collection.py
```

Options:
```bash
python run_collection.py --skip tiktok     # skip TikTok
python run_collection.py --only instagram  # only Instagram
```

### Step 2: Process data

```bash
python run_processing.py
```

### Step 3: Launch dashboard

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
├── seeds/              # Curated list of DR fitness coaches
├── collectors/         # Apify scrapers (Instagram, TikTok, websites)
├── processors/         # Data cleaning and transformation
├── dashboard/          # Streamlit dashboard
│   ├── app.py          # Home page
│   ├── pages/          # 4 analytics sections
│   └── components/     # Shared charts, filters, data loaders
├── data/
│   ├── raw/            # Raw Apify JSON output
│   └── processed/      # Cleaned CSVs for dashboard
├── run_collection.py   # Master collection script
└── run_processing.py   # Master processing script
```

## Dashboard Sections

| Page | What it shows |
|---|---|
| 💰 Pricing | Price ranges, avg online vs in-person, distribution by service type |
| 📱 Social Media | Followers, engagement rates, platform breakdown |
| 🛎️ Services | Which services each coach offers, market gaps, lead magnets |
| 🔗 Funnels | CTA channels, Sankey flow diagram, funnel sophistication scores |
