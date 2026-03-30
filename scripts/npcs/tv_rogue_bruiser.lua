local NPC = {}

NPC.template_id    = "tv_rogue_bruiser"
NPC.name           = "Marn"
NPC.article        = ""
NPC.title          = "the bruiser"
NPC.description    = "Broad-shouldered and broken-nosed, Marn wears the look of a man who has ended more arguments with leverage than with eloquence."
NPC.home_room_id   = 17819

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
    training = "Sweep, Subdue, Cheapshots.  Pretty names for the same lesson: finish the exchange before the fool across from you understands it started.",
    cheapshot = "If it feels unfair, good.  That's the point.",
    subdue = "A clean takedown beats a corpse when the guild needs answers.",
    sweep = "Feet go, then balance goes, then the rest of them follows.",
    default = "Marn folds his arms.  'If you're looking for graceful, try the drill court.  If you're looking to win, stay here.'",
}
NPC.ambient_emotes = {
    "Marn nudges the practice dummy's footing with one boot and sends it flat with a contemptuous twist.",
    "Marn drags a crate aside with one hand, clearing space for another ugly lesson.",
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
    if topic:find("cheapshot", 1, true) then
        return { guild_action = "rogue_train_skill", skill_name = "Cheapshots", skip_quest = true }
    end
    if topic:find("subdue", 1, true) then
        return { guild_action = "rogue_train_skill", skill_name = "Subdue", skip_quest = true }
    end
    if topic:find("sweep", 1, true) then
        return { guild_action = "rogue_train_skill", skill_name = "Sweep", skip_quest = true }
    end
    if topic == "lesson" or topic == "teach" or topic == "training" or topic == "train" or topic == "dirty fighting" or topic == "trial" then
        return {
            guild_action = "rogue_train_skill",
            skill_name = "Cheapshots",
            quest_key = "rogue_dirty_fighting",
            extra_unlocks = { "rogue_skill_sweep_intro", "rogue_skill_subdue_intro" },
        }
    end
    if topic == "coinroll" or topic == "flourish" or topic == "emote" then
        return {
            response = "Earn it.  Finish my dirty fighting trial and the coin trick sticks with you for good.",
        }
    end
    return nil
end

return NPC
