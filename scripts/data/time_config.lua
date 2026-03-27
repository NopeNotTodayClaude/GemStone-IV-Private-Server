--[[
    time_config.lua
    Canonical Elanthian calendar definitions.
    Source: https://gswiki.play.net/Elanthian_Calendar

    This is the SINGLE SOURCE OF TRUTH for all Elanthian time names.
    Python loads this via ElanthianClock. LUA scripts can require it directly.

    Year offset: real year + 3100 = Elanthian year
      (established in 1995 as 5095 Modern Era, so 1995 + 3100 = 5095)
--]]

local Calendar = {}

-- Real year -> Elanthian year offset
Calendar.year_offset = 3100

-- Days of the week (Python weekday(): 0=Monday ... 6=Sunday)
Calendar.days = {
    [0] = "Volnes",              -- Monday
    [1] = "Tilamaires",          -- Tuesday
    [2] = "Leyan",               -- Wednesday
    [3] = "Niiman",              -- Thursday
    [4] = "Day of the Huntress", -- Friday
    [5] = "Feastday",            -- Saturday
    [6] = "Restday",             -- Sunday
}

-- Months (Python month: 1=January ... 12=December)
Calendar.months = {
    [1]  = "Lormesta",   -- January
    [2]  = "Fashanos",   -- February
    [3]  = "Charlatos",  -- March
    [4]  = "Olaesta",    -- April
    [5]  = "Ivastaen",   -- May
    [6]  = "Lumnea",     -- June
    [7]  = "Koaratos",   -- July
    [8]  = "Phoenatos",  -- August
    [9]  = "Imaerasta",  -- September
    [10] = "Jastatos",   -- October
    [11] = "Eoantos",    -- November
    [12] = "Eorgaen",    -- December
}

--[[
    Time of day periods (by real hour, 0-23).
    GS4 wiki names four canonical "Hours" but also uses prose period names
    in the TIME verb output ("It is currently late evening.").
    We define both.

    Named hours (canonical GS4):
      Hour of Lumnis  = Dawn       (5am-7am)
      Hour of Phoen   = Noon       (11am-1pm)
      Hour of Tonis   = Dusk       (6pm-8pm)
      Hour of Ronan   = Midnight   (11pm-1am)

    Period names (from TIME verb output, "late evening" etc.):
      deep night   : 0-4
      dawn         : 5-6
      morning      : 7-10
      midday       : 11-13
      afternoon    : 14-17
      evening      : 18-20
      night        : 21-23
--]]

Calendar.hour_names = {
    -- Named by canonical GS4 hour
    -- hour_name, period_name, period_id
    [0]  = { hour = "Hour of Ronan",  period = "deep night",   period_id = "deep_night"  },
    [1]  = { hour = "Hour of Ronan",  period = "deep night",   period_id = "deep_night"  },
    [2]  = { hour = "Hour of Ronan",  period = "deep night",   period_id = "deep_night"  },
    [3]  = { hour = "Hour of Ronan",  period = "deep night",   period_id = "deep_night"  },
    [4]  = { hour = "Hour of Ronan",  period = "deep night",   period_id = "deep_night"  },
    [5]  = { hour = "Hour of Lumnis", period = "dawn",         period_id = "dawn"        },
    [6]  = { hour = "Hour of Lumnis", period = "dawn",         period_id = "dawn"        },
    [7]  = { hour = "Hour of Lumnis", period = "morning",      period_id = "morning"     },
    [8]  = { hour = "Hour of Lumnis", period = "morning",      period_id = "morning"     },
    [9]  = { hour = "Hour of Lumnis", period = "morning",      period_id = "morning"     },
    [10] = { hour = "Hour of Lumnis", period = "morning",      period_id = "morning"     },
    [11] = { hour = "Hour of Phoen",  period = "midday",       period_id = "midday"      },
    [12] = { hour = "Hour of Phoen",  period = "midday",       period_id = "midday"      },
    [13] = { hour = "Hour of Phoen",  period = "midday",       period_id = "midday"      },
    [14] = { hour = "Hour of Phoen",  period = "afternoon",    period_id = "afternoon"   },
    [15] = { hour = "Hour of Phoen",  period = "afternoon",    period_id = "afternoon"   },
    [16] = { hour = "Hour of Phoen",  period = "afternoon",    period_id = "afternoon"   },
    [17] = { hour = "Hour of Phoen",  period = "afternoon",    period_id = "afternoon"   },
    [18] = { hour = "Hour of Tonis",  period = "evening",      period_id = "evening"     },
    [19] = { hour = "Hour of Tonis",  period = "evening",      period_id = "evening"     },
    [20] = { hour = "Hour of Tonis",  period = "evening",      period_id = "evening"     },
    [21] = { hour = "Hour of Tonis",  period = "late evening", period_id = "late_evening"},
    [22] = { hour = "Hour of Ronan",  period = "late evening", period_id = "late_evening"},
    [23] = { hour = "Hour of Ronan",  period = "night",        period_id = "night"       },
}

-- Elanthian holidays (month, day) -> holiday name
Calendar.holidays = {
    { month = 2,  day = 14, name = "Day of Voaris and Laethe"  },
    { month = 4,  day = 1,  name = "Day of Zelia's Warning"    },
    { month = 5,  day = 1,  name = "Day of Kuon's Blessing"    },
    { month = 5,  day = 20, name = "Festival of Oleani"        },
    { month = 7,  day = 14, name = "Cholen's Eve"              },
    { month = 10, day = 31, name = "Eve of the Reunion"        },
    { month = 12, day = 20, name = "Feast of the Immortals"    },
    { month = 12, day = 21, name = "Feast of the Immortals"    },
    { month = 12, day = 22, name = "Feast of the Immortals"    },
    { month = 12, day = 23, name = "Feast of the Immortals"    },
    { month = 12, day = 24, name = "Feast of the Immortals"    },
    { month = 12, day = 25, name = "Feast of the Immortals"    },
    { month = 12, day = 31, name = "Lornon's Eve"              },
}

return Calendar
