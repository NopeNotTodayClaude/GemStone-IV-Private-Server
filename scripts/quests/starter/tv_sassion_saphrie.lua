local Quest = {}

Quest.key_name    = "tv_sassion_saphrie"
Quest.title       = "Herbal Requisition"
Quest.description = "Carry Sassion's sealed message to Saphrie's shop."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "sassion"
Quest.turnin_npc_template_id = "tv_saphrie"
Quest.start_room_id          = 3490
Quest.start_lich_room_id     = 14100010
Quest.start_message          = "Saphrie is waiting on this requisition note.  Take it to her before she starts complaining to me."
Quest.start_items            = {
    { short_name = "sealed message for Saphrie", noun = "message" },
}

Quest.stages = {
    {
        objective_event = "give_npc:tv_saphrie:message",
        required_count  = 1,
        objective       = "Deliver the sealed message to Saphrie.",
        hint            = "Find Saphrie's Herbs and GIVE the message TO SAPHRIE.",
    },
}

Quest.rewards = {
    experience = 130,
    silver     = 110,
}

return Quest
