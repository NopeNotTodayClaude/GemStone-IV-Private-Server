local Quest = {}

Quest.key_name    = "imt_bondsman_penguin"
Quest.title       = "Penguin House Packet"
Quest.description = "Carry a sealed packet from Clovertooth Hall to the Thirsty Penguin."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "imt_bondsman"
Quest.turnin_npc_template_id = "imt_inn_keeper_imt"
Quest.start_room_id          = 2438
Quest.start_lich_room_id     = 4043042
Quest.start_message          = "This packet goes to the Penguin.  Hand it to the innkeeper and keep moving."
Quest.start_items            = {
    { short_name = "sealed packet for the Penguin", noun = "packet" },
}

Quest.stages = {
    {
        objective_event = "give_npc:imt_inn_keeper_imt:packet",
        required_count  = 1,
        objective       = "Deliver the sealed packet to the innkeeper at the Thirsty Penguin.",
        hint            = "Go to the Thirsty Penguin front desk and GIVE the packet TO the innkeeper.",
    },
}

Quest.rewards = {
    experience = 125,
    silver     = 100,
}

return Quest
