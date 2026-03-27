local Quest = {}

Quest.key_name    = "tv_guard_water_annatto"
Quest.title       = "Annatto Gate Water Run"
Quest.description = "Bring a fresh glass of water to Daervith at Annatto Gate."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 4

Quest.start_npc_template_id  = "guard_annatto_daervith"
Quest.turnin_npc_template_id = "guard_annatto_daervith"
Quest.start_room_id          = 5906
Quest.start_lich_room_id     = 14100039
Quest.start_message          = "Bring me a glass of water from Malwith Inn and you'll have done the watch a service."

Quest.stages = {
    {
        objective_event = "give_npc:guard_annatto_daervith:water",
        required_count  = 1,
        objective       = "Bring a glass of water to Daervith.",
        hint            = "Buy or fetch a glass of water, then GIVE it TO DAERVITH at Annatto Gate.",
    },
}

Quest.rewards = {
    experience = 110,
    silver     = 85,
}

return Quest
