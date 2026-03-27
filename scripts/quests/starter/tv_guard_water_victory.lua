local Quest = {}

Quest.key_name    = "tv_guard_water_victory"
Quest.title       = "Victory Gate Water Run"
Quest.description = "Bring a fresh glass of water to Laerindra at Victory Gate."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 4

Quest.start_npc_template_id  = "guard_victory_laerindra"
Quest.turnin_npc_template_id = "guard_victory_laerindra"
Quest.start_room_id          = 5907
Quest.start_lich_room_id     = 14100052
Quest.start_message          = "Good.  Bring me a fresh glass of water from the Malwith Inn and do not meander."

Quest.stages = {
    {
        objective_event = "give_npc:guard_victory_laerindra:water",
        required_count  = 1,
        objective       = "Bring a glass of water to Laerindra.",
        hint            = "Buy or fetch a glass of water, then GIVE it TO LAERINDRA at Victory Gate.",
    },
}

Quest.rewards = {
    experience = 110,
    silver     = 85,
}

return Quest
