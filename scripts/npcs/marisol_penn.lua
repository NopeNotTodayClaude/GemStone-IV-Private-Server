local NPC = {}

NPC.template_id    = "marisol_penn"
NPC.name           = "Marisol Penn"
NPC.article        = ""
NPC.title          = "the menagerie attendant"
NPC.description    = "Marisol has the practical posture of a dockside merchant, though the silver stars sewn into her dark coat soften the effect whenever she turns beneath the lamplight."
NPC.home_room_id   = 36480

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
    pet = "That portrait wall handles every adoption, swap, and training purchase in the menagerie.  PET SHOP opens it.",
    floofer = "First Floofer is free.  It still needs a proper claim and a proper name, though, so use PET SHOP.",
    treat = "Treats belong in your pack, not in our display bowls.  Feed them in the field with PET FEED <treat> when the cooldown is ready.",
    swap = "Swap as often as you like, so long as you do it here through the portrait wall.",
    default = "If you want the catalogue, use PET SHOP.  PET STATUS covers your active companion, and PET HELP covers the rest.",
}

NPC.ambient_emotes = {
    "Marisol Penn adjusts a velvet collar stand and scribbles a price correction onto a tiny tag.",
    "Marisol Penn checks the portrait wall, making sure each framed companion image is still glowing steadily.",
    "Marisol Penn shakes a tin of training treats, listening to the rattle with professional concentration.",
    "Marisol Penn folds a stack of adoption papers with dockside efficiency.",
}
NPC.ambient_chance = 0.05
NPC.emote_cooldown = 25
NPC.chat_interval  = 320
NPC.chat_chance    = 0.14
NPC.chat_lines = {
    "A companion claimed properly will follow you for years.  One claimed carelessly usually follows you into trouble.",
    "Training is slower than spoiling, but the results are better.",
    "The wall tracks every companion you own.  It does not forget, and neither do I.",
    "Free first Floofer, yes.  Free second one?  Not a chance.",
}

return NPC
