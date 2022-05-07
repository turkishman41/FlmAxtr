import imp
import pytz
from datetime import datetime

def guncelTarih(timezone = 'Europe/Istanbul'):
    a = str(datetime.now(pytz.timezone(timezone)))
    return a.replace('\n', '').strip()
