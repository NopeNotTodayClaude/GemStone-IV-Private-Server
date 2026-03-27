-- NPC: Gorvik Ironmantle
-- Role: townsfolk  |  Room: 3727
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "dwarven_recruiter"
NPC.name           = "Gorvik Ironmantle"
NPC.article        = ""
NPC.title          = "the Legion recruiter"
NPC.description    = "A stocky dwarf in a crisp Legion auxiliary uniform that is clearly a custom fit.  He carries a leather satchel stuffed with recruitment pamphlets and has the relentless cheer of someone who has been told 'no' so many times it no longer registers."
NPC.home_room_id   = 3727

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = true
NPC.can_emote      = true
NPC.can_chat       = true
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Wander / patrol ──────────────────────────────────────────────────────────
NPC.patrol_rooms   = { 3727, 3483, 3484, 3489, 3500, 3509, 3519, 3542, 3519, 3516, 3519, 3542, 3489, 3727 }
NPC.wander_chance  = 0.4
NPC.move_interval  = 25

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "makes a beeline toward you with a pamphlet already extended."
NPC.dialogues = {
    recruit = "The Vaalor Legion Auxiliary needs capable individuals!  Non-elves welcome in support roles.",
    auxiliary = "Auxiliary service is honorable work.  Logistics, scouting, supply - critical to the Legion's function.",
    dwarf = "I'm proof it can work.  Seven years of service.  Best decision I ever made.",
    join = "Interested in signing up?  The pay is steady, the food is decent, and you're never bored.",
    elves = "They're warming up to the idea.  Slowly.  Very slowly.  But progress is progress.",
    default = "Gorvik thrusts a pamphlet toward you.  'Have you considered a career with the Legion Auxiliary?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Gorvik Ironmantle presses a pamphlet into the hands of a passing elf, who accepts it politely.",
    "Gorvik Ironmantle waves cheerfully at a guardsman who pointedly looks the other way.",
    "Gorvik Ironmantle straightens his auxiliary uniform and resumes his route.",
    "Gorvik Ironmantle pauses to add a note to a small ledger, then returns the pamphlets to his satchel.",
    "Gorvik Ironmantle holds a pamphlet out to a citizen, who walks faster.",
    "Gorvik Ironmantle calls out, 'The Legion Auxiliary is hiring!' to no one in particular.",
}
NPC.ambient_chance  = 0.06
NPC.emote_cooldown  = 20
NPC.chat_interval   = 330
NPC.chat_chance     = 0.18
NPC.chat_lines = {
    "Legion Auxiliary, friends.  Solid work, steady pay, respectable boots.",
    "No, really, take the pamphlet.  It gets lonely in the satchel.",
    "Support work wins campaigns, no matter what the glory-seekers tell you.",
    "I've served seven years and only been nearly trampled twice.  Fine odds.",
    "Scouting, supply, courier work, camp logistics.  Adventure with paperwork.",
    "A city this size always needs people who can carry orders and follow them.",
    "You don't have to be born Vaalor to serve Ta'Vaalor well.",
    "I know that look.  That's the look of someone pretending not to need silver.",
    "The food really is decent.  Better than you'd expect from military rations.",
    "A pamphlet now saves me a longer speech later, though I'm prepared for either.",
    "Honorable work is still honorable if it involves ledgers and crates.",
    "Some of the best soldiers started as somebody's reliable courier.",
    "If you're quick on your feet and not afraid of being useful, come talk to me.",
    "I've been told my enthusiasm is relentless.  I choose to hear that as praise.",
}

return NPC
