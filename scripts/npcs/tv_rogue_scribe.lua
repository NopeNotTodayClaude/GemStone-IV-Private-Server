local NPC = {}

NPC.template_id    = "tv_rogue_scribe"
NPC.name           = "a slender elven woman"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A slender elven woman with ink-stained fingers and the patient expression of someone assigned to hear more than she ever intends to repeat."
NPC.home_room_id   = 17835

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
    records = "If it matters to the guild later, somebody in this room has probably written it down already.",
    meeting = "The conference room handles matters the guild prefers not to discuss in hallways.",
    default = "The slender elven woman glances up from her notes, offers a distant nod, and returns to writing.",
}
NPC.ambient_emotes = {
    "The slender elven woman turns a page in her notebook and resumes writing in a swift, practiced hand.",
    "The slender elven woman pauses to sharpen a charcoal stylus before going back to her notes.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45

return NPC
