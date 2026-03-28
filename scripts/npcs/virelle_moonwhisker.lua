local NPC = {}

NPC.template_id    = "virelle_moonwhisker"
NPC.name           = "Virelle"
NPC.article        = ""
NPC.title          = "the Moonwhisker keeper"
NPC.description    = "Virelle wears layered violet silks dusted with silver thread, and she carries herself with the effortless calm of someone entirely accustomed to excitable companions and nervous first-time owners."
NPC.home_room_id   = 36479

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
    pet = "The portrait wall handles every adoption, swap, and training purchase here.  Use PET SHOP when you are ready to open it.",
    floofer = "Your first Floofer is listed as FREE, but you still need to claim it properly through PET SHOP and give it a name.",
    treat = "Training treats are bought here, carried in your normal inventory, and fed in the field with PET FEED <treat>.  Each companion can only benefit once every two hours.",
    swap = "Swaps are free for companions you already own, but they are always handled here through PET SHOP while you stand in the menagerie.",
    default = "Welcome to Moonwhisker Menagerie.  Use PET SHOP to open the portrait wall, PET STATUS to review your companion, and PET HELP if you want the full command list.",
}

NPC.ambient_emotes = {
    "Virelle dusts one of the glowing portrait frames and quietly checks a training ledger.",
    "Virelle straightens a row of treat tins and smiles to herself.",
    "Virelle murmurs something encouraging to a drifting portrait image before smoothing her sleeves.",
    "Virelle taps a silver stylus against the counter and studies the companion board.",
}
NPC.ambient_chance = 0.06
NPC.emote_cooldown = 20
NPC.chat_interval  = 280
NPC.chat_chance    = 0.18
NPC.chat_lines = {
    "Companions are adopted through the portrait wall, not bought off the shelf like rope or soap.",
    "A Floofer grows with patience, routine, and perhaps a suspicious number of treats.",
    "If you are here for a swap, the wall already knows which companions belong to you.",
    "The menagerie keeps careful records.  Your companion's gear stays with the companion, not the shelf.",
}

return NPC
