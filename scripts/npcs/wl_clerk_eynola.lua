-- NPC: Clerk Eynola
-- Zone/Town: auto-placed  |  Room: 400
local NPC = {}

NPC.template_id    = "wl_clerk_eynola"
NPC.name           = "Clerk Eynola"
NPC.article        = ""
NPC.title          = "bank teller"
NPC.description    = "A precise halfling woman with an immaculate ledger open before her."
NPC.home_room_id   = 400

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
    default = "Clerk Eynola doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
