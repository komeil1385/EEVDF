#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ex6_comparison_demo.py — Exercise 6: Peterson vs Dekker vs Semaphore vs Monitor.
Same workload for all four mechanisms: two threads increment a shared
counter NITER times each. Correct final value = 2 * NITER.

Run:  python3 ex6_comparison_demo.py

Experiments:
  0. No synchronization (baseline — shows the race condition)
  1. Peterson's algorithm (flag + turn, busy waiting)
  2. Dekker's algorithm   (flag + turn + back-off, busy waiting)
  3. Binary semaphore     (threading.Semaphore(1), blocking)
  4. Monitor              (threading.Lock + Condition, blocking;
                           here the "monitor" is a tiny Counter class
                           whose only methods touch the shared data)

Same warning as in the documents: Peterson/Dekker are teaching
demos, not production code. CPython's GIL makes the plain bool/int
assignments work reliably in practice here, but Python gives no
memory-ordering guarantee like C11 _Atomic. In real programs use
threading.Lock / Semaphore (experiments 3-4).
"""
import threading
import time

NITER = 20_000
EXPECTED = 2 * NITER


def run_pair(name, worker):
    counter = [0]
    t0 = threading.Thread(target=worker, args=(0, counter))
    t1 = threading.Thread(target=worker, args=(1, counter))
    t0.start(); t1.start(); t0.join(); t1.join()
    ok = "OK " if counter[0] == EXPECTED else "FAIL"
    print(f"[{name:<10}] counter = {counter[0]} (expected {EXPECTED})  {ok}")
    return counter[0]


def no_sync(_i, counter):
    # Load-increment-store written out in full, with a scheduling
    # point between the load and the store — exactly the unlucky
    # interleaving a real machine produces from time to time.
    # (A bare `counter[0] += 1` in CPython usually *happens* to
    # give the right answer, because the GIL rarely switches
    # inside those few bytecodes; that would hide the race.)
    for _ in range(NITER):
        value = counter[0]      # load
        time.sleep(0)           # another thread may run here
        counter[0] = value + 1  # store


def peterson(my_id, counter):
    other = 1 - my_id
    for _ in range(NITER):
        flag[my_id] = True
        turn[0] = other
        while flag[other] and turn[0] == other:
            time.sleep(0)
        counter[0] += 1
        flag[my_id] = False


def dekker(my_id, counter):
    other = 1 - my_id
    for _ in range(NITER):
        flag[my_id] = True
        while flag[other]:
            if turn[0] != my_id:
                flag[my_id] = False
                while turn[0] != my_id:
                    time.sleep(0)
                flag[my_id] = True
        counter[0] += 1
        turn[0] = other
        flag[my_id] = False


sem = threading.Semaphore(1)  # binary semaphore, initial value 1
def semaphore_worker(_i, counter):
    for _ in range(NITER):
        sem.acquire()       # wait / P
        counter[0] += 1     # critical section
        sem.release()       # signal / V


class CounterMonitor:
    """Tiny monitor: data is private; only increment() touches it;
    the lock guarantees at most one thread inside at a time."""
    def __init__(self):
        self._lock = threading.Lock()
        self.value = 0
    def increment(self):
        with self._lock:     # enter monitor procedure
            self.value += 1  # exit monitor procedure (lock released)


monitor = CounterMonitor()
def monitor_worker(_i, counter):
    for _ in range(NITER):
        monitor.increment()
    counter[0] = monitor.value


if __name__ == "__main__":
    print(f"Workload: 2 threads x {NITER} increments; expected = {EXPECTED}\n")
    print("0. Baseline (no synchronization) — the race condition:")
    run_pair("none", no_sync)
    print("\n1-2. Software algorithms (busy waiting, 2 processes only):")
    flag = [False, False]; turn = [0]
    run_pair("peterson", peterson)
    flag = [False, False]; turn = [0]
    run_pair("dekker", dekker)
    print("\n3-4. Blocking primitives (any number of processes):")
    run_pair("semaphore", semaphore_worker)
    run_pair("monitor", monitor_worker)
    print("\nSummary: all four mechanisms give the exact final value;")
    print("the baseline loses updates (the race condition).")
    print("Peterson/Dekker spin while waiting; semaphore/monitor block.")
