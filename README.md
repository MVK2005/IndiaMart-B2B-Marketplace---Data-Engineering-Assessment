# IndiaMART B2B Marketplace — Data Engineering Assessment

End-to-end data engineering pipeline that scrapes product/supplier data from IndiaMART, transforms it through an ETL pipeline, and produces exploratory data analysis with visualisations.

## Project Structure

```
├── main.py                  # CLI entry-point for all pipeline stages
├── requirements.txt         # Python dependencies
├── src/
│   ├── config.py            # Central configuration (URLs, delays, paths)
│   ├── http_client.py       # Resilient HTTP client (retries, rate-limit, UA rotation)
│   ├── parser.py            # HTML parser for IndiaMART search pages
│   ├── scraper.py           # Crawl orchestrator (categories × pages)
│   ├── etl.py               # ETL pipeline (load → clean → save)
│   └── sample_data.py       # Realistic sample data generator (offline fallback)
├── data/
│   ├── raw/                 # Raw scraped JSON files
│   └── processed/           # Cleaned CSV + JSON
└── notebooks/
    └── eda.ipynb            # Exploratory Data Analysis notebook
```

## Quick Start

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Run the pipeline

**Option A — Full offline pipeline** (sample data + ETL):
```bash
python main.py all
```

**Option B — Live scraping + ETL**:
```bash
python main.py scrape-all
```

**Individual stages**:
```bash
python main.py scrape      # Live scrape only
python main.py sample      # Generate sample data only
python main.py etl         # Run ETL on latest raw data
```

### 3. Run the EDA notebook

```bash
cd notebooks
jupyter notebook eda.ipynb
```

The notebook auto-detects processed data. If none exists, it runs the full pipeline inline.

## Part A — Data Collection

### Approach

- **Target**: IndiaMART search results across 3 product categories:
  - Industrial Machinery
  - Electronics & Components
  - Textiles & Fabrics
- **Method**: Custom Python web crawler using `requests` + `BeautifulSoup`
- **Anti-blocking measures**:
  - Randomised delays between requests (2–5 s)
  - Rotating User-Agent headers via `fake-useragent`
  - Exponential back-off on 429/5xx responses
  - Configurable retry limits and timeouts
- **Offline fallback**: A sample data generator produces realistic records mirroring the actual scrape schema, enabling full pipeline testing without network access.

### Data Schema

Each record contains:

| Field | Description |
|-------|-------------|
| `product_name` | Product listing title |
| `supplier_name` | Company / supplier name |
| `description` | Product description snippet |
| `product_url` | Link to full listing |
| `location` | Raw location string |
| `category` | Product category |
| `price_raw` | Original price text |
| `price_min` | Parsed minimum price (₹) |
| `price_max` | Parsed maximum price (₹) |
| `price_unit` | Price unit (Piece, Kg, Meter, etc.) |

### ETL Pipeline

The ETL stage (`src/etl.py`):
1. **Loads** the latest raw JSON from `data/raw/`
2. **Deduplicates** on (product_name, supplier_name, product_url)
3. **Parses** price strings into numeric min/max values
4. **Normalises** locations into city + state columns
5. **Adds** quality flags (`has_price`, `has_location`)
6. **Outputs** cleaned CSV + JSON to `data/processed/`

## Part B — Exploratory Data Analysis

The Jupyter notebook (`notebooks/eda.ipynb`) covers:

1. **Dataset overview** — shape, types, missing values
2. **Category distribution** — bar + pie charts
3. **Price analysis** — histograms, box-plots, unit breakdown
4. **Regional insights** — top cities/states, category mix by state, median price by state
5. **Supplier analysis** — top suppliers, diversity per category
6. **Product keyword analysis** — word clouds, top keywords by category
7. **Data quality assessment** — completeness heatmap, outlier detection (IQR)
8. **Cross-category insights** — price range prevalence, state × category heatmap
9. **Key findings & hypotheses**

## Tech Stack

| Component | Library |
|-----------|---------|
| HTTP | `requests`, `fake-useragent` |
| Parsing | `beautifulsoup4`, `lxml` |
| Data | `pandas`, `numpy` |
| Visualisation | `matplotlib`, `seaborn`, `wordcloud`, `plotly` |
| Notebook | `jupyter` |
