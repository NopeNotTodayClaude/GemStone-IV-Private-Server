-- NPC: Raging Thrak
-- Source: GemStone IV Wiki / starter mentor guidance
local NPC = {}

NPC.template_id    = "raging_thrak"
NPC.name           = "Raging Thrak"
NPC.article        = ""
NPC.title          = "the old warrior"
NPC.description    = "A battered old warrior lounges in his booth with the heavy stillness of someone who once lived by motion alone.  A scarred mug sits near one broad hand, and his pale eyes are sharper than the rest of him suggests."
NPC.home_room_id   = 8722   -- LICH 4041001

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

NPC.greeting       = "squints at you over his mug.  'Need sense talked into you?'"
NPC.dialogues = {
    advice = "If you want the fast version, listen first and survive second.  If you want the longer version, start my lesson properly.",
    lesson = "Sit down, keep your ears open, and use QUEST START raging_thrak_lesson when you're ready to prove you were listening.",
    work = "Not work.  Wisdom.  Less profitable, more durable.",
    new = "New blood ought to learn the town before it learns the graveyard.  I can help with the first part.",
    default = "Raging Thrak snorts softly.  'Well?  Need advice, or just shelter?'",
}
NPC.ambient_emotes = {
    "Raging Thrak scratches at an old scar and watches the room through half-lidded eyes.",
    "Raging Thrak snorts into his mug as if remembering something unpleasantly funny.",
    "Raging Thrak shifts in his chair, the leather creaking like an old warning.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.chat_interval  = 420
NPC.chat_chance    = 0.12
NPC.chat_lines = {
    "You can learn a lot in town if you keep your mouth shut long enough.",
    "The trick to heroics is living long enough to deserve the word.",
    "Most trouble starts with folk deciding rules are meant for somebody else.",
    "Ask polite, listen close, and don't grab what isn't yours.",
    "If you want the lesson, say so plain and take it seriously.",
}

return NPC
