-- NPC: an off-duty Legion officer
-- Role: townsfolk  |  Room: 3519
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "legion_officer_leave"
NPC.name           = "an off-duty Legion officer"
NPC.article        = "an"
NPC.title          = ""
NPC.description    = "A trim elven officer who has exchanged her armor for good civilian clothes but can't quite exchange the upright posture.  She's clearly savoring having nowhere to be."
NPC.home_room_id   = 3519

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = true
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Wander / patrol ──────────────────────────────────────────────────────────
NPC.patrol_rooms   = { 3519, 3542, 3519 }
NPC.wander_chance  = 0.1
NPC.move_interval  = 90

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "gives you a relaxed nod, a gesture very different from the on-duty version."
NPC.dialogues = {
    legion = "Fifteen years active.  Three days leave.  I intend to sleep for all of them.",
    combat = "I just got back from a patrol rotation near the Dragonspine pass.  Let's talk about something else.",
    hunting = "If you're level one or two, stick to the road south.  The fanged rodents are good practice.",
    rest = "The Legendary Rest has excellent beds.  I recommend them professionally and personally.",
    default = "The officer gives you a good-natured look.  'On leave.  Can't help you with official business.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "An off-duty Legion officer stretches and exhales slowly, the posture of someone deliberately not being anywhere.",
    "An off-duty Legion officer watches the city go by with the particular appreciation of someone who has been away.",
    "An off-duty Legion officer rolls her shoulders back and briefly looks like she's about to give an order, then stops.",
    "An off-duty Legion officer gets a small pastry from a nearby vendor and eats it with visible satisfaction.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 40

return NPC
