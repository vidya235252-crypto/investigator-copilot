from scenarios import SCENARIOS
from datetime import datetime

for name, fn in SCENARIOS.items():
    account_id, events, label = fn(datetime.now())
    print(name, "label:", label)
    for e in events:
        print(" ", e["timestamp"], e["event_type"], e.get("amount"))
    print()
    