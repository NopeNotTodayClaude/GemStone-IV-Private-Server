-- NPC: Vorenus Faendryl
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Old Ta'Faendryl
local NPC = {}

NPC.template_id    = "vorenus_faendryl"
NPC.name           = "Vorenus Faendryl"
NPC.article        = ""
NPC.title          = "Faendryl sorcerer"
NPC.description    = "A dark elven sorcerer whose work in necromantic theory is both extensive and carefully documented."
NPC.home_room_id   = 10886

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    sorcerer = "The Sorcerer Guild is not for the timid.  We cultivate command over dangerous principles, not excuses.",
    join = "If you have survived long enough to qualify, the guild can acknowledge you.",
    training = "Shadowcraft, demonology, and necromancy all punish laziness differently.",
    scrolls = "Infused texts are useful only to sorcerers who understand what they are waking.",
    default = "Vorenus Faendryl regards you coolly.  'Do not waste either of our time.'",
}
NPC.ambient_emotes = {
    "Vorenus Faendryl flips through a black-bound folio, pausing at one page longer than the rest.",
    "Vorenus Faendryl adjusts a ring set with a dull violet stone and says nothing.",
    "Vorenus Faendryl studies the room as if evaluating structural weaknesses invisible to others.",
}
NPC.ambient_chance = 0.025
NPC.emote_cooldown = 60
NPC.guild_id       = "sorcerer"

return NPC
