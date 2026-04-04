local SpellTargeting = {}

SpellTargeting.defaults = {
    bolt = "current_target_optional",
    warding = "current_target_optional",
    maneuver = "current_target_optional",
    buff = "room_player_or_self",
    healing = "room_player_or_self",
    utility = "none",
    summon = "none",
}

SpellTargeting.by_spell = {
    [108] = "room_player_or_self",   -- Stun Relief
    [113] = "room_player_or_self",   -- Undisease
    [114] = "room_player_or_self",   -- Unpoison
    [116] = "room_player_only",      -- Locate Person
    [119] = "current_target_optional", -- Spirit Dispel
    [130] = "room_player_only",      -- Spirit Guide

    [304] = "room_player_or_self",   -- Bless
    [305] = "room_player_only",      -- Preservation
    [315] = "room_player_or_self",   -- Remove Curse
    [318] = "room_player_only",      -- Raise Dead

    [706] = "room_player_or_self",   -- Phoen's Strength
    [712] = "room_player_or_self",   -- Cloak of Shadows
    [715] = "current_target_optional", -- Curse
    [719] = "room_player_or_self",   -- Darkness

    [903] = "room_player_or_self",   -- Minor Elemental Wave? keep player-usable buffs explicit where needed
    [905] = "room_player_or_self",
    [911] = "room_player_or_self",
    [913] = "room_player_or_self",
    [919] = "room_player_or_self",
    [925] = "room_player_or_self",

    [1101] = "room_player_or_self",  -- Heal/Harm defaults to self/friendly on hotbar
    [1102] = "room_player_or_self",
    [1103] = "room_player_or_self",
    [1104] = "room_player_or_self",
    [1105] = "room_player_or_self",
    [1107] = "room_player_or_self",
    [1111] = "room_player_or_self",
    [1112] = "room_player_or_self",
    [1113] = "room_player_or_self",
    [1114] = "room_player_or_self",
    [1116] = "room_player_or_self",
    [1118] = "self_only",            -- Herb Production
    [1125] = "room_player_or_self",
    [1135] = "room_player_or_self",
    [1140] = "room_player_or_self",
    [1150] = "room_player_or_self",

    [1601] = "room_player_only",     -- Familiar Gate style utility
    [1604] = "room_player_or_self",
    [1605] = "room_player_or_self",
    [1606] = "room_player_or_self",
    [1609] = "room_player_or_self",
}

return SpellTargeting
