-- NPC: Kharst
-- Zone/Town: auto-placed  |  Room: 17806
local NPC = {}

NPC.template_id    = "tv_rogue_guild_contact"
NPC.name           = "Kharst"
NPC.article        = ""
NPC.title          = "the guild factor"
NPC.description    = "Kharst has the unhurried look of a man who is never surprised twice by the same mistake."
NPC.home_room_id   = 17806

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
    rogue = "The shed proves you can find the door.  The inner hall proves you can keep your head.  Everything after that is ledger work and training.",
    guild = "If you need the ledger, use GLD here.  Once the guild knows you, Shind's chute becomes the clean way back in.",
    join = "If you came through the shed and the inner door correctly, GLD JOIN will put your name on my books.",
    invite = "The shed on Gaeld Var is the beginning, not the end.  After that comes the basement door and the sequence.",
    password = "The inner door listens only after you LEAN.  The sequence after that is the one in your invitation.",
    training = "Use GLD SKILLS to review your tracks, GLD TASK for work, GLD PRACTICE for hall drills, GLD COMPLETE when you're done, and GLD QUEST START if you want the guild to test you directly.",
    quest = "Check in first.  Then walk the rooms, meet the trainers, and start asking the guild for proper work.",
    default = "Kharst looks you over once.  'If it's guild business, say it straight.'",
}
NPC.ambient_emotes = {}
NPC.ambient_chance = 0.02
NPC.emote_cooldown = 60
NPC.guild_id       = "rogue"

local function norm(text)
    return tostring(text or ""):lower():gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
end

function NPC:on_player_talk(player, keyword)
    local topic = norm(keyword)
    if topic == "" then
        return nil
    end
    if topic == "status" or topic == "ledger" or topic == "records" or topic == "task" or topic == "tasks" or topic == "skills" or topic == "training" or topic == "checkin" or topic == "quest" or topic == "quests" then
        return { guild_action = "rogue_training_admin_status" }
    end
    if topic == "rank" or topic == "promotion" or topic == "promote" then
        return { guild_action = "rogue_rank_status" }
    end
    return nil
end

return NPC
