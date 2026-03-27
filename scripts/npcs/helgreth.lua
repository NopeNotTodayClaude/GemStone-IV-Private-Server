-- NPC: Helgreth
-- Role: shopkeeper  |  Room: 10424
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "helgreth"
NPC.name           = "Helgreth"
NPC.article        = ""
NPC.title          = "the tavernkeeper"
NPC.description    = "A barrel-chested elven man with a booming laugh and forearms like ham hocks.  He runs his tavern with the same commanding presence he once used on a battlefield."
NPC.home_room_id   = 10424

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = true
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Shop ─────────────────────────────────────────────────────────────────────
NPC.shop_id        = 11

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "bellows a welcome loud enough to be heard over any noise."
NPC.dialogues = {
    drink = "Finest spirits in Ta'Vaalor.  Pressed from grapes grown on the southern slopes.",
    food = "Kitchen's open all hours.  Good honest fare - nothing fancy, nothing disappointing.",
    stay = "Rooms are available upstairs.  Quiet after midnight, that's my only rule.",
    legion = "Half my regulars are off-duty Legion.  Best customers in the world - as long as the drinks keep coming.",
    rumors = "Keep your ears open in here.  Soldiers talk when they drink.  Useful information floats around.",
    tedrik = "Tedrik?  Corner table, same as always.  Drinks the same thing he's drunk for forty years.  I respect that kind of commitment.",
    buy = "LIST to see what's on the menu.  BUY what you want.",
    default = "Helgreth sets down a large mug.  'Drink?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Helgreth wipes down the bar with a broad sweep of his arm.",
    "Helgreth draws a large mug of ale with practiced efficiency.",
    "Helgreth laughs explosively at something an off-duty soldier says.",
    "Helgreth calls back to the kitchen in a voice that carries through walls.",
    "Helgreth leans on the bar and surveys his domain with obvious satisfaction.",
    "Helgreth polishes a glass until it squeaks, holding it up to the lamplight.",
}
NPC.ambient_chance  = 0.05
NPC.emote_cooldown  = 25

return NPC
