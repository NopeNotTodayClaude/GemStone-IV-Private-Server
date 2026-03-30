local NPC = {}

NPC.template_id    = "tv_rogue_drillmaster"
NPC.name           = "Velk"
NPC.article        = ""
NPC.title          = "the drillmaster"
NPC.description    = "Velk has the posture of a duelist, the stare of a quartermaster, and none of the patience usually associated with either."
NPC.home_room_id   = 17822

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
    training = "Stun Maneuvers and Gambits are timing, nerve, and recovery.  Do them late and you're prey.",
    stun = "If you wait for the world to stop ringing before you act, you've already lost.",
    gambit = "A proper gambit changes the room before anyone notices you touched it.",
    drill = "The court is for repetition.  The field is for consequences.",
    default = "Velk points at the chalk lanes.  'Again.  Whatever you thought was good enough, it wasn't.'",
}
NPC.ambient_emotes = {
    "Velk snaps a cane against a hanging target, then nods once as it starts to sway.",
    "Velk redraws a chalk circle with exacting care and steps back to judge the spacing.",
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
    if topic:find("gambit", 1, true) then
        return { guild_action = "rogue_train_skill", skill_name = "Rogue Gambits", skip_quest = true }
    end
    if topic:find("stun", 1, true) then
        return { guild_action = "rogue_train_skill", skill_name = "Stun Maneuvers", skip_quest = true }
    end
    if topic == "lesson" or topic == "teach" or topic == "training" or topic == "train" or topic == "drill" or topic == "fieldcraft" then
        return {
            guild_action = "rogue_train_skill",
            skill_name = "Rogue Gambits",
            quest_key = "rogue_fieldcraft",
            extra_unlocks = { "rogue_skill_stunman_intro" },
        }
    end
    if topic == "shadowpose" or topic == "flourish" or topic == "emote" then
        return {
            response = "Earn it through the fieldcraft trial.  Then the shadow pose is yours whenever you need it.",
        }
    end
    return nil
end

return NPC
