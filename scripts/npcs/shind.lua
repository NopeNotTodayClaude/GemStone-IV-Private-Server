-- NPC: Shind
-- Role: shopkeeper  |  Room: 10434
-- Source: scripts/data/npc_data.py → migrated to Lua
local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "shind"
NPC.name           = "Shind"
NPC.article        = ""
NPC.title          = "the locksmith"
NPC.description    = "A dexterous elf with quick, clever hands and a mischievous glint in his eye.  Lockpicks of every variety hang from pegs on the wall behind him.  A battered wooden board nailed beside the counter lists open picking jobs with their offered fees."
NPC.home_room_id   = 10434

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
NPC.shop_id        = 7

-- ── Dialogue ─────────────────────────────────────────────────────────────────
NPC.greeting       = "glances up from the counter and nods.  'Buying picks, or need a locked box opened?  I run a picking service — type BOXPICK if you want in.'"
NPC.dialogues = {
    lockpicks = "Good picks make the difference.  ORDER to see what I carry.",
    picks = "I carry copper, steel, mithril, and vultite picks.  Each has its advantages.",
    locks = "A good pick is only as good as the hand that holds it, remember that.",
    training = "Picking locks is about feel as much as skill.  Practice on easy ones first.",
    guild = "Ta'Vaalor rogues start with the shed on Gaeld Var.  Once the guild takes them in properly, they use the chute here instead of the long way around.",
    rogue = "If you mean the guild, they want you proving yourself in that shed before anyone bothers with the inner ledger.",
    shed = "Gaeld Var.  The shed.  Get inside, LOOK TOOL, and mind the panel before you worry about the inner door.",
    buy = "ORDER to browse my selection, then BUY.",
    sell = "I'll buy quality picks back.  Gently used is fine, snapped in half is not.",
    repair = "Broken pick?  Hold it in your hand and type REPAIR <pick>.  I'll restore it for a fee.",
    broken = "Happens to everyone.  Hold the broken pick and use REPAIR <pick>.  Cheaper than buying new.",
    queue = "The picking queue is how it works: you drop off a locked box with a fee, a rogue picks it up, cracks it, and brings it back.  I take ten percent.  Type BOXPICK to see open jobs or submit your own.",
    service = "Easy: drop off your locked box with a bounty fee, a rogue picks it up and cracks it.  I take ten percent off the top.  Type BOXPICK to see it all.",
    submit = "Hold your locked box and type: SUBMIT <box> <fee>.  I take the box and post the job.  Your silver is held until the job's done.",
    claim = "Rogues: type BOXPICK to see waiting jobs.  Then TAKE <job number> to claim one.  Pick the lock, then DONE <job number> here to collect your pay.",
    done = "Bring the opened box back here and type DONE <job number>.  I hand it to the owner and pay your cut minus my ten percent.",
    cancel = "Change your mind?  CANCEL <job number> while the job is still waiting.  You get your box and silver back immediately.",
    forfeit = "Can't crack it?  FORFEIT <job number> and hand the box back.  The owner gets their full fee back.  You walk away empty-handed.",
    fee = "Post a fee worth a rogue's time.  Nobody's cracking a coffer for pocket change.",
    myjobs = "MYJOBS lists everything you've submitted and whether it's been picked yet.",
    default = "Shind grins.  'Buying picks, or need something opened?'",
}

-- ── Ambient emotes ───────────────────────────────────────────────────────────
NPC.ambient_emotes = {
    "Shind picks up a lock from under the counter and works it open absently with a single pick.",
    "Shind holds a new set of picks up to the light, checking the temper.",
    "Shind rapidly opens and closes a padlock over and over, barely looking at it.",
    "Shind polishes a steel pick on his sleeve until it gleams.",
    "Shind spins a lockpick between his fingers like a coin, clearly out of habit.",
    "Shind scans the job board and makes a notation with a grease pencil.",
    "Shind checks a locked coffer behind the counter, shakes his head slightly, and sets it back down.",
    "Shind tallies something in a small ledger, lips moving silently.",
}
NPC.ambient_chance  = 0.04
NPC.emote_cooldown  = 30

return NPC
