# Lessons Learned

## 2026-03-13 - redirect_stdout is NOT thread-safe

**Mistake:** Used `contextlib.redirect_stdout` inside `ThreadPoolExecutor` workers to capture per-thread output into `StringIO` buffers. Output was interleaved and misaligned across devices.

**Root cause:** `redirect_stdout` works by temporarily replacing the global `sys.stdout`. In multi-threaded code, all threads share the same `sys.stdout` — threads race and overwrite each other's redirections.

**Rule:** Never use `redirect_stdout` in threaded code. Instead, write directly to a per-thread `io.StringIO` buffer with `buf.write()`, then print the collected output on the main thread after all workers complete.

**Pattern:**
```python
# BAD — not thread-safe
buf = io.StringIO()
with redirect_stdout(buf):
    print("hello")  # may go to wrong buffer or real stdout

# GOOD — fully thread-safe
buf = io.StringIO()
buf.write("hello\n")  # always goes to this buffer
return buf.getvalue()
```
