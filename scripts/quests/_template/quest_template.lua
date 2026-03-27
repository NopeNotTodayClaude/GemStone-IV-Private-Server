---------------------------------------------------
-- Quest Template
---------------------------------------------------

local Quest = {}

Quest.id          = 0
Quest.name        = "Template Quest"
Quest.description = "A quest description shown to the player."
Quest.level_req   = 1
Quest.repeatable  = false
Quest.quest_type  = "general"   -- "general" or "guild"

-- Optional start / turn-in metadata used by the shared quest loader.
Quest.start_npc_template_id  = nil   -- example: "tv_sassion"
Quest.turnin_npc_template_id = nil   -- defaults to start NPC when omitted
Quest.start_room_id          = nil   -- internal room id
Quest.start_lich_room_id     = nil   -- preferred room identity when relevant
Quest.prereq_quests          = {}    -- list of quest key_names
Quest.start_topics           = {"quest", "work", "assignment"}
Quest.turnin_topics          = {"quest", "work", "progress", "hint"}

-- Quest stages (sequential)
Quest.stages = {
    [1] = {
        objective  = "Speak with the townguard.",
        hint       = "The guard patrols near the town gate.",
        on_complete = function(player)
            player:message("The guard nods solemnly.")
        end,
    },
    [2] = {
        objective  = "Retrieve the lost pendant from the cave.",
        hint       = "The cave entrance is north of town.",
        item_required = "lost_pendant",
        on_complete = function(player)
            player:message("You found the pendant!")
        end,
    },
}

-- Rewards given on quest completion
Quest.rewards = {
    experience = 500,
    silver     = 100,
    items      = {},  -- item IDs
}

function Quest.onStart(player)
    player:message("Quest started: " .. Quest.name)
end

function Quest.onComplete(player)
    player:message("Quest complete: " .. Quest.name)
end

return Quest
