# GDB User Guide

## Purpose

This guide explains how to use GDB to debug native C/C++ applications on the Pi4 runtime image built from this repository.

## Prerequisites

1. Build debug symbols into your binary (`-g` recommended).
2. Ensure target binary is present on Pi4 (for example under `/usr/local/bin`).
3. Install GDB on target image if not already enabled in Buildroot.

## Quick Start (On Pi4)

### 1. Start program under GDB

```bash
gdb /usr/local/bin/your_app
```

Inside GDB:

```gdb
break main
run
next
print some_variable
backtrace
quit
```

### 2. Attach to a running process

```bash
pidof your_app
gdb -p <PID>
```

Inside GDB:

```gdb
thread apply all backtrace
continue
detach
quit
```

## Core Debug Commands

### Breakpoints

```gdb
break main
break file.cpp:120
info breakpoints
disable 1
enable 1
delete 1
```

### Stepping

```gdb
run
next
step
finish
continue
```

### Inspect Data

```gdb
print var
print *ptr
print arr[3]
info locals
info args
```

### Stack and Threads

```gdb
backtrace
frame 2
info threads
thread 3
thread apply all backtrace
```

## Debugging Crashes

### 1. Enable core dumps

```bash
ulimit -c unlimited
```

### 2. Run app and capture core

If app crashes, a core file is generated (location depends on system core pattern).

### 3. Open core in GDB

```bash
gdb /usr/local/bin/your_app core
```

Useful commands:

```gdb
backtrace
info threads
thread apply all backtrace
info registers
```

## Debugging systemd Services

If the app is managed by systemd (example: `av-core-health.service`):

1. Stop service before manual debugging:

```bash
systemctl stop av-core-health
```

2. Run under GDB manually:

```bash
gdb /usr/local/bin/av-core-health
```

3. Check service logs separately:

```bash
journalctl -u av-core-health -b --no-pager
```

## Remote Debugging (Optional)

Use this when debugging from a host machine while the app runs on Pi4.

### On Pi4

```bash
gdbserver :2345 /usr/local/bin/your_app
```

### On host (with matching binary + symbols)

```bash
gdb /path/to/your_app
```

Inside host GDB:

```gdb
target remote <PI4_IP>:2345
break main
continue
```

## Build Tips for Better Debugging

For applications you compile in development mode:

```bash
-g -O0 -fno-omit-frame-pointer
```

Notes:

- `-g` adds symbol information.
- `-O0` reduces optimization complexity while debugging.
- `-fno-omit-frame-pointer` improves stack traces.

## Common Issues

### No symbols loaded

Symptom: GDB shows `??` for functions.

Fix:

1. Rebuild binary with `-g`.
2. Ensure stripped release binary is not replacing your debug build.

### Breakpoint not hit

Possible causes:

1. Wrong executable or old binary running.
2. Function inlined by optimization.

Fix:

1. Verify binary path and checksum.
2. Rebuild with lower optimization for debug (`-O0`).

### Permission denied on attach

If attach fails, run as root or adjust ptrace restrictions depending on system policy.

## Recommended Debug Workflow for av-core Services

1. Rebuild service with debug symbols.
2. Stop the systemd unit.
3. Run service directly under GDB.
4. Reproduce issue.
5. Capture `backtrace` and relevant variable state.
6. Re-run as service and confirm fix with `journalctl`.

## Useful One-Liners

List service process and attach:

```bash
pidof av-core-orchestrator | xargs -I{} gdb -p {}
```

Capture all thread backtraces in batch:

```bash
gdb -batch -ex "thread apply all bt full" -p <PID>
```
