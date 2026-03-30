local NPC = {}

NPC.template_id    = "tv_rogue_bruiser"
NPC.name           = "Marn"
NPC.article        = ""
NPC.title          = "the bruiser"
NPC.description    = "Broad-shouldered and broken-nosed, Marn wears the look of a man who has ended more arguments with leverage than with eloquence."
NPC.home_room_id   = 17819

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
    training = "Sweep, Subdue, Cheapshots.  Pretty names for the same lesson: finish the exchange before the fool across from you understands it started.",
    cheapshot = "If it feels unfair, good.  That's the point.",
    subdue = "A clean takedown beats a corpse when the guild needs answers.",
    sweep = "Feet go, then balance goes, then the rest of them follows.",
    default = "Marn folds his arms.  'If you're looking for graceful, try the drill court.  If you're looking to win, stay here.'",
}
NPC.ambient_emotes = {
    "Marn nudges the practice dummy's footing with one boot and sends it flat with a contemptuous twist.",
    "Marn drags a crate aside with one hand, clearing space for another ugly lesson.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.guild_id       = "rogue"

return NPC
