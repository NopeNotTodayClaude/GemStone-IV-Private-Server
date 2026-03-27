-- NPC: Foreman Belgast
-- Role: service  |  Room: 10439
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "moving_foreman"
NPC.name           = "Foreman Belgast"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A broad-shouldered elf who looks like he could carry a house single-handedly.  He coordinates the flow of goods and containers through the warehouse."
NPC.home_room_id   = 10439

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
NPC.greeting       = "nods briefly without stopping what he's doing."
NPC.dialogues = {
    move = "Need goods transported?  We handle crates, furniture, containers, anything.",
    warehouse = "We store containers here between moves.  Ask about our storage rates.",
    canopies = "We also sell canopies, decorations, and signage for merchants.  Quality stock.",
    default = "Foreman Belgast crosses his arms.  'Moving something?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Foreman Belgast directs workers loading a large crate onto a cart.",
    "Foreman Belgast checks items off a manifest with a stubby pencil.",
    "Foreman Belgast hefts a heavy crate effortlessly and stacks it.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
