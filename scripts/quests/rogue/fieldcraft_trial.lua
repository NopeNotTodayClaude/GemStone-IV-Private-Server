local Quest = {}

Quest.key_name    = "rogue_fieldcraft"
Quest.guild_id    = "rogue"
Quest.title       = "Never Lose the Edge"
Quest.description = "When the work turns rough, a rogue keeps moving and keeps the advantage."
Quest.repeatable  = false
Quest.start_npc_template_ids = {
    "tv_rogue_drillmaster",
    "tv_rogue_master_pyll",
}
Quest.turnin_npc_template_ids = {
    "tv_rogue_drillmaster",
    "tv_rogue_master_pyll",
}
Quest.start_message = "You want fieldcraft, then prove you can keep moving through the ugly seconds.  Show me stun recovery, two clean gambits, and one that actually shifts the fight."
Quest.rewards = {
    unlocks = {
        {
            key = "rogue_emote_shadowpose",
            type = "emote",
            notes = "Fieldcraft flourish taught by Velk.",
            message = "You permanently learn the guild's shadowpose flourish.  You can now SHADOWPOSE.",
        },
    },
}

Quest.stages = {
    {
        objective_event = "stunman_success",
        required_count  = 1,
        objective       = "Fight through a stun with STUNMAN.",
        hint            = "A guild rogue does not freeze just because the world spins.",
    },
    {
        objective_event = "rgambit_perform",
        required_count  = 2,
        objective       = "Perform a pair of rogue gambits cleanly.",
        hint            = "Any practiced RGAMBIT will do, though combat diversions count too.",
    },
    {
        objective_event = "rgambit_success",
        required_count  = 1,
        objective       = "Use a rogue gambit to throw a foe off balance.",
        hint            = "DIVERT is only one answer, but it is an effective one.",
    },
}

return Quest
