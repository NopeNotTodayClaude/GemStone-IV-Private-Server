local Quest = {}

Quest.key_name    = "rogue_dirty_fighting"
Quest.guild_id    = "rogue"
Quest.title       = "A Knife in the Dark"
Quest.description = "A rogue survives by ending a fight on their own terms."
Quest.repeatable  = false

Quest.stages = {
    {
        objective_event = "hide_success",
        required_count  = 1,
        objective       = "Vanish from sight.",
        hint            = "Use HIDE where the shadows will actually take you.",
    },
    {
        objective_event = "ambush_success",
        required_count  = 1,
        objective       = "Strike from hiding.",
        hint            = "AMBUSH is the guild's old answer to a careless foe.",
    },
    {
        objective_event = "cheapshot_success",
        required_count  = 1,
        objective       = "Land a successful cheapshot.",
        hint            = "Use CHEAPSHOT with a maneuver you know.",
    },
    {
        objective_event = "subdue_success",
        required_count  = 1,
        objective       = "Subdue a foe from hiding.",
        hint            = "A clean SUBDUE says as much about your control as your aggression.",
    },
    {
        objective_event = "sweep_success",
        required_count  = 1,
        objective       = "Put an opponent on the ground with SWEEP.",
        hint            = "The guild likes to see that you can take away a foe's footing.",
    },
}

return Quest
