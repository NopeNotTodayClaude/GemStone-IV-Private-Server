-- NPC: a concealed figure
-- Zone/Town: auto-placed  |  Room: 17984
local NPC = {}

NPC.template_id    = "rr_rogue_contact_rr"
NPC.name           = "a concealed figure"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A figure occupying a back corner of the inn pantry who speaks only to those they expect."
NPC.home_room_id   = 17984

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = true
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    rogue = "The River's Rest cell keeps its own books, but the guild ledger is shared.",
    guild = "Use GLD if you need the guild records.  I can still point you toward the next quiet job.",
    training = "Cheapshots, locks, and nerve.  That is what keeps rogues alive.",
    quest = "If you need guided work, use GLD QUEST START.",
    default = "The concealed figure studies you from the pantry shadows.  'Talk softly, if you talk at all.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
