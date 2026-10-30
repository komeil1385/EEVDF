# 📊 RM vs. EDF Gantt Chart Comparison & Scheduling Analysis

This directory contains a Python-based simulation and visual text-based **Gantt Chart** generator comparing **Rate Monotonic (RM)** and **Earliest Deadline First (EDF)** real-time CPU scheduling algorithms.

---

## 📌 Overview of the Simulation

In hard real-time systems, visualizing the execution timeline via Gantt charts helps identify preemption points, CPU idle times, and potential deadline violations.

* **Rate Monotonic (RM):** Assigns static priorities based on task periods/deadlines. A task with a shorter period receives a higher static priority throughout its lifetime.
* **Earliest Deadline First (EDF):** Assigns dynamic priorities based on absolute deadlines. The task with the nearest absolute deadline is always executed first.

---

## 📈 Visual Gantt Chart Comparison

Below is the simulated execution timeline generated under heavy utilization workload:

### 1. Rate Monotonic (RM) Gantt Chart
```text
| T1 | T1 | T2 | T2 | T2 |
0    1    2    3    4    5

### 2. Earliest Deadline First (EDF) Gantt Chart
```text
| T1 | T1 | T2 | T2 | T2 |
0    1    2    3    4    5
