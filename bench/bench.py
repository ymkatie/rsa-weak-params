"""Generic benchmark harness. Every attack plugs into run_sweep().

You supply:
  make_key(param)  -> dict with at least N, e (plus anything the attack needs);
                      an optional 'log' dict adds per-key columns to the CSV
  attack(key)      -> dict of results (e.g. recovered p, q, 'iterations',
                      'queries'); only this call is timed
  check(key, out)  -> True if the attack really broke the key (run untimed)
The harness times the attack, repeats it `trials` times per parameter value,
and writes one CSV row per trial to results/<name>.csv.
"""
import csv
import os
import time

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")


def run_sweep(name, param_name, values, make_key, attack, check, trials=5, verbose=True):
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, f"{name}.csv")
    rows = []
    for v in values:
        for t in range(trials):
            key = make_key(v)
            start = time.perf_counter()
            out = attack(key)
            elapsed = time.perf_counter() - start
            success = bool(check(key, out))
            # recovered secrets are not logged, only the measurements
            logged = {k: val for k, val in out.items() if not k.startswith("_")}
            row = {param_name: v, "trial": t, "n_bits": key["N"].bit_length(),
                   "success": success, "time_s": elapsed, **logged,
                   **key.get("log", {})}
            rows.append(row)
        if verbose:
            ok = sum(r["success"] for r in rows if r[param_name] == v)
            times = sorted(r["time_s"] for r in rows if r[param_name] == v)
            print(f"{param_name}={v:>4}: {ok}/{trials} succeeded, "
                  f"median {times[len(times) // 2]:.4f}s")

    fields = list(dict.fromkeys(k for r in rows for k in r))  # keep column order
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    if verbose:
        print(f"Saved {len(rows)} rows -> {path}")
    return path
