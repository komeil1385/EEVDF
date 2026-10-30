EEVDF

Earliest Eligible Virtual Deadline First

A fair CPU scheduling algorithm in the Linux kernel’s fair scheduling class

Two core concepts

1 · ELIGIBILITY

lag ≥ 0

lag = ideal fair share − CPU time actually received

An eligible task has received no more than its fair share.

2 · VIRTUAL DEADLINE

vd = ve + slice / weight

Measured in **virtual time** — not wall-clock time, and not a real-time guarantee.

Used to order the eligible tasks.

Eligibility decides **who may run**. Virtual deadline decides **who runs first**.

Scheduling process

Ready queue

Task A Eligible · lag ≥ 0 vd 12

Task B Eligible · lag ≥ 0 vd 8

Task C Ineligible · lag \< 0

CPU

**1 · Examine** each task’s eligibility by checking its lag.

**2 · Exclude** ineligible tasks — C already received more than its fair share.

**3 · Compare** virtual deadlines of the eligible tasks only.

**4 · Select** the eligible task with the earliest virtual deadline: B.

**5 · Dispatch** Task B to the CPU.

1 Examine

2 Exclude

3 Compare

4 Select

5 Dispatch

Example: virtual-time axis

0

virtual time →

Task A\
vd = 12

Eligible

Task B\
vd = 8

Eligible

Task C\
vd = 5

Ineligible ✗ skipped

Selected: Task B

Earliest virtual deadline **among eligible tasks**. Task C’s smaller deadline is irrelevant — ineligible tasks are excluded first.

Summary

Fairness — EEVDF aims to distribute CPU time fairly.

Eligibility — determines which tasks can be selected.

Earliest virtual deadline — picks which eligible task runs next.

EEVDF – Earliest Eligible Virtual Deadline First

0:00 / 1:30