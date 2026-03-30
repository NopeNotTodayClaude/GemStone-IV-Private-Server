local Quest = {}

Quest.key_name    = "rogue_orientation"
Quest.guild_id    = "rogue"
Quest.title       = "The First Walkthrough"
Quest.description = "A new rogue is expected to learn the rooms, the trainers, and the hands that actually keep the Ta'Vaalor chapter moving."
Quest.repeatable  = false
Quest.start_npc_template_ids = {
    "tv_rogue_guild_contact",
    "tv_rogue_guildmaster",
    "tv_rogue_training_admin",
}
Quest.start_message = "Your dues are square.  Now learn the chapter properly.  Go back through the inner alley, then meet the lockmaster, the bruiser, and the drillmaster before you start pretending you belong here."
Quest.turnin_npc_template_ids = {
    "tv_rogue_guild_contact",
    "tv_rogue_training_admin",
}

Quest.stages = {
    {
        objective_event = "rogue_enter_alley",
        required_count  = 1,
        objective       = "Reach the inner guild alley.",
        hint            = "The guild proper begins in the inner alley beyond the basement door.",
    },
    {
        objective_event = "rogue_meet_lockmaster",
        required_count  = 1,
        objective       = "Meet the lockmaster.",
        hint            = "Find Sable on the lockmaster floor and speak to her about lock mastery.",
    },
    {
        objective_event = "rogue_meet_bruiser",
        required_count  = 1,
        objective       = "Meet the bruiser on the warehouse floor.",
        hint            = "The warehouse floor is where the guild keeps its uglier lessons.",
    },
    {
        objective_event = "rogue_meet_drillmaster",
        required_count  = 1,
        objective       = "Meet the drillmaster in the court.",
        hint            = "Find Velk in the drill court and ask about training.",
    },
}

return Quest
