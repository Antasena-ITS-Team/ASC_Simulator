"""
publisher.py — instructor-side script for the Antasena Super Course MQTT module.

Publishes a pre-recorded telemetry CSV (voltage, current, speed, distance,
lap, time_s) to an MQTT broker, row by row, as JSON — simulating a live car
sending telemetry over the air. Course takers connect with subscriber.py to
practice receiving real-time data before moving on to analysis and
efficiency calculations.

Usage:
    python publisher.py
    python publisher.py --csv data/DataASC_80V_12A.csv --speed 20
    python publisher.py --loop --speed 50
"""

import argparse
import csv
import json
import time

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "antasena/course/telemetry"


def load_rows(csv_path):
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            parsed = {}
            for key, value in row.items():
                try:
                    parsed[key] = float(value)
                except ValueError:
                    parsed[key] = value
            rows.append(parsed)
    return rows


def publish_rows(client, rows, speed, topic):
    prev_time_s = None
    for row in rows:
        # sleep according to the gap between real sample timestamps, sped up
        # by --speed so a multi-minute log can play back in a class-friendly time
        if prev_time_s is not None and "time_s" in row:
            gap = max(0.0, row["time_s"] - prev_time_s) / speed
            time.sleep(gap)
        prev_time_s = row.get("time_s", prev_time_s)

        payload = json.dumps(row)
        client.publish(topic, payload, qos=1)
        print(f"Published: {payload}")


def main():
    ap = argparse.ArgumentParser(description="Publish a recorded telemetry "
                                             "CSV to an MQTT broker for the course")
    ap.add_argument("--csv", default="data/DataASC_105V_9A.csv",
                    help="telemetry CSV to replay (default: data/DataASC_105V_9A.csv)")
    ap.add_argument("--broker", default=BROKER, help=f"MQTT broker host (default: {BROKER})")
    ap.add_argument("--port", type=int, default=PORT, help=f"MQTT broker port (default: {PORT})")
    ap.add_argument("--topic", default=TOPIC, help=f"MQTT topic (default: {TOPIC})")
    ap.add_argument("--speed", type=float, default=10.0,
                    help="playback speed multiplier vs. real recorded time "
                         "(default: 10x — a 34-minute log plays in ~3.4 minutes)")
    ap.add_argument("--loop", action="store_true",
                    help="replay the CSV from the start forever, instead of stopping at the end")
    args = ap.parse_args()

    rows = load_rows(args.csv)
    print(f"Loaded {len(rows)} rows from {args.csv}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.connect(args.broker, args.port, 60)
    client.loop_start()
    print(f"Connected to MQTT broker: {args.broker}:{args.port}")
    print(f"Publishing to topic: {args.topic} (speed x{args.speed})\n")

    try:
        while True:
            publish_rows(client, rows, args.speed, args.topic)
            if not args.loop:
                break
            print("\n--- reached end of CSV, looping back to start ---\n")
    except KeyboardInterrupt:
        print("\nStopping publisher...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
