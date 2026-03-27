--[[
    events_config.lua
    Configuration for scheduled server events.

    All timing uses real-world days/hours.
    All XP values are pre-scaled for this server's x3 XP_GAIN_MULTIPLIER.

    LUMNIS:
      Fires every Saturday AND Sunday at midnight (server local time).
      Affects the absorption pulse — field XP drains at normal rate,
      but each drained point converts to more absorbed XP.
      Phase 1: x3 absorption until lumnis_phase1_pool is consumed.
      Phase 2: x2 absorption until lumnis_phase2_pool is consumed.
      Caps scale x3 from live GS4's 14,600 / 7,300 to account for
      server XP multiplier so the bonus lasts a comparable wall-clock time.

    BONUS_XP_EVENT:
      Fires every Sunday only at midnight.
      Multiplies XP awarded on kills (going into the field pool).
      Stacks additively with Lumnis (which affects absorption not gains).
      Auto-expires after bonus_xp_duration_hours.

    ANNOUNCEMENTS:
      Shown to players on login when an event is active.
      Also broadcast to all online players when an event starts.
--]]

local Config = {}

-- ── Gift of Lumnis ────────────────────────────────────────────────────────────

Config.lumnis = {
    -- Days of week to activate (1=Monday ... 6=Saturday, 7=Sunday  per Lua os.date %w: 0=Sun,6=Sat)
    -- We handle this in Python with datetime.weekday(): 5=Sat, 6=Sun
    active_days      = { 5, 6 },   -- Saturday=5, Sunday=6

    -- Start hour (0-23, server local time). Midnight = 0.
    start_hour       = 0,

    -- Absorption multipliers per phase
    phase1_multiplier = 3,
    phase2_multiplier = 2,

    -- Bonus pool caps (XP absorbed at the boosted rate before dropping to next phase)
    -- Live GS4: 14600 / 7300.  Scaled x3 for this server.
    phase1_pool      = 43800,
    phase2_pool      = 21900,

    -- Login announcement (shown when player logs in while Lumnis is active)
    announce_login   = {
        "The silvery light of Lumnis shimmers through the ether.",
        "The Goddess smiles upon Elanthia this weekend!",
        "Your mind absorbs knowledge with extraordinary clarity.",
        "The Gift of Lumnis is underway!",
    },

    -- Broadcast when event starts (sent to all online players)
    announce_start   = "A soft, silvery luminescence fills the sky.  The Gift of Lumnis has descended upon Elanthia!  Your mind will absorb experience with extraordinary swiftness this weekend.",

    -- Phase transition messages (shown to the individual player)
    phase1_msg       = "The Gift of Lumnis empowers your learning — your mind absorbs experience at triple the normal rate!",
    phase2_msg       = "The first gift of Lumnis fades slightly.  Your mind continues to absorb experience at double the normal rate.",
    expired_msg      = "The Gift of Lumnis draws to a close.  Your mind returns to its normal pace of learning.",
}

-- ── Sunday Bonus XP Event ─────────────────────────────────────────────────────

Config.bonus_xp = {
    -- Day of week to activate (6=Sunday using datetime.weekday())
    active_days      = { 6 },   -- Sunday only

    -- Start hour (midnight)
    start_hour       = 0,

    -- Duration in hours before auto-expiry
    duration_hours   = 24,

    -- Kill XP multiplier (additive with Lumnis absorption bonus)
    -- 2 = double XP from kills on Sundays
    multiplier       = 2,

    -- Login announcement
    announce_login   = {
        "A surge of vital energy permeates the land.",
        "Creatures yield their secrets more freely today!",
        "You will earn bonus experience from every kill.",
        "The Sunday Bonus XP Event is underway!",
    },

    -- Broadcast when event starts
    announce_start   = "A surge of vital energy sweeps across Elanthia!  Creatures yield their secrets more freely today.  Bonus experience is now active for the next 24 hours!",

    -- Expiry broadcast
    announce_expired = "The surge of vital energy fades.  Experience gains return to their normal rate.",
}

-- ── Combined announcement (both events active simultaneously on Sunday) ───────

Config.combined_announce_login = {
    "The Gift of Lumnis shimmers in the air and vital energy surges through the land.",
    "The Goddess smiles upon Elanthia — and creatures yield their secrets more freely!",
    "Your mind absorbs knowledge swiftly, and every kill brings bonus experience.",
    "The Gift of Lumnis and the Sunday Bonus XP Event are both underway!",
}

return Config
