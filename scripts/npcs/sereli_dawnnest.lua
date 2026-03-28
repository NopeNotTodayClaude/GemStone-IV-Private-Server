local NPC = {}

NPC.template_id    = "sereli_dawnnest"
NPC.name           = "Sereli Dawnnest"
NPC.article        = ""
NPC.title          = "the starleaf companioner"
NPC.description    = "Sereli's pale hair is woven with tiny crystal leaves, and her calm voice never rises even when the portrait wall flickers with sudden color and motion."
NPC.home_room_id   = 36482

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = true
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    pet = "The portrait wall will present every companion available to you once you invoke PET SHOP.",
    floofer = "Your first Floofer costs nothing, but naming and claiming it is still a deliberate choice.  PET SHOP will guide you through it.",
    treat = "Training food should be carried with you.  Feed it in the field with PET FEED <treat> when the two-hour window has reset.",
    swap = "The wall handles swaps cleanly, but only while you stand inside the menagerie.",
    default = "Moonwhisker Menagerie is prepared whenever you are.  Use PET SHOP to begin, PET STATUS to review your companion, and PET HELP for the full command list.",
}

NPC.ambient_emotes = {
    "Sereli Dawnnest smooths a star-patterned cloth beneath a row of crystal treat jars.",
    "Sereli Dawnnest rests her fingertips on a portrait frame until its glow steadies into a warm pulse.",
    "Sereli Dawnnest studies a ledger page, then marks it with a precise silver stroke.",
    "Sereli Dawnnest glances toward the companion portraits with quiet approval.",
}
NPC.ambient_chance = 0.05
NPC.emote_cooldown = 25
NPC.chat_interval  = 315
NPC.chat_chance    = 0.14
NPC.chat_lines = {
    "Companions respond well to ritual and consistency.  Treats are part of that, not a shortcut around it.",
    "The first Floofer is free because every worthy adventurer should know what loyal starlight feels like.",
    "A companion dismissed here is not lost.  It is merely waiting for your next proper call.",
    "The portrait wall only opens for those already standing in the menagerie.  That is quite intentional.",
}

return NPC
