import pytz
import json

# True = development, False = production
MODE = True

# Sites to monitor (now only youdo.com)
MAIN_SITES = ["https://youdo.com"]

# If this words have in title, wee ignore the task
with open("./data/ban_words.json", "r", encoding="utf-8") as f:
    BAN_WORDS = json.load(f)


def load_stats():
    """Load statistics from the stats file."""
    try:
        with open("./data/stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"all": 0}  # Default stats if file does not exist


# Loading statistics
STATS = load_stats()

# Script Active time (from, to) 24h format
ACTIVE_TIME = [9, 18]

# Script timezone (read before change https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
TIME_ZONE = pytz.timezone('Europe/Moscow')
