import os
import time
import feedparser
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "@digitalmanipur"
SENT_LOG = "sent_notices.txt"

FEEDS = [
    "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "https://www.sarkariresult.com/feed/",
    "https://www.mysarkarinaukri.com/feed",
    "https://jobalertshub.com/feed/",
]


def load_sent_notices():
  if not os.path.exists(SENT_LOG):
    return set()
  with open(SENT_LOG, "r") as f:
    return set(line.strip() for line in f)


def save_sent_notice(notice_id):
  with open(SENT_LOG, "a") as f:
    f.write(f"{notice_id}\n")


def send_telegram_msg(text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": CHAT_ID,
      "text": text,
      "parse_mode": "Markdown",
      "disable_web_page_preview": False,
  }
  try:
    res = requests.post(url, data=payload)
    return res.status_code == 200
  except Exception as e:
    print("Telegram broadcast error:", e)
    return False


def run_crawler():
  sent_ids = load_sent_notices()
  print("Scanning live portals for All-India exams & Manipur scholarships...")

  new_posts_count = 0
  for feed_url in FEEDS:
    try:
      parsed_feed = feedparser.parse(feed_url)
      for entry in parsed_feed.entries[:10]:
        title = entry.get("title", "")
        link = entry.get("link", "")
        item_id = entry.get("id", link)

        if item_id in sent_ids:
          continue

        keywords = [
            "exam",
            "scholarship",
            "recruitment",
            "vacancy",
            "upsc",
            "ssc",
            "ibps",
            "nsp",
            "manipur",
            "st",
            "post-matric",
            "police",
            "teacher",
            "ugc",
            "csir",
            "ishan uday",
        ]

        if not any(kw in title.lower() for kw in keywords):
          continue

        message = f"""
📢 *OFFICIAL RECRUITMENT / SCHOLARSHIP ALERT*

🔹 *Title:* {title}

📝 *Details:*
Check official eligibility, age limits, required documents, and application deadlines at the portal link below.

🔗 *Official Portal / Apply Online:*
{link}

—
📢 *Join @digitalmanipur for real-time exam call notices & scholarship updates!*
"""
        print(f"Broadcasting: {title[:60]}...")
        if send_telegram_msg(message):
          save_sent_notice(item_id)
          new_posts_count += 1
          time.sleep(3)
    except Exception as e:
      print(f"Feed error ({feed_url}): {e}")

  print(f"Crawl complete! Broadcasted {new_posts_count} new updates.")


if __name__ == "__main__":
  run_crawler()
