-- NPC: Raertria
-- Zone/Town: auto-placed  |  Room: 3519
local NPC = {}

NPC.template_id    = "tv_raertria"
NPC.name           = "a Legion courier-captain"
NPC.article        = "a"
NPC.title          = ""
NPC.description    = "A lean elven officer with a satchel of sealed dispatches and the brisk stare of someone who measures time in missed deadlines."
NPC.home_room_id   = 3519

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
    courier = "A city this size lives or dies on messages that arrive where they should.",
    dispatch = "If a dispatch is marked urgent, I prefer not to see it become historical.",
    court = "Victory Court is the right place to catch a runner, a clerk, or trouble pretending to be either.",
    default = "The courier-captain taps the satchel at her hip.  'If this is official business, be concise.'",
}
NPC.ambient_emotes = {
    "The courier-captain checks the wax seals on two folded dispatches.",
    "The courier-captain scans the square for runners with the eye of long practice.",
    "The courier-captain jots a short note and slips it into her satchel.",
    "The courier-captain exchanges a brisk nod with a passing guard.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
