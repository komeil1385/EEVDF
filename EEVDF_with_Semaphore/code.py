import threading
import time

# Binary Semaphore to protect the Critical Section (CPU execution resource)
# Initial value of 1 ensures Mutual Exclusion (only one thread executes at a time)
cpu_semaphore = threading.Semaphore(1)

# Helper lock for clean console logging
print_lock = threading.Lock()

# Global simulation clock and synchronization event
current_time = 0
scheduler_step_done = threading.Event()


class ProcessThread(threading.Thread):
    def __init__(self, pid, arrival, burst, weight, time_slice):
        super().__init__()
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.weight = weight
        self.slice = time_slice

        # EEVDF specific attributes
        self.vruntime = 0.0
        self.v_deadline = 0.0

        # Metrics tracking
        self.completed = False
        self.first_run = -1
        self.completion_time = 0

        # Thread synchronization event controlled by the EEVDF scheduler
        self.turn_event = threading.Event()

    def run(self):
        while not self.completed:
            # Wait until the EEVDF scheduler selects this thread
            self.turn_event.wait()

            if self.completed:
                break

            # --- Enter Critical Section (Wait / P Operation) ---
            cpu_semaphore.acquire()

            with print_lock:
                print(
                    f"[Time {current_time:2d}] 🔒 Semaphore Acquired by {self.pid:<16} | "
                    f"vruntime: {self.vruntime:4.1f} | v_deadline: {self.v_deadline:4.1f}"
                )

            # Simulate 1 unit of CPU execution inside the critical section
            self.remaining -= 1
            self.vruntime += 1.0 / self.weight
            time.sleep(0.02)

            with print_lock:
                print(
                    f"[Time {current_time + 1:2d}] 🔓 Semaphore Released by {self.pid:<16} | "
                    f"Remaining Burst: {self.remaining}"
                )

            # --- Exit Critical Section (Signal / V Operation) ---
            cpu_semaphore.release()

            # Reset turn event and notify the scheduler that the time unit is complete
            self.turn_event.clear()
            scheduler_step_done.set()


def run_eevdf_with_semaphore(processes):
    global current_time
    n = len(processes)
    completed_count = 0

    print("=" * 88)
    print("🚀 Starting EEVDF Scheduling with Semaphore Synchronization...")
    print("=" * 88)

    # Start all process threads (they will block on their turn_event)
    for p in processes:
        p.start()

    while completed_count < n:
        # Filter active processes that have arrived and are not yet completed
        active_procs = [
            p for p in processes if p.arrival <= current_time and not p.completed
        ]

        if not active_procs:
            current_time += 1
            continue

        # --- Step 1: Identify Eligible Processes (Lag >= 0) ---
        # Processes whose virtual runtime is less than or equal to the average
        avg_vruntime = sum(p.vruntime for p in active_procs) / len(active_procs)
        eligible_procs = [p for p in active_procs if p.vruntime <= avg_vruntime]

        if not eligible_procs:
            eligible_procs = active_procs

        # --- Step 2: Calculate Virtual Deadlines ---
        # Formula: Virtual Deadline = vruntime + (Time Slice / Weight)
        for p in eligible_procs:
            p.v_deadline = p.vruntime + (p.slice / p.weight)

        # Select the eligible process with the earliest virtual deadline
        eligible_procs.sort(key=lambda x: x.v_deadline)
        selected_proc = eligible_procs[0]

        # Record first execution time for Response Time calculation
        if selected_proc.first_run == -1:
            selected_proc.first_run = current_time

        # Signal the selected thread to acquire the semaphore and execute for 1 tick
        scheduler_step_done.clear()
        selected_proc.turn_event.set()

        # Wait for the thread to release the semaphore and finish its tick
        scheduler_step_done.wait()

        current_time += 1

        # Check if the process has completed its total burst time
        if selected_proc.remaining == 0:
            selected_proc.completed = True
            selected_proc.completion_time = current_time
            completed_count += 1
            selected_proc.turn_event.set()  # Unblock thread so it can exit the loop

    # Wait for all threads to terminate cleanly
    for p in processes:
        p.join()

    # Print final scheduling metrics table
    print("\n" + "=" * 88)
    print("📊 Final Scheduling Metrics (EEVDF + Semaphore):")
    print("-" * 88)
    print(
        f"{'Process ID':<18} | {'Arrival':<8} | {'Burst':<6} | {'Slice':<6} | "
        f"{'Completion':<10} | {'Turnaround':<10} | {'Waiting':<8} | {'Response':<8}"
    )
    print("-" * 88)

    total_wait, total_turn, total_resp = 0, 0, 0
    for p in processes:
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
    # Define workload: two heavy batch tasks and one latency-sensitive interactive task
    workload = [
        ProcessThread(pid="P1 (Heavy-Batch)", arrival=0, burst=4, weight=1, time_slice=4),
        ProcessThread(pid="P2 (Heavy-Batch)", arrival=0, burst=4, weight=1, time_slice=4),
        ProcessThread(pid="P3 (Interactive)", arrival=1, burst=2, weight=1, time_slice=1),
    ]

    run_eevdf_with_semaphore(workload)