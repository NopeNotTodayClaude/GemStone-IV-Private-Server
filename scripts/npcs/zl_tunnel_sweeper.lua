-- NPC: a tunnel sweeper
-- Zone/Town: auto-placed  |  Room: 9472
local NPC = {}

NPC.template_id    = "zl_tunnel_sweeper"
NPC.name           = "a tunnel sweeper"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A gnome with a long broom keeping the tunnel approaches clear of debris."
NPC.home_room_id   = 9472

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
    default = "a tunnel sweeper doesn't respond.",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60

return NPC
