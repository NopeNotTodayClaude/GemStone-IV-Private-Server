local Quest = {}

Quest.key_name    = "tv_guard_water_amaranth"
Quest.title       = "Amaranth Gate Water Run"
Quest.description = "Bring a fresh glass of water to Sorvael at Amaranth Gate."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 4

Quest.start_npc_template_id  = "guard_amaranth_sorvael"
Quest.turnin_npc_template_id = "guard_amaranth_sorvael"
Quest.start_room_id          = 3727
Quest.start_lich_room_id     = 14100003
Quest.start_message          = "Bring me a glass of water from Malwith Inn.  Promptly."

Quest.stages = {
    {
        objective_event = "give_npc:guard_amaranth_sorvael:water",
        required_count  = 1,
        objective       = "Bring a glass of water to Sorvael.",
        hint            = "Buy or fetch a glass of water, then GIVE it TO SORVAEL at Amaranth Gate.",
    },
}

Quest.rewards = {
    experience = 110,
    silver     = 85,
}

return Quest
