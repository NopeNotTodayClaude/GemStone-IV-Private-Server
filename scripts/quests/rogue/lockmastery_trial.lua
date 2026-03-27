local Quest = {}

Quest.key_name    = "rogue_lockmastery"
Quest.guild_id    = "rogue"
Quest.title       = "Locks Within Locks"
Quest.description = "The guild expects more than brute persistence from a locksmith."
Quest.repeatable  = false

Quest.stages = {
    {
        objective_event = "lm_sense",
        required_count  = 1,
        objective       = "Use LMASTER SENSE to judge locksmithing conditions.",
        hint            = "A patient rogue reads the room before reading the lock.",
    },
    {
        objective_event = "lm_calipers",
        required_count  = 1,
        objective       = "Measure a lock with LMASTER CALIPERS.",
        hint            = "Calipers help you size the mechanism before forcing the wrong pick on it.",
    },
    {
        objective_event = "detect_success",
        required_count  = 1,
        objective       = "Detect the workings of a trapped or locked box.",
        hint            = "Use DETECT on a real field container.",
    },
    {
        objective_event = "disarm_success",
        required_count  = 1,
        objective       = "Disarm a trap cleanly.",
        hint            = "A guild locksmith is expected to leave no surprises behind.",
    },
    {
        objective_event = "pick_success",
        required_count  = 1,
        objective       = "Pick a lock cleanly.",
        hint            = "Open a real lock in the field after preparing properly.",
    },
}

return Quest
