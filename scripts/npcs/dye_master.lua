-- NPC: Chromial
-- Role: shopkeeper  |  Room: 13547
-- Dye shop — Ta'Vaalor Dye Wares, Main Room
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "dye_master"
NPC.name           = "Chromial"
NPC.article        = ""
NPC.title          = "the dyer"
NPC.description    = "An elf with permanently stained hands in a dozen colors, wearing an apron that looks like a painter's canvas.  Chromial's sharp eyes size up the color of everything you are wearing the moment you walk in."
NPC.home_room_id   = 13547

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = true
NPC.shop_id        = 248
NPC.can_wander     = false
NPC.can_emote      = true
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "waves a cheerfully multi-colored hand in greeting."
NPC.dialogues = {
    dye        = "I stock vials for every standard color — and a few special ones.  Type ORDER to see what I carry.",
    colors     = "My stock runs from pure white and ivory through every shade to deepest black.  I also carry custom blends: ambrosia, periwinkle, rose, and others you won't find elsewhere.",
    price      = "A standard dye vial runs 250 silver.  Specialty colors cost a little more.",
    how        = "Buy the vial, then type DYE <item> <color>.  Works on anything you wear — armor included.  Type DYE HAIR <color> for your hair.  Use DYE <item> REMOVE to strip the color.",
    default    = "Chromial looks up, leaving a blue thumbprint on a doorframe.  'Color consultation?  Type ORDER.'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Chromial stirs a vat of deep crimson dye, steam rising from the surface.",
    "Chromial holds a swatch of freshly dyed cloth up to the light, examining the color critically.",
    "Chromial carefully measures powdered pigment on a small scale, muttering about ratios.",
    "Chromial shakes a vial of liquid dye to check its consistency, then nods in satisfaction.",
    "Chromial dips a finger in a pot of midnight blue dye and draws a small arc in the air.",
    "Chromial compares two swatches of fabric, squinting between them with one eye closed.",
}
NPC.ambient_chance  = 0.03
NPC.emote_cooldown  = 45

return NPC
