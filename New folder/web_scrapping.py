"""
📚 Books to Scrape — Web Scraper & Analyzer
============================================
Website : https://books.toscrape.com
Purpose : Scrape all books across all pages, then analyze the data

PARTS COVERED:
  1. Data Collection  — crawl all pages, extract book details
  2. Contact Analysis — top genres/categories by book count
  3. Topic ID         — most common words in book titles
  4. Categorization   — price buckets (Budget / Mid-range / Premium)
  5. Insights         — top category, avg price, highest rated, cheapest
  BONUS               — matplotlib charts

HOW IT ACTS LIKE A "CRAWLER":
  Just like the Gmail analyzer crawled emails one by one,
  this script crawls web pages one by one:
    1. Start at the homepage (page 1)
    2. Extract all book data from that page (scrape)
    3. Find the "next page" link and follow it
    4. Repeat until no more pages exist
  This is exactly how Google's web crawler works!
"""

import requests                          # Fetch web pages (HTTP requests)
from bs4 import BeautifulSoup           # Parse HTML (like reading the page)
import pandas as pd                      # Store and analyze data
import matplotlib.pyplot as plt          # Charts
import re                                # Text cleaning
from collections import Counter          # Count frequencies
import time                              # Polite delay between requests



BASE_URL    = "https://books.toscrape.com/"
CATALOGUE   = "https://books.toscrape.com/catalogue/"
DELAY       = 0.5    # Seconds to wait between page requests (be polite!)
MAX_PAGES   = 50     # Site has 50 pages total (1000 books)

# Stopwords for title keyword analysis
STOPWORDS = {
    "the","a","an","and","of","in","to","for","is","on","with","at",
    "by","from","or","as","it","its","be","this","that","are","was",
    "were","but","not","have","has","had","do","did","my","your","his",
    "her","our","their","we","i","you","he","she","they","me","him",
    "us","them","what","which","who","how","when","where","than","into",
    "so","if","up","out","no","more","than","then","about","after",
    "before","between","through","during","very","just","over","new"
}




def get_page(url):
    """
    Fetch a single web page and return a BeautifulSoup object.
    BeautifulSoup parses the raw HTML so we can easily extract data.
    """
    headers = {"User-Agent": "Mozilla/5.0 (BookScraper/1.0)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"   ⚠️  Failed to fetch {url}: {e}")
        return None


def parse_rating(word):
    """Convert word rating (e.g. 'Three') to number (3)."""
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return ratings.get(word, 0)


def scrape_books():
    """
    🕷️ THE MAIN CRAWLER FUNCTION

    Visits every page of books.toscrape.com and extracts:
      - Title, Price, Rating, Availability, Category URL

    Crawl logic:
      page 1 → scrape → follow "next" → page 2 → scrape → ... → page 50
    """
    print("\n" + "═" * 60)
    print("   📚 BOOKS TO SCRAPE — Web Scraper & Analyzer")
    print("═" * 60)
    print("\n🕷️  Starting crawler on https://books.toscrape.com ...\n")

    all_books = []
    url = BASE_URL
    page_num = 1

    while url and page_num <= MAX_PAGES:
        print(f"   📄 Crawling page {page_num}... ({url})")
        soup = get_page(url)

        if not soup:
            break

        # Find all book cards on the page
        # Each book is inside an <article class="product_pod"> tag
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            try:
                # --- Title ---
                # Stored in the 'title' attribute of the <a> tag
                title = book.find("h3").find("a")["title"]

                # --- Price ---
                # Inside <p class="price_color">, strip the £ symbol
                price_text = book.find("p", class_="price_color").text.strip()
                price = float(re.sub(r'[^\d.]', '', price_text))

                # --- Rating ---
                # The star rating is a CSS class: "One", "Two", etc.
                rating_word = book.find("p", class_="star-rating")["class"][1]
                rating = parse_rating(rating_word)

                # --- Availability ---
                availability = book.find("p", class_="availability").text.strip()

                all_books.append({
                    "title":        title,
                    "price":        price,
                    "rating":       rating,
                    "availability": availability,
                })

            except Exception:
                continue  # Skip any malformed book entry

        # --- Follow "next" link (this is how crawlers move page to page) ---
        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_href = next_btn.find("a")["href"]
            # Handle relative URLs
            if page_num == 1:
                url = CATALOGUE + next_href
            else:
                url = CATALOGUE + next_href
        else:
            url = None  # No more pages — stop crawling

        page_num += 1
        time.sleep(DELAY)  # Be polite — don't hammer the server

    df = pd.DataFrame(all_books)
    print(f"\n✅ Crawl complete! Scraped {len(df)} books across {page_num-1} pages.\n")
    return df




def analyze_ratings(df):
    """Show distribution of star ratings — like contact frequency analysis."""
    print("=" * 60)
    print("⭐ PART 2: RATING ANALYSIS — Distribution of Star Ratings")
    print("=" * 60)

    rating_labels = {1: "★☆☆☆☆ One", 2: "★★☆☆☆ Two",
                     3: "★★★☆☆ Three", 4: "★★★★☆ Four", 5: "★★★★★ Five"}
    counts = df["rating"].value_counts().sort_index(ascending=False)

    print(f"\n  {'Rating':<18} {'Count':<8} Bar")
    print("  " + "-" * 50)
    max_c = counts.max()
    for rating, count in counts.items():
        label = rating_labels.get(rating, str(rating))
        bar = "█" * int(count / max_c * 25)
        print(f"  {label:<18} {count:<8} {bar}")
    print()


def analyze_topics(df):
    """Extract most common words from book titles."""
    print("=" * 60)
    print("🔍 PART 3: TOPIC IDENTIFICATION — Top Title Keywords")
    print("=" * 60)

    all_text = " ".join(df["title"].fillna("")).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_text)
    filtered = [w for w in words if w not in STOPWORDS]
    top15 = Counter(filtered).most_common(15)

    print(f"\n  {'Rank':<6} {'Keyword':<22} {'Frequency'}")
    print("  " + "-" * 40)
    for i, (word, count) in enumerate(top15, 1):
        print(f"  #{i:<5} {word:<22} {count}")
    print()

    return top15




def categorize_books(df):
    """
    Categorize books by price into Budget / Mid-range / Premium.
    (Same idea as email categorization — rule-based classification)
    """
    print("=" * 60)
    print("📂 PART 4: CATEGORIZATION — Price Buckets")
    print("=" * 60)

    def price_category(price):
        if price < 20:    return "Budget      (< £20)"
        elif price < 40:  return "Mid-range   (£20–£40)"
        else:             return "Premium     (> £40)"

    df["category"] = df["price"].apply(price_category)
    counts = df["category"].value_counts()
    total  = len(df)

    print(f"\n  {'Category':<24} {'Count':<8} {'%':<8} Bar")
    print("  " + "-" * 58)
    for cat, count in counts.items():
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {cat:<24} {count:<8} {pct:.1f}%   {bar}")
    print()

    return df




def show_insights(df, top_keywords):
    """Show the most interesting findings from the data."""
    print("=" * 60)
    print("💡 PART 5: KEY INSIGHTS")
    print("=" * 60)

    avg_price    = df["price"].mean()
    min_price    = df["price"].min()
    max_price    = df["price"].max()
    avg_rating   = df["rating"].mean()
    top_rated    = df[df["rating"] == 5]["title"].head(3).tolist()
    cheapest     = df.nsmallest(3, "price")[["title","price"]].values.tolist()
    most_exp     = df.nlargest(3, "price")[["title","price"]].values.tolist()
    top_word     = top_keywords[0][0] if top_keywords else "—"

    print(f"""
  💰 Price Statistics:
     Average price     : £{avg_price:.2f}
     Cheapest book     : £{min_price:.2f}
     Most expensive    : £{max_price:.2f}

  ⭐ Rating Statistics:
     Average rating    : {avg_rating:.2f} / 5.0
     Total 5-star books: {len(df[df['rating']==5])}

  🏆 Top 3 Highest Rated Books (5 Stars):""")

    for title in top_rated:
        print(f"     • {title}")

    print(f"""
  💸 Top 3 Cheapest Books:""")
    for title, price in cheapest:
        print(f"     • £{price:.2f}  —  {title[:50]}")

    print(f"""
  💎 Top 3 Most Expensive Books:""")
    for title, price in most_exp:
        print(f"     • £{price:.2f}  —  {title[:50]}")

    print(f"""
  🔑 Most Common Title Keyword : '{top_word}'

  📊 Category Breakdown:""")
    for cat, count in df["category"].value_counts().items():
        print(f"     {cat}  →  {count} books")

    print()



def plot_charts(df, top_keywords):
    """Generate 4 charts: price dist, rating dist, top keywords, category split."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("📚 Books to Scrape — Analysis Dashboard",
                 fontsize=16, fontweight="bold", y=1.01)

    colors = ["#4C72B0","#55A868","#C44E52","#8172B2","#CCB974"]

    # --- Chart 1: Price Distribution (histogram) ---
    ax1 = axes[0, 0]
    ax1.hist(df["price"], bins=20, color="#4C72B0", edgecolor="white", alpha=0.85)
    ax1.set_title("Price Distribution", fontweight="bold")
    ax1.set_xlabel("Price (£)")
    ax1.set_ylabel("Number of Books")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Chart 2: Rating Distribution (bar chart) ---
    ax2 = axes[0, 1]
    rating_counts = df["rating"].value_counts().sort_index()
    bars = ax2.bar(rating_counts.index, rating_counts.values,
                   color=colors[:len(rating_counts)], edgecolor="white")
    ax2.set_title("Star Rating Distribution", fontweight="bold")
    ax2.set_xlabel("Star Rating")
    ax2.set_ylabel("Number of Books")
    ax2.set_xticks([1,2,3,4,5])
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    for bar in bars:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 str(int(bar.get_height())), ha="center", fontsize=9)

    # --- Chart 3: Top 10 Keywords (horizontal bar) ---
    ax3 = axes[1, 0]
    words  = [w for w, _ in top_keywords[:10]]
    counts = [c for _, c in top_keywords[:10]]
    ax3.barh(words[::-1], counts[::-1], color="#55A868", edgecolor="white")
    ax3.set_title("Top 10 Title Keywords", fontweight="bold")
    ax3.set_xlabel("Frequency")
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    # --- Chart 4: Price Category Pie Chart ---
    ax4 = axes[1, 1]
    cat_counts = df["category"].value_counts()
    ax4.pie(cat_counts.values, labels=cat_counts.index,
            colors=colors[:len(cat_counts)], autopct="%1.1f%%",
            startangle=140, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax4.set_title("Price Category Split", fontweight="bold")

    plt.tight_layout()
    plt.savefig("books_analysis.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("  📊 Chart saved as books_analysis.png\n")


def main():
    # PART 1: Crawl all books
    df = scrape_books()

    if df.empty:
        print("⚠️  No data scraped. Check your internet connection.")
        return

    # Save raw data to CSV
    df.to_csv("books_data.csv", index=False)
    print("💾 Raw data saved to books_data.csv\n")

    # PART 2: Rating analysis
    analyze_ratings(df)

    # PART 3: Topic identification
    top_kw = analyze_topics(df)

    # PART 4: Price categorization
    df = categorize_books(df)

    # PART 5: Insights
    show_insights(df, top_kw)

    # BONUS: Charts
    print("=" * 60)
    print("📊 BONUS: Generating analysis dashboard...")
    print("=" * 60)
    plot_charts(df, top_kw)

    print("✅ All done!")
    print("═" * 60)
    print("   Output files:")
    print("   • books_data.csv      ← all scraped book data")
    print("   • books_analysis.png  ← 4-chart dashboard")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()