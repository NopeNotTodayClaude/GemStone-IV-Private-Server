-- NPC: Daervith
-- Role: guard  |  Room: 5906
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_annatto_daervith"
NPC.name           = "Daervith"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "A stocky elven soldier who gives the impression of someone doing an excellent job of pretending not to be bored.  He brightens noticeably when anyone approaches."
NPC.home_room_id   = 5906

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Shift system ─────────────────────────────────────────────────────────────
NPC.shift_id       = "annatto"
NPC.shift_phase    = 0
NPC.spawn_at_start = true

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "brightens noticeably when he sees you approaching."
NPC.dialogues = {
    bored = "Eight hours at this post with nothing to look at but the Neartofar road.  I could tell you every rut in it.",
    drink = "I'd give a week's pay for something cold to drink right now.  Not complaining.  Just saying.",
    neartofar = "Neartofar is a good day's travel south.  Nothing interesting on the road until you get there.",
    hunting = "You want to hunt?  Go back to Amaranth Gate.  Better hunting south of there.",
    gate = "Annatto Gate.  All trade traffic to Neartofar.  Merchants, travelers.  Rarely anything exciting.",
    water = "A fresh glass of water from Malwith Inn would improve the watch.  Use QUEST START tv_guard_water_annatto first so I know you're serious.",
    job = "If you want something useful to do, bring water and I'll make it worth your while.",
    default = "Daervith perks up slightly.  'Someone to talk to!  I mean - state your business.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Daervith sighs quietly and resumes watching the road.",
    "Daervith counts the paving stones for what is clearly not the first time.",
    "Daervith straightens abruptly as someone approaches, then relaxes when he sees who it is.",
    "Daervith drums his fingers on his spear shaft once, then stops himself.",
    "Daervith glances toward Helgreth's Tavern with a wistful expression.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 35
NPC.chat_interval   = 510
NPC.chat_chance     = 0.15
NPC.chat_lines = {
    "Annatto Gate is quiet enough that a person starts naming the paving stones.",
    "Quiet posts are good for the nerves and bad for the imagination.",
    "I keep hoping for interesting weather and then remember I'd hate that.",
    "The merchants on this side complain less than the ones at Vermilion.  I appreciate that.",
    "If Helgreth sends a runner with food, tell him I am grateful and suffering nobly.",
    "A calm road has its own sort of music.",
    "Most people think guard duty is excitement.  Mostly it is attention stretched over hours.",
    "If the road stays boring, I count the day a success.",
    "I would never say I enjoy this post.  I would say it grows on a person.",
    "Someone has to guard the gate even on the days when nothing memorable happens.",
    "When Annatto gets lively, everyone suddenly misses the quiet.",
    "I have learned that boredom is usually a sign the professionals are doing their jobs.",
}

return NPC
