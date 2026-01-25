import argparse
import os
import re
from datetime import datetime
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models import TemperatureReading

def parse_args():
    parser = argparse.ArgumentParser(description="Migrate legacy temp.log to SQLite database")
    # Default to ../legacy/temp.log if not provided, for local dev
    default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "legacy", "temp.log")
    parser.add_argument("--log-file", type=str, default=default_path, help="Path to temp.log file")
    return parser.parse_args()

def parse_line(line):
    # Formats:
    # DATA: 2026-01-24 00:00:01 | 37.48 | DATA
    # SUMMARY: 2026-01-18 00:00:00 | 36.51 (09:50)/47.23 (13:10) | SUMMARY
    
    parts = line.strip().split(" | ")
    if len(parts) != 3:
        return []

    date_str, data_part, type_part = parts
    
    readings = []
    
    if type_part == "DATA":
        try:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            temp = float(data_part)
            readings.append({"timestamp": timestamp, "temperature": temp})
        except ValueError as e:
            print(f"Skipping malformed DATA line: {line.strip()} ({e})")

    elif type_part == "SUMMARY":
        # Format: 36.51 (09:50)/47.23 (13:10)
        try:
            # Base date from date_str
            base_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
            
            # Split min/max
            min_max = data_part.split("/")
            if len(min_max) == 2:
                # Regex to extract temp and time: 36.51 (09:50)
                pattern = r"([\d\.]+)\s\((\d{2}:\d{2})\)"
                
                for part in min_max:
                    match = re.search(pattern, part)
                    if match:
                        temp = float(match.group(1))
                        time_str = match.group(2)
                        
                        # Combine base_date and time_str
                        dt_time = datetime.strptime(time_str, "%H:%M").time()
                        timestamp = datetime.combine(base_date, dt_time)
                        
                        readings.append({"timestamp": timestamp, "temperature": temp})
        except ValueError as e:
            print(f"Skipping malformed SUMMARY line: {line.strip()} ({e})")
            
    return readings

def migrate(log_file):
    if not os.path.exists(log_file):
        print(f"Error: Log file not found at {log_file}")
        return

    print(f"Reading from: {log_file}")
    
    create_db_and_tables()
    
    count_new = 0
    count_skipped = 0
    
    with Session(engine) as session:
        # Get existing timestamps to avoid heavy duplicates
        # Ideally we'd query specifically, but for a simple migration script, 
        # let's just check existence before insert or rely on the fact it's a migration.
        # To be safe and efficient enough for this scale (<10k rows likely):
        # We'll just insert. If the user runs this multiple times, they might get duplicates 
        # unless we check. Let's check.
        
        # Pre-load all timestamps? Might be too memory intensive if huge, but fine for temp logs.
        existing_timestamps = set(session.exec(select(TemperatureReading.timestamp)).all())
        
        with open(log_file, "r") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                
                readings_data = parse_line(line)
                for r_data in readings_data:
                    ts = r_data["timestamp"]
                    temp = r_data["temperature"]
                    
                    if ts in existing_timestamps:
                        count_skipped += 1
                        continue
                    
                    reading = TemperatureReading(temperature=temp, timestamp=ts)
                    session.add(reading)
                    existing_timestamps.add(ts) # Add to set to catch duplicates within the file itself
                    count_new += 1
        
        session.commit()
    
    print(f"Migration complete.")
    print(f"Imported: {count_new} readings")
    print(f"Skipped (duplicate timestamps): {count_skipped} readings")

if __name__ == "__main__":
    args = parse_args()
    migrate(args.log_file)
