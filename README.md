# Antasena Super Course — MQTT Telemetry Module

Learn to receive live vehicle telemetry over MQTT, then move on to data
analysis and efficiency calculation.

## Setup

```
pip install paho-mqtt pandas numpy matplotlib jupyter
```

## 1. Instructor runs the publisher

Replays a recorded telemetry CSV to the broker as if it were a live car.

```
python publisher.py
```

Options:
- `--csv data/DataASC_80V_12A.csv` — pick which recorded run to replay (two are provided in `data/`)
- `--speed 20` — play back faster than real time (default 10x)
- `--loop` — replay from the start forever, useful for a live classroom demo

## 2. Course takers run the subscriber

```
python subscriber.py
```

This connects to the same public broker (`broker.hivemq.com`) and topic
(`antasena/course/telemetry`), prints each incoming message, and saves it to
`received_telemetry.csv`.

Each row contains: `lap`, `time_s`, `voltage_V`, `current_A`, a speed column
(`speed_ms` or `speed_kmh` depending on the CSV in use), and `distance_m`.

## 3. Course takers analyze the data

Open `analysis_template.ipynb`. It loads the two sample runs in `data/`
(`105V / 9A` vs `80V / 12A`), computes `power_W`, cumulative `energy_Wh`, and
`efficiency_km_per_kWh`, plots them, builds a per-lap summary table, and asks
guided questions about why one run is more efficient than the other.

To analyze your *own* collected data instead: run `subscriber.py --out
attempt_a.csv` and `attempt_b.csv` for two different publisher runs, then
point the `ATTEMPTS` list in the notebook's config cell at those files and
re-run.
