local NPC = {}

NPC.template_id    = "tv_rogue_training_admin"
NPC.name           = "the training administrator"
NPC.article        = ""
NPC.title          = ""
NPC.description    = "A cool-eyed elf seated behind a salmon-colored desk, quietly keeping the guild's training ledgers and schedules in order."
NPC.home_room_id   = 17836

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
    training = "The guild keeps separate records for every track.  Use GLD SKILLS when you need the ledger, GLD TASK when you want new work, and GLD SWAP if a voucher is worth spending.",
    tasks = "The trainers handle the dirt and bruises.  I handle the paperwork that proves you survived them.",
    vouchers = "Vouchers let you trade an active assignment.  Check them with GLD VOUCHERS and spend them with GLD SWAP.",
    checkin = "If your dues are current, GLD CHECKIN keeps the guild records from going stale.",
    records = "Promotion records, task ledgers, voucher counts, and check-ins all cross this desk eventually.",
    default = "The training administrator glances up from a sheaf of notes.  'If you are here for guild records, use GLD.  If you are here to complain about the trainers, spare me.'",
}
NPC.ambient_emotes = {
    "The training administrator straightens a stack of guild ledgers and marks a notation beside one name.",
    "The training administrator reviews a slate of task assignments and quietly reshuffles two of them.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.guild_id       = "rogue"

local function norm(text)
    return tostring(text or ""):lower():gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
end

function NPC:on_player_talk(player, keyword)
    local topic = norm(keyword)
    if topic == "" then
        return nil
    end
    if topic == "status" or topic == "training" or topic == "skills" or topic == "task" or topic == "tasks" or topic == "records" or topic == "ledger" or topic == "vouchers" or topic == "checkin" or topic == "quest" or topic == "quests" then
        return { guild_action = "rogue_training_admin_status" }
    end
    if topic == "rank" or topic == "promotion" or topic == "promote" then
        return { guild_action = "rogue_rank_status" }
    end
    return nil
end

return NPC
