local Quest = {}

Quest.key_name    = "imt_bondsman_berrytoe"
Quest.title       = "Market Packet"
Quest.description = "Carry a sealed packet from Clovertooth Hall to Berrytoe's store."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "imt_bondsman"
Quest.turnin_npc_template_id = "imt_berrytoe_shopkeeper"
Quest.start_room_id          = 2438
Quest.start_lich_room_id     = 4043042
Quest.start_message          = "This packet goes to Berrytoe.  Deliver it before you stop anywhere warm."
Quest.start_items            = {
    { short_name = "sealed packet for Berrytoe", noun = "packet" },
}

Quest.stages = {
    {
        objective_event = "give_npc:imt_berrytoe_shopkeeper:packet",
        required_count  = 1,
        objective       = "Deliver the sealed packet to Berrytoe.",
        hint            = "Find Berrytoe's General Store and GIVE the packet TO BERR YTOE.",
    },
}

Quest.rewards = {
    experience = 120,
    silver     = 90,
}

return Quest
