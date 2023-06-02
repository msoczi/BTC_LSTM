import requests
import time
from datetime import datetime, timedelta
from pandas import DataFrame, to_datetime
import calendar
import pytz

# TODO gdy jest zmiana czasu to nagle nie zgadza nam sie czas UTC i obecny.
# Trzeba dac jakiegos if'a zeby radzil sobie ze zmiana czasu, bo na razie po 25/26 marca nie spina sie godzina

# TODO obecnie maksymalna liczba wierszy do sciagniecia to 10 tys. - trzeba poprawic aby mozna bylo wiecej

def download_data(START_TIME, END_TIME, INTERVAL, TIMEZONE="Europe/Warsaw", LIMIT=10000):
    """
    Function to download btc data.
    
    Args:
        START_TIME - data poczatkowa w formacie YYYY-MM-DD HH:MM:SS
        END_TIME - data koncowa w formacie YYYY-MM-DD HH:MM:SS
        INTERVAL - interwal czasowy [1m|5m|15m|30m|1h|3h|6h|12h|1D|7D|14D|1M]
        TIMEZONE - strefa czasowa dla podanych dat START_TIME i END_TIME
    """
    if TIMEZONE != "UTC":
        local = pytz.timezone(TIMEZONE)
        START_TIME = datetime.strptime(START_TIME, "%Y-%m-%d %H:%M:%S")
        END_TIME = datetime.strptime(END_TIME, "%Y-%m-%d %H:%M:%S")
        START_TIME = START_TIME.astimezone(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
        END_TIME = END_TIME.astimezone(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
    
    start_time_ms = calendar.timegm(time.strptime(START_TIME, '%Y-%m-%d %H:%M:%S'))*1000 # time UTC because we add 2h
    end_time_ms = calendar.timegm(time.strptime(END_TIME, '%Y-%m-%d %H:%M:%S'))*1000 # time UTC because we add 2h

    URL = f"https://api.bitfinex.com/v2//candles/trade:{INTERVAL}:tBTCUSD/hist?limit={str(LIMIT)}&start={start_time_ms}&end={end_time_ms}&sort=-1"
    page = requests.get(url = URL)
    
    df = DataFrame(page.json(), columns=['date', 'open', 'close', 'high', 'low', 'volume'])
    if TIMEZONE != "UTC":
        df['date'] = to_datetime(df['date'],unit='ms', utc=True).map(lambda x: x.tz_convert(TIMEZONE))
    if TIMEZONE == "UTC":
        df['date'] = to_datetime(df['date'],unit='ms')
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    return df

