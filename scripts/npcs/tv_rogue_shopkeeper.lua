local NPC = {}

NPC.template_id    = "tv_rogue_shopkeeper"
NPC.name           = "the dour shopkeeper"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A raggedly dressed elf with the stance of a prosperous fence, watching the room with one hand never far from the counter."
NPC.home_room_id   = 17821

NPC.can_combat     = false
NPC.can_shop       = true
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.shop_id        = 460

NPC.greeting       = "gives you a flat look across the counter.  'If there is anything worth selling today, ORDER will tell you.'"
NPC.dialogues = {
    guild = "Guild folk buy what keeps them useful.  The sentimental rubbish gets sold somewhere else.",
    wares = "If there is anything on offer today, ORDER will show it.  If there is not, then there is not.",
    order = "ORDER shows what is on the counter.  BUY takes it.  SELL lets me judge whether your clutter deserves coin.",
    buy = "Use ORDER first.  I do not recite inventories for free.",
    sell = "Hold it and SELL it.  I will decide whether it is worth the trouble.",
    default = "The dour shopkeeper flicks two fingers toward the counter.  'Browse if you must.'",
}
NPC.ambient_emotes = {
    "The dour shopkeeper adjusts a display with the care of someone counting profit by habit.",
    "The dour shopkeeper glances at the shelves, then at you, in that order.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45

return NPC
