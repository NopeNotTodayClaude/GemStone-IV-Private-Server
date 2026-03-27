-- NPC: a brewery worker
-- Zone/Town: auto-placed  |  Room: 16838
local NPC = {}

NPC.template_id    = "zl_rogue_contact_zl"
NPC.name           = "a brewery worker"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A dwarven worker at the brewery whose secondary occupation is carefully unspoken."
NPC.home_room_id   = 16838

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
    rogue = "A brewery teaches patience, timing, and how to keep your hands steady.  So does the guild.",
    guild = "Use GLD for the formal side of things.  I handle the quiet local side.",
    training = "Work your tasks, mind your locks, and learn to turn a bad fight your way.",
    quest = "If you want guided guild work, use GLD QUEST START.",
    default = "The worker barely glances over.  'If this is guild business, say it plain and low.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

return NPC
