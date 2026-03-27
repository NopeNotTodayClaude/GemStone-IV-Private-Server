local Quest = {}

Quest.key_name    = "wl_town_clerk_kilron"
Quest.title       = "Pawn Counter Notice"
Quest.description = "Carry a sealed dispatch from Moot Hall to Kilron's pawnshop."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "wl_town_clerk"
Quest.turnin_npc_template_id = "wl_kilron"
Quest.start_room_id          = 7970
Quest.start_lich_room_id     = 2020
Quest.start_message          = "Kilron needs this notice.  Get it into his hands, not his doorway."
Quest.start_items            = {
    { short_name = "sealed dispatch for Kilron", noun = "dispatch" },
}

Quest.stages = {
    {
        objective_event = "give_npc:wl_kilron:dispatch",
        required_count  = 1,
        objective       = "Deliver the sealed dispatch to Kilron.",
        hint            = "Find Kilron's pawnshop and GIVE the dispatch TO KILRON.",
    },
}

Quest.rewards = {
    experience = 125,
    silver     = 100,
}

return Quest
