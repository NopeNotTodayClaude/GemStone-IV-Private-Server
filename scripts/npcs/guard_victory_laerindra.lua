-- NPC: Laerindra
-- Role: guard  |  Room: 5907
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "guard_victory_laerindra"
NPC.name           = "Laerindra"
NPC.article        = ""
NPC.title          = "the gate warden"
NPC.description    = "An older elven soldier whose close-cropped white hair and deep-set eyes give her the look of someone who has outlasted a great deal.  She moves with the economy of someone who stopped wasting effort long ago."
NPC.home_room_id   = 5907

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
NPC.shift_id       = "victory"
NPC.shift_phase    = 0
NPC.spawn_at_start = true

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = nil
NPC.dialogues = {
    wars = "I stood this gate during the Undead War.  Different gate then.  The old one didn't survive.  We rebuilt.",
    history = "Seven hundred years.  I've seen six kings, two succession crises, and one attempted coup.  The gate is still standing.",
    hunting = "Victory Road leads south through the forest.  Creatures get worse the deeper you go.  Know your limits.",
    gate = "The Victory Gate.  Named for the battle that ended the first major undead incursion.  We chose the name carefully.",
    water = "If you're looking to make yourself useful, bring me a glass of water from the Malwith Inn and use QUEST START tv_guard_water_victory before you go.",
    work = "Water first.  Heroics later.",
    rest = "Get rest when you can.  Eat properly.  Sleep.  These seem obvious.  You'd be surprised how often young soldiers forget.",
    default = "Laerindra observes you with calm, unhurried eyes.  'Through?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Laerindra stands with the absolute stillness of someone who has long since made peace with standing still.",
    "Laerindra watches the road south with eyes that have seen worse things on it.",
    "Laerindra turns her head slightly at a sound, evaluates it, and returns to stillness.",
    "Laerindra touches the wall of the gate briefly, a habitual gesture.",
}
NPC.ambient_chance  = 0.02
NPC.emote_cooldown  = 70
NPC.chat_interval   = 420
NPC.chat_chance     = 0.14
NPC.chat_lines = {
    "South road is quiet enough today.  I prefer it that way.",
    "If you're heading beyond the bridge, keep your eyes open and your pace steady.",
    "A gate holds because the people on it do not get careless.",
    "Victory Gate has seen uglier days than this one and remained standing.",
    "Most travelers announce themselves without realizing it.  The road tells on them first.",
    "Young guards think stillness is easy.  It only looks easy after a few decades.",
    "The bridge wind carries news faster than most runners.",
    "If you come back after dusk, don't drift across the threshold half asleep.",
    "The city sleeps because somebody remains awake.",
    "Hunters leave this gate bold and return through it thoughtful.",
    "Stone remembers every hand that has leaned against it in worry.",
    "The first lesson of gate duty is patience.  The second is more patience.",
}

return NPC
