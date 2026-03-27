--[[
    weather_config.lua
    Canonical weather state definitions and climate rules.

    STATES (ordered from best to worst):
      clear, partly_cloudy, overcast, light_rain, rain, heavy_rain,
      storm, blizzard, blood_rain (charm-only), fog, drizzle, sleet, snow, heavy_snow

    CLIMATES cap which states are possible naturally:
      temperate   : clear → storm (no blizzard)
      arctic      : clear → blizzard (all snow states)
      desert      : clear → overcast (very rare light_rain)
      tropical    : clear → storm (frequent rain, no snow)
      underground : always "still" — no weather at all
      coastal     : clear → storm (+ fog states)
      swamp       : overcast → rain most of the time (+ fog)

    TRANSITION WEIGHTS per climate define how often states change and
    which direction they tend to drift. Higher weight = more likely.
    Transitions only move one step at a time (clear→partly_cloudy, not clear→storm).

    TERRAIN TYPES (for foraging — weather-independent):
      deciduous, coniferous, mixed_forest, grassland, scrubland,
      swamp, desert, tundra, alpine, coastal, underground, urban, farmland

    INTENSITY LEVELS:
      light, moderate, heavy
      Not all states have intensities (clear always has none, storm always heavy).
--]]

local Weather = {}

-- ── State definitions ─────────────────────────────────────────────────────────

Weather.states = {
    clear         = { label = "clear",          has_intensity = false, precipitation = false, outdoor_only = false },
    partly_cloudy = { label = "partly cloudy",  has_intensity = false, precipitation = false, outdoor_only = false },
    overcast      = { label = "overcast",        has_intensity = false, precipitation = false, outdoor_only = false },
    fog           = { label = "foggy",           has_intensity = true,  precipitation = false, outdoor_only = true  },
    drizzle       = { label = "drizzling",       has_intensity = false, precipitation = true,  outdoor_only = true  },
    light_rain    = { label = "lightly raining", has_intensity = false, precipitation = true,  outdoor_only = true  },
    rain          = { label = "raining",         has_intensity = true,  precipitation = true,  outdoor_only = true  },
    heavy_rain    = { label = "heavily raining", has_intensity = false, precipitation = true,  outdoor_only = true  },
    storm         = { label = "storming",        has_intensity = false, precipitation = true,  outdoor_only = true  },
    snow          = { label = "snowing",         has_intensity = true,  precipitation = true,  outdoor_only = true  },
    heavy_snow    = { label = "heavily snowing", has_intensity = false, precipitation = true,  outdoor_only = true  },
    blizzard      = { label = "blizzard",        has_intensity = false, precipitation = true,  outdoor_only = true  },
    sleet         = { label = "sleeting",        has_intensity = false, precipitation = true,  outdoor_only = true  },
    -- Charm-only states (cannot occur naturally)
    blood_rain    = { label = "blood rain",      has_intensity = false, precipitation = true,  outdoor_only = true, charm_only = true },
    thunderstorm  = { label = "thunderstorm",    has_intensity = false, precipitation = true,  outdoor_only = true, charm_only = true },
}

-- ── Climate definitions ───────────────────────────────────────────────────────
-- allowed_states: which states can occur naturally
-- transition_map: {from_state: {to_state: weight}} — how states naturally flow
-- default_state: what state new zones start with
-- change_chance: probability per tick (0-100) that weather changes at all

Weather.climates = {
    temperate = {
        default_state  = "clear",
        change_chance  = 20,    -- 20% each weather tick (~every 5 min)
        allowed_states = {
            "clear", "partly_cloudy", "overcast", "drizzle",
            "light_rain", "rain", "heavy_rain", "storm", "fog"
        },
        transitions = {
            clear         = { partly_cloudy = 60, clear = 40 },
            partly_cloudy = { clear = 35, overcast = 35, partly_cloudy = 30 },
            overcast      = { partly_cloudy = 30, drizzle = 25, light_rain = 20, fog = 10, overcast = 15 },
            drizzle       = { light_rain = 40, overcast = 35, drizzle = 25 },
            light_rain    = { rain = 35, drizzle = 30, overcast = 25, light_rain = 10 },
            rain          = { heavy_rain = 25, light_rain = 35, storm = 15, rain = 25 },
            heavy_rain    = { storm = 30, rain = 40, heavy_rain = 30 },
            storm         = { heavy_rain = 50, storm = 30, rain = 20 },
            fog           = { clear = 40, partly_cloudy = 35, drizzle = 25 },
        },
    },

    arctic = {
        default_state  = "overcast",
        change_chance  = 15,
        allowed_states = {
            "clear", "partly_cloudy", "overcast", "snow",
            "heavy_snow", "blizzard", "sleet", "fog"
        },
        transitions = {
            clear         = { partly_cloudy = 55, clear = 45 },
            partly_cloudy = { clear = 30, overcast = 40, partly_cloudy = 30 },
            overcast      = { snow = 35, sleet = 20, partly_cloudy = 25, overcast = 20 },
            snow          = { heavy_snow = 30, overcast = 30, snow = 30, blizzard = 10 },
            heavy_snow    = { blizzard = 35, snow = 40, heavy_snow = 25 },
            blizzard      = { heavy_snow = 55, blizzard = 30, snow = 15 },
            sleet         = { snow = 40, overcast = 35, sleet = 25 },
            fog           = { clear = 35, overcast = 40, fog = 25 },
        },
    },

    desert = {
        default_state  = "clear",
        change_chance  = 8,     -- weather rarely changes in desert
        allowed_states = {
            "clear", "partly_cloudy", "overcast", "light_rain", "fog"
        },
        transitions = {
            clear         = { partly_cloudy = 25, clear = 75 },
            partly_cloudy = { clear = 60, overcast = 20, partly_cloudy = 20 },
            overcast      = { clear = 50, light_rain = 15, partly_cloudy = 35 },
            light_rain    = { overcast = 60, clear = 40 },
            fog           = { clear = 55, partly_cloudy = 45 },
        },
    },

    tropical = {
        default_state  = "partly_cloudy",
        change_chance  = 30,    -- weather changes frequently
        allowed_states = {
            "clear", "partly_cloudy", "overcast", "rain",
            "heavy_rain", "storm", "fog"
        },
        transitions = {
            clear         = { partly_cloudy = 50, clear = 50 },
            partly_cloudy = { overcast = 40, clear = 30, rain = 15, partly_cloudy = 15 },
            overcast      = { rain = 40, heavy_rain = 20, partly_cloudy = 25, overcast = 15 },
            rain          = { heavy_rain = 35, storm = 20, overcast = 30, rain = 15 },
            heavy_rain    = { storm = 40, rain = 35, heavy_rain = 25 },
            storm         = { heavy_rain = 40, rain = 35, storm = 25 },
            fog           = { clear = 30, partly_cloudy = 40, drizzle = 30 },
        },
    },

    coastal = {
        default_state  = "partly_cloudy",
        change_chance  = 25,
        allowed_states = {
            "clear", "partly_cloudy", "overcast", "fog", "drizzle",
            "light_rain", "rain", "heavy_rain", "storm"
        },
        transitions = {
            clear         = { partly_cloudy = 45, fog = 20, clear = 35 },
            partly_cloudy = { clear = 30, overcast = 30, fog = 15, partly_cloudy = 25 },
            overcast      = { fog = 25, drizzle = 25, light_rain = 20, partly_cloudy = 30 },
            fog           = { clear = 30, drizzle = 30, partly_cloudy = 25, fog = 15 },
            drizzle       = { light_rain = 35, fog = 30, overcast = 35 },
            light_rain    = { rain = 35, drizzle = 30, overcast = 25, light_rain = 10 },
            rain          = { heavy_rain = 25, light_rain = 35, storm = 20, rain = 20 },
            heavy_rain    = { storm = 35, rain = 40, heavy_rain = 25 },
            storm         = { heavy_rain = 50, storm = 25, rain = 25 },
        },
    },

    swamp = {
        default_state  = "overcast",
        change_chance  = 20,
        allowed_states = {
            "overcast", "fog", "drizzle", "light_rain",
            "rain", "heavy_rain", "storm", "partly_cloudy"
        },
        transitions = {
            partly_cloudy = { overcast = 50, fog = 25, partly_cloudy = 25 },
            overcast      = { fog = 35, drizzle = 30, light_rain = 20, overcast = 15 },
            fog           = { overcast = 40, drizzle = 35, fog = 25 },
            drizzle       = { rain = 35, fog = 30, overcast = 35 },
            light_rain    = { rain = 40, drizzle = 30, overcast = 30 },
            rain          = { heavy_rain = 30, light_rain = 35, storm = 15, rain = 20 },
            heavy_rain    = { storm = 35, rain = 40, heavy_rain = 25 },
            storm         = { heavy_rain = 50, rain = 30, storm = 20 },
        },
    },

    underground = {
        default_state  = "still",
        change_chance  = 0,     -- underground weather never changes
        allowed_states = { "still" },
        transitions    = {},
    },
}

-- ── Terrain types ─────────────────────────────────────────────────────────────
-- Used by foraging to determine which herbs grow here.
-- NOT affected by weather state.

Weather.terrains = {
    "deciduous",    -- broadleaf forest (oak, maple, elm)
    "coniferous",   -- pine, spruce, fir
    "mixed_forest", -- combination
    "grassland",    -- open fields, meadows
    "scrubland",    -- dry brush, low shrubs
    "swamp",        -- wetlands, bogs
    "desert",       -- arid, sandy
    "tundra",       -- treeless, frozen ground
    "alpine",       -- high elevation
    "coastal",      -- shoreline, beach
    "underground",  -- caves, tunnels
    "urban",        -- city streets, buildings
    "farmland",     -- cultivated fields
    "riverbank",    -- along rivers and streams
    "moorland",     -- open high ground, heather
}

-- ── Weather tick interval ─────────────────────────────────────────────────────
-- How many real seconds between each potential weather change per zone.
-- Each zone rolls against its change_chance each tick.
Weather.tick_interval_seconds = 300   -- 5 minutes

-- ── Message pools by weather state ───────────────────────────────────────────
-- Global fallback messages for each weather state.
-- Zone LUA files can override/extend these with zone.weather_messages = {...}
-- These fire in outdoor rooms only.

Weather.global_messages = {
    clear = {
        "A warm ray of sunlight filters through the air.",
        "The sky overhead is clear and brilliant.",
        "A gentle breeze drifts through, carrying the scent of fresh air.",
        "Fluffy clouds drift lazily at the horizon.",
        "Bright sunlight casts crisp shadows across the ground.",
    },
    partly_cloudy = {
        "Patches of cloud drift across the sun, dappling the ground with shifting shadows.",
        "A cool breeze stirs as a cloud passes overhead.",
        "The sky shifts between sunshine and shadow.",
        "White clouds pile up at the edge of the horizon.",
    },
    overcast = {
        "The sky is heavy with grey clouds, the light flat and diffuse.",
        "A grey ceiling of cloud hangs low overhead.",
        "The air feels thick and damp beneath the overcast sky.",
        "No shadows fall — the cloud cover is complete.",
    },
    fog = {
        "A thin mist clings to the ground, blurring distant shapes.",
        "Tendrils of fog drift through the area, dampening sound.",
        "The fog thickens around you, reducing visibility.",
        "Beads of moisture from the fog collect on your clothing.",
        "A cold, damp mist swirls around your ankles.",
    },
    drizzle = {
        "A light drizzle falls, barely more than mist.",
        "Fine droplets of rain drift down from the grey sky.",
        "The soft patter of drizzle taps against leaves and stone.",
        "A cool drizzle mists the air around you.",
    },
    light_rain = {
        "A light rain begins to fall, tapping softly on the ground.",
        "Rain patters down in a gentle, steady rhythm.",
        "The smell of rain on earth rises around you.",
        "Raindrops catch the light as they fall.",
    },
    rain = {
        "The rain falls steadily, drumming against leaves and stone.",
        "Rivulets of water run across the ground as the rain persists.",
        "The steady drumming of rain fills the air.",
        "Water streams from every surface as the rain continues.",
    },
    heavy_rain = {
        "Heavy rain lashes down, soaking everything in sight.",
        "Rain hammers the ground in thick, driving sheets.",
        "The roar of heavy rain drowns out other sounds.",
        "Water pools rapidly as the heavy rain continues.",
    },
    storm = {
        "Thunder rolls in the distance as the storm intensifies.",
        "A crack of lightning illuminates the sky for an instant.",
        "The storm rages, wind driving rain almost horizontally.",
        "Lightning flares, followed moments later by a deep boom of thunder.",
        "The wind howls through the area, bending everything before it.",
    },
    snow = {
        "Soft snowflakes drift down from a grey sky.",
        "Snow falls silently, blanketing everything in white.",
        "Your breath fogs in the cold air as snow settles around you.",
        "The snow muffles sound, wrapping the world in quiet.",
    },
    heavy_snow = {
        "Heavy snow falls in thick curtains, visibility dropping rapidly.",
        "The world disappears behind a dense wall of falling snow.",
        "Snow accumulates quickly underfoot as it falls heavily.",
    },
    blizzard = {
        "The blizzard howls around you, wind-driven snow cutting exposed skin.",
        "You can barely see your hand in front of you through the blizzard.",
        "Ice crystals sting your face as the blizzard rages.",
        "The wind screams past, carrying walls of blinding snow.",
    },
    sleet = {
        "Sleet hisses down, ice crystals mixed with rain.",
        "The cold bite of sleet stings wherever it touches exposed skin.",
        "Ice pellets rattle against hard surfaces.",
    },
    blood_rain = {
        "A crimson rain falls from a sky the colour of an open wound.",
        "The air tastes of copper as blood-red rain splatters the ground.",
        "Dark red droplets fall, staining everything they touch.",
        "The unnatural crimson rain sends a chill through you that has nothing to do with temperature.",
    },
    still = {
        -- Underground / indoor "weather" — never shown outdoors
        "The air is still and cool here, untouched by any wind.",
        "The silence underground is complete, broken only by your own movement.",
    },
}

return Weather
