-------------------------------------------------------------------
-- pets.lua
-- Canonical pet/companion system data.
-- All species, shop data, quest flow text, treat progression, and
-- pet scaling live here so the runtime stays loader-driven.
-------------------------------------------------------------------

local PetData = {}

PetData.system = {
    shop_name                = "Moonwhisker Menagerie",
    shop_entry_exit_key      = "go_menagerie",
    shop_entry_display       = "menagerie",
    shop_web_path            = "/pets",
    sprite_name              = "Twillip",
    sprite_nag_room_interval = 5,
    sprite_nag_seconds       = 600,
    feed_cooldown_seconds    = 7200,
    max_pet_level            = 50,
    naming = {
        min_length = 3,
        max_length = 18,
        allow_pattern = "^[A-Za-z][A-Za-z' %-]+$",
    },
    city_shops = {
        ta_illistim = {
            city_name        = "Ta'Illistim",
            outside_room_id  = 166,
            pet_room_id      = 36478,
            outside_title    = "Ta'Illistim, Kaerinar Wey",
        },
        ta_vaalor = {
            city_name        = "Ta'Vaalor",
            outside_room_id  = 3513,
            pet_room_id      = 36479,
            outside_title    = "Ta'Vaalor, Aethenireas Wey",
        },
        solhaven = {
            city_name        = "Solhaven",
            outside_room_id  = 1446,
            pet_room_id      = 36480,
            outside_title    = "Solhaven, Latirus Lane",
        },
        rivers_rest = {
            city_name        = "River's Rest",
            outside_room_id  = 10857,
            pet_room_id      = 36481,
            outside_title    = "River's Rest, Small Clearing",
        },
        cysaegir = {
            city_name        = "Cysaegir",
            outside_room_id  = 4649,
            pet_room_id      = 36482,
            outside_title    = "Cysaegir, Treetop Market",
        },
    },
}

PetData.shopkeeper = {
    name = "Virelle",
    full_name = "Virelle the companioner",
    race = "human",
    title = "Moonwhisker keeper",
    description = "Virelle wears layered violet silks dusted with silver thread, and she carries herself with the effortless calm of someone entirely accustomed to excitable companions and nervous first-time owners.",
    greeting = "Virelle smiles warmly and says, \"Welcome to Moonwhisker Menagerie.  If you are ready, the portrait wall will open the companion catalogue for you.\"",
    idle_emotes = {
        "Virelle dusts one of the glowing portrait frames and quietly checks a training ledger.",
        "Virelle straightens a row of treat tins and smiles to herself.",
        "Virelle murmurs something encouraging to a drifting portrait image before smoothing her sleeves.",
        "Virelle taps a silver stylus against the counter and studies the companion board.",
    },
    look_lines = {
        "She seems equal parts shopkeeper, tutor, and guardian of every tiny creature under her care.",
        "Her steady attention suggests that very little escapes her notice once a companion is involved.",
    },
}

PetData.quest = {
    intro_lines = {
        "A tiny prismatic sprite swoops down in front of you in a shower of glittering motes.",
        "\"Oh!  There you are,\" chirps Twillip.  \"You are finally old enough for a proper companion.\"",
        "\"If you ACCEPT, I will show you how to claim your first pet at Moonwhisker Menagerie.  And yes, I will keep following you until you do.\"",
    },
    accept_lines = {
        "Twillip spins in delight.  \"Knew you had sense in you!  Good.  Now listen carefully.\"",
        "\"Go to the herbalist lane in town.  You will notice a new path to the menagerie now that I have unlocked it for you.\"",
        "\"Your very first companion is free, but you must still visit the catalogue yourself and choose one properly.\"",
    },
    reminder_lines = {
        "\"ACCEPT already.  I have an entire menagerie waiting on you.\"",
        "\"I am absolutely not going away until you ACCEPT, by the way.\"",
        "\"You are level five now.  That means companion time.  Type ACCEPT.\"",
        "\"Still no ACCEPT?  That seems like a questionable life choice.\"",
        "\"Moonwhisker Menagerie is ready for you the moment you ACCEPT.\"",
    },
    accepted_nag_lines = {
        "\"Moonwhisker Menagerie is open to you now.  Go claim your free companion.\"",
        "\"The menagerie path is waiting near the herbalist.  Your first pet will not choose itself.\"",
        "\"You accepted.  Excellent.  Now go finish the job and claim your first companion.\"",
        "\"Yes, yes, I am still here.  Go to the menagerie and pick your pet already.\"",
    },
    shop_arrival_lines = {
        "\"Good, you made it.  Now use PET SHOP and the portrait wall will open the companion catalogue.\"",
        "\"This is the place.  PET SHOP opens the catalogue, and your first Floofer will be listed as FREE.\"",
        "\"Do not just stand there looking enchanted.  Type PET SHOP, name your Floofer, and claim it properly.\"",
        "\"The portrait wall is ready.  PET SHOP first, then pick and name your companion.\"",
    },
    shop_reminder_lines = {
        "\"PET SHOP.  Truly, I cannot make this simpler for you.\"",
        "\"The wall will not open itself.  PET SHOP.\"",
        "\"Your free Floofer is in the catalogue, not in my pocket.  PET SHOP.\"",
        "\"Use PET SHOP, choose your Floofer, and name it.  You are almost done.\"",
    },
    completion_lines = {
        "\"There you are!  Your first companion is bound to you now.  About time.\"",
        "\"Use PET STATUS to check on it, PET CALL to bring it close, and PET DISMISS if you want it to drift out of view for a while.\"",
        "\"Treats help companions grow.  Training items are bought at the menagerie and fed in the field, but only every two hours per pet.\"",
        "\"Take care of your new friend.  I expect great things from the two of you.\"",
    },
}

PetData.treats = {
    { key = "shimmer_crumb",      short_name = "shimmer crumb",      item_short_name = "shimmer crumb",      label = "Shimmer Crumb",      xp = 250,  price = 150,   tier = 1 },
    { key = "moonmilk_biscuit",   short_name = "moonmilk biscuit",   item_short_name = "moonmilk biscuit",   label = "Moonmilk Biscuit",   xp = 450,  price = 500,   tier = 2 },
    { key = "starpetal_chew",     short_name = "starpetal chew",     item_short_name = "starpetal chew",     label = "Starpetal Chew",     xp = 750,  price = 1500,  tier = 3 },
    { key = "velvet_comet_tart",  short_name = "velvet comet tart",  item_short_name = "velvet comet tart",  label = "Velvet Comet Tart",  xp = 1300, price = 4000,  tier = 4 },
    { key = "aurora_heart_treat", short_name = "aurora heart treat", item_short_name = "aurora heart treat", label = "Aurora Heart Treat", xp = 2200, price = 10000, tier = 5 },
}

PetData.pet_slots = { "collar", "trinket", "tool" }

PetData.xp_curve = {}
do
    local cumulative = 0
    for level = 1, 50 do
        PetData.xp_curve[level] = {
            level = level,
            total_xp = cumulative,
            xp_to_next = (level < 50) and (100 + (level * 40)) or 0,
        }
        cumulative = cumulative + ((level < 50) and (100 + (level * 40)) or 0)
    end
end

local guardian_levels = {}
local regen_levels = {}
local recall_levels = {}
local scale_ward_levels = {}
local scale_arc_levels = {}
local scale_tempest_levels = {}
for level = 1, 50 do
    local guardian_cd = math.floor(10800 - ((level - 1) * ((10800 - 3600) / 49)))
    if guardian_cd < 3600 then guardian_cd = 3600 end
    guardian_levels[level] = {
        level = level,
        cooldown_seconds = guardian_cd,
        charges = (level >= 50) and 2 or 1,
    }

    local regen_pct = 0.01 + ((level - 1) * (0.04 / 49))
    regen_levels[level] = {
        level = level,
        threshold_pct = 0.60,
        heal_pct = regen_pct,
        duration_seconds = 60,
        recast_seconds = 180,
        tick_interval = 5,
    }

    recall_levels[level] = {
        level = level,
        unlocked = (level >= 50),
        cooldown_seconds = 3600,
        revive_health_pct = 0.10,
    }

    local ward_recast = math.floor(80 - ((level - 1) * ((80 - 32) / 49)))
    if ward_recast < 32 then ward_recast = 32 end
    scale_ward_levels[level] = {
        level = level,
        threshold_pct = 0.72,
        absorb_amount = 8 + math.floor((level - 1) * (28 / 49)),
        ds_bonus = 4 + math.floor((level - 1) * (10 / 49)),
        duration_seconds = 25,
        recast_seconds = ward_recast,
    }

    local arc_recast = math.floor(42 - ((level - 1) * ((42 - 16) / 49)))
    if arc_recast < 16 then arc_recast = 16 end
    scale_arc_levels[level] = {
        level = level,
        min_damage = 6 + math.floor((level - 1) * (10 / 49)),
        max_damage = 11 + math.floor((level - 1) * (18 / 49)),
        recast_seconds = arc_recast,
    }

    scale_tempest_levels[level] = {
        level = level,
        unlocked = (level >= 50),
        cooldown_seconds = 3600,
        min_damage = 22,
        max_damage = 36,
    }
end

PetData.species = {
    floofer = {
        species_key = "floofer",
        race_name = "Floofer",
        sale_label = "Floofer",
        image_key = "floofer",
        image_path = "/assets/floofer",
        ability_sfx = "FlooferAbility.mp3",
        first_pet_only = false,
        base_price = 25000,
        free_first_pet = true,
        description = "A tiny sparkly pink-and-violet companion with oversized ears, galaxy-dark eyes, and an alarming instinct for dramatic emotional support.",
        appearance_lines = {
            "It looks like a plush little forest creature made of pastel starlight and impossible fluff.",
            "Glittering motes drift through its fur as though the night sky got caught in its coat.",
        },
        personality = {
            random_emotes = {
                "{pet} rises onto its hind paws and gives a hopeful chirrup, as if asking whether admiration might be available right now.",
                "{pet}'s fur catches the light in a brief wash of pink-violet sparkles.",
                "{pet} twitches its ears, does a neat little spin, and stares up expectantly at {owner}.",
                "{pet} pads in a quick circle around {owner}'s boots before settling with obvious self-satisfaction.",
                "{pet} emits a soft trill and leans toward the nearest friendly hand with shameless optimism.",
            },
            state_emotes = {
                treat_ready = {
                    "{pet} bounces in place and lets out a bright little trill, clearly hoping for a training treat.",
                    "{pet} sits up very straight and stares meaningfully at {owner}'s packs, as if reminding them that treat time is available again.",
                },
                low_health = {
                    "{pet} circles anxiously around {owner}, its sparkles flaring brighter with concern.",
                    "{pet}'s ears droop as it watches {owner}'s injuries with obvious worry.",
                },
                recovered = {
                    "{pet} relaxes with a relieved chirp now that {owner} looks steadier on their feet.",
                },
            },
        },
        abilities = {
            guardian_spark = {
                key = "guardian_spark",
                label = "Guardian Spark",
                type = "death_prevention",
                description = "Prevents a killing blow and leaves the owner at 1 HP.",
                scaling = guardian_levels,
            },
            comforting_glow = {
                key = "comforting_glow",
                label = "Comforting Glow",
                type = "pet_spell",
                trigger = "low_health",
                spell_number = 5001,
                status_effect = "floofer_glow",
                spell_name = "Comforting Glow",
                description = "When the owner drops below 60%% health, the Floofer quietly casts a restorative glow that heals over time.",
                cast_lines = {
                    self = "{pet} gathers a soft restorative glow around you.",
                    room = "{pet} gathers a soft restorative glow around {owner}.",
                },
                scaling = regen_levels,
            },
            starlight_recall = {
                key = "starlight_recall",
                label = "Starlight Recall",
                type = "death_recall",
                description = "At level 50, once per hour, the Floofer can pull the owner back from death with a dim starlit revival.",
                scaling = recall_levels,
            },
        },
    },
    scale = {
        species_key = "scale",
        race_name = "Scale",
        sale_label = "Scale",
        image_key = "scale",
        image_path = "/assets/scale",
        ability_sfx = "ScaleAbility.mp3",
        first_pet_only = false,
        free_first_pet = false,
        allow_before_first_pet = true,
        required_professions = {},
        base_price = 30000,
        description = "A sleek, rune-marked drakelet with layered cobalt scales, bright gold eyes, and a habit of crouching between danger and the empath it has chosen to protect.",
        appearance_lines = {
            "Its scales overlap in neat lacquered rows that flash with traced sigils whenever danger draws close.",
            "A dry crackle of static clings to its claws and jawline, suggesting that the little creature takes offense very personally.",
        },
        personality = {
            random_emotes = {
                "{pet} curls its tail around {owner}'s boots and watches the room with bright, suspicious eyes.",
                "{pet}'s scales click softly as it shifts, then it lifts its muzzle to scent the air for trouble.",
                "{pet} lets out a low electric chirr and settles into a protective crouch near {owner}.",
                "{pet} flexes its tiny claws against the floor and a brief blue spark jumps between two scales.",
            },
            state_emotes = {
                low_health = {
                    "{pet} flares its neck spines and wedges itself closer to {owner}, clearly ready to intercept danger.",
                    "{pet}'s scales brighten with warning light as it circles {owner} in a tight protective path.",
                },
                recovered = {
                    "{pet} relaxes a fraction, though it still keeps one watchful eye on every possible threat.",
                },
            },
        },
        abilities = {
            scaleguard_ward = {
                key = "scaleguard_ward",
                label = "Scaleguard Ward",
                type = "pet_spell",
                trigger = "low_health",
                spell_number = 5002,
                description = "When the owner is pressured, the Scale casts a layered ward that absorbs a chunk of incoming damage and stiffens the owner's defenses.",
                cast_lines = {
                    self = "{pet} snaps its jaws and a sapphire ward settles over you.",
                    room = "{pet} snaps its jaws and a sapphire ward settles over {owner}.",
                },
                scaling = scale_ward_levels,
            },
            static_lash = {
                key = "static_lash",
                label = "Static Lash",
                type = "pet_attack_spell",
                trigger = "combat_target",
                spell_number = 5003,
                description = "The Scale periodically lashes the owner's current foe with a quick wizard-like burst of crackling arcane force.",
                cast_lines = {
                    self = "{pet} spits a crackling ribbon of blue force at {target}.",
                    room = "{pet} spits a crackling ribbon of blue force at {target}, shielding {owner}'s flank while it strikes.",
                },
                scaling = scale_arc_levels,
            },
            static_tempest = {
                key = "static_tempest",
                label = "Static Tempest",
                type = "pet_room_attack_spell",
                trigger = "room_hostiles",
                spell_number = 5004,
                description = "At level 50, the Scale can unleash a violent room-wide storm of crackling force that lashes every hostile enemy near its owner.",
                cast_lines = {
                    self = "{pet} arches its back and detonates into a room-wide storm of sapphire force!",
                    room = "{pet} arches its back and detonates into a room-wide storm of sapphire force around {owner}!",
                },
                scaling = scale_tempest_levels,
            },
        },
    },
}

return PetData
