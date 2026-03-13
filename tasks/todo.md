# TODO: Multi-Device Parallel Execution

## Plan
The CLI currently processes only one device (the last one parsed, due to YAML duplicate keys).
We need to:
1. Fix YAML structure (already done — `devices:` list)
2. Fix `DeviceConfig` multi-load (already done — `from_yaml_multi()`)
3. Fix `ASAManager` to store device list (already done — `device_configs`)
4. **Add a `run_on_device()` helper** in `__main__.py` that runs an operation on a single device
5. **Add parallel dispatch** in `__main__.py` using `concurrent.futures.ThreadPoolExecutor`
6. **Aggregate and display results** per-device with clear labeling
7. Update `CHANGE.md`

## Architecture Decision
- Use `concurrent.futures.ThreadPoolExecutor` (stdlib, no new deps)
- Each thread gets its **own `ASAManager` instance** → no shared mutable state, fully thread-safe
- `max_workers` = number of devices (bounded by device count, not unbounded)
- Single device = no thread pool overhead (direct call)
- Print output is collected per-device and printed sequentially to avoid interleaving

## Open Items
- [x] Restructure `device.yaml` as `devices:` list
- [x] Add `DeviceConfig.from_yaml_multi()`
- [x] Update `ASAManager.load_device_config()` to populate `device_configs`
- [x] Extract `_run_preview_on_device()` / `_run_commit_on_device()` helpers in `__main__.py`
- [x] Add `ThreadPoolExecutor` parallel dispatch in `__main__.py`
- [x] Collect output per-device into StringIO buffers, print sequentially
- [x] Handle partial failures (one device fails, others succeed)
- [x] Fix output interleaving — replace `redirect_stdout` with `buf.write()`
- [x] Fix state file: store per-device state so parallel commits don't overwrite each other
- [x] Fix revert: match saved state device_name to the right DeviceConfig, connect to that device
- [x] Fix revert: support reverting multiple devices from a single `--revert` call
- [x] Test: change nameif to "TestRevert", commit, verify, revert, verify

## Review
- Both devices (192.168.1.185 and 192.168.1.186) connected concurrently at the same timestamp
- Output cleanly separated per device with headers and summary
- No new dependencies added (stdlib `concurrent.futures` only)
- Single-device path skips thread pool overhead entirely
- Legacy single-device YAML format still supported via `from_yaml_multi()` fallback
- Per-device state files (`state/lab-asav-1.json`, `state/lab-asav-2.json`) — no overwriting
- Full cycle tested: preview → commit (Inside→TestRevert) → revert (TestRevert→Inside) → verify (Inside) ✅
- State files properly cleaned up after successful revert ✅
