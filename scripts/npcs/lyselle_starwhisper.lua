local NPC = {}

NPC.template_id    = "lyselle_starwhisper"
NPC.name           = "Lyselle Starwhisper"
NPC.article        = ""
NPC.title          = "the moonwhisker companioner"
NPC.description    = "A serene elf with silver-dusted braids and a gauzy lilac shawl, Lyselle keeps one hand on a slim training ledger and the other near a tray of glittering treat tins."
NPC.home_room_id   = 36478

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
    pet = "The portrait wall will guide you through every companion purchase, swap, and training supply here.  Use PET SHOP when you are ready.",
    floofer = "A first Floofer costs you nothing but attention and good sense.  Open PET SHOP, claim it, and choose a proper name.",
    treat = "Treats are fed in the field, not here.  Use PET FEED <treat> after you buy them, and remember each companion only learns from one every two hours.",
    swap = "Companion swaps are always done through the portrait wall while you are standing in the menagerie.",
    default = "Welcome to Moonwhisker Menagerie.  PET SHOP opens the portrait wall, and PET HELP will remind you of the rest.",
}

NPC.ambient_emotes = {
    "Lyselle Starwhisper adjusts a glowing portrait frame until its starlight settles into a soft pulse.",
    "Lyselle Starwhisper records a tiny note in her ledger and nods to herself.",
    "Lyselle Starwhisper straightens a line of treat jars, carefully aligning each silver label.",
    "Lyselle Starwhisper studies a painted Floofer portrait with obvious fondness.",
}
NPC.ambient_chance = 0.05
NPC.emote_cooldown = 25
NPC.chat_interval  = 300
NPC.chat_chance    = 0.16
NPC.chat_lines = {
    "Moonwhisker companions are claimed through the portrait wall, never by grabbing at the counter.",
    "A free first Floofer is still a proper adoption, not a shortcut.",
    "Training treats help a companion grow, but patience matters just as much as silver.",
    "One active companion at a time, darling.  The rest remain safely registered to your care.",
}

return NPC
