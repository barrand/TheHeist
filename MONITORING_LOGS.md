# Log Monitoring Guide

## Backend Logs

### Full logs (see everything including errors):
```bash
tail -f /tmp/theheist-backend.log
```

### Critical errors only:
```bash
tail -f /tmp/theheist-backend.log | grep -E "(ERROR|Exception|Traceback)" -i --line-buffered
```

### Important events (better filter):
```bash
tail -f /tmp/theheist-backend.log | grep -E "(ERROR|WARNING|room|player|role|WebSocket)" -i --line-buffered
```

### Super verbose (all important lines):
```bash
tail -f /tmp/theheist-backend.log | grep -Ev "^INFO:.*HTTP/1.1\" 200" --line-buffered
```
This shows everything EXCEPT successful HTTP requests (which are noisy).

## Frontend Logs

### Flutter debug output:
```bash
tail -f /tmp/theheist-flutter.log
```

### Flutter errors only:
```bash
tail -f /tmp/theheist-flutter.log | grep -E "(Error|Exception|Failed)" -i --line-buffered
```

### Flutter WebSocket activity:
```bash
tail -f /tmp/theheist-flutter.log | grep -E "(🔌|📤|📥|🎭|🏠)" --line-buffered
```

## Recommended: Two Terminal Windows

**Terminal 1 - Backend (All Logs):**
```bash
tail -f /tmp/theheist-backend.log
```

**Terminal 2 - Backend (Errors Only):**
```bash
tail -f /tmp/theheist-backend.log | grep -E "(ERROR|Exception|Traceback|RuntimeError)" -i --line-buffered --color=always
```

## Quick Health Check

```bash
# Check if services are running
ps aux | grep -E "(python.*run.py|flutter run)" | grep -v grep

# Check last 50 lines for errors
tail -50 /tmp/theheist-backend.log | grep -E "(ERROR|Exception)" -i
```

## Why Your Current Filter Misses Things

Your filter: `grep -E "(🎭|📢|✅|❌|📤)"`

**Misses:**
- ❗ ERROR messages (they say "ERROR:" not have ❌)
- ❗ Tracebacks (Python exception stack traces)
- ❗ WARNING messages
- ❗ RuntimeError, ValueError, etc.
- ❗ WebSocket disconnects/crashes

**Better for debugging:**
```bash
# Shows errors AND your emoji markers
tail -f /tmp/theheist-backend.log | grep -E "(ERROR|Exception|🎭|📢|✅|❌|📤|role|player)" -i --line-buffered
```
