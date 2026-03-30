local NPC = {}

NPC.template_id    = "tv_rogue_lockmaster"
NPC.name           = "Sable"
NPC.article        = ""
NPC.title          = "the lockmaster"
NPC.description    = "A lean woman with iron-gray eyes, scarred fingertips, and the patient expression of someone who has watched more than one overeager rogue ruin a promising set of picks."
NPC.home_room_id   = 17827

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = true
NPC.is_quest       = true
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    lock = "Locks lie.  Tumblers, springs, false chambers, all of them.  Lock Mastery teaches you how to make them tell the truth.",
    mastery = "Use GLD TASK when you want the guild to hand you real work, and GLD PRACTICE when the hall itself is the lesson.",
    training = "Boxes, traps, calipers, and patience.  A loud rogue learns slowly and bleeds often.",
    guild = "The factor keeps the ledger.  I keep rogues from pretending a snapped pick counts as progress.",
    default = "Sable glances up from a half-open practice box.  'If you're here for Lock Mastery, keep your hands steady and your mouth shut.'",
}
NPC.ambient_emotes = {
    "Sable turns a practice lock half a notch, listens, and resets it without looking impressed.",
    "Sable lines up a row of bent picks and dismisses two of them with a quiet click of her tongue.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.guild_id       = "rogue"

return NPC
