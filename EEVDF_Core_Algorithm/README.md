# ⚙️ EEVDF (Earliest Eligible Virtual Deadline First) - Core Algorithm

This directory contains the foundational explanation, mathematical formulation, and pure Python implementation of the **EEVDF** CPU scheduling algorithm.

## 📌 What is EEVDF?

**Earliest Eligible Virtual Deadline First (EEVDF)** is a proportional-share CPU scheduling algorithm introduced by Ion Stoica and Hussein Abdel-Wahab (1995) and merged into the **Linux Kernel (v6.6)** as the replacement for the Completely Fair Scheduler (CFS).

While CFS only focuses on equalizing `vruntime` (which often causes high latency for interactive tasks), EEVDF introduces two distinct concepts to achieve both **strict fairness** and **low latency**:

### 1. Lag & Eligibility ($Lag_i \ge 0$)
Every task $i$ has an associated weight $w_i$. **Lag** measures the difference between the CPU time a task *should* have received in an ideal fluid system and the actual service it received:
$$Lag_i(t) = S_i(t) - s_i(t)$$

* A task is **Eligible** to be scheduled if and only if its lag is non-negative ($Lag_i \ge 0$), meaning its virtual runtime (`vruntime`) is less than or equal to the system's weighted average virtual runtime ($\overline{V}$):
  $$\text{Eligible}(i) \iff vruntime_i \le \overline{V}$$

### 2. Virtual Deadline ($V_{deadline}$)
Each task requests a specific time slice (quantum) $r_i$. To prioritize latency-sensitive tasks without breaking fairness, EEVDF computes a **Virtual Deadline** for every eligible task:
$$V_{deadline}(i) = vruntime_i + \frac{r_i}{w_i}$$

* **Heavy/Batch Tasks:** Request large time slices ($r_i$), resulting in further virtual deadlines.
* **Interactive Tasks:** Request small time slices ($r_i$), receiving early virtual deadlines and immediate CPU execution.

## 🔄 Step-by-Step Execution Flow

1. **System Virtual Time Calculation:** At each scheduling decision point, the scheduler calculates the weighted average of `vruntime` across all active tasks in the runqueue.
2. **Eligibility Filtering:** Tasks with `vruntime` greater than the system average (negative lag) are temporarily filtered out because they have already consumed more than their fair share. Only tasks with `vruntime <= average` enter the eligible pool.
3. **Deadline Arbitration:** Among the eligible tasks, the scheduler calculates $V_{deadline}$ based on each task's requested quantum ($r_i$) and weight ($w_i$), granting the CPU to the task with the minimum virtual deadline.
4. **Virtual Runtime Update:** As the chosen task executes for $\Delta t$, its virtual runtime increases inversely proportional to its weight:
   $$vruntime_{new} = vruntime_{old} + \frac{\Delta t}{w_i}$$

## 📊 Sample Simulation Output

| Task ID | Arrival | Burst | Weight | Slice ($r_i$) | Finish | Turnaround | Waiting | Response |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **T1 (Batch)** | 0 | 4 | 1 | 4 | 9 | 9 | 5 | 0 |
| **T2 (Batch)** | 0 | 4 | 1 | 4 | 10 | 10 | 6 | 1 |
| **T3 (Interactive)** | 1 | 2 | 2 | 1 | 4 | 3 | 1 | **0** |

* **Execution Timeline:** `T1 -> T3 -> T2 -> T3 -> T1 -> T2 -> T1 -> T2 -> T1 -> T2`
* **Average Waiting Time:** `4.00`
* **Average Turnaround Time:** `7.33`
* **Average Response Time:** `0.33`

## Execution Preview

The following screenshot shows the EEVDF simulator
during execution.

![EEVDF Simulator](result.png)

## 📑 Technical Documentation & Reports

The complete theoretical and technical documentation for the core EEVDF algorithm is available in both English and Persian:

* 🇬🇧 **English Version (`document_english.docx`):**  
  [![Preview EN](https://img.shields.io/badge/Live_Preview-English_Report-blue?style=flat-square)](https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fraw.githubusercontent.com%2Fkomeil1385%2FEEVDF%2Fmain%2FEEVDF_Core_Algorithm%2Fdocument_english.docx)
  [![Download EN](https://img.shields.io/badge/Download-.docx-success?style=flat-square)](./document_english.docx)

* 🇮🇷 **Persian Version (`document_farsi.docx`):**  
  [![Preview FA](https://img.shields.io/badge/پیش‌نمایش_آنلاین-گزارش_فارسی-blue?style=flat-square)](https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fraw.githubusercontent.com%2Fkomeil1385%2FEEVDF%2Fmain%2FEEVDF_Core_Algorithm%2Fdocument_farsi.docx)
  [![Download FA](https://img.shields.io/badge/دانلود_فایل-.docx-success?style=flat-square)](./document_farsi.docx)
