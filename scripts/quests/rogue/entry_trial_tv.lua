local Quest = {}

Quest.key_name    = "rogue_entry"
Quest.guild_id    = "rogue"
Quest.title       = "Quiet Entry"
Quest.description = "A rogue is expected to prove they can find the way in, get through the inner door, and keep the guild ledger satisfied."
Quest.repeatable  = false

Quest.stages = {
    {
        objective_event = "rogue_shed_entry_used",
        required_count  = 1,
        objective       = "Work the hidden shed entry on Gaeld Var.",
        hint            = "In Ta'Vaalor, the first proof is the shed.  LOOK TOOL and work the panel sequence properly.",
    },
    {
        objective_event = "rogue_inner_door_used",
        required_count  = 1,
        objective       = "Open the inner basement door and reach the guild proper.",
        hint            = "In the basement, LEAN by the inner door, use the pass sequence, and OPEN DOOR before the latch settles.",
    },
    {
        objective_event = "guild_join_rogue",
        required_count  = 1,
        objective       = "Join the Rogue Guild.",
        hint            = "Once you are inside the guild proper, use GLD JOIN with the guild factor.",
    },
    {
        objective_event = "guild_checkin_rogue",
        required_count  = 1,
        objective       = "Check in with the guild ledger.",
        hint            = "Settle your first dues payment and use GLD CHECKIN with the guild factor.",
    },
}

return Quest
