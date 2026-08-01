"""
utils.py
Common utility functions for SGTPA Scraper
"""

import random
import re
import time
import logging
from functools import wraps


# -----------------------------
# Logging
# -----------------------------

def setup_logger(log_file="crawler.log"):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )


# -----------------------------
# Text Cleaning
# -----------------------------

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


# -----------------------------
# Random Delay
# -----------------------------

def random_delay(min_delay=0.5, max_delay=1.5):
    time.sleep(random.uniform(min_delay, max_delay))


# -----------------------------
# Retry Decorator
# -----------------------------

def retry(max_retry=3, delay=2):
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            last_error = None

            for attempt in range(max_retry):

                try:
                    return func(*args, **kwargs)

                except Exception as e:

                    last_error = e

                    logging.warning(
                        f"{func.__name__} failed "
                        f"({attempt+1}/{max_retry}) : {e}"
                    )

                    time.sleep(delay * (attempt + 1))

            raise last_error

        return wrapper

    return decorator


# -----------------------------
# Email Extraction
# -----------------------------

def extract_emails(text):

    if not text:
        return []

    return sorted(
        set(
            re.findall(
                r'[\w\.-]+@[\w\.-]+\.\w+',
                text
            )
        )
    )


# -----------------------------
# Phone Extraction
# -----------------------------

def extract_phones(text):

    if not text:
        return []

    phones = re.findall(
        r'(\+?\d[\d\s\-\(\)]{6,})',
        text
    )

    result = []

    for p in phones:

        p = clean_text(p)

        if len(p) >= 7:
            result.append(p)

    return sorted(set(result))