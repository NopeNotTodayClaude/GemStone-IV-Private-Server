local NPC = {}

NPC.template_id    = "tv_rogue_master_pyll"
NPC.name           = "Pyll"
NPC.article        = ""
NPC.title          = "the rogue master"
NPC.description    = "Pyll is all quiet angles and old scars, carrying himself with the relaxed watchfulness of someone who learned long ago how to survive tight spaces and bad footing."
NPC.home_room_id   = 18345

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
    training = "The cellar handles the guild's rougher footwork.  If you want the kind of lesson that leaves witnesses uncomfortable, you came to the right alcove.",
    gambit = "A gambit is timing with intent behind it.  Do it late and it is theater.  Do it cleanly and the room changes shape.",
    masters = "The masters are here to watch how you move when there is nowhere comfortable left to stand.",
    footpads = "A footpad survives on position, nerve, and knowing when to disappear before the story settles.",
    default = "Pyll leans against the cellar wall.  'If you need me, ask straight.  I dislike wasting words underground.'",
}
NPC.ambient_emotes = {
    "Pyll studies the cellar alcoves in silence, as if listening for a mistake before it happens.",
    "Pyll raps one knuckle against the sewer grate, then steps back with faint approval.",
}
NPC.ambient_chance = 0.03
NPC.emote_cooldown = 45
NPC.guild_id       = "rogue"

function NPC:on_player_talk(player, keyword)
    local topic = tostring(keyword or ""):lower():gsub("%s+", " "):gsub("^%s+", ""):gsub("%s+$", "")
    if topic == "train gambits" then
        return {
            response = "Fine.  Use the dark alcove if you want room enough to fail in private.",
            move_to_room = 30766,
            move_verb = "ask",
        }
    end
    return nil
end

return NPC
