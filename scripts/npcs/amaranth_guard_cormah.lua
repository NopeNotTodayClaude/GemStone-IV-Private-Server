local NPC = {}

NPC.template_id    = "amaranth_guard_cormah"
NPC.name           = "Cormah"
NPC.article        = ""
NPC.title          = "the Legion guardsman"
NPC.description    = "A silver-browed elven guardsman with a weathered scabbard and the calm confidence of a seasoned professional."
NPC.home_room_id   = 3727

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
    legion = "A gate crew is strongest when nobody needs to raise their voice.",
    hunting = "Amaranth traffic teaches you the look of a hunter before the mud on the boots does.",
    default = "Cormah gives you a professional once-over and a short nod.",
}
NPC.ambient_emotes = {
    "Cormah rests his thumb against his belt buckle and watches the bridge traffic.",
    "Cormah glances toward Sorvael as if confirming an unspoken agreement.",
    "Cormah shifts a foot half an inch and somehow makes the motion look ceremonial.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 90

return NPC
