local Quest = {}

Quest.key_name    = "tv_guard_water_vermilion"
Quest.title       = "Vermilion Gate Water Run"
Quest.description = "Bring a fresh glass of water to Raertria at Vermilion Gate."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 4

Quest.start_npc_template_id  = "guard_vermilion_raertria"
Quest.turnin_npc_template_id = "guard_vermilion_raertria"
Quest.start_room_id          = 5827
Quest.start_lich_room_id     = 14100015
Quest.start_message          = "Malwith Inn serves water.  Bring me a glass and return while it's still cold."

Quest.stages = {
    {
        objective_event = "give_npc:guard_vermilion_raertria:water",
        required_count  = 1,
        objective       = "Bring a glass of water to Raertria.",
        hint            = "Buy or fetch a glass of water, then GIVE it TO RAERTRIA at Vermilion Gate.",
    },
}

Quest.rewards = {
    experience = 110,
    silver     = 90,
}

return Quest
