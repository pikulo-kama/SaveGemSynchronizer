from datetime import datetime

import pytz
from babel.dates import format_datetime
from babel.localtime import get_localzone

from constants import TimeFormat
from savegem.common.core.context import app


def string_to_date(date_string: str):
    """
    Used to transform string date to actual date object.
    Uses current timezone of machine when creating date.
    """

    creation_datetime_naive = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_datetime = pytz.utc.localize(creation_datetime_naive)
    time_zone = pytz.timezone(str(get_localzone()))

    return utc_datetime.astimezone(time_zone)


def get_verbose_date(datetime_object: datetime, show_year: bool = True):
    """
    Used to extract date from datetime object
    and transform it to readable string.
    """

    date_format = "d MMMM"

    if show_year:
        date_format += " YYYY"

    return format_datetime(datetime_object, date_format, locale=app().state.locale)


def get_verbose_time(datetime_object: datetime):
    """
    Used to extract time from datetime object
    and transform it to readable string.
    """

    # 24-hour format.
    time_format = "%H:%M"

    if app().state.time_format == TimeFormat.Regular:
        time_format = "%I:%M %p"

    return datetime_object.strftime(time_format)
