-- NPC: Torsidr
local NPC = {}

NPC.template_id    = "torsidr"
NPC.name           = "Torsidr"
NPC.article        = ""
NPC.title          = "the taskmaster"
NPC.description    = "A lean Vaalor elf with a soldier's economy of movement, Torsidr keeps the guild ledger in exacting order and measures adventurers with the cool eye of a quartermaster."
NPC.home_room_id   = 10332   -- LICH 14103502

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = true
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.greeting       = "looks you over briskly.  'State your business.  If it's work, keep it brief.'"
NPC.dialogues = {
    bounty = "The Guild issues contracts according to ability and need.  Ask about bounty and I can issue cull, gem, skin, forage, escort, rescue, bandit, boss, or heirloom recovery work.",
    work = "If you want city errands, Sassion has them.  If you want contracts beyond the walls, ask me.",
    guild = "The Guild rewards discipline.  Ta'Vaalor approves of that arrangement.",
    vouchers = "Task exchanges are not free.  Earn vouchers through steady work and proper check-ins.",
    checkin = "I can record your check-in here and keep your file in order.",
    default = "Torsidr waits with military patience.  'Well?'",
}
NPC.ambient_emotes = {
    "Torsidr straightens a stack of contracts until their edges line up exactly.",
    "Torsidr marks a note on the board and steps back to inspect it.",
    "Torsidr glances toward the door each time it opens, taking stock automatically.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 55
NPC.chat_interval  = 440
NPC.chat_chance    = 0.10
NPC.chat_lines = {
    "A short contract finished well is worth more than a grand promise abandoned halfway through.",
    "The city keeps soldiers.  The Guild keeps specialists.",
    "Read the posting once.  Then read it again before you leave.",
}

return NPC
