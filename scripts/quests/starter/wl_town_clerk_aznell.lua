local Quest = {}

Quest.key_name    = "wl_town_clerk_aznell"
Quest.title       = "Arms Ledger Dispatch"
Quest.description = "Carry a sealed dispatch from Moot Hall to Aznell's Armory."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "wl_town_clerk"
Quest.turnin_npc_template_id = "wl_aznell_armorer"
Quest.start_room_id          = 7970
Quest.start_lich_room_id     = 2020
Quest.start_message          = "Take this dispatch to Aznell's Armory and don't crumple it on the way."
Quest.start_items            = {
    { short_name = "sealed dispatch for Aznell", noun = "dispatch" },
}

Quest.stages = {
    {
        objective_event = "give_npc:wl_aznell_armorer:dispatch",
        required_count  = 1,
        objective       = "Deliver the sealed dispatch to Aznell.",
        hint            = "Find Aznell in his forge and GIVE the dispatch TO AZNELL.",
    },
}

Quest.rewards = {
    experience = 120,
    silver     = 90,
}

return Quest
