local Quest = {}

Quest.key_name    = "rogue_orientation"
Quest.guild_id    = "rogue"
Quest.title       = "The First Walkthrough"
Quest.description = "A new rogue is expected to learn the rooms, the trainers, and the hands that actually keep the Ta'Vaalor chapter moving."
Quest.repeatable  = false

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
        hint            = "Take the north passage and let the lockmaster size you up.",
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
        hint            = "The drill court handles the forms, recoveries, and gambit work.",
    },
}

return Quest
