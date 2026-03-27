local NPC = {}

NPC.template_id    = "vermilion_guard_calikran"
NPC.name           = "Calikran"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A pale-haired guardsman with a spare expression and the unmistakable bearing of someone trusted with unpleasant roads."
NPC.home_room_id   = 5827

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    gate = "Vermilion duty suits soldiers who value caution over bragging.",
    cemetery = "Nothing good comes from treating cemetery road lightly.",
    default = "Calikran dips his chin in a restrained acknowledgment.",
}
NPC.ambient_emotes = {
    "Calikran studies the road beyond the gate with unsmiling attention.",
    "Calikran rubs a thumb along the edge of one vambrace and stills his hand.",
    "Calikran takes a slow look over each traveler entering from the bridge.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
