# 🔒🖥️ EEVDF Scheduling with Semaphore and Monitor Synchronization

This directory contains the implementation and comparative documentation of the **EEVDF (Earliest Eligible Virtual Deadline First)** CPU scheduling algorithm synchronized using two fundamental Operating System primitives: **Semaphores** and **Monitors**.

## 📌 Architectural Overview

In a concurrent operating system, multiple threads compete for shared execution resources (Critical Sections). This project demonstrates how EEVDF arbitrates access using both low-level and high-level synchronization mechanisms:

### 1. EEVDF with Semaphore (`threading.Semaphore`)
A **Semaphore** is a low-level signaling mechanism defined by an integer counter and two atomic operations:
* **Wait / P Operation (`acquire()`):** Decrements the semaphore value. If the value is `0`, the calling thread blocks until signaled.
* **Signal / V Operation (`release()`):** Increments the semaphore value, waking a blocked thread.
* **Implementation Logic:** An external scheduler loop computes EEVDF eligibility ($vruntime_i \le \overline{V}$) and virtual deadlines ($V_d = vruntime_i + \frac{r_i}{w_i}$), signaling the winning thread via an event flag to acquire the binary semaphore (`Semaphore(1)`).

### 2. EEVDF with Monitor (`threading.Condition`)
A **Monitor** is a high-level, object-oriented synchronization construct that encapsulates shared state, mutual exclusion locks, and condition variables inside a single class (`EEVDFMonitor`):
* **Mutual Exclusion:** Automatically enforced upon entering `request_cpu()` and `release_cpu()` procedures via `with self.condition:`.
* **Condition Synchronization (`wait()` / `notify_all()`):** Threads evaluate the EEVDF guard condition inside a Mesa-style `while` loop. If a thread is not selected by EEVDF, it calls `condition.wait()`, atomically releasing the lock and sleeping until the active thread exits and broadcasts `condition.notify_all()`.

## ⚖️ Structural Comparison: Semaphore vs. Monitor in EEVDF

| Feature | Semaphore Implementation | Monitor Implementation |
| :--- | :--- | :--- |
| **Abstraction Level** | Low-Level Primitive | High-Level Object-Oriented Class |
| **State Encapsulation** | Global / External Scheduler | Fully Encapsulated inside `EEVDFMonitor` |
| **Synchronization Primitives** | `Semaphore(1)` + `Event()` | `Lock()` + `Condition()` |
| **Wakeup Mechanism** | Direct Event Signaling (`set()`) | Broadcast Condition (`notify_all()`) |
| **Safety & Maintainability** | Prone to manual `release()` omissions | Immune to lock leaks via context managers |

## 📊 Simulation Benchmark & Output

Both synchronization models are tested against an identical workload: two heavy batch threads (`P1`, `P2` with `slice = 4`) and one latency-sensitive interactive thread (`P3` arriving at `t = 1` with `slice = 1`).

### Execution Results (Identical Across Both Models)

| Process ID | Arrival | Burst | Slice ($r_i$) | Finish | Turnaround | Waiting | Response |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1 (Heavy-Batch)** | 0 | 4 | 4 | 9 | 9 | 5 | 0 |
| **P2 (Heavy-Batch)** | 0 | 4 | 4 | 10 | 10 | 6 | 1 |
| **P3 (Interactive)** | 1 | 2 | 1 | 5 | 4 | 2 | **1** |

* **Execution Timeline:** `P1 -> P2 -> P3 -> P1 -> P3 -> P2 -> P1 -> P2 -> P1 -> P2`
* **Average Waiting Time:** `4.33`
* **Average Turnaround Time:** `7.67`
* **Average Response Time:** `0.67`

## 🚀 How to Run

```bash
python eevdf_sync_comparison.py
