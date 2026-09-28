def progress_percent(current, target):
    if target <= 0: return 0
    return min(100, round(current / target * 100, 1))
