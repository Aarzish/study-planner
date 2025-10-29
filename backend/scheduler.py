def allocate_time(topics, available_hours, alpha=0.6, beta=0.4):
    """
    Allocate study hours among topics based on urgency and difficulty.
    topics: list of dicts with 'name', 'days_until_deadline', 'estimated_difficulty'
    available_hours: total study time available
    """
    scores = []
    for t in topics:
        urgency = 1 / max(1, t["days_until_deadline"])   # sooner deadlines = more urgent
        weakness = t["estimated_difficulty"]             # harder topics = higher priority
        score = alpha * urgency + beta * weakness
        scores.append(score)

    total = sum(scores)
    allocations = [round(available_hours * s / total, 2) for s in scores]
    return allocations

