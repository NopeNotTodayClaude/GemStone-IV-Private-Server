-- NPC: Sergeant Khorval
-- Role: townsfolk  |  Room: 10419
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "drill_sergeant"
NPC.name           = "Sergeant Khorval"
NPC.article        = ""
NPC.title          = "the drill sergeant"
NPC.description    = "A scarred, battle-hardened elf with a booming voice and an exacting eye.  He trains recruits with relentless discipline."
NPC.home_room_id   = 10419

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
NPC.greeting       = "eyes you critically.  'Another recruit?  Let's see what you're made of.'"
NPC.dialogues = {
    training = "You want to get stronger?  Then fight!  Experience is the only true teacher.",
    combat = "Strike hard, strike true, and never leave your flank exposed.  Simple.  Hard to remember when something's trying to kill you.",
    skills = "Practice your weapon skills every day.  A dull blade and dull skills will get you killed.",
    hunting = "Head south past the Amaranth Gate if you want real combat training.  The fanged rodents won't grade on a curve.",
    legion = "Every recruit thinks they're ready.  Three in ten actually are.  You look like you might be.",
    default = "Sergeant Khorval barks, 'Less talking, more fighting!'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Sergeant Khorval barks orders at a group of elven recruits.",
    "Sergeant Khorval demonstrates a sword technique with fluid precision.",
    "Sergeant Khorval shakes his head at a recruit's clumsy footwork.",
    "Sergeant Khorval bellows, 'Again!  And this time with FEELING!'",
    "Sergeant Khorval paces the line of trainees with his hands clasped behind his back.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 30

return NPC
