# gmailanalyzer
python code for webscrapping and gmail analysis 
# 📧📚 Data Mining Case Studies
### Gmail Mailbox Analyzer + Books Web Scraper

> Two beginner-friendly Python projects that demonstrate real-world **data collection**, **text analysis**, **categorization**, and **visualization** — one mining your Gmail inbox, one crawling a live website.

---

## 📁 Repository Structure

```
gmail-books-scraper/
│
├── 📂 gmail_analyzer/
│   ├── gmail_analyzer_api_1.py     # Main Gmail analyzer script
│   ├── credentials.json            # ⚠️ Your own — DO NOT share (gitignored)
│   ├── token.json                  # ⚠️ Auto-generated — DO NOT share (gitignored)
│   └── top_contacts.png            # Output: bar chart of top senders
│
├── 📂 books_scraper/
│   ├── books_scraper.py            # Main books scraper script
│   ├── books_data.csv              # Output: all 1000 books scraped
│   └── books_analysis.png          # Output: 4-panel dashboard chart
│
├── .gitignore                      # Hides credentials & token files
└── README.md                       # This file
```

---

## 🔹 Project 1 — Gmail Mailbox Analyzer

### 📌 Overview
A Python script that connects to your Gmail inbox using the **Gmail API (OAuth2)** and performs a full data mining analysis — just like a web crawler, but for emails.

### 🕷️ How It Crawls
Just like a web crawler visits URLs one by one, this script **crawls emails one by one**:
1. Authenticates via OAuth2
2. Fetches message IDs (like a list of URLs)
3. Visits each message and extracts data (like scraping a page)
4. Stores everything in a Pandas DataFrame for analysis

### 📊 Analysis Parts

| Part | Description |
|------|-------------|
| **Part 1** | Load & parse emails via Gmail API — extract sender, subject, body, date |
| **Part 2** | Count sender frequency — display top 5 most contacted people |
| **Part 3** | Extract keywords from subjects/bodies — remove stopwords — show top topics |
| **Part 4** | Categorize emails → Spam / Newsletter / Personal |
| **Part 5** | Insights: most active contact, top topic, activity by time of day |
| **Bonus** | Matplotlib horizontal bar chart of top 5 senders |

### 🛠️ Tech Stack
```
Python 3.x
├── google-auth                 # OAuth2 authentication
├── google-auth-oauthlib        # OAuth flow (browser login)
├── google-api-python-client    # Gmail API client
├── pandas                      # Data analysis
├── matplotlib                  # Charts
├── collections.Counter         # Frequency counting
└── re                          # Text cleaning
```

### ⚙️ Setup & Run

**1. Install dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pandas matplotlib
```

**2. Get Gmail API credentials:**
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create a project → Enable Gmail API
- Create OAuth credentials (Desktop app) → Download `credentials.json`
- Add your email as a Test User in OAuth consent screen

**3. Run:**
```bash
cd gmail_analyzer
python gmail_analyzer_api_1.py
```
A browser window opens → log in → allow access → analysis runs automatically.

### 📤 Sample Output
```
══════════════════════════════════════════════════════
   📧 GMAIL MAILBOX ANALYZER — Live Gmail API Edition
══════════════════════════════════════════════════════

✅ Authenticated successfully!

📡 Fetching emails (query: 'in:inbox OR in:sent')...
   Crawling batch of 100 emails...
✅ Fetched 200 emails total.

══════════════════════════════════════════════════════
👥 PART 2: CONTACT ANALYSIS — Top 5 Senders
══════════════════════════════════════════════════════

  Rank   Sender                                Emails
  ──────────────────────────────────────────────────
  #1     notifications@github.com              42
  #2     noreply@medium.com                    31
  #3     support@coursera.org                  18
  #4     hello@leetcode.com                    15
  #5     team@notion.so                        12

══════════════════════════════════════════════════════
📂 PART 4: EMAIL CATEGORIZATION
══════════════════════════════════════════════════════

  Category       Count     Percentage
  ────────────────────────────────────
  Personal       124       62.0%  ████████████████████
  Newsletter      51       25.5%  ████████
  Spam            25       12.5%  ████
```

---

## 🔹 Project 2 — Books.toscrape.com Web Scraper

### 📌 Overview
A Python web scraper that crawls all **50 pages** of [books.toscrape.com](https://books.toscrape.com), extracts data on all **1000 books**, and performs a complete analysis.

### 🕷️ How It Crawls
```
Homepage (page 1)
    ↓  scrape all books
    ↓  find "next →" button
Page 2
    ↓  scrape all books
    ↓  find "next →" button
...
Page 50
    ↓  scrape all books
    ↓  no "next →" button → STOP
```
This is exactly how **Google's web crawler** works — follow links, extract data, repeat.

### 📊 Analysis Parts

| Part | Description |
|------|-------------|
| **Part 1** | Crawl all 50 pages — extract title, price, rating, availability |
| **Part 2** | Star rating distribution (1★ to 5★) |
| **Part 3** | Most common keywords in book titles (after stopword removal) |
| **Part 4** | Price categorization → Budget / Mid-range / Premium |
| **Part 5** | Insights: avg price, top rated books, cheapest, most expensive |
| **Bonus** | 4-panel matplotlib dashboard (price histogram, ratings, keywords, pie) |

### 🛠️ Tech Stack
```
Python 3.x
├── requests                    # HTTP requests (fetch web pages)
├── beautifulsoup4              # HTML parsing (extract data from pages)
├── pandas                      # Data storage and analysis
├── matplotlib                  # 4-panel chart dashboard
├── collections.Counter         # Keyword frequency
└── re                          # Text cleaning
```

### ⚙️ Setup & Run

**1. Install dependencies:**
```bash
pip install requests beautifulsoup4 pandas matplotlib
```

**2. Run (no login needed — public website):**
```bash
cd books_scraper
python books_scraper.py
```

### 📤 Sample Output
```
══════════════════════════════════════════════════════
   📚 BOOKS TO SCRAPE — Web Scraper & Analyzer
══════════════════════════════════════════════════════

🕷️  Starting crawler on https://books.toscrape.com ...

   📄 Crawling page 1 ... (https://books.toscrape.com/)
   📄 Crawling page 2 ... (https://books.toscrape.com/catalogue/page-2.html)
   ...
   📄 Crawling page 50... (https://books.toscrape.com/catalogue/page-50.html)

✅ Crawl complete! Scraped 1000 books across 50 pages.

══════════════════════════════════════════════════════
💡 PART 5: KEY INSIGHTS
══════════════════════════════════════════════════════

  💰 Price Statistics:
     Average price     : £35.07
     Cheapest book     : £10.00
     Most expensive    : £59.99

  ⭐ Rating Statistics:
     Average rating    : 2.93 / 5.0
     Total 5-star books: 203

  📊 Category Breakdown:
     Budget    (< £20)    →  189 books
     Mid-range (£20–£40)  →  534 books
     Premium   (> £40)    →  277 books
```

---

## 🔄 Comparison: Gmail Crawler vs Web Crawler

| Feature | Gmail Analyzer | Books Scraper |
|---|---|---|
| Data source | Gmail inbox (API) | Website (HTTP) |
| Authentication | OAuth2 login | None (public site) |
| Iterator | Gmail message list | HTML "next page" link |
| Data extractor | `google-api-python-client` | `BeautifulSoup` |
| Output | Email insights + chart | CSV + 4-panel chart |
| Pages/items crawled | Up to 200 emails | 1000 books / 50 pages |

---

## 🚀 Quick Start (Both Projects)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/gmail-books-scraper.git
cd gmail-books-scraper

# Install all dependencies at once
pip install google-auth google-auth-oauthlib google-auth-httplib2 \
            google-api-python-client requests beautifulsoup4 pandas matplotlib

# Run Gmail analyzer
cd gmail_analyzer
python gmail_analyzer_api_1.py

# Run Books scraper
cd ../books_scraper
python books_scraper.py
```

---

## ⚠️ Important Notes

- **Never share** `credentials.json` or `token.json` — they give access to your Gmail
- Both files are listed in `.gitignore` so they won't be pushed to GitHub
- The Gmail analyzer requires a one-time browser login (OAuth)
- The books scraper needs no login — `books.toscrape.com` is a public practice site

---

## 👤 Author

**Zaid Noor** — `zaidnoor168@gmail.com`

---

## 📄 License

This project is for educational purposes. `books.toscrape.com` is a sandbox website specifically designed for scraping practice.
