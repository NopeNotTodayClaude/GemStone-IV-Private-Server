-- NPC: Beldrin
-- Zone/Town: auto-placed  |  Room: 16393
local NPC = {}

NPC.template_id    = "wl_beldrin"
NPC.name           = "Beldrin"
NPC.article        = ""
NPC.title          = "rogue guildmaster"
NPC.description    = "A lean half-elven man who moves with deliberate quietness."
NPC.home_room_id   = 8820

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
    rogue = "A rogue guildmaster has one duty above all: keep the guild useful and keep it quiet.",
    guild = "Use GLD for the ledger.  Use GLD NOMINATE and GLD PROMOTE when the time comes to recognize real mastery.",
    training = "You are expected to know dirty fighting, locks, recovery, and nerve.  The guild tracks all of it.",
    guildmaster = "Guildmaster candidates need 125 total ranks and a mastered track.  The rest is judgment.",
    quest = "If you still need proving work, use GLD QUEST START and finish what the guild lays before you.",
    default = "Beldrin watches you in patient silence before speaking.  'The guild records skill, not excuses.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
