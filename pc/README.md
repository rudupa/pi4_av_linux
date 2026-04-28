# PC Edge Stack

Implements camera/radar playback, baseline perception, fusion, schema validation, drop-safe queueing, and edge publishing adapters.

Architecture conformance:

- Primary runtime path is now available in C++ under `pc/cpp/` for native-service alignment.
- Python modules under `pc/src/` remain as reference and rapid-iteration harness.

Run:

```bash
python3 -m pc.src.playback_service --config pc/config/default.yaml
```

Build and run C++ node:

```bash
cmake -S pc/cpp -B pc/cpp/build
cmake --build pc/cpp/build -j
./pc/cpp/build/pc_perception_node
```
