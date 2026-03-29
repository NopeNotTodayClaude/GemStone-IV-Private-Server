-------------------------------------------------------------------
-- traps.lua
-- Canonical trap registry for treasure containers.
--
-- Trap behavior is authored here and interpreted by the Python trap
-- runtime.  Detect/disarm messaging, tool requirements, trap weights,
-- and high-level effect metadata all live here so the runtime does
-- not fall back to a hardcoded generic damage table.
-------------------------------------------------------------------

local TrapData = {}

TrapData.spawn = {
    min_level = 3,
    base_chance_per_level = 0.03,
    max_chance = 0.60,
}

TrapData.weight_tiers = {
    { min = 1,  max = 5,  weights = {
        needle = 30, spring = 25, jaws = 15, scarab = 10,
        sphere = 10, scales = 5, gas = 5,
    }},
    { min = 6,  max = 10, weights = {
        needle = 15, spring = 15, jaws = 15, scarab = 12,
        sphere = 10, scales = 8, gas = 8, spores = 5,
        rods = 5, acid = 4, plate = 3,
    }},
    { min = 11, max = 15, weights = {
        needle = 8, spring = 8, jaws = 10, scarab = 10,
        sphere = 8, scales = 8, gas = 8, spores = 6,
        rods = 6, acid = 6, plate = 5, dark_crystal = 5,
        sulphur = 4, fire_vial = 4, glyph = 2, boomer = 2,
    }},
    { min = 16, max = 20, weights = {
        jaws = 6, scarab = 8, gas = 6, spores = 6,
        rods = 6, acid = 8, plate = 8, dark_crystal = 8,
        sulphur = 8, fire_vial = 8, glyph = 6, boomer = 6,
        needle = 4, spring = 4, sphere = 4, scales = 2,
        temporal_rift = 2,
    }},
    { min = 21, max = 99, weights = {
        acid = 8, plate = 8, dark_crystal = 10, sulphur = 10,
        fire_vial = 10, glyph = 10, boomer = 10, temporal_rift = 8,
        scarab = 6, gas = 6, spores = 6, rods = 6,
        jaws = 2, needle = 2, spring = 0, sphere = 2, scales = 0,
    }},
}

TrapData.definitions = {
    scarab = {
        key = "scarab",
        examine = "You notice a tiny scarab mechanism wedged into the lock housing, waiting to spring free when the tumblers shift.",
        disarm_msg = "You gum the scarab mechanism into stillness with putty and pry the little menace free before it can leap.",
        fail_msg = "A trap scarab bursts from the lock and fastens itself to you in a frenzy of tiny stabbing bites!",
        room_msg = "{name} recoils as a trap scarab erupts from the container!",
        damage_type = "puncture",
        base_damage = { min = 6, max = 14 },
        diff_bonus = 15,
        tools = { "putty" },
        tool_action = {
            "You press putty over the tiny scarab mechanism, locking its legs and wing-cases in place.",
        },
        special = {
            kind = "scarab",
            default_duration = 30,
            tick_interval = 5,
            variants = {
                {
                    key = "blood_red",
                    label = "blood-red scarab",
                    attach_line = "A blood-red scarab latches onto you, drilling in with frantic little bites!",
                    room_attach = "A blood-red scarab fastens itself to {name} and begins drinking greedily.",
                    tick_message = "The blood-red scarab drinks deeply, leaving you slick with fresh blood!",
                    damage_min = 4,
                    damage_max = 10,
                    wound_location = "right_hand",
                    wound_rank = 3,
                    applies_bleed = true,
                    jump_on_death = true,
                },
                {
                    key = "scarlet_gold",
                    label = "scarlet-gold scarab",
                    attach_line = "A scarlet-gold scarab darts across your skin with a burning, feverish bite!",
                    room_attach = "A scarlet-gold scarab skitters over {name}'s hand and bites viciously.",
                    tick_message = "The scarlet-gold scarab bites again, leaving a poisonous burn in its wake!",
                    damage_min = 3,
                    damage_max = 8,
                    wound_location = "right_hand",
                    wound_rank = 2,
                    statuses = {
                        { id = "poisoned", duration = 60, stacks = 1, magnitude = 1 },
                    },
                },
                {
                    key = "spiked_onyx",
                    label = "spiked onyx scarab",
                    attach_line = "A spiked onyx scarab clamps down and sends an icy surge through your arm!",
                    room_attach = "A spiked onyx scarab anchors itself to {name}, its black shell pulsing faintly.",
                    tick_message = "The spiked onyx scarab drives its spines in again, leaving your limbs numb and shaky.",
                    damage_min = 5,
                    damage_max = 12,
                    wound_location = "right_arm",
                    wound_rank = 2,
                    statuses = {
                        { id = "staggered", duration = 15, stacks = 1, magnitude = 1 },
                    },
                    jump_on_death = true,
                },
            },
        },
    },

    needle = {
        key = "needle",
        examine = "You notice a tiny hole beside the lock plate with a poison needle recessed inside.",
        disarm_msg = "You block the tiny hole with putty and safely pin the spring-loaded needle in place.",
        fail_msg = "A poison needle shoots out and pricks your finger!",
        room_msg = "{name} jerks a hand back from a suddenly snapping needle trap!",
        damage_type = "puncture",
        base_damage = { min = 4, max = 12 },
        diff_bonus = 0,
        tools = { "putty" },
        tool_action = {
            "You carefully press putty into the tiny aperture beside the lock plate.",
        },
        wound = { location = "right_hand", rank = 1, bleed = false },
        statuses = {
            { id = "poisoned", duration = 90, stacks = 1, magnitude = 1 },
        },
    },

    jaws = {
        key = "jaws",
        examine = "You notice spring-loaded jaws pressed flush against the interior walls of the container.",
        disarm_msg = "You use the metal grips to pull the retaining pins free and let the jaws snap harmlessly shut.",
        fail_msg = "Steel jaws slam shut on your hand with brutal force!",
        room_msg = "{name} cries out as steel jaws clamp shut on a hand!",
        damage_type = "crush",
        base_damage = { min = 18, max = 34 },
        diff_bonus = 5,
        tools = { "grips" },
        tool_action = {
            "You work the metal grips into the mechanism and begin teasing the retaining pins loose.",
        },
        wound = { location = "right_hand", rank = 4, bleed = true },
        statuses = {
            { id = "stunned", duration = 6, stacks = 1, magnitude = 1 },
        },
    },

    sphere = {
        key = "sphere",
        examine = "You locate a tiny humming sphere seated toward the back of the lock mechanism.",
        disarm_msg = "You slip a lockpick inside and gently work the sphere free until the dangerous hum fades away.",
        fail_msg = "The tiny sphere flashes and discharges a violent wave of force through the room!",
        room_msg = "A violent wave of force erupts from {name}'s container!",
        damage_type = "impact",
        base_damage = { min = 16, max = 30 },
        diff_bonus = 10,
        tools = { "lockpick" },
        tool_action = {
            "You slip a lockpick into the mechanism and carefully nudge the sphere from its bracket.",
        },
        special = {
            kind = "room_wave",
            same_room_damage = { min = 8, max = 20 },
            same_room_statuses = {
                { id = "staggered", duration = 8, stacks = 1, magnitude = 1 },
            },
        },
        statuses = {
            { id = "staggered", duration = 8, stacks = 1, magnitude = 1 },
        },
    },

    dark_crystal = {
        key = "dark_crystal",
        examine = "A dark crystal shard pulses faintly from the lock mechanism, feeding off stray magic.",
        disarm_msg = "You file the crystal down until its hungry pulse gutters out into harmless dust.",
        fail_msg = "The dark crystal flares and tears at your reserves with a brutal pulse of anti-magic!",
        room_msg = "A dark pulse of anti-magic bursts from {name}'s container!",
        damage_type = "magic",
        base_damage = { min = 14, max = 28 },
        diff_bonus = 15,
        tools = { "file" },
        tool_action = {
            "You file away the crystal's anchor points, trying not to let the shard flare under the strain.",
        },
        special = {
            kind = "mana_burn",
            mana_burn_pct = 0.50,
        },
        statuses = {
            { id = "dazed", duration = 10, stacks = 1, magnitude = 1 },
        },
    },

    scales = {
        key = "scales",
        examine = "The lock appears to be lined with metallic scales waiting to burst outward if disturbed.",
        disarm_msg = "You work around the scale lining and scrape the razor-edged scales loose before they can spring.",
        fail_msg = "The metallic scales burst outward in a slicing spray!",
        room_msg = "A slicing spray of metallic scales bursts from {name}'s container!",
        damage_type = "slash",
        base_damage = { min = 12, max = 24 },
        diff_bonus = 10,
        tools = { "lockpick" },
        tool_action = {
            "You work a fine implement around the scale lining, easing the trigger away from the tumblers.",
        },
        wound = { location = "right_hand", rank = 2, bleed = true },
    },

    sulphur = {
        key = "sulphur",
        examine = "A foul sulphurous compound is packed into the trap housing around a delicate trigger catch.",
        disarm_msg = "You file away the sulphur compound and tease the hidden trigger free with a needle.",
        fail_msg = "The sulphur compound ignites in a hot flash that singes you and floods the air with choking smoke!",
        room_msg = "A hot sulphurous flash erupts from {name}'s container!",
        damage_type = "fire",
        base_damage = { min = 20, max = 36 },
        diff_bonus = 15,
        tools = { "file", "needle" },
        tool_action = {
            "You carefully file away the sulphur compound packed around the trigger.",
            "You use a fine needle to trip the catch after the compound is thinned.",
        },
        wound = { location = "right_hand", rank = 2, bleed = false },
        statuses = {
            { id = "clumsy", duration = 20, stacks = 1, magnitude = 1 },
        },
    },

    gas = {
        key = "gas",
        examine = "A tiny vial of compressed gas is wired into the lock and poised to vent into the opener's face.",
        disarm_msg = "You steady the vial with metal grips and disconnect the trigger wire before the gas can vent.",
        fail_msg = "A choking cloud of gas vents into your face and spills through the room!",
        room_msg = "A choking cloud of gas spills from {name}'s container!",
        damage_type = "poison",
        base_damage = { min = 8, max = 18 },
        diff_bonus = 10,
        tools = { "grips" },
        tool_action = {
            "You hold the gas vial steady with the metal grips and work the trigger loose.",
        },
        special = {
            kind = "gas_cloud",
            same_room_damage = { min = 3, max = 8 },
            duration = 10,
            tick_interval = 5,
        },
        statuses = {
            { id = "poisoned", duration = 90, stacks = 1, magnitude = 1 },
        },
    },

    acid = {
        key = "acid",
        examine = "A vial of acid is balanced over the lock and ready to tip and shatter at the slightest mistake.",
        disarm_msg = "You pad the vial with cotton and remove it with the grips before it can spill.",
        fail_msg = "The acid vial tips and shatters, splashing caustic fluid over you!",
        room_msg = "{name} hisses in pain as acid splashes out of a trapped container!",
        damage_type = "acid",
        base_damage = { min = 18, max = 34 },
        diff_bonus = 12,
        tools = { "cotton", "grips" },
        tool_action = {
            "You pack cotton around the vial to catch any sudden spill.",
            "You use the grips to lift the acid vial out of danger.",
        },
        wound = { location = "right_hand", rank = 2, bleed = false },
        statuses = {
            { id = "feeble", duration = 20, stacks = 1, magnitude = 1 },
        },
    },

    spring = {
        key = "spring",
        examine = "A coiled spring has been rigged to snap the lid down violently when the mechanism shifts.",
        disarm_msg = "You trap the spring with the grips and bend it until the tension bleeds away.",
        fail_msg = "The lid snaps down brutally on your fingers!",
        room_msg = "{name}'s hand is smashed by a snapping lid!",
        damage_type = "crush",
        base_damage = { min = 8, max = 18 },
        diff_bonus = 5,
        tools = { "grips" },
        tool_action = {
            "You wedge the grips against the coiled spring and begin forcing it flat.",
        },
        wound = { location = "right_hand", rank = 1, bleed = false },
    },

    fire_vial = {
        key = "fire_vial",
        examine = "A volatile fire vial is wired into the lock and will ignite if the trigger slips.",
        disarm_msg = "You catch the vial with the grips and slip the trigger wire free without letting it strike.",
        fail_msg = "The fire vial shatters and erupts in a spray of flame!",
        room_msg = "Flame erupts from {name}'s trapped container!",
        damage_type = "fire",
        base_damage = { min = 24, max = 42 },
        diff_bonus = 18,
        tools = { "grips" },
        tool_action = {
            "You catch the vial with the grips and carefully lift the firing wire free.",
        },
        special = {
            kind = "room_blast",
            same_room_damage = { min = 6, max = 14 },
        },
        wound = { location = "right_hand", rank = 2, bleed = false },
    },

    spores = {
        key = "spores",
        examine = "You spot a tiny tube of spores capped by a fragile membrane that the tumblers will tear open.",
        disarm_msg = "You plug the end of the spore tube with putty, sealing it before the membrane can rupture.",
        fail_msg = "A dark cloud of spores erupts into the air and everyone nearby begins choking!",
        room_msg = "A dark cloud of spores erupts from {name}'s trapped container!",
        damage_type = "poison",
        base_damage = { min = 0, max = 0 },
        diff_bonus = 12,
        tools = { "putty" },
        tool_action = {
            "You seal the end of the spore tube with putty, blocking the trap's payload.",
        },
        special = {
            kind = "room_hazard",
            hazard_id = "spores",
            duration = 25,
            tick_interval = 5,
            same_room_damage = { min = 4, max = 10 },
            wound = { location = "chest", rank = 1, bleed = false },
            same_room_statuses = {
                { id = "poisoned", duration = 60, stacks = 1, magnitude = 1 },
            },
        },
    },

    plate = {
        key = "plate",
        examine = "A heavy plate has been fitted across the lock, with razor fragments ready to kick loose when tampered with.",
        disarm_msg = "You melt through the plate's anchors and let it fall harmlessly away from the lock face.",
        fail_msg = "The plated face kicks loose in a violent burst of razor-edged metal!",
        room_msg = "Razor-edged fragments spray from {name}'s trapped container!",
        damage_type = "slash",
        base_damage = { min = 18, max = 34 },
        diff_bonus = 14,
        tools = { "vials" },
        tool_action = {
            "You drip acid across the plated anchors and wait for the fastenings to weaken.",
        },
        wound = { location = "right_hand", rank = 2, bleed = true },
    },

    glyph = {
        key = "glyph",
        examine = "A magical glyph has been inscribed along the inner lock housing and hums with unstable force.",
        disarm_msg = "You scrape away the glyph line by line until the ward flickers out.",
        fail_msg = "The glyph flares and twists space violently around the trapped container!",
        room_msg = "A violent magical flare erupts from {name}'s trapped container!",
        damage_type = "magic",
        base_damage = { min = 20, max = 40 },
        diff_bonus = 20,
        tools = {},
        tool_action = {},
        special = {
            kind = "magic_blast",
            same_room_damage = { min = 5, max = 12 },
            same_room_statuses = {
                { id = "dazed", duration = 8, stacks = 1, magnitude = 1 },
            },
        },
        statuses = {
            { id = "dazed", duration = 10, stacks = 1, magnitude = 1 },
        },
    },

    rods = {
        key = "rods",
        examine = "A cluster of metal rods lies in wait, ready to lance outward if the lock shifts.",
        disarm_msg = "You catch the rods with the grips and bend them aside before they can launch.",
        fail_msg = "Metal rods lance out of the container and stab into you!",
        room_msg = "{name} recoils as a cluster of metal rods launches from a trapped container!",
        damage_type = "puncture",
        base_damage = { min = 14, max = 28 },
        diff_bonus = 10,
        tools = { "grips" },
        tool_action = {
            "You secure the rods with the grips and begin levering them away from the trigger.",
        },
        wound = { location = "right_hand", rank = 2, bleed = true },
    },

    boomer = {
        key = "boomer",
        examine = "A packed explosive charge has been hidden under the lock face and will detonate if jarred.",
        disarm_msg = "You smother the ignition point with putty and gently lift the powder charge clear.",
        fail_msg = "The trap detonates in a deafening explosion!",
        room_msg = "{name}'s trapped container detonates in a deafening explosion!",
        damage_type = "fire",
        base_damage = { min = 36, max = 72 },
        diff_bonus = 30,
        tools = { "putty" },
        tool_action = {
            "You smother the ignition point with putty before reaching for the charge itself.",
        },
        special = {
            kind = "room_blast",
            destroys_box = true,
            same_room_damage = { min = 14, max = 28 },
            adjacent_room_damage = { min = 4, max = 12 },
            adjacent_room_message = "A heavy explosion booms nearby and the walls shudder from the force!",
        },
        wound = { location = "right_hand", rank = 3, bleed = false },
        statuses = {
            { id = "stunned", duration = 6, stacks = 1, magnitude = 1 },
        },
    },

    temporal_rift = {
        key = "temporal_rift",
        examine = "A warped glyph is set into the lock housing, and the air around it seems to bend in on itself.",
        disarm_msg = "You break the warped line of the glyph and the air stops folding around the lock.",
        fail_msg = "The trap tears open a temporal rift and drags you through collapsing space!",
        room_msg = "Space folds in on itself around {name} as a temporal rift yanks them away!",
        damage_type = "magic",
        base_damage = { min = 10, max = 18 },
        diff_bonus = 28,
        tools = {},
        tool_action = {},
        special = {
            kind = "temporal_rift",
            destination_room_id = 1768,
            same_room_message = "The room ripples violently as the rift snaps shut.",
        },
        statuses = {
            { id = "stunned", duration = 8, stacks = 1, magnitude = 1 },
        },
    },
}

return TrapData
