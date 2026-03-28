local NPC = {}

NPC.template_id    = "brindle_fenwhisker"
NPC.name           = "Brindle Fenwhisker"
NPC.article        = ""
NPC.title          = "the fen-born companioner"
NPC.description    = "A willow-thin halfling with bright alert eyes, Brindle wears a moss-green vest lined with tiny hidden pockets that seem to produce treats, ribbons, and paperwork on demand."
NPC.home_room_id   = 36481

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
    pet = "Use PET SHOP and the portrait wall will open right up for you.  That is where adoptions, swaps, and training supplies are handled.",
    floofer = "First Floofer is free.  Best kind of expensive, that.  Open PET SHOP, claim it, and give it a name worth hearing.",
    treat = "Two-hour wait between training treats per companion.  Buy them here, carry them with you, and feed them later with PET FEED <treat>.",
    swap = "Swaps are easy enough, but only here where the wall can keep the paperwork honest.",
    default = "Moonwhisker Menagerie keeps the wall ready.  PET SHOP opens it, and PET HELP lays out the rest.",
}

NPC.ambient_emotes = {
    "Brindle Fenwhisker flips a sugar-dusted treat into the air and catches it again with a satisfied nod.",
    "Brindle Fenwhisker polishes a portrait frame using the corner of a moss-green handkerchief.",
    "Brindle Fenwhisker hums under his breath while counting small stacks of silver tokens.",
    "Brindle Fenwhisker crouches to straighten a companion bed tucked neatly beneath the counter.",
}
NPC.ambient_chance = 0.05
NPC.emote_cooldown = 25
NPC.chat_interval  = 305
NPC.chat_chance    = 0.15
NPC.chat_lines = {
    "Companions are easier to train when you remember the treats, harder when you forget the cooldown.",
    "Every pet's gear stays with the pet.  Makes swaps tidier and tempers shorter.",
    "A Floofer can save your life, but it cannot save you from stubbornness.",
    "The portrait wall knows your companions better than most adventurers know their own lockers.",
}

return NPC
