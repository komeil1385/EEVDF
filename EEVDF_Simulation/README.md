# EEVDF Scheduler Simulator
Interactive, educational single-CPU simulator of Earliest Eligible Virtual Deadline First. Vanilla HTML/CSS/JS, no backend.

## Run
Open `index.html` in a browser, or publish the folder with GitHub Pages (Settings → Pages → deploy from branch). `node tests.js` runs the scheduler checks.

## Model (integer ticks, one CPU)
| Quantity | Formula |
|---|---|
| virtual runtime | `v += 1/w` per executed tick |
| virtual time | `V = Σ(w·v) / Σw` over runnable tasks |
| lag | `w·(V − v)`; eligible when `lag ≥ 0` |
| virtual deadline | `d = v + q/w`, renewed when a slice is requested |

New tasks join with `v = V` (lag 0). When the CPU is free the scheduler runs the eligible task with the smallest `d` (ties: lowest task number) for `min(q, remaining)` ticks. Ineligible tasks are skipped even with an earlier deadline, so this is not EDF.

## Not modeled (differs from Linux)
Multi-CPU, wakeup preemption, nice-to-weight tables, per-task slices, lag clamping and sleeper placement, cgroups, fixed-point math. Statistics are illustrative, not kernel measurements.

## Files
`script.js` holds the pure engine (`EEVDF`, no DOM) and, below it, the UI. `tests.js` imports the engine in Node.
