# Test Cases: Multi-Device Parallel Execution

## TC-1: YAML Multi-Device Parsing
- [x] Load `device.yaml` with `devices:` list containing 2 devices
- [x] Verify `DeviceConfig.from_yaml_multi()` returns a list of 2 `DeviceConfig` objects
- [x] Verify each has correct host, credentials, device_name

## TC-2: Legacy Single-Device YAML Backward Compatibility
- [x] Load a flat YAML file (no `devices:` key)
- [x] Verify `from_yaml_multi()` returns a list of 1 `DeviceConfig`
- [x] Verify `from_yaml()` still returns a single `DeviceConfig`

## TC-3: Parallel Preview (--preview)
- [x] Run `python -m asa_manager --preview` with 2 devices
- [x] Both devices should be connected concurrently via ThreadPoolExecutor
- [x] Output should show results for BOTH devices, clearly labeled
- [x] If one device fails to connect, the other should still succeed

## TC-4: Parallel Commit (--commit)
- [x] Set `changes.yaml` to a NEW nameif value (e.g. "TestRevert")
- [x] Run `python -m asa_manager --commit` with 2 devices
- [x] Both devices should have changes applied concurrently
- [x] Each device gets its own backup, state saved per-device
- [x] Output shows per-device success/failure

## TC-5: Revert After Multi-Device Commit (--revert)
- [x] Run `python -m asa_manager --revert` after multi-device commit
- [x] Revert should connect to EACH device that had changes
- [x] Each device should be reverted to its original nameif
- [x] State file should store per-device changes (not overwrite)

## TC-6: Sequential Fallback
- [x] If only 1 device in config, behavior is identical to before (no threading overhead)

## TC-7: Error Isolation
- [x] If device-1 connection times out, device-2 should still complete
- [x] Per-device error messages should be clear
- [x] Overall exit code = 1 if ANY device fails

## TC-8: Thread Safety
- [x] Each device gets its own ASAManager instance (own connection, interface_manager)
- [x] No shared mutable state between threads
- [x] Log output should include device_name for traceability

## TC-9: State Cleanup
- [x] After successful revert, per-device state files are deleted
- [x] After revert, `--revert` shows "No changes to revert"
- [x] Final preview confirms both devices back to original nameif
