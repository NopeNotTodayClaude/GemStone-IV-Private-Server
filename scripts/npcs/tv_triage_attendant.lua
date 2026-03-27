-- NPC: a triage attendant
-- Zone/Town: auto-placed  |  Room: 10397
local NPC = {}

NPC.template_id    = "tv_triage_attendant"
NPC.name           = "a triage attendant"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A calm elven nurse who moves between patients with practiced efficiency."
NPC.home_room_id   = 10397

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
    healing = "If it is bleeding, fevered, or attached at an unfortunate angle, say so first.",
    herbs = "Herbs help.  Clear answers help more.",
    triage = "Triage is the art of deciding what cannot wait and making sure it does not.",
    default = "The attendant gives you a calm, assessing look.  'If you need treatment, describe the problem.'",
}
NPC.ambient_emotes = {
    "The attendant folds a clean strip of linen and places it with other supplies.",
    "The attendant checks a small tray of vials and replaces one stopper more firmly.",
    "The attendant rinses a pair of instruments and lays them out in order.",
    "The attendant glances over a nearby patient with practiced professional calm.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
