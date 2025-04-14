from datetime import datetime, timezone


def get_current_time():
    """UTC の現在時刻をタイムゾーン情報なしで返却する"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
