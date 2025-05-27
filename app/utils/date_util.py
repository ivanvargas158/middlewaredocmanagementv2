import time
import pytz
from datetime import datetime

def get_est_time()->datetime:
    est = pytz.timezone('America/New_York')
    return datetime.now(est)