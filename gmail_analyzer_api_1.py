"""
📧 Gmail Mailbox Analyzer — Using Gmail API (OAuth2)
=====================================================
Run this in VS Code after completing the setup steps in SETUP.md

PARTS COVERED:
  1. Data Collection  — fetch emails via Gmail API
  2. Contact Analysis — top 5 senders
  3. Topic ID         — common keywords
  4. Categorization   — Spam / Newsletter / Personal
  5. Insights         — top contact, topic, time of day
  BONUS               — matplotlib bar chart
"""

import os
import re
import base64
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ─────────────────────────────────────────────────────────────
# ⚙️  CONFIG
# ─────────────────────────────────────────────────────────────

# Scopes: read-only access to Gmail is enough for this analysis
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# How many emails to fetch per query (max 500 total recommended)
MAX_EMAILS = 200

# Stopwords to exclude from keyword analysis
STOPWORDS = {
    "the","and","is","in","it","of","to","a","an","for","on","with","this",
    "that","are","was","be","have","has","you","your","we","our","i","my",
    "me","from","at","or","not","but","do","will","can","if","about","re",
    "fw","hi","hello","dear","please","thank","thanks","just","would","could",
    "should","so","no","more","new","get","all","up","out","as","by","into",
    "its","there","their","they","what","how","when","been","also","any",
    "he","she","via","fwd","nbsp","http","https","com","www","mail","email",
    "hey","get","us","am","pm","one","two","three","see","know","time","day"
}


# ─────────────────────────────────────────────────────────────
# 🔐 PART 0: AUTHENTICATION — Get Gmail API Access
# ─────────────────────────────────────────────────────────────

def authenticate():
    """
    Handles OAuth2 login with Google.

    First run:  Opens your browser → you log in → grants permission
                → saves token.json for future runs (no login needed again)
    Later runs: Loads token.json automatically (silent login)
    """
    creds = None

    # Load saved credentials if they exist
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Silently refresh expired token
            creds.refresh(Request())
        else:
            # Open browser for login — uses credentials.json from Google Cloud
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    print("✅ Authenticated successfully!\n")
    return creds


# ─────────────────────────────────────────────────────────────
# 📬 PART 1: DATA COLLECTION — Fetch Emails via Gmail API
# ─────────────────────────────────────────────────────────────

def fetch_emails(service, query="in:inbox OR in:sent", max_results=MAX_EMAILS):
    """
    🕷️ THE CRAWLER FUNCTION

    Uses the Gmail API to:
      1. Search for message IDs matching a query (like a search engine)
      2. Fetch full details for each message (like visiting each page)
      3. Extract: sender, subject, body snippet, date

    This is exactly how a web crawler works — find URLs → visit each → extract data.
    """
    print(f"📡 Fetching emails (query: '{query}')...")
    emails = []
    page_token = None
    fetched = 0

    while fetched < max_results:
        # Step 1: Get list of message IDs (like getting a list of URLs to crawl)
        batch_size = min(100, max_results - fetched)
        params = {"userId": "me", "q": query, "maxResults": batch_size}
        if page_token:
            params["pageToken"] = page_token

        results = service.users().messages().list(**params).execute()
        messages = results.get("messages", [])

        if not messages:
            break

        print(f"   Crawling batch of {len(messages)} emails...")

        # Step 2: Fetch full details for each message ID
        for msg_ref in messages:
            try:
                # Get the full message (like fetching the full web page)
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_ref["id"],
                    format="full"
                ).execute()

                # Step 3: Extract headers (metadata)
                headers = {h["name"]: h["value"]
                           for h in msg.get("payload", {}).get("headers", [])}

                sender  = headers.get("From", "Unknown")
                subject = headers.get("Subject", "(No Subject)")
                date    = headers.get("Date", "")

                # Extract body text from payload
                body = extract_body(msg.get("payload", {}))

                emails.append({
                    "sender":  sender,
                    "subject": subject,
                    "date":    date,
                    "body":    body[:500]  # Cap at 500 chars for speed
                })

            except Exception as e:
                continue  # Skip malformed messages

        fetched += len(messages)
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    print(f"✅ Fetched {len(emails)} emails total.\n")
    return pd.DataFrame(emails)


def extract_body(payload):
    """
    Recursively extract plain text from a Gmail message payload.
    Gmail messages can be nested (multipart), so we walk the tree.
    """
    # If this part has a body with data, decode it
    body_data = payload.get("body", {}).get("data", "")
    if body_data:
        try:
            # Gmail API encodes body as URL-safe Base64
            decoded = base64.urlsafe_b64decode(body_data + "==").decode("utf-8", errors="replace")
            # Return only if it looks like plain text (not HTML)
            if "<html" not in decoded.lower():
                return decoded.strip()
        except Exception:
            pass

    # Recurse into multipart message parts
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                try:
                    return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace").strip()
                except Exception:
                    pass
        # Go deeper for nested multipart
        result = extract_body(part)
        if result:
            return result

    return ""


# ─────────────────────────────────────────────────────────────
# 👥 PART 2: CONTACT ANALYSIS
# ─────────────────────────────────────────────────────────────

def analyze_contacts(df):
    print("=" * 58)
    print("👥 PART 2: CONTACT ANALYSIS — Top 5 Senders")
    print("=" * 58)

    def extract_email(s):
        m = re.search(r'[\w.\-+]+@[\w.\-]+', s)
        return m.group(0).lower() if m else s.lower().strip()

    df["sender_clean"] = df["sender"].apply(extract_email)
    top5 = Counter(df["sender_clean"]).most_common(5)

    print(f"\n  {'Rank':<6} {'Sender':<38} {'Emails'}")
    print("  " + "-" * 54)
    for i, (sender, count) in enumerate(top5, 1):
        print(f"  #{i:<5} {sender:<38} {count}")
    print()

    return top5, df


# ─────────────────────────────────────────────────────────────
# 🔍 PART 3: TOPIC IDENTIFICATION
# ─────────────────────────────────────────────────────────────

def analyze_topics(df):
    print("=" * 58)
    print("🔍 PART 3: TOPIC IDENTIFICATION — Top Keywords")
    print("=" * 58)

    all_text = " ".join(df["subject"].fillna("") + " " + df["body"].fillna(""))
    words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    top15 = Counter(filtered).most_common(15)

    print(f"\n  {'Rank':<6} {'Keyword':<22} {'Frequency'}")
    print("  " + "-" * 40)
    for i, (word, count) in enumerate(top15, 1):
        print(f"  #{i:<5} {word:<22} {count}")
    print()

    return top15


# ─────────────────────────────────────────────────────────────
# 📂 PART 4: EMAIL CATEGORIZATION
# ─────────────────────────────────────────────────────────────

def categorize_emails(df):
    print("=" * 58)
    print("📂 PART 4: EMAIL CATEGORIZATION")
    print("=" * 58)

    spam_kw = ["offer","win","free","prize","claim","winner",
               "congratulations","discount","deal","limited time","exclusive"]
    news_kw = ["unsubscribe","newsletter","mailing list",
               "subscription","opt out","manage preferences"]

    def categorize(row):
        text = (str(row["subject"]) + " " + str(row["body"])).lower()
        if any(k in text for k in spam_kw):   return "Spam"
        if any(k in text for k in news_kw):   return "Newsletter"
        return "Personal"

    df["category"] = df.apply(categorize, axis=1)
    counts = df["category"].value_counts()
    total  = len(df)

    print(f"\n  {'Category':<16} {'Count':<10} {'%':<8} Bar")
    print("  " + "-" * 50)
    for cat, count in counts.items():
        pct = count / total * 100
        bar = "█" * int(pct / 3)
        print(f"  {cat:<16} {count:<10} {pct:.1f}%   {bar}")
    print()

    return df


# ─────────────────────────────────────────────────────────────
# 💡 PART 5: INSIGHTS
# ─────────────────────────────────────────────────────────────

def show_insights(df, top5_contacts, top_keywords):
    print("=" * 58)
    print("💡 PART 5: INSIGHTS")
    print("=" * 58)

    # Most active contact
    if top5_contacts:
        name, count = top5_contacts[0]
        print(f"\n  🏆 Most active contact : {name}")
        print(f"     Emails received     : {count}")

    # Most common topic
    if top_keywords:
        word, freq = top_keywords[0]
        print(f"\n  🔑 Most common topic   : '{word}'")
        print(f"     Appeared            : {freq} times")

    # Email activity by time of day
    def time_period(date_str):
        m = re.search(r'(\d{1,2}):\d{2}:\d{2}', str(date_str))
        if m:
            h = int(m.group(1))
            if 5  <= h < 12: return "Morning   (5am–12pm)"
            if 12 <= h < 17: return "Afternoon (12pm–5pm)"
            if 17 <= h < 21: return "Evening   (5pm–9pm)"
            return "Night     (9pm–5am)"
        return "Unknown"

    df["time_period"] = df["date"].apply(time_period)
    time_counts = df["time_period"].value_counts()

    print("\n  🕐 Activity by time of day:")
    max_c = time_counts.max()
    for period, count in time_counts.items():
        bar = "█" * int(count / max_c * 20)
        print(f"     {period}  {count:>4}  {bar}")

    print("\n  📊 Category breakdown:")
    for cat, count in df["category"].value_counts().items():
        print(f"     {cat:<14} {count} emails")
    print()


# ─────────────────────────────────────────────────────────────
# 📊 BONUS: MATPLOTLIB CHART
# ─────────────────────────────────────────────────────────────

def plot_top_contacts(top5):
    if not top5:
        return

    senders = [s[:28] + "..." if len(s) > 28 else s for s, _ in top5]
    counts  = [c for _, c in top5]
    colors  = ["#4C72B0","#55A868","#C44E52","#8172B2","#CCB974"]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(senders[::-1], counts[::-1], color=colors, edgecolor="white", height=0.6)

    for bar, count in zip(bars, counts[::-1]):
        ax.text(bar.get_width() - max(counts) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                str(count), va="center", ha="right",
                color="white", fontweight="bold", fontsize=11)

    ax.set_xlabel("Emails received", fontsize=12)
    ax.set_title("Top 5 Most Frequent Email Senders", fontsize=14, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig("top_contacts.png", dpi=150)
    plt.show()
    print("  📊 Chart saved as top_contacts.png\n")


# ─────────────────────────────────────────────────────────────
# 🚀 MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 58)
    print("   📧 GMAIL MAILBOX ANALYZER — Live Gmail API Edition")
    print("═" * 58 + "\n")

    # Authenticate and build Gmail service
    creds   = authenticate()
    service = build("gmail", "v1", credentials=creds)

    # Fetch emails (inbox + sent combined)
    df = fetch_emails(service, query="in:inbox OR in:sent", max_results=MAX_EMAILS)

    if df.empty:
        print("⚠️  No emails fetched. Check your credentials and try again.")
        return

    top5, df  = analyze_contacts(df)
    top_kw    = analyze_topics(df)
    df        = categorize_emails(df)
    show_insights(df, top5, top_kw)

    print("=" * 58)
    print("📊 BONUS: Generating chart...")
    print("=" * 58)
    plot_top_contacts(top5)

    print("✅ Analysis complete!")
    print("═" * 58 + "\n")


if __name__ == "__main__":
    main()
