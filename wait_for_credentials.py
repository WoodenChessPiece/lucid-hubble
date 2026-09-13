import os
import glob
import shutil
import time

downloads_dir = os.path.expanduser("~/Downloads")
dest = "client_secret.json"

print("Watching ~/Downloads for client_secret*.json...")
found = False
for _ in range(60): # watch for 2 minutes
    matches = glob.glob(os.path.join(downloads_dir, "client_secret*.json"))
    if matches:
        latest = max(matches, key=os.path.getctime)
        shutil.copy(latest, dest)
        print(f"Found and copied: {latest} -> {dest}")
        found = True
        break
    time.sleep(2)

if not found:
    print("No client_secret file detected yet.")
