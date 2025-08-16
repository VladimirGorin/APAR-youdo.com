import pytz
import json

# True = development, False = production
MODE = True

# Sites to monitor (now only youdo.com)
MAIN_SITES = ["https://youdo.com"]

# If this words have in title, wee ignore the task
with open("./data/ban_words.json", "r") as f:
    BAN_WORDS = json.load(f)


# Script Active time (from, to) 24h format
ACTIVE_TIME = [9, 18]

# Script timezone (read before change https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
TIME_ZONE = pytz.timezone('Europe/Moscow')
