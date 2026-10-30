import threading
import time
import copy

# Helper lock for clean console output
print_lock = threading.Lock()


# =====================================================================
# PART 1: EEVDF WITH SEMAPHORE IMPLEMENTATION
# =====================================================================
class SemaphoreProcess(threading.Thread):
    def __init__(self, pid, arrival, burst, weight, time_slice, sem, step_done):
        super().__init__()
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.weight = weight
        self.slice = time_slice

        self.vruntime = 0.0
        self.v_deadline = 0.0
        self.completed = False
        self.first_run = -1
        self.completion_time = 0

        self.sem = sem
        self.turn_event = threading.Event()
        self.step_done = step_done

    def run(self):
        while not self.completed:
            self.turn_event.wait()
            if self.completed:
                break

            # Wait / P Operation on Binary Semaphore
            self.sem.acquire()

            self.remaining -= 1
            self.vruntime += 1.0 / self.weight
            time.sleep(0.01)

            # Signal / V Operation on Binary Semaphore
            self.sem.release()

            self.turn_event.clear()
            self.step_done.set()


def run_semaphore_eevdf(workload_specs):
    cpu_semaphore = threading.Semaphore(1)
    step_done = threading.Event()
    processes = [
        SemaphoreProcess(
            w['pid'], w['arrival'], w['burst'], w['weight'], w['slice'], cpu_semaphore, step_done
        )
        for w in workload_specs
    ]

    current_time = 0
    completed_count = 0
    n = len(processes)
    timeline = []

    for p in processes:
        p.start()

    while completed_count < n:
        active = [p for p in processes if p.arrival <= current_time and not p.completed]
        if not active:
            timeline.append("IDLE")
            current_time += 1
            continue

        # 1. Eligibility Filter (Lag >= 0)
        avg_vruntime = sum(p.vruntime for p in active) / len(active)
        eligible = [p for p in active if p.vruntime <= avg_vruntime] or active

        # 2. Virtual Deadline Calculation
        for p in eligible:
            p.v_deadline = p.vruntime + (p.slice / p.weight)

        eligible.sort(key=lambda x: (x.v_deadline, x.arrival))
        selected = eligible[0]

        if selected.first_run == -1:
            selected.first_run = current_time

        timeline.append(selected.pid.split()[0])
        step_done.clear()
        selected.turn_event.set()
        step_done.wait()

        current_time += 1

        if selected.remaining == 0:
            selected.completed = True
            selected.completion_time = current_time
            completed_count += 1
            selected.turn_event.set()

    for p in processes:
        p.join()

    return processes, " -> ".join(timeline)


# =====================================================================
# PART 2: EEVDF WITH MONITOR IMPLEMENTATION
# =====================================================================
class EEVDFMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.current_time = 0
        self.cpu_busy = False
        self.threads = []
        self.timeline = []

    def register(self, t):
        with self.lock:
            self.threads.append(t)

    def _select_next(self):
        ready = [t for t in self.threads if t.arrival <= self.current_time and not t.completed]
        if not ready:
            return None

        avg_vruntime = sum(t.vruntime for t in ready) / len(ready)
        eligible = [t for t in ready if t.vruntime <= avg_vruntime] or ready

        for t in eligible:
            t.v_deadline = t.vruntime + (t.slice / t.weight)

        eligible.sort(key=lambda x: (x.v_deadline, x.arrival))
        return eligible[0]

    def request_cpu(self, thread):
        with self.condition:
            while True:
                ready = [t for t in self.threads if t.arrival <= self.current_time and not t.completed]
                if not ready and not self.cpu_busy:
                    self.timeline.append("IDLE")
                    self.current_time += 1
                    self.condition.notify_all()
                    continue

                selected = self._select_next()
                if not self.cpu_busy and selected == thread:
                    self.cpu_busy = True
                    if thread.first_run == -1:
                        thread.first_run = self.current_time
                    self.timeline.append(thread.pid.split()[0])
                    break
                else:
                    self.condition.wait()

    def release_cpu(self, thread):
        with self.condition:
            thread.remaining -= 1
            thread.vruntime += 1.0 / thread.weight
            self.current_time += 1

            if thread.remaining == 0:
                thread.completed = True
                thread.completion_time = self.current_time

            self.cpu_busy = False
            self.condition.notify_all()


class MonitorProcess(threading.Thread):
    def __init__(self, pid, arrival, burst, weight, time_slice, monitor):
        super().__init__()
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.weight = weight
        self.slice = time_slice
        self.monitor = monitor

        self.vruntime = 0.0
        self.v_deadline = 0.0
        self.completed = False
        self.first_run = -1
        self.completion_time = 0

    def run(self):
        while not self.completed:
            self.monitor.request_cpu(self)
            time.sleep(0.01)
            self.monitor.release_cpu(self)


def run_monitor_eevdf(workload_specs):
    monitor = EEVDFMonitor()
    processes = [
        MonitorProcess(w['pid'], w['arrival'], w['burst'], w['weight'], w['slice'], monitor)
        for w in workload_specs
    ]
    for p in processes:
        monitor.register(p)
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    return processes, " -> ".join(monitor.timeline)


# =====================================================================
# BENCHMARK RUNNER & OUTPUT TABLE
# =====================================================================
def print_metrics(title, processes, timeline):
    n = len(processes)
    print("\n" + "=" * 86)
    print(f"📊 {title}")
    print("=" * 86)
    print(f"Execution Timeline: {timeline}\n")
    print(
        f"{'Process ID':<18} | {'Arrival':<7} | {'Burst':<5} | {'Slice':<5} | "
        f"{'Finish':<6} | {'Turnaround':<10} | {'Waiting':<7} | {'Response':<8}"
    )
    print("-" * 86)

    total_wait, total_turn, total_resp = 0, 0, 0
    for p in processes:
        turn = p.completion_time - p.arrival
        wait = turn - p.burst
        resp = p.first_run - p.arrival
        total_turn += turn
        total_wait += wait
        total_resp += resp
        print(
            f"{p.pid:<18} | {p.arrival:<7} | {p.burst:<5} | {p.slice:<5} | "
            f"{p.completion_time:<6} | {turn:<10} | {wait:<7} | {resp:<8}"
        )

    print("-" * 86)
    print(
        f"Averages -> Waiting: {total_wait / n:.2f} | "
        f"Turnaround: {total_turn / n:.2f} | "
        f"Response (Latency): {total_resp / n:.2f}"
    )
    print("=" * 86)


if __name__ == "__main__":
    workload = [
        {'pid': 'P1 (Heavy-Batch)', 'arrival': 0, 'burst': 4, 'weight': 1, 'slice': 4},
        {'pid': 'P2 (Heavy-Batch)', 'arrival': 0, 'burst': 4, 'weight': 1, 'slice': 4},
        {'pid': 'P3 (Interactive)', 'arrival': 1, 'burst': 2, 'weight': 1, 'slice': 1},
    ]

    sem_procs, sem_tl = run_semaphore_eevdf(copy.deepcopy(workload))
    print_metrics("1. EEVDF with SEMAPHORE Synchronization", sem_procs, sem_tl)

    mon_procs, mon_tl = run_monitor_eevdf(copy.deepcopy(workload))
    print_metrics("2. EEVDF with MONITOR Synchronization", mon_procs, mon_tl)
