class Task:
    def __init__(self, tid, arrival, burst, weight, time_slice):
        self.tid = tid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.weight = weight
        self.slice = time_slice

        # EEVDF Core Parameters
        self.vruntime = 0.0
        self.v_deadline = 0.0
        self.lag = 0.0

        # Statistics
        self.completed = False
        self.first_run = -1
        self.completion_time = 0


def run_pure_eevdf(tasks):
    n = len(tasks)
    current_time = 0
    completed_count = 0
    timeline = []

    print("=" * 80)
    print("🚀 Running Pure EEVDF (Earliest Eligible Virtual Deadline First) Scheduler")
    print("=" * 80)

    while completed_count < n:
        # 1. Filter active (ready) tasks at current clock tick
        active_tasks = [t for t in tasks if t.arrival <= current_time and not t.completed]

        if not active_tasks:
            timeline.append("IDLE")
            current_time += 1
            continue

        # 2. Compute system virtual time (weighted average of active vruntime)
        total_weight = sum(t.weight for t in active_tasks)
        avg_vruntime = sum(t.vruntime * t.weight for t in active_tasks) / total_weight

        # 3. Determine Eligible Tasks (Lag >= 0 <==> vruntime <= avg_vruntime)
        eligible_tasks = []
        for t in active_tasks:
            t.lag = (avg_vruntime - t.vruntime) * t.weight
            if t.vruntime <= avg_vruntime:
                eligible_tasks.append(t)

        if not eligible_tasks:
            eligible_tasks = active_tasks

        # 4. Calculate Virtual Deadline for eligible tasks
        # Formula: V_deadline = vruntime + (requested_slice / weight)
        for t in eligible_tasks:
            t.v_deadline = t.vruntime + (t.slice / t.weight)

        # 5. Pick the eligible task with the earliest virtual deadline
        eligible_tasks.sort(key=lambda x: (x.v_deadline, x.arrival))
        selected = eligible_tasks[0]

        if selected.first_run == -1:
            selected.first_run = current_time

        # 6. Execute task for 1 time unit
        timeline.append(selected.tid)
        selected.remaining -= 1
        selected.vruntime += 1.0 / selected.weight
        current_time += 1

        if selected.remaining == 0:
            selected.completed = True
            selected.completion_time = current_time
            completed_count += 1

    # Print Execution Timeline
    print(f"\nExecution Timeline: {' -> '.join(timeline)}\n")

    # Print Metrics Table
    print("-" * 80)
    print(
        f"{'Task ID':<16} | {'Arrival':<7} | {'Burst':<5} | {'Weight':<6} | "
        f"{'Slice':<5} | {'Finish':<6} | {'Turnaround':<10} | {'Waiting':<7} | {'Response':<8}"
    )
    print("-" * 80)

    total_wait, total_turn, total_resp = 0, 0, 0
    for t in tasks:
        turnaround = t.completion_time - t.arrival
        waiting = turnaround - t.burst
        response = t.first_run - t.arrival

        total_turn += turnaround
        total_wait += waiting
        total_resp += response

        print(
            f"{t.tid:<16} | {t.arrival:<7} | {t.burst:<5} | {t.weight:<6} | "
            f"{t.slice:<5} | {t.completion_time:<6} | {turnaround:<10} | {waiting:<7} | {response:<8}"
        )

    print("-" * 80)
    print(f"Average Waiting Time    : {total_wait / n:.2f}")
    print(f"Average Turnaround Time : {total_turn / n:.2f}")
    print(f"Average Response Time   : {total_resp / n:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    workload = [
        Task(tid="T1 (Batch)", arrival=0, burst=4, weight=1, time_slice=4),
        Task(tid="T2 (Batch)", arrival=0, burst=4, weight=1, time_slice=4),
        Task(tid="T3 (Interactive)", arrival=1, burst=2, weight=2, time_slice=1),
    ]
    run_pure_eevdf(workload)
