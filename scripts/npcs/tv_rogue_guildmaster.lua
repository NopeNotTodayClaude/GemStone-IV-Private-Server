local NPC = {}

NPC.template_id    = "tv_rogue_guildmaster"
NPC.name           = "the guildmaster"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A composed veteran rogue whose stillness feels more deliberate than restful, as though every sound in the guild reaches him sooner or later."
NPC.home_room_id   = 17831

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
    guild = "A guildmaster's business is continuity.  Membership, invitations, promotions, and the quiet correction of mistakes all end up here sooner or later.",
    guildmaster = "Guildmaster candidates need 125 total guild ranks and a mastered track.  After that, the guild decides whether the office would survive them.",
    nominate = "Use GLD NOMINATE when you are ready to put a real name behind a real candidate.",
    promote = "Use GLD PROMOTE when the ledger says someone has earned the step and the room agrees.",
    invite = "An invitation is not a courtesy.  It is the guild deciding someone might be worth the risk.",
    initiate = "If you hold the office, GLD INITIATE brings a proven candidate in cleanly.",
    password = "The inner-door sequence matters because fools repeat what they overhear.  Rogues keep it because they were trusted with it.",
    default = "The guildmaster studies you for a long moment.  'If you need the office, say it plainly.'",
}
NPC.ambient_emotes = {
    "The guildmaster closes a worn ledger, rests one hand on it, and looks toward the hallway without comment.",
    "The guildmaster glances toward the treated window, then resumes reviewing the records on the desk.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.guild_id       = "rogue"

return NPC
