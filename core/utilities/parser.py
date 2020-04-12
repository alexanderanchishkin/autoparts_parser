def get_remains_delay(delay, start_time, end_time):
    elapsed_time = end_time - start_time
    return max(delay - elapsed_time, 0)
