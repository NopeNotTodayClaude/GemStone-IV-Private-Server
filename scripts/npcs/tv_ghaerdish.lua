-- NPC: Ghaerdish
-- Zone/Town: auto-placed  |  Room: 10329
local NPC = {}

NPC.template_id    = "tv_ghaerdish"
NPC.name           = "Ghaerdish"
NPC.article        = ""
NPC.title          = "master furrier"
NPC.description    = "A stocky elven woman whose practiced eye can identify a pelt's origin at twenty paces."
NPC.home_room_id   = 10329

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
    furs = "A fine pelt announces itself before a customer says a word.",
    cold = "People wait until winter to care about quality.  That's how they end up paying twice.",
    trade = "Good furriers know trappers, roads, and weather almost as well as they know stitching.",
    default = "Ghaerdish eyes your gear appraisingly.  'If it's hide or fur, I have opinions.'",
}
NPC.ambient_emotes = {
    "Ghaerdish rubs a folded pelt between finger and thumb, testing its finish.",
    "Ghaerdish shakes out a fur-lined cloak and inspects the seams with narrowed eyes.",
    "Ghaerdish trims a loose thread with a small, sharp knife.",
    "Ghaerdish folds a finished garment with efficient, practiced care.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
