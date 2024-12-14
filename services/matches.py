import pandas as pd
from statsbombpy import sb

def get_events(match_id):
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return full_events