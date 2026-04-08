
import pytz
import dateutil.parser
import datetime

def get_gantt_date(date_field, tz=None):
    if not date_field:
        return ''
    if tz and hasattr(date_field, 'astimezone'):
        return date_field.astimezone(tz).strftime('%Y-%m-%dT%H:%M:%S')
    return date_field.strftime('%Y-%m-%dT%H:%M:%S')


def from_gantt_date(value):
    # Bryntum can send empty string/None for optional date fields.
    # Returning False allows Odoo to keep/clear datetime safely instead of crashing update.
    if value in (None, False, ''):
        return False
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min)
    try:
        dt = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        dt = dt.astimezone(pytz.utc)
        return dt.replace(tzinfo=None)
    except Exception:
        try:
            return dateutil.parser.parse(str(value), ignoretz=True)
        except Exception:
            return False