import threading
import time


class EEVDFMonitor:
    """
    A high-level Monitor synchronization construct that encapsulates the shared
    CPU resource, mutual exclusion lock, condition variables, and the EEVDF
    scheduling state inside a single thread-safe object.
    """

    def __init__(self):
        # Monitor's internal mutual exclusion lock and condition variable
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

        # Shared state encapsulated within the Monitor
        self.current_time = 0
        self.cpu_busy = False
        self.active_thread_id = None
        self.registered_threads = []

    def register_thread(self, thread):
        with self.lock:
            self.registered_threads.append(thread)

    def _select_next_eevdf_process(self):
        """Internal Monitor procedure to compute Eligibility and Virtual Deadlines."""
        ready_procs = [
            p for p in self.registered_threads
            if p.arrival <= self.current_time and not p.completed
        ]

        if not ready_procs:
            return None

        # Step 1: Identify Eligible threads (Lag >= 0 -> vruntime <= avg_vruntime)
        avg_vruntime = sum(p.vruntime for p in ready_procs) / len(ready_procs)
        eligible_procs = [p for p in ready_procs if p.vruntime <= avg_vruntime]

        if not eligible_procs:
            eligible_procs = ready_procs

        # Step 2: Calculate Virtual Deadline = vruntime + (slice / weight)
        for p in eligible_procs:
            p.v_deadline = p.vruntime + (p.slice / p.weight)

        # Select thread with the earliest virtual deadline
        eligible_procs.sort(key=lambda x: (x.v_deadline, x.arrival))
        return eligible_procs[0]

    def request_cpu(self, process):
        """
        Monitor Entry Procedure:
        Threads call this method to enter the critical section. If the CPU is busy
        or the thread is not chosen by EEVDF, it waits on the Condition Variable.
        """
        with self.condition:
            while True:
                # Advance idle clock if no tasks have arrived yet
                ready_procs = [
                    p for p in self.registered_threads
                    if p.arrival <= self.current_time and not p.completed
                ]
                if not ready_procs and not self.cpu_busy:
                    self.current_time += 1
                    self.condition.notify_all()
                    continue

                selected = self._select_next_eevdf_process()

                # Guard condition: CPU must be free AND this thread must be selected by EEVDF
                if not self.cpu_busy and selected == process:
                    self.cpu_busy = True
                    self.active_thread_id = process.pid

                    if process.first_run == -1:
                        process.first_run = self.current_time

                    print(
                        f"[Time {self.current_time:2d}] 🖥️ Monitor Entered by  {process.pid:<16} | "
                        f"vruntime: {process.vruntime:4.1f} | v_deadline: {process.v_deadline:4.1f}"
                    )
                    break
                else:
                    # Wait inside the Monitor's condition queue (automatically releases lock)
                    self.condition.wait()

    def release_cpu(self, process):
        """
        Monitor Exit Procedure:
        Updates virtual runtime, advances simulation clock, releases the resource,
        and broadcasts a notification to all waiting threads via the Condition Variable.
        """
        with self.condition:
            process.remaining -= 1
            process.vruntime += 1.0 / process.weight
            self.current_time += 1

            print(
                f"[Time {self.current_time:2d}] ✅ Monitor Exited by   {process.pid:<16} | "
                f"Remaining Burst: {process.remaining}"
            )

            if process.remaining == 0:
                process.completed = True
                process.completion_time = self.current_time

            self.cpu_busy = False
            self.active_thread_id = None

            # Wake up all waiting threads to re-evaluate the EEVDF guard condition
            self.condition.notify_all()


class ProcessThread(threading.Thread):
    def __init__(self, pid, arrival, burst, weight, time_slice, monitor):
        super().__init__()
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.weight = weight
        self.slice = time_slice
        self.monitor = monitor

        # EEVDF metrics
        self.vruntime = 0.0
        self.v_deadline = 0.0

        # Benchmark stats
        self.completed = False
        self.first_run = -1
        self.completion_time = 0

    def run(self):
        while not self.completed:
            # 1. Request access via Monitor Entry Procedure
            self.monitor.request_cpu(self)

            # 2. Simulate execution inside the protected critical section
            time.sleep(0.02)

            # 3. Release access via Monitor Exit Procedure
            self.monitor.release_cpu(self)


def run_simulation():
    monitor = EEVDFMonitor()

    # Define workload: Two heavy batch threads and one latency-sensitive interactive thread
    threads = [
        ProcessThread("P1 (Heavy-Batch)", arrival=0, burst=4, weight=1, time_slice=4, monitor=monitor),
        ProcessThread("P2 (Heavy-Batch)", arrival=0, burst=4, weight=1, time_slice=4, monitor=monitor),
        ProcessThread("P3 (Interactive)", arrival=1, burst=2, weight=1, time_slice=1, monitor=monitor),
    ]

    for t in threads:
        monitor.register_thread(t)

    print("=" * 88)
    print("🚀 Starting EEVDF Scheduling with Monitor (Condition Variable) Synchronization...")
    print("=" * 88)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # Print final summary table
    n = len(threads)
    print("\n" + "=" * 88)
    print("📊 Final Scheduling Metrics (EEVDF + Monitor):")
    print("-" * 88)
    print(
        f"{'Process ID':<18} | {'Arrival':<8} | {'Burst':<6} | {'Slice':<6} | "
        f"{'Completion':<10} | {'Turnaround':<10} | {'Waiting':<8} | {'Response':<8}"
    )
    print("-" * 88)

    total_wait, total_turn, total_resp = 0, 0, 0
    for p in threads:
        turnaround = p.completion_time - p.arrival
        waiting = turnaround - p.burst
        response = p.first_run - p.arrival

        total_turn += turnaround
        total_wait += waiting
        total_resp += response

        print(
            f"{p.pid:<18} | {p.arrival:<8} | {p.burst:<6} | {p.slice:<6} | "
            f"{p.completion_time:<10} | {turnaround:<10} | {waiting:<8} | {response:<8}"
        )

    print("-" * 88)
    print(f"Average Waiting Time    : {total_wait / n:.2f}")
    print(f"Average Turnaround Time : {total_turn / n:.2f}")
    print(f"Average Response Time   : {total_resp / n:.2f}")
    print("=" * 88)


if __name__ == "__main__":
    run_simulation()