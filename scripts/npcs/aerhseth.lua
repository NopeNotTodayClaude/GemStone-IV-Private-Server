-- NPC: Aerhseth
-- Role: shopkeeper  |  Room: 10367
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "aerhseth"
NPC.name           = "Aerhseth"
NPC.article        = ""
NPC.title          = "the weaponsmith"
NPC.description    = "A broad-shouldered elf with soot-streaked arms and keen eyes that appraise every weapon with a master's touch.  His hands are calloused from decades at the forge."
NPC.home_room_id   = 10367

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
NPC.shop_id        = 1

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks up from the anvil and nods in greeting."
NPC.dialogues = {
    weapons = "I forge the finest blades in all of Ta'Vaalor.  Browse my wares with LIST.",
    vaalorn = "Vaalorn is the sacred metal of our people.  Only the most skilled can work it.  I have a few pieces, but they don't come cheap.",
    forge = "This forge has burned for three centuries.  The heat never falters.",
    training = "You want to improve with a blade?  Hunt.  Nothing teaches you faster than something trying to kill you back.",
    legion = "I supply the Legion's standard issue.  What I sell here is the good stuff - personal work.",
    buy = "Use LIST to see my stock, then BUY to purchase.",
    sell = "I'll appraise your weapons.  Just SELL what you wish to part with.",
    default = "Aerhseth glances up from the anvil.  'Looking for a blade, are you?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Aerhseth hammers a glowing bar of steel with precise, ringing blows.",
    "Aerhseth examines a newly forged blade, turning it to catch the firelight.",
    "Aerhseth wipes sweat from his brow with a sooty forearm.",
    "Aerhseth stokes the forge, sending a shower of sparks upward.",
    "Aerhseth tests the edge of a longsword against his thumbnail and nods approvingly.",
    "Aerhseth quenches a blade in a trough of water, steam hissing dramatically upward.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
