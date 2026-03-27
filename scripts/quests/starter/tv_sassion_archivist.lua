local Quest = {}

Quest.key_name    = "tv_sassion_archivist"
Quest.title       = "Archive Message"
Quest.description = "Carry Sassion's sealed message to Archivist Yendrel."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "sassion"
Quest.turnin_npc_template_id = "tv_antiques_archivist"
Quest.start_room_id          = 3490
Quest.start_lich_room_id     = 14100010
Quest.start_message          = "Take this message to Archivist Yendrel.  He dislikes delays almost as much as I do."
Quest.start_items            = {
    { short_name = "sealed message for Yendrel", noun = "message" },
}

Quest.stages = {
    {
        objective_event = "give_npc:tv_antiques_archivist:message",
        required_count  = 1,
        objective       = "Deliver the sealed message to Archivist Yendrel.",
        hint            = "Find the antique goods shop and GIVE the message TO YENDREL.",
    },
}

Quest.rewards = {
    experience = 125,
    silver     = 100,
}

return Quest
