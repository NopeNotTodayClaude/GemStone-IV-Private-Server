local CreatureSpawns = {}

CreatureSpawns.defaults = {
    active_player_bubble_rooms = 60,
    planner_workers = 2,
    planner_queue_multiplier = 2,
    planner_submit_interval_ticks = 30,
    wander_submit_interval_ticks = 150,
    perf_log_interval_seconds = 60,
}

return CreatureSpawns
