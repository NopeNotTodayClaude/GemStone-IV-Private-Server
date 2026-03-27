------------------------------------------------------------------------
-- scripts/npcs/npc_base.lua
-- GemStone IV NPC Base Template
--
-- Every NPC Lua file follows this structure.  Copy this file, rename it,
-- fill in what you need, delete what you don't.
--
-- CAPABILITY FLAGS — set the ones your NPC uses to true:
--   can_combat    NPC can fight (uses combat engine, has HP/AS/DS)
--   can_shop      NPC has a shop (shop_id links to npc_shop_inventory)
--   can_wander    NPC moves between rooms on a timer
--   can_emote     NPC fires random ambient emotes
--   can_chat      NPC broadcasts random lines to the room
--   can_loot      NPC picks up silver/gems/items from dead mobs
--   is_guild      NPC manages a guild rank system
--   is_quest      NPC has quest hooks (on_player_talk, etc.)
--   is_house      NPC manages player housing
--   is_bot        NPC acts as a fake player (all of the above)
--   is_invasion   NPC participates in / triggers invasion events
--
-- HOOKS — define these functions to add behavior.
-- All hooks are optional.  Undefined hooks are silently skipped.
--
--   NPC:on_load()                 Server start / NPC spawn
--   NPC:on_player_enter(player)   A player enters the NPC's current room
--   NPC:on_player_talk(player, keyword)  Player says something to the NPC
--   NPC:on_combat_start(target)   NPC enters combat
--   NPC:on_combat_victory(target) NPC kills its target
--   NPC:on_death()                NPC is killed
--   NPC:on_tick()                 Once per NPC tick (use sparingly)
--   NPC:on_invasion(zone)         An invasion event starts in NPC's zone
--   NPC:on_loot(item, room)       NPC finds loot on the ground
--   NPC:on_guild_rank_up(player, new_rank)  Player advances in guild
--
------------------------------------------------------------------------

local NPC = {}

-- ── Identity ──────────────────────────────────────────────────────────────────
NPC.template_id    = "npc_base"           -- UNIQUE identifier (snake_case, no spaces)
NPC.name           = "an unnamed NPC"     -- Display name
NPC.article        = "an"                 -- "a" / "an" / "" (for proper names)
NPC.title          = ""                   -- Shown after name: "Sorvael the gate warden"
NPC.description    = "You see nothing unusual."
NPC.home_room_id   = 0                    -- Room where this NPC starts / respawns

-- ── Capabilities ─────────────────────────────────────────────────────────────
NPC.can_combat     = false
NPC.can_shop       = false
NPC.can_wander     = false
NPC.can_emote      = false
NPC.can_chat       = false
NPC.can_loot       = false
NPC.is_guild       = false
NPC.is_quest       = false
NPC.is_house       = false
NPC.is_bot         = false
NPC.is_invasion    = false

-- ── Combat stats (required if can_combat = true) ──────────────────────────────
NPC.level          = 1
NPC.hp             = 100
NPC.as_melee       = 50
NPC.ds_melee       = 30
NPC.ds_ranged      = 20
NPC.td             = 10
NPC.armor_asg      = 5       -- matches creature armor system (1=none → 20=full plate)
NPC.body_type      = "biped"
NPC.aggressive     = false   -- attacks players on sight
NPC.unkillable     = false   -- cannot be killed (set for lore NPCs)
NPC.respawn_seconds = 600    -- seconds to respawn after death (0 = never)

NPC.attacks = {
    -- { type = "broadsword", as = 80, damage_type = "slash" },
    -- { type = "bite",       as = 60, damage_type = "puncture" },
}

-- ── Shop (required if can_shop = true) ───────────────────────────────────────
NPC.shop_id        = nil     -- links to npc_shop_inventory.template_id in DB

-- ── Wander / patrol (required if can_wander = true) ──────────────────────────
NPC.patrol_rooms   = {}      -- list of room IDs to patrol in order
NPC.wander_chance  = 0.2     -- 0.0-1.0, checked each move_interval
NPC.move_interval  = 30      -- seconds between move checks

-- ── Shift system (gate guards etc.) ──────────────────────────────────────────
NPC.shift_id       = nil     -- e.g. "amaranth" — groups primary+relief pair
NPC.shift_phase    = 0       -- 0 = primary (spawns at start), 1 = relief
NPC.spawn_at_start = true    -- false = only spawns on first shift change

-- ── Rare / conditional spawn ──────────────────────────────────────────────────
NPC.rare_spawn     = false
NPC.spawn_chance   = 1.0     -- 0.0-1.0; only used when rare_spawn = true

-- ── Dialogue ──────────────────────────────────────────────────────────────────
-- Keywords are lowercased. "default" is the fallback.
-- {player} is replaced with the player's name at runtime.
NPC.dialogues = {
    default = "The NPC doesn't seem to be listening.",
}
NPC.greeting       = nil     -- String shown to player who enters the room, or nil

-- ── Ambient emotes (used if can_emote = true) ─────────────────────────────────
NPC.ambient_emotes = {}      -- List of strings; {name} replaced with NPC.name
NPC.ambient_chance = 0.03    -- 0.0-1.0; checked every 5 seconds
NPC.emote_cooldown = 45      -- minimum seconds between emotes

-- ── Chat lines (used if can_chat = true) ──────────────────────────────────────
-- Broadcast to the room as NPC speech, not targeted at any player.
NPC.chat_lines     = {}
NPC.chat_interval  = 120     -- seconds between random chat lines
NPC.chat_chance    = 0.12    -- chance to speak each 5s tick once chat_interval has elapsed

-- ── Loot config (used if can_loot = true) ─────────────────────────────────────
NPC.loot_silver    = true
NPC.loot_gems      = false
NPC.loot_items     = false
NPC.loot_radius    = 1       -- 0 = current room only, 1 = adjacent rooms too

-- ── Guild config (used if is_guild = true) ────────────────────────────────────
NPC.guild_id       = nil     -- matches npc_guild_ranks.guild_id in DB

-- ── Bot behavior (used if is_bot = true) ──────────────────────────────────────
-- Bot NPCs act as fake players: hunt, chat, buy/sell, emote.
-- These settings tune that behavior.
NPC.bot_hunt       = false   -- actively seeks and fights creatures
NPC.bot_hunt_rooms = {}      -- rooms the bot is allowed to hunt in
NPC.bot_rest_room  = 0       -- room to return to when injured
NPC.bot_hp_flee    = 0.25    -- flee to rest room when HP drops below this %
NPC.bot_chat_world = false   -- can broadcast to world/zone chat channels

-- ── Invasion config (used if is_invasion = true) ──────────────────────────────
NPC.invasion_zone  = nil     -- zone_slug this NPC is associated with
NPC.invasion_side  = "enemy" -- "enemy" = fights players; "ally" = fights with players

-- ── Hooks ─────────────────────────────────────────────────────────────────────
-- Delete the ones you don't use. Defined as no-ops here so nothing breaks
-- if a partially implemented NPC is loaded.

function NPC:on_load()
    -- Called when the server starts and the NPC is registered.
end

function NPC:on_player_enter(player)
    -- Called when a player enters the NPC's current room.
    -- player: player API object
end

function NPC:on_player_talk(player, keyword)
    -- Called when a player says something to this NPC.
    -- Return a string to send as the NPC's response, or nil to use dialogues{}.
    return nil
end

function NPC:on_combat_start(target)
    -- Called when the NPC enters combat.
    -- target: the entity being attacked
end

function NPC:on_combat_victory(target)
    -- Called when the NPC kills its target.
end

function NPC:on_death()
    -- Called when the NPC dies.
end

function NPC:on_tick()
    -- Called every NPC tick. Use sparingly — this runs for every NPC.
    -- Prefer hooks over on_tick when possible.
end

function NPC:on_invasion(zone)
    -- Called when an invasion event starts in this NPC's zone.
    -- zone: zone slug string
end

function NPC:on_loot(item, room)
    -- Called when the NPC finds a lootable item on the ground.
    -- Return true to pick it up, false to leave it.
    return self.can_loot
end

function NPC:on_guild_rank_up(player, new_rank)
    -- Called when a player advances a rank in this NPC's guild.
end

return NPC
