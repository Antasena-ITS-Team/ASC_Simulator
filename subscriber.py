"""
subscriber.py — course taker starter script for the Antasena Super Course MQTT module.

Connects to the same MQTT broker/topic as publisher.py, listens for the live
telemetry stream, and saves every message to a CSV so you can move on to the
data analysis and efficiency calculation part of the course.

Usage:
    python subscriber.py
    python subscriber.py --out my_received_data.csv
"""

import argparse
import csv
import json
import os

import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "antasena/course/telemetry"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker!")
        client.subscribe(userdata["topic"], qos=1)
        print(f"Subscribed to topic: {userdata['topic']}")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(f"Received: {payload}")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("  (skipped: not valid JSON)")
        return

    out_path = userdata["out_path"]
    file_exists = os.path.isfile(out_path) and os.path.getsize(out_path) > 0

    # keep the column order stable by reusing the header already written to disk,
    # falling back to this message's own keys the first time the file is created
    if file_exists:
        with open(out_path, newline="") as f:
            headers = next(csv.reader(f))
    else:
        headers = list(data.keys())

    with open(out_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def main():
    ap = argparse.ArgumentParser(description="Subscribe to the course MQTT "
                                             "telemetry stream and log it to CSV")
    ap.add_argument("--broker", default=BROKER, help=f"MQTT broker host (default: {BROKER})")
    ap.add_argument("--port", type=int, default=PORT, help=f"MQTT broker port (default: {PORT})")
    ap.add_argument("--topic", default=TOPIC, help=f"MQTT topic (default: {TOPIC})")
    ap.add_argument("--out", default="received_telemetry.csv",
                    help="CSV file to save incoming telemetry to (default: received_telemetry.csv)")
    args = ap.parse_args()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1,
        userdata={"topic": args.topic, "out_path": args.out},
    )
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.broker, args.port, 60)
        print(f"Saving incoming telemetry to: {args.out}")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client.disconnect()


if __name__ == "__main__":
    main()
