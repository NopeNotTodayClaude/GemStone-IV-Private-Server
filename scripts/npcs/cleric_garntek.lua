-- NPC: Cleric Garntek
-- Source: GemStone IV Wiki / Category:Non-Player_Characters
-- location_hint: Wehnimer's Landing
local NPC = {}

NPC.template_id    = "cleric_garntek"
NPC.name           = "Cleric Garntek"
NPC.article        = ""
NPC.title          = "cleric"
NPC.description    = "A dwarven cleric whose devotion to Lorminstra is absolute and occasionally inconvenient."
NPC.home_room_id   = 10376

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
    cleric = "The Cleric Guild tempers devotion with discipline.  Piety alone is not enough.",
    join = "If your calling is true and your level sufficient, the guild can receive you.",
    training = "Prayer, liturgy, and controlled channeling all matter.  Every rite has its proper form.",
    mana = "Shared grace is best offered with care.  A channeler who wastes power serves no one.",
    default = "Cleric Garntek folds his hands solemnly.  'Speak plainly, and with respect.'",
}
NPC.ambient_emotes = {
    "Cleric Garntek murmurs a quiet prayer beneath his breath.",
    "Cleric Garntek straightens a devotional text and presses it flat with a broad hand.",
    "Cleric Garntek surveys the courtyard with a stern but patient expression.",
}
NPC.ambient_chance = 0.025
NPC.emote_cooldown = 60
NPC.guild_id       = "cleric"

return NPC
