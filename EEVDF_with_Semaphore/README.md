# 🔒 EEVDF CPU Scheduling with Semaphore Synchronization

This repository contains a Python implementation of the **EEVDF (Earliest Eligible Virtual Deadline First)** scheduling algorithm integrated with **POSIX-style Semaphore synchronization** (`threading.Semaphore`). 

The project demonstrates how modern operating systems combine proportional-share CPU scheduling with mutual exclusion primitives to manage concurrent threads safely while minimizing latency for interactive tasks.

---

## 📌 System Architecture & Logic

### 1. Semaphore Synchronization (Mutual Exclusion)
Each process is modeled as an independent concurrent thread (`threading.Thread`) competing for a shared resource (the CPU / Critical Section). A binary semaphore (`threading.Semaphore(1)`) guards the critical section:
* **Wait / P Operation (`acquire()`):** Ensures only the scheduled thread can enter the critical section at any given clock tick, preventing race conditions.
* **Signal / V Operation (`release()`):** Executed once the thread completes its time unit, releasing the lock for the next scheduling decision.

### 2. EEVDF Scheduling Policy
Instead of allowing threads to acquire the semaphore in a naive FIFO or random order, the **EEVDF scheduler** arbitrates access based on two core metrics:
1. **Eligibility (Lag $\ge 0$):** A thread is eligible to acquire the semaphore only if its virtual runtime (`vruntime`) is less than or equal to the system average:
   $$\text{Eligible} \iff vruntime_i \le \frac{1}{N} \sum_{j=1}^{N} vruntime_j$$
2. **Virtual Deadline ($V_{deadline}$):** Among eligible threads, the scheduler selects the one with the earliest virtual deadline, calculated using its requested time slice ($r_i$) and weight ($w_i$):
   $$V_{deadline} = vruntime_i + \frac{\text{Time Slice}_i}{\text{Weight}_i}$$

---

## ⚖️ Comparison: Standard Semaphore vs. EEVDF-Arbitrated Semaphore

| Feature / Metric | Standard Semaphore Queue (FIFO) | EEVDF-Arbitrated Semaphore |
| :--- | :---: | :---: |
| **Lock Acquisition Order** | First-Come, First-Served | Earliest Eligible Virtual Deadline |
| **Fairness Guarantee** | Poor (Heavy threads monopolize resource) | **Strict Proportional Fairness (`vruntime`)** |
| **Interactive Task Latency** | High (Convoy Effect) | **Near-Zero (Short slices get early deadlines)** |
| **Starvation Prevention** | Yes | **Yes (via Eligibility filtering)** |

---

## 📊 Simulation Workload & Results

The simulation tests two heavy batch threads (`P1`, `P2`) arriving at `t = 0` with large time slices (`slice = 4`), alongside a latency-sensitive interactive thread (`P3`) arriving at `t = 1` with a small time slice (`slice = 1`).

### Console Output Table

| Process ID | Arrival | Burst | Slice | Completion | Turnaround | Waiting | Response |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1 (Heavy-Batch)** | 0 | 4 | 4 | 9 | 9 | 5 | 0 |
| **P2 (Heavy-Batch)** | 0 | 4 | 4 | 10 | 10 | 6 | 1 |
| **P3 (Interactive)** | 1 | 2 | 1 | 5 | 4 | 2 | **1** |

* **Average Waiting Time:** `4.33`
* **Average Turnaround Time:** `7.67`
* **Average Response Time:** `0.67`

### 💡 Key Observations
When `P3 (Interactive)` arrives at `t = 1`, it immediately becomes eligible (`vruntime = 0.0`). Because it requests a short time slice (`slice = 1`), EEVDF assigns it an early virtual deadline (`v_deadline = 1.0`), allowing it to preempt the heavy batch tasks and acquire the semaphore with minimal latency.

---

## 🚀 How to Run

Requires **Python 3.x** (uses standard library `threading` and `time` modules only).

```bash
# Clone the repository
git clone https://github.com/komeil1385/EEVDF.git

# Navigate to the folder
cd EEVDF_with_Semaphore

# Run the simulation
python eevdf_semaphore.py
