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
        return []  # Default stats if file does not exist


# Days of the week when the script is active
ACTIVE_DAYS = {
    0: True,   # Monday
    1: True,  # Tuesday
    2: True,  # Wednesday
    3: True,   # Thursday
    4: True,  # Friday
    5: False,  # Saturday
    6: False   # Sunday
}

# Array for response templates
RESPONSE_TEMPLATES = [
    {
        "Дизайн сайта": ["дизайн сайта", "дизайн"],
    },
    {
        "Редизайн сайта": ["редизайн сайта", "редизайн"],
    },
    {
        "SEO (поисковая оптимизация)": ["seo", "поисковая оптимизация", "сео"],
    },
    {
        "Сайт WordPress": ["wordpress", "сайт на wordpress", "вордпресс"],
    },
    {
        "Сайт на 1С-Битрикс": ["1с-битрикс", "битрикс", "сайт на 1с-битрикс"],
    },
    {
        "Создание лэндинга": ["создание лэндинга", "лендинг", "landing page"],
    }
]

BASE_TEMPLATE_NAME = "Общий отклик"

# Loading statistics
STATS = load_stats()

# Script Active time (from, to) 24h format
ACTIVE_TIME = [9, 18]

# Script timezone (read before change https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
TIME_ZONE = pytz.timezone('Europe/Moscow')
