-- NPC: Sylindra
-- Role: shopkeeper  |  Room: 10329
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "sylindra"
NPC.name           = "Sylindra"
NPC.article        = ""
NPC.title          = "the leatherworker"
NPC.description    = "A lean elven woman with sharp eyes and nimble fingers.  She works leather with an artisan's care, each stitch precise and nearly invisible."
NPC.home_room_id   = 10329

-- ── Capabilities ─────────────────────────────────────────────────────────────
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

-- ── Shop ─────────────────────────────────────────────────────────────────────
NPC.shop_id        = 3

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks up from her stitching with a professional smile."
NPC.dialogues = {
    leather = "My leathers are supple yet strong.  Perfect for those who value mobility.",
    armor = "I specialize in leather armor - from simple jerkins to reinforced brigandine.",
    containers = "I also craft fine leather packs and pouches.  Every adventurer needs good storage.",
    furs = "The fur stock is in back.  Ghaerdish handles those - he's out on a buying trip.",
    buy = "LIST to see my goods, BUY what suits you.",
    sell = "I'll buy quality leatherwork.  SELL me what you don't need.",
    default = "Sylindra looks up from her stitching.  'Something catch your eye?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Sylindra stitches a seam on a dark leather jerkin with thread so fine it's nearly invisible.",
    "Sylindra tests the suppleness of a piece of cured leather, bending it back and forth.",
    "Sylindra cuts a precise pattern from a sheet of tanned hide.",
    "Sylindra applies a coat of oil to a finished leather backpack.",
    "Sylindra trims an errant thread with a small, wickedly sharp knife.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
