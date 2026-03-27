-- NPC: Kreldor
-- Role: service  |  Room: 3521
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "kreldor"
NPC.name           = "Kreldor"
NPC.article        = ""
NPC.title          = "the weapon trainer"
NPC.description    = "A battle-scarred elven veteran with a missing finger on his left hand and eyes that have seen enough combat to recognize a fighter at a glance."
NPC.home_room_id   = 17215

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "looks you over with a veteran's assessment.  'You've been fighting.  I can tell.'"
NPC.dialogues = {
    training = "The Warrior Guild charges for advanced training, but the basics are on me.  Stance and footwork - the rest follows.",
    combat = "Every fight teaches you something.  Surviving it long enough to learn is the hard part.",
    weapons = "Find a weapon that fits your style and master it.  Generalists die faster.",
    skills = "Physical Fitness, Dodging, your weapon skill.  Those are your priorities at your level.",
    guild = "The Guild tracks your progress.  Come back when you've earned your first rank advancement.",
    legion = "I served twelve years in the Legion before retiring to this.  Teaching is its own reward.",
    default = "Kreldor crosses his arms and studies you.  'How's your footwork?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Kreldor demonstrates a disarm technique in slow motion, narrating each step.",
    "Kreldor corrects the grip of an imaginary sword, explaining the mechanics to no one in particular.",
    "Kreldor runs through a short weapon form, muscle memory making it effortless.",
    "Kreldor massages the stump of his missing finger absently, lost in thought.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 35
NPC.guild_id        = "warrior"

return NPC
