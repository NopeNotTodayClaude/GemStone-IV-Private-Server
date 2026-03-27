--[[
    body_types.lua
    Defines valid hit locations for each creature body type.

    Fields per location:
      weight      - relative probability for RANDOM (unaimed) hits
      aim_penalty - bonus difficulty added to aim success roll (higher = harder to aim at)
                    0 = easy target (chest), higher = harder (eye, neck)
      label       - display string shown in combat messages

    Body types:
      biped     - humanoid creatures with two legs/arms (kobold, skeleton, ghoul, orc, etc.)
      quadruped - four-legged creatures (wolf, bear, bobcat, etc.)
      ophidian  - snake/serpent body (no limbs - chest/abdomen dominant)
      hybrid    - partially humanoid (myklian, cockatrice, etc.)
      avian     - winged creatures (bird-type)
      arachnid  - multi-limbed (spider, etc.)
      insectoid - multi-limbed insects
--]]

local BodyTypes = {}

-- ── BIPED ─────────────────────────────────────────────────────────────────────
-- Standard humanoid. Full limb set.
BodyTypes["biped"] = {
    locations = {
        ["head"]       = { weight = 5,  aim_penalty = 15, label = "head"       },
        ["neck"]       = { weight = 3,  aim_penalty = 20, label = "neck"       },
        ["chest"]      = { weight = 20, aim_penalty = 0,  label = "chest"      },
        ["abdomen"]    = { weight = 15, aim_penalty = 5,  label = "abdomen"    },
        ["back"]       = { weight = 10, aim_penalty = 10, label = "back"       },
        ["right arm"]  = { weight = 10, aim_penalty = 10, label = "right arm"  },
        ["left arm"]   = { weight = 10, aim_penalty = 10, label = "left arm"   },
        ["right hand"] = { weight = 5,  aim_penalty = 15, label = "right hand" },
        ["left hand"]  = { weight = 5,  aim_penalty = 15, label = "left hand"  },
        ["right leg"]  = { weight = 8,  aim_penalty = 10, label = "right leg"  },
        ["left leg"]   = { weight = 8,  aim_penalty = 10, label = "left leg"   },
        ["right eye"]  = { weight = 1,  aim_penalty = 30, label = "right eye"  },
        ["left eye"]   = { weight = 1,  aim_penalty = 30, label = "left eye"   },
    },
    -- Valid AIM targets (what a player can type "AIM <x>" for)
    aimable = {
        "head", "neck", "chest", "abdomen", "back",
        "right arm", "left arm", "right hand", "left hand",
        "right leg", "left leg", "right eye", "left eye",
    },
}

-- ── QUADRUPED ─────────────────────────────────────────────────────────────────
-- Four-legged creatures. No hands. Neck/head harder to reach. Flanks instead of back.
BodyTypes["quadruped"] = {
    locations = {
        ["head"]       = { weight = 5,  aim_penalty = 20, label = "head"       },
        ["neck"]       = { weight = 5,  aim_penalty = 15, label = "neck"       },
        ["chest"]      = { weight = 18, aim_penalty = 0,  label = "chest"      },
        ["abdomen"]    = { weight = 15, aim_penalty = 5,  label = "abdomen"    },
        ["back"]       = { weight = 12, aim_penalty = 5,  label = "back"       },
        ["right flank"]= { weight = 10, aim_penalty = 10, label = "right flank"},
        ["left flank"] = { weight = 10, aim_penalty = 10, label = "left flank" },
        ["right foreleg"]={ weight = 8, aim_penalty = 15, label = "right foreleg"},
        ["left foreleg"] = { weight = 8, aim_penalty = 15, label = "left foreleg" },
        ["right hindleg"]= { weight = 5, aim_penalty = 20, label = "right hindleg"},
        ["left hindleg"] = { weight = 5, aim_penalty = 20, label = "left hindleg" },
        ["right eye"]  = { weight = 1,  aim_penalty = 35, label = "right eye"  },
        ["left eye"]   = { weight = 1,  aim_penalty = 35, label = "left eye"   },
    },
    aimable = {
        "head", "neck", "chest", "abdomen", "back",
        "right flank", "left flank",
        "right foreleg", "left foreleg",
        "right hindleg", "left hindleg",
        "right eye", "left eye",
    },
}

-- ── OPHIDIAN ─────────────────────────────────────────────────────────────────
-- Snake/serpent body. No limbs. Slash crits on body are dominant.
-- Head crits more dangerous due to poison glands.
BodyTypes["ophidian"] = {
    locations = {
        ["head"]   = { weight = 10, aim_penalty = 15, label = "head"   },
        ["neck"]   = { weight = 8,  aim_penalty = 10, label = "neck"   },
        ["body"]   = { weight = 45, aim_penalty = 0,  label = "body"   },
        ["tail"]   = { weight = 25, aim_penalty = 5,  label = "tail"   },
        ["eye"]    = { weight = 2,  aim_penalty = 30, label = "eye"    },
    },
    aimable = {
        "head", "neck", "body", "tail", "eye",
    },
}

-- ── HYBRID ───────────────────────────────────────────────────────────────────
-- Partially humanoid (e.g. cockatrice, myklian, etc.)
-- Has a torso/arms but also wings/tail — no standard leg set.
BodyTypes["hybrid"] = {
    locations = {
        ["head"]       = { weight = 5,  aim_penalty = 15, label = "head"      },
        ["neck"]       = { weight = 3,  aim_penalty = 20, label = "neck"      },
        ["chest"]      = { weight = 18, aim_penalty = 0,  label = "chest"     },
        ["abdomen"]    = { weight = 12, aim_penalty = 5,  label = "abdomen"   },
        ["right wing"] = { weight = 10, aim_penalty = 10, label = "right wing"},
        ["left wing"]  = { weight = 10, aim_penalty = 10, label = "left wing" },
        ["right arm"]  = { weight = 8,  aim_penalty = 10, label = "right arm" },
        ["left arm"]   = { weight = 8,  aim_penalty = 10, label = "left arm"  },
        ["tail"]       = { weight = 12, aim_penalty = 10, label = "tail"      },
        ["right leg"]  = { weight = 7,  aim_penalty = 15, label = "right leg" },
        ["left leg"]   = { weight = 7,  aim_penalty = 15, label = "left leg"  },
        ["right eye"]  = { weight = 1,  aim_penalty = 30, label = "right eye" },
        ["left eye"]   = { weight = 1,  aim_penalty = 30, label = "left eye"  },
    },
    aimable = {
        "head", "neck", "chest", "abdomen",
        "right wing", "left wing",
        "right arm", "left arm",
        "tail", "right leg", "left leg",
        "right eye", "left eye",
    },
}

-- ── AVIAN ────────────────────────────────────────────────────────────────────
-- Bird-like creatures (harpy, giant hawk, etc.)
BodyTypes["avian"] = {
    locations = {
        ["head"]       = { weight = 8,  aim_penalty = 20, label = "head"      },
        ["chest"]      = { weight = 20, aim_penalty = 0,  label = "chest"     },
        ["abdomen"]    = { weight = 12, aim_penalty = 5,  label = "abdomen"   },
        ["right wing"] = { weight = 15, aim_penalty = 10, label = "right wing"},
        ["left wing"]  = { weight = 15, aim_penalty = 10, label = "left wing" },
        ["right talon"]= { weight = 8,  aim_penalty = 15, label = "right talon"},
        ["left talon"] = { weight = 8,  aim_penalty = 15, label = "left talon"},
        ["tail"]       = { weight = 10, aim_penalty = 10, label = "tail"      },
        ["right eye"]  = { weight = 2,  aim_penalty = 35, label = "right eye" },
        ["left eye"]   = { weight = 2,  aim_penalty = 35, label = "left eye"  },
    },
    aimable = {
        "head", "chest", "abdomen",
        "right wing", "left wing",
        "right talon", "left talon",
        "tail", "right eye", "left eye",
    },
}

-- ── ARACHNID ─────────────────────────────────────────────────────────────────
-- Spiders and multi-limbed creatures. Many legs = individual leg targeting.
BodyTypes["arachnid"] = {
    locations = {
        ["head"]       = { weight = 8,  aim_penalty = 20, label = "head"       },
        ["abdomen"]    = { weight = 25, aim_penalty = 0,  label = "abdomen"    },
        ["cephalothorax"] = { weight = 18, aim_penalty = 5, label = "cephalothorax"},
        ["leg 1"]      = { weight = 5,  aim_penalty = 20, label = "leg"        },
        ["leg 2"]      = { weight = 5,  aim_penalty = 20, label = "leg"        },
        ["leg 3"]      = { weight = 5,  aim_penalty = 20, label = "leg"        },
        ["leg 4"]      = { weight = 5,  aim_penalty = 20, label = "leg"        },
        ["right eye"]  = { weight = 1,  aim_penalty = 35, label = "right eye"  },
        ["left eye"]   = { weight = 1,  aim_penalty = 35, label = "left eye"   },
    },
    aimable = {
        "head", "abdomen", "cephalothorax",
        "right eye", "left eye",
    },
}

-- ── INSECTOID ────────────────────────────────────────────────────────────────
-- Large insects. Exoskeleton makes crits harder (high ASG).
BodyTypes["insectoid"] = {
    locations = {
        ["head"]      = { weight = 8,  aim_penalty = 20, label = "head"         },
        ["thorax"]    = { weight = 25, aim_penalty = 0,  label = "thorax"       },
        ["abdomen"]   = { weight = 20, aim_penalty = 5,  label = "abdomen"      },
        ["right foreleg"] = { weight = 8, aim_penalty = 15, label = "right foreleg"},
        ["left foreleg"]  = { weight = 8, aim_penalty = 15, label = "left foreleg" },
        ["right midleg"]  = { weight = 6, aim_penalty = 20, label = "right midleg" },
        ["left midleg"]   = { weight = 6, aim_penalty = 20, label = "left midleg"  },
        ["right hindleg"] = { weight = 6, aim_penalty = 20, label = "right hindleg"},
        ["left hindleg"]  = { weight = 6, aim_penalty = 20, label = "left hindleg" },
        ["antenna"]   = { weight = 3,  aim_penalty = 25, label = "antenna"      },
        ["right eye"] = { weight = 1,  aim_penalty = 35, label = "right eye"    },
        ["left eye"]  = { weight = 1,  aim_penalty = 35, label = "left eye"     },
    },
    aimable = {
        "head", "thorax", "abdomen", "antenna",
        "right foreleg", "left foreleg",
        "right hindleg", "left hindleg",
        "right eye", "left eye",
    },
}

-- Fallback: anything unknown defaults to biped
BodyTypes["default"] = BodyTypes["biped"]

return BodyTypes
