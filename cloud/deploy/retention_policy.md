# Retention and Downsampling Policy

- vehicle_state: 7d raw, 30d 1m downsample
- vehicle_health: 30d raw, 180d 5m downsample
- events/ota: 180d raw

Data quality checks:
- missing intervals > 10s
- outlier spikes by z-score > 4
