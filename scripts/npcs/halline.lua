-- NPC: Halline
local NPC = {}

NPC.template_id    = "halline"
NPC.name           = "Halline"
NPC.article        = ""
NPC.title          = "the taskmaster"
NPC.description    = "A broad-smiled but sharp-eyed woman manages the guild office with easy confidence.  Warmth reaches her expression faster than indulgence does."
NPC.home_room_id   = 3779   -- LICH 15004002

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

NPC.greeting       = "looks up with an appraising smile.  'Cold enough out there to make bounty work sound appealing?'"
NPC.dialogues = {
    bounty = "I issue work suited to what an adventurer can survive.  When the contracts are in order, ask and I'll point you at something useful.",
    work = "Town errands?  Talk to the bondsman.  Field work?  Talk to me.",
    guild = "The Adventurer's Guild exists to turn willing hands into useful hands.",
    default = "Halline gestures to the contract board.  'What sort of work are you after?'",
}
NPC.ambient_emotes = {
    "Halline pins a fresh contract to the board with quick, practiced fingers.",
    "Halline warms her hands near the hearth before returning to her paperwork.",
    "Halline scans a report and gives a low approving hum.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 55
NPC.chat_interval  = 450
NPC.chat_chance    = 0.10
NPC.chat_lines = {
    "The wise adventurer knows the difference between brave and unprepared.",
    "I prefer assignments that end with the contractor alive.",
    "Snow, wolves, brigands, paperwork.  Every town has its hazards.",
}

return NPC
