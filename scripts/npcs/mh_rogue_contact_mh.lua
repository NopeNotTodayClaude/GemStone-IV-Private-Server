-- NPC: a broken stein patron
-- Zone/Town: auto-placed  |  Room: 19337
local NPC = {}

NPC.template_id    = "mh_rogue_contact_mh"
NPC.name           = "a broken stein patron"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A regular at the back corner of the Broken Stein who seems to be waiting for something."
NPC.home_room_id   = 19337

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
    rogue = "Broken Stein or not, guild business still keeps to the shadows.",
    guild = "If you belong here, use GLD and the ledger will answer you.",
    join = "If you have the standing to join, the hidden way inward will open to you here soon enough.",
    training = "Use GLD SKILLS for your tracks, GLD TASK for assignments, and GLD QUEST START for guided work.",
    lock = "A rogue who cannot read a lock is only half trained.",
    gambit = "Nerve matters as much as blade work.  The guild trains both.",
    default = "The patron tips a broken stein toward you.  'If this is guild business, keep it brief.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
