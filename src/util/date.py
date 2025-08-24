from datetime import datetime

from babel.dates import format_datetime
from pytz import timezone

from src.core.holders import prop


def extract_date(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    date += timezone(prop("timeZone")).utcoffset(date)

    return {
        "date": format_datetime(date, "d MMMM", locale=prop("locale")),
        "time": date.strftime("%H:%M")
    }
