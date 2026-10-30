# Earliest Eligible Virtual Deadline First (EEVDF)
# 🖥️ Operating Systems Projects: EEVDF Scheduler

Welcome to the central repository for my Operating Systems course assignments. This repository focuses on the implementation, synchronization, and comparative analysis of the **EEVDF (Earliest Eligible Virtual Deadline First)** CPU scheduling algorithm—the modern proportional-share scheduler adopted in the Linux kernel (v6.6+).

---

## 📂 Repository Structure & Assignments

This repository is organized into dedicated directories for each assignment:

| Directory / Assignment | Description | Status |
| :--- | :--- | :---: |
| 📁 **[`EEVDF_with_Semaphore`](./EEVDF_with_Semaphore)** | Implementation of the EEVDF scheduler integrated with POSIX-style **Semaphore** synchronization (`threading.Semaphore`). | ✅ Completed |
| 📁 **[`EEVDF_vs_RM_EDF`](./EEVDF_vs_RM_EDF)** | Comparative simulation and benchmark of **EEVDF** against classic real-time algorithms (**Rate Monotonic** and **Earliest Deadline First**). | ✅ Completed |
| 📁 **[`EEVDF_with_Monitor`](./EEVDF_with_Monitor)** | Object-oriented implementation of EEVDF encapsulated inside a **Monitor** (`threading.Condition`) with comparison against Semaphores. | ✅ Completed |
| 📁 **[`EEVDF_Core_Algorithm`](./EEVDF_Core_Algorithm)** | Pure Python implementation of **EEVDF**, mathematical formulation (Lag & Virtual Deadline), and formal **Pseudocode**. | ✅ Completed |

---

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
