-- NPC: Old Taervek
-- Role: townsfolk  |  Room: 13482
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "fisherman"
NPC.name           = "Old Taervek"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A weathered elf who smells strongly of fish and river water.  He has the unhurried manner of someone who has spent decades watching a bobber."
NPC.home_room_id   = 13482

-- ── Capabilities ─────────────────────────────────────────────────────────────
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

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "nods slowly without looking up from his line."
NPC.dialogues = {
    fish = "The Mistydeep runs cold and deep.  Good fishing if you're patient.",
    bait = "Worms work best in the morning.  Flies in the evening.  Don't let anyone tell you different.",
    river = "I've fished this river for two hundred years.  She keeps her secrets.  I keep mine.",
    hunting = "Young people these days.  Always hunting.  The fish don't try to kill you back.",
    default = "Old Taervek squints at you.  'You fish?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Old Taervek jiggles his fishing line with a practiced flick.",
    "Old Taervek rebaits his hook with a calm, practiced motion.",
    "Old Taervek stares at the water with total, peaceful concentration.",
    "Old Taervek mutters something to the river that no one else can hear.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 90

return NPC
