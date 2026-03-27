-- NPC: a travel clerk
-- Zone/Town: auto-placed  |  Room: 10302
local NPC = {}

NPC.template_id    = "tv_travel_clerk_tv"
NPC.name           = "a travel clerk"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A brisk elven clerk who processes transit documents with mechanical precision."
NPC.home_room_id   = 10302

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
    travel = "Routes are simple.  People insisting on special exceptions are not.",
    documents = "If you have papers, have them ready before you reach the counter.",
    routes = "A clerk can save you half a day if you ask before choosing badly.",
    default = "The clerk taps a sheaf of route papers.  'If you need directions, say where.'",
}
NPC.ambient_emotes = {
    "The travel clerk straightens a pile of route slips into a crisp square.",
    "The travel clerk compares two schedules and frowns at a tiny discrepancy.",
    "The travel clerk sands a line of fresh ink and blows the excess away.",
    "The travel clerk checks a posted route notice and pins one corner flatter.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
