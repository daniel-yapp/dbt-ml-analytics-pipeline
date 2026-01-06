# Deployment Guide

This guide covers deploying the E-Commerce Analytics Dashboard to Streamlit Cloud for your portfolio.

## Quick Start (Recommended for Portfolio)

The app is designed to work immediately with a pre-built database for the best visitor experience.

### 1. Build the Database Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Download data from Kaggle and load into DuckDB
python scripts/download_and_load_data.py

# Build dbt models
cd dbt
dbt run --profiles-dir . --project-dir ecommerce_analytics
dbt test --profiles-dir . --project-dir ecommerce_analytics
cd ..
```

This creates `ecommerce.duckdb` (~80MB) with all analytics models built.

### 2. Commit to GitHub

The database file is **allowed in Git** (see `.gitignore` exception):

```bash
git add ecommerce.duckdb
git commit -m "Add pre-built database for instant portfolio access"
git push
```

### 3. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file: `app.py`
4. (Optional) Add Kaggle credentials in Secrets:
   ```toml
   [kaggle]
   api_token = "your_kaggle_token_here"
   ```
5. Deploy!

**Result:** Visitors see the dashboard **instantly** - no waiting for data downloads!

---

## Architecture Options

### Option 1: Pre-Built Database (Recommended)

**Pros:**
- ✅ Instant access for visitors
- ✅ Professional UX
- ✅ No Kaggle API calls on every visit
- ✅ Showcases the finished product

**Cons:**
- ⚠️ 80MB in Git (acceptable for modern Git)
- ⚠️ Data is static (from 2016-2018 anyway)

**Best for:** Portfolio projects, demos, showcasing skills

### Option 2: Build on First Visit

**Pros:**
- ✅ Smaller Git repo
- ✅ Always fresh data

**Cons:**
- ❌ First visitor waits 5-10 minutes
- ❌ Uses Kaggle API on every cold start
- ❌ May timeout on Streamlit Cloud
- ❌ Most visitors will bounce

**Best for:** Internal tools, personal use

---

## Streamlit Cloud Configuration

### Required Files

```
.
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── ecommerce.duckdb         # Pre-built database
└── .streamlit/
    └── secrets.toml.example # Template (DO NOT commit actual secrets)
```

### Streamlit Secrets (Optional)

If you want to enable the "Refresh Data" feature on Streamlit Cloud:

1. In Streamlit Cloud dashboard, go to **App settings > Secrets**
2. Add your Kaggle credentials:
   ```toml
   [kaggle]
   api_token = "your_kaggle_api_token"
   ```

**Note:** This is **optional** - the app works perfectly without it using the pre-built database.

---

## Local Development

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd dbt-ml-analytics-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Kaggle credentials (for data refresh)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Kaggle API token
```

### Run Locally

```bash
# Option 1: Use existing database (instant)
streamlit run app.py

# Option 2: Rebuild from scratch
python scripts/download_and_load_data.py
cd dbt && dbt build --profiles-dir . --project-dir ecommerce_analytics
streamlit run app.py
```

---

## Database Size Considerations

The `ecommerce.duckdb` file is ~80MB:
- **Raw data:** ~40MB (9 CSV files)
- **dbt models:** ~40MB (staging + intermediate + marts)

### Is 80MB too big for Git?

**No!** Modern Git handles this fine:
- GitHub limit: 100MB per file (we're under)
- Git LFS: Not needed for single 80MB file
- Clone time: Adds ~10 seconds on fast connection

### Alternative: Use Git LFS (Optional)

If you prefer Git LFS:

```bash
# Install Git LFS
git lfs install

# Track database files
git lfs track "*.duckdb"

# Commit
git add .gitattributes ecommerce.duckdb
git commit -m "Add database with LFS"
```

---

## CI/CD (Optional)

### GitHub Actions Workflow

Create `.github/workflows/dbt.yml`:

```yaml
name: dbt CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: dbt compile
        run: |
          cd dbt
          dbt compile --profiles-dir . --project-dir ecommerce_analytics

      - name: dbt test (if database exists)
        if: hashFiles('ecommerce.duckdb') != ''
        run: |
          cd dbt
          dbt test --profiles-dir . --project-dir ecommerce_analytics
```

---

## Troubleshooting

### App loads slowly on Streamlit Cloud

**Cause:** Database not found, trying to download from Kaggle
**Fix:** Ensure `ecommerce.duckdb` is committed to Git

### "Database not found" error

**Check:**
1. `ecommerce.duckdb` exists in repository
2. `.gitignore` has exception: `!ecommerce.duckdb`
3. File was pushed to GitHub: `git ls-files ecommerce.duckdb`

### dbt models not showing in dashboard

**Cause:** Database has raw data but marts not built
**Fix:** Run `dbt build` locally and commit updated database

---

## Performance Tips

### Streamlit Cloud

- Pre-built database ensures instant load times
- Dashboard queries are fast (DuckDB is optimized for analytics)
- No external API calls needed for viewing

### Local Development

- Use `read_only=True` for dashboard queries (prevents locks)
- DuckDB `.wal` files are gitignored (temporary)

---

## Security Notes

### Secrets

- **DO commit:** `ecommerce.duckdb` (public dataset)
- **DO commit:** `.streamlit/secrets.toml.example` (template)
- **DON'T commit:** `.streamlit/secrets.toml` (actual credentials)
- **DON'T commit:** `kaggle.json` (API credentials)

### Kaggle API Token

Only needed for "Refresh Data" feature. Visitors can use the dashboard without it.

---

## Summary

**For portfolio deployment:**

1. ✅ Build database locally
2. ✅ Commit to Git (it's fine!)
3. ✅ Deploy to Streamlit Cloud
4. ✅ Visitors get instant access

**Optional:** Add Kaggle credentials to enable data refresh demo.
