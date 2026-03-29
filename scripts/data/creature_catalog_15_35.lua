local Catalog = {}

Catalog.overrides = {
    gnoll_ranger = {
        preferred_stance = "guarded",
        stance_profile = "ranged",
        pursue_chance = 0.45,
        skills = { "tracking", "perception", "ambush" },
    },
    black_leopard = {
        preferred_stance = "offensive",
        stance_profile = "skirmisher",
        pursue_chance = 0.55,
        skills = { "stalking", "ambush" },
    },
    puma = {
        preferred_stance = "offensive",
        stance_profile = "skirmisher",
        pursue_chance = 0.55,
        skills = { "stalking", "ambush" },
    },
    wolfshade = {
        preferred_stance = "guarded",
        stance_profile = "skirmisher",
        pursue_chance = 0.50,
    },
    fire_guardian = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    ghoul_master = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    plains_ogre = {
        preferred_stance = "forward",
        stance_profile = "berserker",
    },
    death_dirge = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    agresh_troll_chieftain = {
        preferred_stance = "forward",
        stance_profile = "berserker",
    },
    arch_wight = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    crested_basilisk = {
        preferred_stance = "guarded",
        stance_profile = "skirmisher",
    },
    shadowy_spectre = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    revenant = {
        preferred_stance = "forward",
        stance_profile = "berserker",
    },
    grutik_shaman = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    cold_guardian = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    moor_witch = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    luminous_spectre = {
        level = 34,
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    troll_wraith = {
        preferred_stance = "guarded",
        stance_profile = "caster",
    },
    bog_troll = {
        preferred_stance = "forward",
        stance_profile = "berserker",
    },
}

Catalog.creatures = {
    -- Level 15
    { template_id = "arctic_puma",         base_template = "puma",                name = "arctic puma",         level = 15, spawn_from = "black_bear",    skin = "a puma hide",             preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "humpbacked_puma",     base_template = "puma",                name = "humpbacked puma",     level = 15, spawn_from = "puma",          skin = "a puma hide",             preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "large_ogre",          base_template = "plains_ogre",         name = "large ogre",          level = 15, spawn_from = "plains_ogre",   skin = "an ogre tooth",           preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "luminous_arachnid",   base_template = "albino_tomb_spider",  name = "luminous arachnid",   level = 15, spawn_from = "dark_shambler", skin = "a luminous arachnid leg", preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "panther",             base_template = "black_leopard",       name = "panther",             level = 15, spawn_from = "black_leopard", skin = "a panther pelt",          preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "ridgeback_boar",      base_template = "great_boar",          name = "ridgeback boar",      level = 15, spawn_from = "plains_ogre",   skin = "a ridgeback boar hide",   preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "tomb_wight",          base_template = "arch_wight",          name = "tomb wight",          level = 15, spawn_from = "dark_shambler", skin = "a wight skin",            preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "wraith",              base_template = "shadowy_spectre",     name = "wraith",              level = 15, spawn_from = "wolfshade",     skin = nil,                       preferred_stance = "guarded",   stance_profile = "caster" },

    -- Level 16
    { template_id = "banded_rattlesnake",  base_template = "crested_basilisk",    name = "banded rattlesnake",  level = 16, spawn_from = "black_leopard", skin = "a rattlesnake skin",      preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "fire_rat",            base_template = "giant_rat_imt",       name = "fire rat",            level = 16, spawn_from = "fire_guardian", skin = "a singed rat tail",       preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "mongrel_troll",       base_template = "hill_troll",          name = "mongrel troll",       level = 16, spawn_from = "hill_troll",    skin = "a troll hide",            preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "mongrel_wolfhound",   base_template = "moor_hound",          name = "mongrel wolfhound",   level = 16, spawn_from = "hill_troll",    skin = "a wolfhound pelt",        preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "phosphorescent_worm", base_template = "carrion_worm",        name = "phosphorescent worm", level = 16, spawn_from = "cave_troll",    skin = "a phosphorescent worm segment", preferred_stance = "advance", stance_profile = "skirmisher" },
    { template_id = "plains_orc_warrior",  base_template = "grey_orc_glatoph",    name = "plains orc warrior",  level = 16, spawn_from = "plains_ogre",   skin = "an orc ear",              preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "red_bear",            base_template = "black_bear",          name = "red bear",            level = 16, spawn_from = "black_bear",    skin = "a red bear skin",         preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "wind_witch",          base_template = "water_witch",         name = "wind witch",          level = 16, spawn_from = "water_witch",   skin = "a wind witch fingernail", preferred_stance = "guarded",   stance_profile = "caster" },

    -- Level 17
    { template_id = "black_panther",       base_template = "black_leopard",       name = "black panther",       level = 17, spawn_from = "black_leopard", skin = "a black panther pelt",    preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "forest_ogre",         base_template = "plains_ogre",         name = "forest ogre",         level = 17, spawn_from = "decaying_woodsman", skin = "an ogre tooth",        preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "giant_veaba",         base_template = "giant_fog_beetle",    name = "giant veaba",         level = 17, spawn_from = "sand_beetle",   skin = "a veaba shell plate",     preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "gnoll_guard",         base_template = "cave_gnoll",          name = "gnoll guard",         level = 17, spawn_from = "gnoll_ranger",  skin = "a gnoll hide",            preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "krolvin_mercenary",   base_template = "krolvin_warrior",     name = "krolvin mercenary",   level = 17, spawn_from = "krolvin_warrior", skin = "a krolvin scalp",       preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "mountain_goat",       base_template = "great_stag",          name = "mountain goat",       level = 17, spawn_from = "neartofar_troll", skin = "a mountain goat hide",  preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "mountain_troll",      base_template = "forest_troll",        name = "mountain troll",      level = 17, spawn_from = "neartofar_troll", skin = "a troll hide",          preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "plains_orc_scout",    base_template = "raider_orc_marauder", name = "plains orc scout",    level = 17, spawn_from = "plains_ogre",   skin = "an orc ear",              preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "spiked_cavern_urchin", base_template = "crystal_crab",       name = "spiked cavern urchin", level = 17, spawn_from = "sand_beetle",  skin = "a cavern urchin spine",   preferred_stance = "guarded",   stance_profile = "skirmisher" },

    -- Level 18
    { template_id = "bighorn_sheep",       base_template = "great_stag",          name = "bighorn sheep",       level = 18, spawn_from = "neartofar_troll", skin = "a bighorn sheep pelt",  preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "cave_lizard",         base_template = "crested_basilisk",    name = "cave lizard",         level = 18, spawn_from = "giant_albino_scorpion", skin = "a cave lizard skin", preferred_stance = "guarded", stance_profile = "skirmisher" },
    { template_id = "elder_ghoul_master",  base_template = "ghoul_master",        name = "elder ghoul master",  level = 18, spawn_from = "ghoul_master",  skin = "a ghoul master claw",     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "fire_cat",            base_template = "black_leopard",       name = "fire cat",            level = 18, spawn_from = "fire_guardian", skin = "a fire cat whisker",      preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "greenwing_hornet",    base_template = "giant_fog_beetle",    name = "greenwing hornet",    level = 18, spawn_from = "plains_lion",   skin = "a greenwing hornet wing", preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "mountain_lion",       base_template = "plains_lion",         name = "mountain lion",       level = 18, spawn_from = "neartofar_troll", skin = "a mountain lion pelt",   preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "plains_orc_shaman",   base_template = "grutik_shaman",       name = "plains orc shaman",   level = 18, spawn_from = "plains_ogre",   family = "orc", skin = "an orc fetish", preferred_stance = "guarded", stance_profile = "caster" },
    { template_id = "rotting_krolvin_pirate", base_template = "krolvin_warrior",  name = "rotting krolvin pirate", level = 18, spawn_from = "krolvin_warrior", classification = "corporeal_undead", skin = "a krolvin skull", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "shelfae_warlord",     base_template = "shelfae_guard",       name = "shelfae warlord",     level = 18, spawn_from = "shelfae_guard", skin = "a shelfae crest",         preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "ghostly_warrior",     base_template = "luminous_spectre",    name = "ghostly warrior",     level = 18, spawn_from = "luminous_spectre", skin = nil,                    preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "thunder_troll",       base_template = "war_troll",           name = "thunder troll",       level = 18, spawn_from = "war_troll",    skin = "a troll hide",           preferred_stance = "forward",   stance_profile = "berserker", abilities = { "thunder_roar", "shock_burst" } },

    -- Level 20
    { template_id = "gnoll_priest",        base_template = "grutik_shaman",       name = "gnoll priest",        level = 20, spawn_from = "gnoll_ranger",  family = "gnoll", skin = "a gnoll fetish", preferred_stance = "guarded", stance_profile = "caster" },
    { template_id = "large_ring_tailed_lemur", base_template = "monkey",          name = "large ring-tailed lemur", level = 20, spawn_from = "monkey",     skin = "a lemur pelt",            preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "major_spider",        base_template = "greater_spider",      name = "major spider",        level = 20, spawn_from = "greater_spider", skin = "a spider carapace",      preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "massive_grahnk",      base_template = "crocodile",           name = "massive grahnk",      level = 20, spawn_from = "crocodile",   skin = "a grahnk hide",           preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "steel_golem",         base_template = "night_golem",         name = "steel golem",         level = 20, spawn_from = "night_golem", skin = "a steel golem plate",     preferred_stance = "guarded",   stance_profile = "berserker" },
    { template_id = "striped_warcat",      base_template = "plains_lion",         name = "striped warcat",      level = 20, spawn_from = "plains_lion",  skin = "a warcat pelt",           preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "wood_wight",          base_template = "arch_wight",          name = "wood wight",          level = 20, spawn_from = "warped_tree_spirit", skin = "a wood wight splinter", preferred_stance = "guarded", stance_profile = "caster" },

    -- Level 21
    { template_id = "ancient_ghoul_master", base_template = "ghoul_master",       name = "ancient ghoul master", level = 21, spawn_from = "ghoul_master", skin = "a ghoul master claw",    preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "arachne_servant",     base_template = "brown_spinner",       name = "arachne servant",     level = 21, spawn_from = "brown_spinner", skin = "an arachne silk gland",   preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "cave_bear",           base_template = "great_brown_bear",    name = "cave bear",           level = 21, spawn_from = "cave_troll",   skin = "a cave bear hide",        preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "plains_orc_chieftain", base_template = "agresh_troll_chieftain", name = "plains orc chieftain", level = 21, spawn_from = "plains_ogre", family = "orc", skin = "an orc war-trophy", preferred_stance = "forward", stance_profile = "berserker" },

    -- Level 22
    { template_id = "cougar",              base_template = "puma",                name = "cougar",              level = 22, spawn_from = "plains_lion",  skin = "a cougar pelt",           preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "dark_panther",        base_template = "black_leopard",       name = "dark panther",        level = 22, spawn_from = "black_leopard", skin = "a dark panther pelt",    preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "enormous_mosquito",   base_template = "giant_fog_beetle",    name = "enormous mosquito",   level = 22, spawn_from = "bog_troll",    skin = "an enormous mosquito proboscis", preferred_stance = "advance", stance_profile = "skirmisher" },
    { template_id = "warthog",             base_template = "great_boar",          name = "warthog",             level = 22, spawn_from = "plains_ogre",  skin = "a warthog tusk",          preferred_stance = "forward",   stance_profile = "berserker" },

    -- Level 23
    { template_id = "arachne_acolyte",     base_template = "arachne_servant",     name = "arachne acolyte",     level = 23, spawn_from = "brown_spinner", skin = "an arachne silk gland", preferred_stance = "guarded", stance_profile = "caster", spells = { { name = "web_bolt", cs = 118, as = 0 } }, abilities = { "web_immobilize", "venom_sting", "mind_blast" } },
    { template_id = "centaur",             base_template = "ogre_warrior",        name = "centaur",             level = 23, spawn_from = "plains_lion",  skin = "a centaur hoof",          preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "centaur_ranger",      base_template = "gnoll_ranger",        name = "centaur ranger",      level = 23, spawn_from = "plains_lion",  skin = "a centaur arrowhead",     preferred_stance = "guarded",   stance_profile = "ranged" },
    { template_id = "crazed_zombie",       base_template = "skeletal_soldier",    name = "crazed zombie",       level = 23, spawn_from = "skeletal_soldier", classification = "corporeal_undead", skin = "a zombie bone", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "fenghai",             base_template = "wood_sprite",         name = "fenghai",             level = 23, spawn_from = "wood_sprite",  skin = "a fenghai charm",         preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "niirsha",             base_template = "wood_sprite",         name = "niirsha",             level = 23, spawn_from = "wood_sprite",  skin = "a niirsha charm",         preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "nonomino",            base_template = "wood_sprite",         name = "nonomino",            level = 23, spawn_from = "wood_sprite",  skin = "a nonomino charm",        preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "rotting_woodsman",    base_template = "decaying_woodsman",   name = "rotting woodsman",    level = 23, spawn_from = "decaying_woodsman", skin = "a woodsman shroud",     preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "zombie",              base_template = "crazed_zombie",       name = "zombie",              level = 23, spawn_from = "skeletal_soldier", classification = "corporeal_undead", skin = "a zombie bone", preferred_stance = "forward", stance_profile = "berserker" },

    -- Level 24
    { template_id = "arctic_wolverine",    base_template = "mountain_snowcat",    name = "arctic wolverine",    level = 24, spawn_from = "black_bear",   skin = "a wolverine pelt",        preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "burly_reiver",        base_template = "krolvin_warfarer",    name = "burly reiver",        level = 24, spawn_from = "krolvin_warfarer", skin = "a reiver scalp",         preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "jungle_feyling",      base_template = "wood_sprite",         name = "jungle feyling",      level = 24, spawn_from = "jungle_troll", skin = "a feyling focus",         preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "night_hound",         base_template = "moor_hound",          name = "night hound",         level = 24, spawn_from = "ice_hound",    skin = "a hound fang",            preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "roa_ter_wormling",    base_template = "roa_ter_zaerthu",     name = "roa'ter wormling",    level = 24, spawn_from = "roa_ter_zaerthu", skin = "a wormling segment",    preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "reiver",              base_template = "krolvin_warfarer",    name = "reiver",              level = 24, spawn_from = "krolvin_warfarer", skin = "a reiver scalp",         preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "storm_hound",         base_template = "ice_hound",           name = "storm hound",         level = 24, spawn_from = "ice_hound",    skin = "a storm hound fang",      preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "tree_viper",          base_template = "crested_basilisk",    name = "tree viper",          level = 24, spawn_from = "jungle_troll", skin = "a viper skin",            preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "vapor_hound",         base_template = "moor_hound",          name = "vapor hound",         level = 24, spawn_from = "ice_hound",    skin = "a vapor hound fang",      preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "veteran_reiver",      base_template = "krolvin_warfarer",    name = "veteran reiver",      level = 24, spawn_from = "krolvin_warfarer", skin = "a veteran reiver scalp", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "water_hound",         base_template = "moor_hound",          name = "water hound",         level = 24, spawn_from = "ice_hound",    skin = "a water hound fang",      preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "wolverine",           base_template = "mountain_snowcat",    name = "wolverine",           level = 24, spawn_from = "black_bear",   skin = "a wolverine pelt",        preferred_stance = "offensive", stance_profile = "skirmisher" },

    -- Level 25
    { template_id = "carceris",            base_template = "shadowy_spectre",     name = "carceris",            level = 25, spawn_from = "shadowy_spectre", skin = nil,                      preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "gnoll_jarl",          base_template = "agresh_troll_chieftain", name = "gnoll jarl",       level = 25, spawn_from = "gnoll_ranger", family = "gnoll", skin = "a gnoll war-trophy", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "huge_jungle_toad",    base_template = "giant_fog_beetle",     name = "huge jungle toad",    level = 25, spawn_from = "jungle_troll", skin = "a jungle toad gland",     preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "sacristan_spirit",    base_template = "luminous_spectre",     name = "sacristan spirit",    level = 25, spawn_from = "luminous_spectre", skin = nil,                     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "spectral_monk",       base_template = "luminous_spectre",     name = "spectral monk",       level = 25, spawn_from = "luminous_spectre", skin = nil,                     preferred_stance = "guarded",   stance_profile = "caster" },

    -- Level 26
    { template_id = "arachne_priest",      base_template = "arachne_acolyte",      name = "arachne priest",      level = 26, spawn_from = "brown_spinner", skin = "an arachne silk gland", preferred_stance = "guarded", stance_profile = "caster", spells = { { name = "web_bolt", cs = 135, as = 0 }, { name = "curse", cs = 132, as = 0 } }, abilities = { "web_immobilize", "mind_blast", "venom_sting", "spell_shield_219" } },
    { template_id = "arachne_priestess",   base_template = "arachne_acolyte",      name = "arachne priestess",   level = 26, spawn_from = "brown_spinner", skin = "an arachne silk gland", preferred_stance = "guarded", stance_profile = "caster", spells = { { name = "web_bolt", cs = 138, as = 0 }, { name = "curse", cs = 135, as = 0 } }, abilities = { "web_immobilize", "mind_blast", "venom_sting", "glamour" } },
    { template_id = "tree_spirit",         base_template = "warped_tree_spirit",   name = "tree spirit",         level = 26, spawn_from = "warped_tree_spirit", skin = "a heartwood knot",      preferred_stance = "guarded",   stance_profile = "caster" },

    -- Level 27
    { template_id = "cloud_sprite_meddler", base_template = "wood_sprite",         name = "cloud sprite meddler", level = 27, spawn_from = "wood_sprite",  skin = "a sprite focus",          preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "cyclops",             base_template = "ogre_warrior",         name = "cyclops",             level = 27, spawn_from = "ogre_warrior", skin = "a cyclops eye",           preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "frenzied_monk",       base_template = "spectral_monk",        name = "frenzied monk",       level = 27, spawn_from = "luminous_spectre", classification = "living", skin = "a monk's sash", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "lesser_stone_gargoyle", base_template = "night_golem",        name = "lesser stone gargoyle", level = 27, spawn_from = "wall_guardian", skin = "a gargoyle shard",       preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "monastic_lich",       base_template = "shadowy_spectre",      name = "monastic lich",       level = 27, spawn_from = "luminous_spectre", skin = "a lich finger bone",     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "snow_leopard",        base_template = "mountain_snowcat",     name = "snow leopard",        level = 27, spawn_from = "black_bear",  skin = "a snow leopard pelt",     preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "troll_chieftain",     base_template = "agresh_troll_chieftain", name = "troll chieftain",  level = 27, spawn_from = "hill_troll",  skin = "a troll chieftain war-trophy", preferred_stance = "forward", stance_profile = "berserker" },

    -- Level 28
    { template_id = "cooks_assistant",     base_template = "deranged_sentry",      name = "cook's assistant",    level = 28, spawn_from = "deranged_sentry", skin = "a cook's keyring",      preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "darken",              base_template = "deranged_sentry",      name = "darken",              level = 28, spawn_from = "deranged_sentry", skin = "a darkened shard",      preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "dobrem",              base_template = "deranged_sentry",      name = "dobrem",              level = 28, spawn_from = "deranged_sentry", skin = "a dobrem talon",        preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "giant_hawk_owl",      base_template = "blood_eagle",          name = "giant hawk-owl",      level = 28, spawn_from = "blood_eagle",  skin = "a hawk-owl feather",      preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "ki_lin",              base_template = "great_stag",           name = "ki-lin",              level = 28, spawn_from = "wood_sprite",  skin = "a ki-lin lock",           preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "martial_eagle",       base_template = "blood_eagle",          name = "martial eagle",       level = 28, spawn_from = "blood_eagle",  skin = "a martial eagle feather", preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "moaning_spirit",      base_template = "moaning_phantom",      name = "moaning spirit",      level = 28, spawn_from = "moaning_phantom", skin = nil,                     preferred_stance = "guarded",   stance_profile = "caster" },

    -- Level 29
    { template_id = "arctic_manticore",    base_template = "scaly_burgee",         name = "arctic manticore",    level = 29, spawn_from = "ice_troll",    skin = "a manticore tail",        preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "bristly_black_tapir", base_template = "great_boar",           name = "bristly black tapir", level = 29, spawn_from = "jungle_troll", skin = "a tapir hide",            preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "praeda",              base_template = "wood_sprite",          name = "pra'eda",             level = 29, spawn_from = "wood_sprite",  skin = "a pra'eda charm",         preferred_stance = "guarded",   stance_profile = "caster" },

    -- Level 30
    { template_id = "elder_tree_spirit",   base_template = "tree_spirit",          name = "elder tree spirit",   level = 30, spawn_from = "warped_tree_spirit", skin = "an elder heartwood knot", preferred_stance = "guarded", stance_profile = "caster" },
    { template_id = "giant_albino_tomb_spider", base_template = "albino_tomb_spider", name = "giant albino tomb spider", level = 30, spawn_from = "albino_tomb_spider", skin = "a tomb spider leg", preferred_stance = "guarded", stance_profile = "skirmisher" },
    { template_id = "hisskra_warrior",     base_template = "greater_burrow_orc",   name = "hisskra warrior",     level = 30, spawn_from = "greater_burrow_orc", skin = "a hisskra scale",        preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "hooded_figure",       base_template = "deranged_sentry",      name = "hooded figure",       level = 30, spawn_from = "deranged_sentry", skin = "a hooded clasp",          preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "hunter_troll",        base_template = "jungle_troll",         name = "hunter troll",        level = 30, spawn_from = "jungle_troll", skin = "a troll hide",            preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "lesser_wood_sprite",  base_template = "wood_sprite",          name = "lesser wood sprite",  level = 30, spawn_from = "wood_sprite",  skin = "a wood sprite focus",     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "mammoth_arachnid",    base_template = "greater_spider",       name = "mammoth arachnid",    level = 30, spawn_from = "greater_spider", skin = "a mammoth arachnid leg", preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "tegursh_sentry",      base_template = "deranged_sentry",      name = "tegursh sentry",      level = 30, spawn_from = "deranged_sentry", skin = "a tegursh crest",        preferred_stance = "forward",   stance_profile = "skirmisher" },

    -- Level 31
    { template_id = "hulking_forest_ape",  base_template = "monkey",               name = "hulking forest ape",  level = 31, spawn_from = "monkey",       skin = "a forest ape pelt",       preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "skeletal_ice_troll",  base_template = "rock_troll_zombie",    name = "skeletal ice troll",  level = 31, spawn_from = "ice_troll",    skin = "a troll bone",            preferred_stance = "forward",   stance_profile = "berserker" },
    { template_id = "wild_hound",          base_template = "fel_wolf",             name = "wild hound",          level = 31, spawn_from = "moor_hound",   skin = "a wild hound fang",       preferred_stance = "offensive", stance_profile = "skirmisher" },

    -- Level 32
    { template_id = "caribou",             base_template = "great_stag",           name = "caribou",             level = 32, spawn_from = "black_bear",   skin = "a caribou pelt",          preferred_stance = "advance",   stance_profile = "skirmisher" },
    { template_id = "cloud_sprite_bully",  base_template = "cloud_sprite_meddler", name = "cloud sprite bully",  level = 32, spawn_from = "wood_sprite",  skin = "a sprite focus",          preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "ghostly_mara",        base_template = "luminous_spectre",     name = "ghostly mara",        level = 32, spawn_from = "luminous_spectre", skin = nil,                     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "rotting_corpse",      base_template = "crazed_zombie",        name = "rotting corpse",      level = 32, spawn_from = "skeletal_soldier", classification = "corporeal_undead", skin = "a corpse scrap", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "rotting_farmhand",    base_template = "rotting_woodsman",     name = "rotting farmhand",    level = 32, spawn_from = "rotting_woodsman", skin = "a farmhand shroud",      preferred_stance = "forward",   stance_profile = "berserker" },

    -- Level 33
    { template_id = "ghostly_pooka",       base_template = "ghostly_mara",         name = "ghostly pooka",       level = 33, spawn_from = "luminous_spectre", skin = nil,                     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "hisskra_shaman",      base_template = "grutik_shaman",        name = "hisskra shaman",      level = 33, spawn_from = "greater_burrow_orc", family = "hisskra", skin = "a hisskra scale", preferred_stance = "guarded", stance_profile = "caster" },
    { template_id = "lesser_fetid_corpse", base_template = "rotting_corpse",       name = "lesser fetid corpse", level = 33, spawn_from = "skeletal_soldier", classification = "corporeal_undead", skin = "a fetid shroud", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "maw_spore",           base_template = "giant_fog_beetle",     name = "maw spore",           level = 33, spawn_from = "bog_troll",    skin = "a spore cap",             preferred_stance = "guarded",   stance_profile = "caster", abilities = { "gas_cloud", "tremors" } },
    { template_id = "mezic",               base_template = "scaly_burgee",         name = "mezic",               level = 33, spawn_from = "scaly_burgee", skin = "a mezic scale",           preferred_stance = "guarded",   stance_profile = "skirmisher" },
    { template_id = "three_toed_tegu",     base_template = "crocodile",            name = "three-toed tegu",     level = 33, spawn_from = "jungle_troll", skin = "a tegu skin",             preferred_stance = "guarded",   stance_profile = "skirmisher" },

    -- Level 34
    { template_id = "colossus_vulture",    base_template = "blood_eagle",          name = "colossus vulture",    level = 34, spawn_from = "blood_eagle",  skin = "a vulture feather",       preferred_stance = "offensive", stance_profile = "skirmisher" },
    { template_id = "hisskra_chieftain",   base_template = "hisskra_shaman",       name = "hisskra chieftain",   level = 34, spawn_from = "greater_burrow_orc", family = "hisskra", skin = "a hisskra scale", preferred_stance = "forward", stance_profile = "berserker" },
    { template_id = "spectral_warrior",    base_template = "luminous_spectre",     name = "spectral warrior",    level = 34, spawn_from = "skeletal_soldier", skin = nil,                     preferred_stance = "forward",   stance_profile = "skirmisher" },
    { template_id = "tundra_giant",        base_template = "frost_giant",          name = "tundra giant",        level = 34, spawn_from = "black_bear",   skin = "a giant bone",            preferred_stance = "forward",   stance_profile = "berserker" },

    -- Level 35
    { template_id = "barghest",            base_template = "moor_hound",           name = "barghest",            level = 35, spawn_from = "moor_hound",   classification = "non_corporeal_undead", skin = nil, preferred_stance = "offensive", stance_profile = "caster" },
    { template_id = "shimmering_fungus",   base_template = "giant_fog_beetle",     name = "shimmering fungus",   level = 35, spawn_from = "bog_troll",    skin = "a shimmering fungus cap", preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "spectral_shade",      base_template = "luminous_spectre",     name = "spectral shade",      level = 35, spawn_from = "luminous_spectre", skin = nil,                     preferred_stance = "guarded",   stance_profile = "caster" },
    { template_id = "spectral_woodsman",   base_template = "rotting_woodsman",     name = "spectral woodsman",   level = 35, spawn_from = "rotting_woodsman", classification = "corporeal_undead", skin = nil, preferred_stance = "guarded", stance_profile = "caster" },
    { template_id = "water_wyrd",          base_template = "water_witch",          name = "water wyrd",          level = 35, spawn_from = "water_witch",  classification = "non_corporeal_undead", skin = nil, preferred_stance = "guarded", stance_profile = "caster" },
}

return Catalog
