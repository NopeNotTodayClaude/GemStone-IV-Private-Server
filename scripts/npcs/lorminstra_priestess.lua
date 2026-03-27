-- NPC: a middle-aged elven priestess
-- Role: townsfolk  |  Room: 3535
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "lorminstra_priestess"
NPC.name           = "a middle-aged elven priestess"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A serene elven woman of indeterminate middle age, with blond hair beginning to silver at her temples.  She wears the simple white and black vestments of Lorminstra's clergy and carries a small prayer book."
NPC.home_room_id   = 3535

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
NPC.patrol_rooms   = { 3535, 3539, 3540, 3542, 3519, 3518, 3542, 3535 }
NPC.wander_chance  = 0.2
NPC.move_interval  = 50

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "nods with quiet warmth."
NPC.dialogues = {
    lorminstra = "The Lady of the Dead offers passage to all who die with courage in their hearts.  She is not to be feared.",
    death = "Death is a threshold, not an end.  I have seen enough of it to know the difference.",
    deeds = "Buy a deed from Clentaran before you hunt in earnest.  The Lady appreciates those who value their own lives.",
    faith = "I don't press my faith on others.  I simply try to be here when it matters.",
    afterlife = "What comes after?  I can tell you what the Lady shows us.  Beyond that, it remains one of life's genuine mysteries.",
    default = "The priestess pauses and offers a calm smile.  'May your journey be safe.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "A middle-aged elven priestess reads quietly from a small prayer book.",
    "A middle-aged elven priestess pauses at a small roadside shrine and adds a flower.",
    "A middle-aged elven priestess offers a quiet word and a nod to a somber-looking passerby.",
    "A middle-aged elven priestess traces a slow, deliberate sign in the air - a blessing.",
    "A middle-aged elven priestess stands in brief stillness, her lips moving in silent prayer.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 40

return NPC
