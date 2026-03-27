-- NPC: a shadowy contact
-- Zone/Town: auto-placed  |  Room: 18348
local NPC = {}

NPC.template_id    = "tv_rogue_guild_contact"
NPC.name           = "a shadowy contact"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "An unremarkable figure whose forgettable appearance is itself a professional achievement."
NPC.home_room_id   = 18348

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
    rogue = "Guild business is handled quietly here.  If you belong, you already know what to ask.",
    guild = "If you need the guild ledger, use GLD while you are here.",
    join = "If you have already been invited inside, GLD JOIN will let me record your membership.",
    invite = "The shed keeps its own secrets.  Earn your invitation first, then use the sequence.",
    password = "The shed sequence begins with a lean.  The rest is not repeated lightly.",
    training = "Use GLD SKILLS to review your tracks, GLD TASK for work, GLD PRACTICE for hall drills, GLD COMPLETE when you're done, and GLD QUEST START if you want the guild to test you more directly.",
    quest = "The guild does not care for dramatics.  If you want guided work, ask the ledger with GLD QUEST START.",
    default = "The shadowy contact studies you for a moment.  'If this is guild business, speak plainly.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
