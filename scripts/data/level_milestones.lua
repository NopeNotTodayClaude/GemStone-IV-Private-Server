---------------------------------------------------
-- data/level_milestones.lua
-- GS4 progression reminders shown on level-up.
-- These are reminders sourced from GS4 behavior/wiki and may
-- mention systems that are not yet fully implemented server-side.
---------------------------------------------------

local LevelMilestones = {}

LevelMilestones.general = {
    [10] = {
        {
            kind = "weapon_techniques",
            title = "Weapon Techniques",
            text = "Weapon techniques become worth reviewing around this point.  Your trained weapon skills may now qualify you for new maneuvers.",
            source = "GSWiki Weapon Techniques",
            command_hint = "Use WEAPON LIST and WEAPON INFO <technique> to review them.",
        },
    },
    [15] = {
        {
            kind = "profession_guild",
            title = "Profession Guild",
            text = "Profession guild invitations begin around level 15 in GS4.  Joining your guild opens profession-guild training, dues, and rank progression.",
            source = "GSWiki Guild",
        },
        {
            kind = "guild_wall",
            title = "Guild Wall",
            text = "Guild training opens at 39 total guild ranks at level 15.",
            source = "GSWiki Guild",
        },
    },
    [20] = {
        {
            kind = "guild_wall",
            title = "Guild Wall",
            text = "The guild wall rises to 64 total guild ranks at level 20.",
            source = "GSWiki Guild",
        },
    },
    [33] = {
        {
            kind = "guildmaster_threshold",
            title = "Guildmaster Eligibility",
            text = "Guildmaster eligibility begins at 125 total guild ranks and one mastered guild skill, aligning with level 33 experience landmarks.",
            source = "GSWiki Guild",
        },
    },
    [43] = {
        {
            kind = "guild_completion",
            title = "Guild Completion Landmark",
            text = "Empaths, clerics, and wizards can complete their guild work by 186 total ranks, which aligns with level 43.",
            source = "GSWiki Guild",
        },
    },
    [52] = {
        {
            kind = "guild_completion",
            title = "Guild Completion Landmark",
            text = "Sorcerers can complete their guild work by 248 total ranks, which aligns with level 52.",
            source = "GSWiki Guild",
        },
    },
    [61] = {
        {
            kind = "guild_wall",
            title = "Guild Wall",
            text = "The guild wall rises to 310 total guild ranks at level 61.",
            source = "GSWiki Guild",
        },
    },
    [69] = {
        {
            kind = "guild_wall_cap",
            title = "Guild Wall Cap",
            text = "The profession guild wall tops out at 372 total ranks at level 69.",
            source = "GSWiki Guild",
        },
    },
}

LevelMilestones.profession = {
    Rogue = {
        [15] = {
            {
                kind = "rogue_guild",
                title = "Rogue Guild",
                text = "Rogues are contacted by the Rogue Guild shortly after level 15.  The invitation includes the hidden-entry instructions and password sequence.",
                source = "GSWiki Guild / Rogue Guild",
            },
        },
    },
    Warrior = {
        [15] = {
            {
                kind = "warrior_guild",
                title = "Warrior Guild",
                text = "Warriors can join the Warrior Guild at this point once invited, opening warrior guild training and rank progression.",
                source = "GSWiki Guild / Warrior Guild",
            },
        },
    },
    Wizard = {
        [15] = {
            {
                kind = "wizard_guild",
                title = "Wizard Guild",
                text = "Wizards can join the Wizard Guild at this point once invited, opening wizard guild skill training.",
                source = "GSWiki Guild / Wizard Guild",
            },
        },
    },
    Cleric = {
        [15] = {
            {
                kind = "cleric_guild",
                title = "Cleric Guild",
                text = "Clerics can join the Cleric Guild at this point once invited, opening cleric guild skill training.",
                source = "GSWiki Guild / Cleric Guild",
            },
        },
    },
    Empath = {
        [15] = {
            {
                kind = "empath_guild",
                title = "Empath Guild",
                text = "Empaths receive an Empath Guild invitation at this point and can begin guild training once they join.",
                source = "GSWiki Guild / Empath Guild",
            },
        },
    },
    Sorcerer = {
        [15] = {
            {
                kind = "sorcerer_guild",
                title = "Sorcerer Guild",
                text = "Sorcerers can join the Sorcerer Guild at this point once invited, opening sorcerous guild training.",
                source = "GSWiki Guild / Sorcerer Guild",
            },
        },
    },
    Ranger = {
        [15] = {
            {
                kind = "ranger_guild",
                title = "Ranger Guild",
                text = "Rangers may join the Ranger Guild at this point.  The guild is social and utility-focused rather than a skill-training guild.",
                source = "GSWiki Ranger Guild",
            },
        },
    },
    Bard = {
        [15] = {
            {
                kind = "bard_guild",
                title = "Bard Guild",
                text = "Bards may join the Bard Guild at this point.  It is primarily social and theatrical rather than a skill-training guild.",
                source = "GSWiki Bard Guild",
            },
        },
    },
}

return LevelMilestones
