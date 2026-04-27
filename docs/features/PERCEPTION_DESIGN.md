# Perception Design (V1)

## 1. Scope and Purpose

This document defines the perception subsystem design for the distributed AV simulation.

System context:

- Laptop (RTX class GPU): perception compute node
- Pi4: control and vehicle simulation node
- Cloud: telemetry and remote command plane

Repository scope note:

- This document describes the perception architecture and runtime contracts.
- Perception runtime executes on the PC node and integrates with Pi4 via Zenoh.

## 2. Design Goals

1. Process camera frames at target 33 FPS (30.3 ms budget per frame)
2. Keep end-to-end latency bounded for control consumption on Pi4
3. Provide deterministic behavior under overload (safe frame drop policy)
4. Support profiling and runtime observability
5. Support multi-model execution path (parallel/serial pipelines)
6. Operate as a production-like managed service on the laptop

## 3. Functional Responsibilities

Perception node responsibilities:

1. Initialize models and runtime resources
2. Subscribe to sensor topics (`/sensor/camera`, optional radar topics)
3. Decode and normalize incoming frames
4. Run inference and post-processing
5. Publish outputs (`/perception/objects`, `/perception/lane`, etc.)
6. Export health and performance metrics

Non-responsibilities:

1. Vehicle control decisions (Pi4 responsibility)
2. Long-term telemetry storage (cloud responsibility)

## 4. Interface Contracts

### 4.1 Input Interfaces (Zenoh)

Primary:

- `/sensor/camera`

Optional extensions:

- `/sensor/radar`
- `/sensor/imu`

Input requirements:

1. Message contains source timestamp and frame id
2. Payload format is versioned and documented
3. Camera frame includes calibration reference id

### 4.2 Output Interfaces (Zenoh)

Primary outputs:

- `/perception/objects`
- `/perception/lane`

Optional outputs:

- `/perception/occupancy_grid`
- `/perception/fusion_summary`

Output requirements:

1. Every message includes `timestamp`, `frame_id`, and `model_version`
2. Every detection includes confidence and class id/name
3. Message schema includes a `schema_version`

## 5. Startup and Lifecycle Design

### 5.1 Service Startup Sequence

At process startup:

1. Load configuration (topic names, thresholds, model paths)
2. Initialize logging and metrics
3. Initialize Zenoh session (subscriber and publishers)
4. Load model(s) and allocate GPU resources
5. Perform warm-up inference passes
6. Transition to `RUNNING`

### 5.2 Runtime States

State machine:

1. `INIT`
2. `WARMUP`
3. `RUNNING`
4. `DEGRADED` (overload, partial model failure, stale input)
5. `STOPPING`
6. `FAILED`

## 6. Frame Processing Architecture

### 6.1 Recommended Pattern: Push + Bounded Queue

Design pattern:

1. Zenoh callback receives incoming frame
2. Callback performs minimal work (decode metadata, enqueue)
3. Worker thread/process performs inference
4. Publisher emits perception output

Reason:

- Avoid expensive inference in callback context
- Control backlog and frame-drop policy explicitly

### 6.2 Processing Pipeline

Per frame:

1. Decode frame
2. Preprocess (resize, normalize, color conversion)
3. Infer model(s)
4. Postprocess (NMS, lane extraction, optional tracking)
5. Publish output
6. Emit profiling metrics

## 7. 33 FPS Timing Design

Target:

- 33 FPS = 30.3 ms frame period

Budget example:

1. Decode + preprocess: 4-6 ms
2. Inference: 15-20 ms
3. Postprocess + publish: 3-5 ms
4. Margin: 2-6 ms

### 7.1 How to Guarantee 33 FPS

Use one of two execution modes:

1. Input-driven mode (camera source paced at 33 FPS)
2. Timer-paced mode (fixed 30.3 ms processing tick)

Recommended V1 approach:

- Input-driven callback + bounded latest-frame queue
- Optional timer watchdog that enforces publish cadence and emits missed-frame metrics

### 7.2 Safe Frame Drop Policy

Use `drop_oldest_keep_latest` policy:

1. Queue size small (for example 1-3 frames)
2. If queue full, drop oldest frame
3. Always process most recent frame to minimize control staleness

Drop rules:

1. Never block callback indefinitely
2. Track dropped frames counter and ratio
3. Enter `DEGRADED` if sustained drop ratio exceeds threshold

## 8. Overload and Degraded Mode Strategy

When frame time exceeds budget consistently:

1. Reduce input resolution
2. Increase confidence threshold
3. Disable optional outputs first (for example occupancy grid)
4. Switch to lighter model variant
5. Maintain output cadence with freshest frame semantics

Degraded-mode telemetry should include:

- current fps
- processing latency p50/p95/p99
- drop ratio
- active model profile

## 9. Profiling and Observability

### 9.1 Per-Frame Metrics

Collect:

1. callback enqueue latency
2. preprocess latency
3. inference latency
4. postprocess latency
5. publish latency
6. total frame time

### 9.2 Aggregate Metrics

Publish at fixed interval:

1. fps actual
2. drop count and drop rate
3. queue depth
4. GPU memory and utilization
5. model error/retry counts

### 9.3 Logging

Log fields:

- frame_id
- source timestamp
- processing start/end
- model version
- output object count
- dropped frame reason

## 10. Multi-Model Parallel Design

### 10.1 Parallel Patterns

Supported patterns:

1. Serial chain (object -> lane -> fusion)
2. Parallel branches (object and lane models concurrently)
3. Hybrid (parallel inference + serial fusion)

Recommended V1:

- Parallel object and lane models with shared preprocessed tensor where feasible
- Final join step for consolidated perception publish

### 10.2 Scheduling

1. Use separate worker pools per model class if resources allow
2. Prevent one model starvation from blocking all outputs
3. Apply per-model timeout and fail-open policy for non-critical branches

## 11. Radar and Camera-Radar Fusion Considerations

### 11.1 Radar Input Handling

1. Subscribe to radar target stream (`/sensor/radar`)
2. Validate timestamp alignment with camera frames
3. Normalize coordinate frames before fusion

### 11.2 Fusion Strategy (V1)

1. Camera detections as semantic primary
2. Radar as motion/range confidence augmentation
3. Associate by temporal window + spatial gating
4. Publish fused attributes in `/perception/objects`

Minimum fused fields:

- object id
- class
- confidence
- range
- relative velocity
- source_flags (`camera`, `radar`, `fused`)

## 12. Reliability and Fault Handling

Failure cases:

1. Model load failure
2. Zenoh disconnect
3. GPU OOM
4. Input stall (camera topic silent)

Required behavior:

1. Detect and report fault quickly
2. Attempt bounded retries
3. Expose health status topic
4. Fail to `DEGRADED` where possible rather than hard exit

## 13. Deployment as a Laptop Service

Recommended service model:

1. systemd unit on laptop for production-like operation
2. Restart policy: `on-failure`
3. Resource limits and watchdog
4. Environment-based config selection (`dev`, `lab`, `stable`)

Service actions:

1. start/stop/restart/status
2. logs via journald or structured file sink

## 14. Security and Integrity

1. Validate all incoming payload structure before decode
2. Treat model files as signed/versioned artifacts
3. Restrict debug endpoints in production profile
4. Keep cloud credentials out of perception process unless required

## 15. Validation and Acceptance Criteria

Perception V1 acceptance:

1. Sustained >= 33 FPS on representative workload OR explicit degraded-mode fallback with bounded latency
2. p95 frame processing latency <= 30.3 ms in target profile (or documented fallback profile)
3. Frame drop policy behaves as specified and metrics are exported
4. Pi4 receives valid `/perception/objects` messages continuously
5. Service recovers automatically from transient failures

## 16. Reference Runtime Pseudocode

```python
initialize_config()
initialize_logging_metrics()
zenoh = open_zenoh_session()
model = load_model()
warmup(model)

queue = LatestFrameQueue(max_size=2)


def on_camera(sample):
    frame = decode_minimal(sample)
    queue.push(frame)  # drop_oldest_keep_latest when full


def worker_loop():
    while running:
        frame = queue.pop(timeout_ms=20)
        if frame is None:
            emit_input_stall_metric()
            continue

        t0 = now()
        x = preprocess(frame)
        y = infer(model, x)
        out = postprocess(y)
        publish('/perception/objects', out)
        emit_timing_metrics(now() - t0)

subscribe('/sensor/camera', on_camera)
start_worker(worker_loop)
run_forever()
```

## 17. Implementation Checklist

1. Define and freeze input/output schemas with `schema_version`
2. Implement bounded latest-frame queue and drop policy
3. Implement timing metrics and periodic health publication
4. Add service unit and runtime config profiles
5. Add overload fallback profiles (resolution/model switch)
6. Add radar integration hooks and fusion baseline
7. Add integration test against Pi4 consumer and replay dataset
