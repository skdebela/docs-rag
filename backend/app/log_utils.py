# log_utils.py - Logging utility for operational events and gotchas
import os
from datetime import datetime

def safe_log_gotcha(message: str):
    """
    Log a gotcha, error, or operational event to gotchas.md in the project root.
    Appends timestamped entries for traceability and compliance.
    """
    gotchas_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gotchas.md'))
    timestamp = datetime.now().isoformat()
    entry = f"[{timestamp}] {message}\n"
    try:
        with open(gotchas_path, 'a') as f:
            f.write(entry)
    except Exception as e:
        # As a last resort, print the error
        print(f"[safe_log_gotcha ERROR] Could not write to gotchas.md: {e}")
