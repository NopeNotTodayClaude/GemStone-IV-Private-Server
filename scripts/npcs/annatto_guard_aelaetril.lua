local NPC = {}

NPC.template_id    = "annatto_guard_aelaetril"
NPC.name           = "Aelaetril"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A poised Vaalor guardswoman whose expression suggests a low tolerance for disorganization."
NPC.home_room_id   = 5906

NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

NPC.dialogues = {
    gate = "Annatto stays pleasant largely because somebody stands here prepared for it not to.",
    merchants = "Trade runs smoother when merchants see order before they see customers.",
    default = "Aelaetril acknowledges you with tidy professional courtesy.",
}
NPC.ambient_emotes = {
    "Aelaetril checks the road toward Neartofar with a level, practical gaze.",
    "Aelaetril smooths the cuff of one glove and resumes her watch.",
    "Aelaetril lets a wagon pass, then studies the next traveler in line.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
