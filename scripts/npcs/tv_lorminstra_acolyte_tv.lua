-- NPC: a Lorminstra acolyte
-- Zone/Town: auto-placed  |  Room: 10376
local NPC = {}

NPC.template_id    = "tv_lorminstra_acolyte_tv"
NPC.name           = "a Lorminstra acolyte"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A robed elven acolyte tending the shrine with obvious devotion."
NPC.home_room_id   = 10376

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
    shrine = "The shrine asks for reverence, not eloquence.",
    death = "Most people fear speaking plainly about death more than death itself.",
    prayer = "If you need quiet, the shrine offers it freely.",
    default = "The acolyte folds his hands and offers a soft nod.  'If you seek the shrine, you are welcome.'",
}
NPC.ambient_emotes = {
    "The acolyte straightens a candle and checks the burn of the wick.",
    "The acolyte murmurs a brief prayer too soft to make out.",
    "The acolyte gathers a few withered petals from the shrine floor and sets them aside.",
    "The acolyte adjusts his robe sleeves and resumes a quiet vigil.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
