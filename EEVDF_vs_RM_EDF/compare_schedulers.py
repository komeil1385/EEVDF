import copy

def simulate_scheduler(algo_name, task_list):
    tasks = copy.deepcopy(task_list)
    n = len(tasks)

    # Initialize state variables for each task
    for t in tasks:
        t['remaining'] = t['burst']
        t['abs_deadline'] = t['arrival'] + t['deadline']
        t['vruntime'] = 0.0
        t['completed'] = False
        t['first_run'] = -1
        t['completion_time'] = 0

    current_time = 0
    completed_count = 0
    missed_deadlines = 0
    preemptions = 0
    last_task_id = None
    timeline = []

    while completed_count < n:
        active_tasks = [t for t in tasks if t['arrival'] <= current_time and not t['completed']]

        if not active_tasks:
            timeline.append("-")
            current_time += 1
            last_task_id = None
            continue

        selected_task = None

        if algo_name == "RM":
            # Rate Monotonic: Static priority based on shortest relative deadline/period
            active_tasks.sort(key=lambda x: (x['deadline'], x['arrival']))
            selected_task = active_tasks[0]

        elif algo_name == "EDF":
            # Earliest Deadline First: Dynamic priority based on absolute deadline
            active_tasks.sort(key=lambda x: (x['abs_deadline'], x['arrival']))
            selected_task = active_tasks[0]

        elif algo_name == "EEVDF":
            # Step 1: Filter eligible tasks (vruntime <= average)
            avg_vruntime = sum(t['vruntime'] for t in active_tasks) / len(active_tasks)
            eligible = [t for t in active_tasks if t['vruntime'] <= avg_vruntime]
            if not eligible:
                eligible = active_tasks

            # Step 2: Calculate Virtual Deadline = vruntime + (slice / weight)
            for t in eligible:
                t['v_deadline'] = t['vruntime'] + (t['slice'] / t['weight'])

            eligible.sort(key=lambda x: (x['v_deadline'], x['abs_deadline']))
            selected_task = eligible[0]

        # Count context switches / preemptions
        if last_task_id is not None and last_task_id != selected_task['id']:
            preemptions += 1
        last_task_id = selected_task['id']

        # Record first run for Response Time
        if selected_task['first_run'] == -1:
            selected_task['first_run'] = current_time

        # Execute for 1 clock tick
        timeline.append(selected_task['id'])
        selected_task['remaining'] -= 1
        selected_task['vruntime'] += 1.0 / selected_task['weight']
        current_time += 1

        # Check completion and deadline status
        if selected_task['remaining'] == 0:
            selected_task['completed'] = True
            selected_task['completion_time'] = current_time
            completed_count += 1
            last_task_id = None  # Task finished naturally

            if current_time > selected_task['abs_deadline']:
                missed_deadlines += 1

    # Compute aggregate metrics
    total_wait, total_turn, total_resp = 0, 0, 0
    for t in tasks:
        turnaround = t['completion_time'] - t['arrival']
        waiting = turnaround - t['burst']
        response = t['first_run'] - t['arrival']

        total_turn += turnaround
        total_wait += waiting
        total_resp += response

    return {
        'missed': missed_deadlines,
        'avg_wait': total_wait / n,
        'avg_turn': total_turn / n,
        'avg_resp': total_resp / n,
        'preemptions': preemptions,
        'timeline': " ".join(timeline)
    }


if __name__ == "__main__":
    # High-utilization workload mixing real-time deadlines and interactive slices
    workload = [
        {'id': 'T1', 'arrival': 0, 'burst': 3, 'deadline': 5, 'weight': 1, 'slice': 2},
        {'id': 'T2', 'arrival': 1, 'burst': 3, 'deadline': 4, 'weight': 2, 'slice': 1},
        {'id': 'T3', 'arrival': 2, 'burst': 2, 'deadline': 8, 'weight': 1, 'slice': 1},
    ]

    print("=" * 82)
    print("📊 CPU Scheduling Benchmark: RM vs. EDF vs. EEVDF")
    print("=" * 82)

    results = {}
    for algo in ["RM", "EDF", "EEVDF"]:
        res = simulate_scheduler(algo, workload)
        results[algo] = res
        print(f">>> {algo:<6} Timeline : {res['timeline']}")

    print("\n" + "=" * 82)
    print(f"{'Algorithm':<10} | {'Missed':<8} | {'Avg Wait':<10} | {'Avg Turnaround':<15} | {'Avg Response':<13} | {'Preempts':<8}")
    print("-" * 82)
    for algo, r in results.items():
        print(
            f"{algo:<10} | {r['missed']:<8} | {r['avg_wait']:<10.2f} | "
            f"{r['avg_turn']:<15.2f} | {r['avg_resp']:<13.2f} | {r['preemptions']:<8}"
        )
    print("=" * 82)