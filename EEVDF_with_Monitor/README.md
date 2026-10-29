# 🖥️ EEVDF CPU Scheduling with Monitor Synchronization

This directory contains a Python implementation of the **EEVDF (Earliest Eligible Virtual Deadline First)** scheduling algorithm encapsulated within a high-level **Monitor** synchronization construct (`threading.Condition` and `threading.Lock`).

Unlike low-level Semaphores where threads manually manage `acquire()` and `release()` primitives across scattered codeblocks, a **Monitor** encapsulates shared data, scheduling state, and synchronization procedures inside a single thread-safe class (`EEVDFMonitor`).

---

## 📌 System Architecture & Monitor Design

### 1. What is a Monitor in OS?
A **Monitor** (introduced by Per Brinch Hansen and C.A.R. Hoare) is a high-level synchronization abstraction composed of:
* **Private Shared State:** `current_time`, `cpu_busy`, and the list of registered threads.
* **Mutual Exclusion Lock (`threading.Lock`):** Ensures only one thread can execute a Monitor procedure at any instant.
* **Condition Variables (`threading.Condition`):** Allows threads whose scheduling guard conditions are not met to block (`wait()`) and automatically release the lock until signaled (`notify_all()`).

### 2. EEVDF Arbitration Inside the Monitor
Threads interact with the CPU exclusively through two Monitor procedures:
1. **`request_cpu(process)` (Entry Procedure):**
   * Evaluates the EEVDF policy inside a `while` loop (Mesa-style Monitor semantics).
   * Filters **Eligible Tasks** whose virtual runtime satisfies $vruntime_i \le \overline{vruntime}$.
   * Computes the **Virtual Deadline** for each eligible thread:
     $$V_{deadline} = vruntime_i + \frac{\text{Time Slice}_i}{\text{Weight}_i}$$
   * If the CPU is busy or the calling thread does not hold the earliest virtual deadline, the thread calls `condition.wait()`, atomically releasing the lock and sleeping.
2. **`release_cpu(process)` (Exit Procedure):**
   * Updates the thread's `vruntime` and remaining burst time.
   * Marks the CPU as free and invokes `condition.notify_all()` to wake waiting threads so the next EEVDF winner can proceed.

---

## ⚖️ Comparison: Semaphore vs. Monitor Implementation

| Feature / Aspect | Semaphore (`EEVDF_with_Semaphore`) | Monitor (`EEVDF_with_Monitor`) |
| :--- | :---: | :---: |
| **Abstraction Level** | Low-Level Primitive | **High-Level Object-Oriented Construct** |
| **State Encapsulation** | External (Global variables & events) | **Fully Encapsulated (`EEVDFMonitor` class)** |
| **Synchronization Mechanism** | `acquire()` / `release()` counters | **Mutex Lock + Condition Variables (`wait` / `notify_all`)** |
| **Error Vulnerability** | High (Forgotten `release()` causes deadlock) | **Low (Automatic lock management via `with self.condition`)** |
| **Condition Evaluation** | External scheduler thread | **Self-governed via Mesa-style `while` guard loops** |

---

## 📊 Simulation Benchmark & Results

The simulation runs three concurrent threads (`P1`, `P2` as heavy batch tasks with `slice = 4`, and `P3` as an interactive task arriving at `t = 1` with `slice = 1`).

### Output Metrics Table

| Process ID | Arrival | Burst | Slice | Completion | Turnaround | Waiting | Response |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1 (Heavy-Batch)** | 0 | 4 | 4 | 9 | 9 | 5 | 0 |
| **P2 (Heavy-Batch)** | 0 | 4 | 4 | 10 | 10 | 6 | 1 |
| **P3 (Interactive)** | 1 | 2 | 1 | 5 | 4 | 2 | **1** |

* **Average Waiting Time:** `4.33`
* **Average Turnaround Time:** `7.67`
* **Average Response Time:** `0.67`

### 💡 Key Takeaways
* **Identical Algorithmic Accuracy, Superior Safety:** The Monitor produces the exact same optimal EEVDF schedule as the Semaphore implementation (`Response Time = 0.67`), proving that encapsulating the scheduler inside a Monitor introduces zero scheduling degradation while eliminating race conditions and manual signaling bugs.
* **Mesa Monitor Semantics:** Using a `while` loop around `self.condition.wait()` protects the EEVDF scheduler against *spurious wakeups*—a critical requirement in real-world OS kernel monitors.

---

## 🚀 How to Run

Requires **Python 3.x** (no external packages needed).

```bash
# Clone the repository
git clone [https://github.com/komeil1385/EEVDF.git](https://github.com/komeil1385/EEVDF.git)

# Navigate to the Monitor directory
cd EEVDF/EEVDF_with_Monitor

# Run the Monitor simulation
python eevdf_monitor.py
