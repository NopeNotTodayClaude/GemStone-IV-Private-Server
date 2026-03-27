-- NPC: a pawnbroker
-- Zone/Town: auto-placed  |  Room: 5711
local NPC = {}

NPC.template_id    = "sol_pawnbroker_sol"
NPC.name           = "a pawnbroker"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A world-weary merchant who has seen every variety of junk and treasure the coast can produce."
NPC.home_room_id   = 5711

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
    default = "a pawnbroker doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
