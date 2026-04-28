# Pi4 Runtime Stack

Implements control/simulation loop boundaries, deterministic tick manager, mode manager, fault injection hook, telemetry publisher, command listener, dashboard API, and smoke test scripts.

Architecture conformance:

- Native C++ control/simulation service path is available in `pi4/cpp/`.
- Python modules in `pi4/src/` remain integration and orchestration baseline.

Run:

```bash
python3 -m pi4.src.main --config pi4/config/runtime.yaml
```

Build and run C++ node:

```bash
cmake -S pi4/cpp -B pi4/cpp/build
cmake --build pi4/cpp/build -j
./pi4/cpp/build/pi4_control_sim_node
```
