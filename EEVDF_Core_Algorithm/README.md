# ⚙️ EEVDF (Earliest Eligible Virtual Deadline First) - Core Algorithm

This directory contains the foundational explanation, mathematical formulation, pseudocode, and pure Python implementation of the **EEVDF** CPU scheduling algorithm.

---

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

---

## 📝 EEVDF Algorithm Pseudocode

```text
ALGORITHM: EEVDF_Scheduler(Task_Queue)
-------------------------------------------------------------------------
INPUT: A set of active tasks T = {T_1, T_2, ..., T_n}
       Each task T_i has: weight (w_i), requested_slice (r_i), vruntime (v_i)

WHILE Active_Tasks is not empty DO:
    
    // Step 1: Compute System Virtual Time (Weighted Average)
    Total_Weight = SUM(w_i for all T_i in Active_Tasks)
    Avg_VRuntime = SUM(v_i * w_i for all T_i in Active_Tasks) / Total_Weight

    // Step 2: Filter Eligible Tasks (Tasks with Lag >= 0)
    Eligible_Set = EMPTY_LIST
    FOR EACH task T_i in Active_Tasks DO:
        IF T_i.vruntime <= Avg_VRuntime THEN:
            ADD T_i to Eligible_Set
        END IF
    END FOR

    // Step 3: Calculate Virtual Deadlines for Eligible Tasks
    FOR EACH task T_i in Eligible_Set DO:
        T_i.virtual_deadline = T_i.vruntime + (T_i.requested_slice / T_i.weight)
    END FOR

    // Step 4: Select Task with Earliest Virtual Deadline
    Selected_Task = MIN_BY(Eligible_Set, key = virtual_deadline)

    // Step 5: Execute Selected Task for Δt and Update Virtual Runtime
    EXECUTE(Selected_Task, Δt)
    Selected_Task.remaining_burst = Selected_Task.remaining_burst - Δt
    Selected_Task.vruntime = Selected_Task.vruntime + (Δt / Selected_Task.weight)

    IF Selected_Task.remaining_burst == 0 THEN:
        REMOVE Selected_Task from Active_Tasks
    END IF

END WHILE
