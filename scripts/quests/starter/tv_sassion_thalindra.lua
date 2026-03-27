local Quest = {}

Quest.key_name    = "tv_sassion_thalindra"
Quest.title       = "Guild Hall Note"
Quest.description = "Carry Sassion's sealed message to Thalindra at the Adventurers' Guild."
Quest.repeatable  = true
Quest.quest_type  = "general"
Quest.level_req   = 1
Quest.max_level   = 5

Quest.start_npc_template_id  = "sassion"
Quest.turnin_npc_template_id = "guild_clerk"
Quest.start_room_id          = 3490
Quest.start_lich_room_id     = 14100010
Quest.start_message          = "Thalindra needs this note.  Deliver it to the guild clerk and come back sharpish."
Quest.start_items            = {
    { short_name = "sealed message for Thalindra", noun = "message" },
}

Quest.stages = {
    {
        objective_event = "give_npc:guild_clerk:message",
        required_count  = 1,
        objective       = "Deliver the sealed message to Thalindra.",
        hint            = "Go to the Adventurers' Guild foyer and GIVE the message TO THALINDRA.",
    },
}

Quest.rewards = {
    experience = 125,
    silver     = 105,
}

return Quest
