-- NPC: a concealed figure
-- Zone/Town: auto-placed  |  Room: 17931
local NPC = {}

NPC.template_id    = "sol_rogue_contact"
NPC.name           = "a concealed figure"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A figure who seems to materialize from the shadows when approached."
NPC.home_room_id   = 17931

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
    rogue = "The Solhaven guild teaches patience before flair.",
    guild = "Use GLD for the ledger.  Use your own head for the rest.",
    training = "A rogue who cannot hide, lock, and recover from a bad stun is no rogue for long.",
    quest = "Ask for guided work with GLD QUEST START when you are ready.",
    default = "The concealed figure emerges just enough to speak.  'State your guild business.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
