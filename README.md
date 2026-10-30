# Earliest Eligible Virtual Deadline First (EEVDF)
# 🖥️ Operating Systems Projects: EEVDF Scheduler

Welcome to the central repository for my Operating Systems course assignments. This repository focuses on the implementation, synchronization, and comparative analysis of the **EEVDF (Earliest Eligible Virtual Deadline First)** CPU scheduling algorithm—the modern proportional-share scheduler adopted in the Linux kernel (v6.6+).

---

## 📂 Repository Structure & Assignments

This repository is organized into dedicated directories for each assignment:

| Directory / Assignment | Description | Status |
| :--- | :--- | :---: |
| 📁 **[`EEVDF_Core_Algorithm`](./EEVDF_Core_Algorithm)** | Pure Python implementation of **EEVDF**, mathematical formulation (Lag & Virtual Deadline), and formal **Pseudocode**. | ✅ Completed |
| 📁 **[`EEVDF_vs_RM_EDF`](./EEVDF_vs_RM_EDF)** | Comparative simulation and benchmark of **EEVDF** against classic real-time algorithms (**Rate Monotonic** and **Earliest Deadline First**). | ✅ Completed |
| 📁 **[`EEVDF_with_Semaphore`](./EEVDF_with_Semaphore)** | Implementation of the EEVDF scheduler integrated with POSIX-style **Semaphore** synchronization (`threading.Semaphore`). | ✅ Completed |
| 📁 **[`EEVDF_with_Monitor`](./EEVDF_with_Monitor)** | Object-oriented implementation of EEVDF encapsulated inside a **Monitor** (`threading.Condition`) with comparison against Semaphores. | ✅ Completed |
| 📁 **[`EEVDF_Semaphore_and_Monitor`](./EEVDF_Semaphore_and_Monitor)** | Unified implementation and comparative documentation of EEVDF using both Semaphores and Monitors. | ✅ Completed |
| 📝 **[`RM_&_EDF_Gantt_Chart`](./RM_EDF_Gantt_Chart)** | Visual Gantt chart timeline simulation and comparison between Rate Monotonic (RM) and Earliest Deadline First (EDF). | ✅ Completed |
| 📲 **[`EEVDF_Simulation`](https://komeil1385.github.io/EEVDF/EEVDF_Simulation/)** | Complete interactive simulation of the EEVDF scheduler showcasing queue management, eligibility filtering, and performance graphs. | ✅ Completed |
---

## 📺 Technical Talk: EEVDF in the Linux Kernel

[![EEVDF is the new (sched_)normal](https://img.youtube.com/vi/5jIbEzTdTks/0.jpg)](https://youtu.be/5jIbEzTdTks)

> **Conference Talk:** [Michal Koutný: EEVDF is the new (sched_)normal (SUSE Labs)](https://youtu.be/5jIbEzTdTks) — Explores the mathematical model of EEVDF, task lag, eligibility, virtual deadlines, and how it replaces CFS in the Linux kernel.

## 🚀 Quick Start

To clone this repository and run the simulations locally:

```bash
# Clone the repository
git clone [https://github.com/komeil1385/EEVDF.git](https://github.com/komeil1385/EEVDF.git)

# Navigate into the main directory
cd EEVDF

# Run the EEVDF + Semaphore simulation
python EEVDF_with_Semaphore/eevdf_semaphore.py

# Run the RM vs. EDF vs. EEVDF comparison benchmark
python EEVDF_vs_RM_EDF/compare_schedulers.py
