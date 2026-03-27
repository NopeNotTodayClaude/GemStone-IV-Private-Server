-- NPC: Rheteger
local NPC = {}

NPC.template_id    = "rheteger"
NPC.name           = "Rheteger"
NPC.article        = ""
NPC.title          = "the taskmaster"
NPC.description    = "A hawk-nosed guild veteran stands behind an elegant desk with the straight-backed patience of someone who has assigned work to every sort of adventurer and been disappointed by most of them."
NPC.home_room_id   = 3785   -- LICH 15000003

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

NPC.greeting       = "reviews a contract, then flicks his attention to you.  'Looking for bounty work?'"
NPC.dialogues = {
    bounty = "The Guild issues practical work, not heroic fantasies.  Ask about bounty and I'll issue cull, gem, skin, forage, escort, rescue, bandit, boss, or heirloom recovery work if your record supports it.",
    work = "If you want civic errands, see the town clerk.  If you want harder work, see me.",
    guild = "The Guild pays for competence.  It has less patience for storytelling.",
    vouchers = "Swaps cost vouchers.  Check in and finish your contracts if you want the Guild to trust you with more latitude.",
    checkin = "I can mark your check-in right here.  It keeps your guild record current.",
    default = "Rheteger folds his hands.  'Ask plainly and I'll answer plainly.'",
}
NPC.ambient_emotes = {
    "Rheteger initials the corner of a contract and slides it into a neat stack.",
    "Rheteger studies the bounty board with a critical eye.",
    "Rheteger rubs a thumb along the edge of a parchment packet before setting it aside.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 55
NPC.chat_interval  = 450
NPC.chat_chance    = 0.10
NPC.chat_lines = {
    "A good contract begins with accurate information.",
    "If you can't follow directions in town, you won't last long in the wilds.",
    "The Guild rewards results, not enthusiasm.",
}

return NPC
