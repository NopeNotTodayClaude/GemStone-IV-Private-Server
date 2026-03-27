local Quest = {}

Quest.key_name    = "imt_bondsman_leaftoe"
Quest.title       = "Apothecary Packet"
Quest.description = "Carry a sealed packet from Clovertooth Hall to Leaftoe's shop."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "imt_bondsman"
Quest.turnin_npc_template_id = "imt_leaftoe"
Quest.start_room_id          = 2438
Quest.start_lich_room_id     = 4043042
Quest.start_message          = "Leaftoe needs this packet.  Try not to misplace it in a drift."
Quest.start_items            = {
    { short_name = "sealed packet for Leaftoe", noun = "packet" },
}

Quest.stages = {
    {
        objective_event = "give_npc:imt_leaftoe:packet",
        required_count  = 1,
        objective       = "Deliver the sealed packet to Leaftoe.",
        hint            = "Find Leaftoe's shop and GIVE the packet TO LEAFTOE.",
    },
}

Quest.rewards = {
    experience = 120,
    silver     = 95,
}

return Quest
