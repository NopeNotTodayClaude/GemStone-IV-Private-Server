local Quest = {}

Quest.key_name    = "wl_town_clerk_krythussa"
Quest.title       = "Sweetshop Receipt Run"
Quest.description = "Carry a sealed dispatch from Moot Hall to Krythussa's shop."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "wl_town_clerk"
Quest.turnin_npc_template_id = "wl_krythussa_baker"
Quest.start_room_id          = 7970
Quest.start_lich_room_id     = 2020
Quest.start_message          = "Krythussa is waiting on this receipt.  Take it there and come straight back."
Quest.start_items            = {
    { short_name = "sealed dispatch for Krythussa", noun = "dispatch" },
}

Quest.stages = {
    {
        objective_event = "give_npc:wl_krythussa_baker:dispatch",
        required_count  = 1,
        objective       = "Deliver the sealed dispatch to Krythussa.",
        hint            = "Find Krythussa's confectionary and GIVE the dispatch TO KRYTHUSSA.",
    },
}

Quest.rewards = {
    experience = 120,
    silver     = 95,
}

return Quest
