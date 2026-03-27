-- NPC: Archivist Yendrel
-- Zone/Town: auto-placed  |  Room: 10379
local NPC = {}

NPC.template_id    = "tv_antiques_archivist"
NPC.name           = "Archivist Yendrel"
NPC.article        = ""
NPC.title          = "antiquarian"
NPC.description    = "A meticulous elven scholar who regards every item as historical document first, merchandise second."
NPC.home_room_id   = 10379

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
    archive = "Most people call them old objects.  I call them mislabeled histories.",
    relics = "A relic without provenance is merely an expensive mystery.",
    message = "If someone has sent me a note, I prefer they also sent legible handwriting.",
    default = "Archivist Yendrel adjusts his lenses.  'If you are bringing me history, begin at the beginning.'",
}
NPC.ambient_emotes = {
    "Archivist Yendrel turns a delicate artifact over in gloved hands and makes a note.",
    "Archivist Yendrel dusts the spine of a leather folio and reshelves it with great care.",
    "Archivist Yendrel squints at a label, frowns, and rewrites it in smaller script.",
    "Archivist Yendrel lifts an old coin to the light and studies its worn stamping.",
}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 80

return NPC
