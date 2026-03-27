local Quest = {}

Quest.key_name    = "rogue_entry"
Quest.guild_id    = "rogue"
Quest.title       = "Quiet Entry"
Quest.description = "A rogue is expected to know how to get in, get out, and keep the guild ledger satisfied."
Quest.repeatable  = false

Quest.stages = {
    {
        objective_event = "guild_join_rogue",
        required_count  = 1,
        objective       = "Join the Rogue Guild.",
        hint            = "Once you have access, use GLD JOIN with a rogue authority.",
    },
    {
        objective_event = "rogue_entry_used",
        required_count  = 1,
        objective       = "Use the hidden guild entry correctly.",
        hint            = "The quiet way in should work only after you begin the proper sequence.",
    },
    {
        objective_event = "guild_checkin_rogue",
        required_count  = 1,
        objective       = "Check in with the guild ledger.",
        hint            = "Use GLD CHECKIN with a local rogue authority once your dues are current.",
    },
}

return Quest
