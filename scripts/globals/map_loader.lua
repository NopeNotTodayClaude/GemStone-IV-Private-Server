--[[
  map_loader.lua
  ──────────────
  Provides Lua-side access to the world map imported from the Lich JSON.

  All 36,452 rooms and 75,813 exits live in MySQL.  At server startup,
  Python's WorldManager.load_from_database() bulk-loads every room into
  the _rooms dict and registers three callbacks into the Lua runtime:

      _MAP_GET_ROOM(room_id)        → table  { id, zone_id, title, description,
                                               is_safe, is_supernode, is_indoor,
                                               lich_uid, location_name,
                                               terrain_type, climate }
      _MAP_GET_EXITS(room_id)       → array  { {direction, target_room_id,
                                               exit_verb, is_special}, ... }
      _MAP_FIND_BY_LICH(lich_uid)   → room_id (integer) or nil

  Lua scripts should require this module and call the helpers below rather
  than calling the raw _MAP_* globals directly.

  Usage:
      local Map = require("globals/map_loader")

      local room   = Map.get_room(1234)       -- room table or nil
      local exits  = Map.get_exits(1234)      -- list of exit tables
      local target = Map.get_exit(1234, "north") -- target room_id or nil
      local dirs   = Map.exit_list(1234)      -- { "north", "east", ... }
      local rid    = Map.find_by_lich(-9054)  -- room_id or nil
      local title  = Map.room_title(1234)
      local desc   = Map.room_desc(1234)
      local safe   = Map.is_safe(1234)
      local indoor = Map.is_indoor(1234)
      Map.look(1234)                          -- prints room to stdout (debug)
--]]

local Map = {}

-- ─── Internal guard ──────────────────────────────────────────────────────────
local function _check_cb(name)
    if type(_G[name]) ~= "function" then
        -- Python bridge not initialised yet; fail quietly
        return false
    end
    return true
end

-- ─── get_room(room_id) ───────────────────────────────────────────────────────
-- Returns a table of room data or nil if not found / bridge unavailable.
function Map.get_room(room_id)
    if not _check_cb("_MAP_GET_ROOM") then return nil end
    local ok, result = pcall(_MAP_GET_ROOM, tonumber(room_id))
    if not ok then return nil end
    return result
end

-- ─── get_exits(room_id) ──────────────────────────────────────────────────────
-- Returns an array of exit tables: { direction, target_room_id, exit_verb, is_special }
-- Returns empty table on failure.
function Map.get_exits(room_id)
    if not _check_cb("_MAP_GET_EXITS") then return {} end
    local ok, result = pcall(_MAP_GET_EXITS, tonumber(room_id))
    if not ok or type(result) ~= "table" then return {} end
    return result
end

-- ─── get_exit(room_id, direction) ────────────────────────────────────────────
-- Returns the target room_id for a given direction, or nil.
-- Accepts short aliases: n/s/e/w/ne/nw/se/sw/u/d
function Map.get_exit(room_id, direction)
    local aliases = {
        n="north", s="south", e="east", w="west",
        ne="northeast", nw="northwest", se="southeast", sw="southwest",
        u="up", d="down",
    }
    direction = aliases[direction] or direction

    local exits = Map.get_exits(room_id)
    for _, ex in ipairs(exits) do
        if ex.direction == direction then
            return ex.target_room_id
        end
    end
    return nil
end

-- ─── exit_list(room_id) ──────────────────────────────────────────────────────
-- Returns a plain list of direction strings for all exits in a room.
function Map.exit_list(room_id)
    local exits = Map.get_exits(room_id)
    local dirs = {}
    for _, ex in ipairs(exits) do
        table.insert(dirs, ex.direction)
    end
    table.sort(dirs)
    return dirs
end

-- ─── find_by_lich(lich_uid) ──────────────────────────────────────────────────
-- Looks up a room by its original Lich map UID (can be negative).
-- Returns room_id integer or nil.
function Map.find_by_lich(lich_uid)
    if not _check_cb("_MAP_FIND_BY_LICH") then return nil end
    local ok, result = pcall(_MAP_FIND_BY_LICH, tonumber(lich_uid))
    if not ok then return nil end
    return result
end

-- ─── room_title(room_id) ─────────────────────────────────────────────────────
function Map.room_title(room_id)
    local r = Map.get_room(room_id)
    return r and r.title or "Unknown Location"
end

-- ─── room_desc(room_id) ──────────────────────────────────────────────────────
function Map.room_desc(room_id)
    local r = Map.get_room(room_id)
    return r and r.description or ""
end

-- ─── is_safe(room_id) ────────────────────────────────────────────────────────
function Map.is_safe(room_id)
    local r = Map.get_room(room_id)
    if not r then return false end
    return r.is_safe == 1 or r.is_safe == true
end

-- ─── is_indoor(room_id) ──────────────────────────────────────────────────────
function Map.is_indoor(room_id)
    local r = Map.get_room(room_id)
    if not r then return false end
    return r.is_indoor == 1 or r.is_indoor == true
        or r.indoor == 1 or r.indoor == true
end

-- ─── is_supernode(room_id) ───────────────────────────────────────────────────
-- Supernodes are mana-rich nodes in GemStone IV.
function Map.is_supernode(room_id)
    local r = Map.get_room(room_id)
    if not r then return false end
    return r.is_supernode == 1 or r.is_supernode == true
end

-- ─── terrain(room_id) ────────────────────────────────────────────────────────
function Map.terrain(room_id)
    local r = Map.get_room(room_id)
    return r and r.terrain_type or "urban"
end

-- ─── climate(room_id) ────────────────────────────────────────────────────────
function Map.climate(room_id)
    local r = Map.get_room(room_id)
    return r and r.climate or ""
end

-- ─── lich_uid(room_id) ───────────────────────────────────────────────────────
function Map.lich_uid(room_id)
    local r = Map.get_room(room_id)
    return r and r.lich_uid or nil
end

-- ─── exits_text(room_id) ─────────────────────────────────────────────────────
-- Returns the canonical GS4-style exit line, e.g. "Obvious exits: north, east"
function Map.exits_text(room_id)
    local dirs  = Map.exit_list(room_id)
    local label = Map.is_indoor(room_id) and "Obvious exits" or "Obvious paths"
    if #dirs == 0 then
        return label .. ": none"
    end
    return label .. ": " .. table.concat(dirs, ", ")
end

-- ─── look(room_id) ───────────────────────────────────────────────────────────
-- Debug helper: prints room title, description, exits to Lua stdout.
function Map.look(room_id)
    local r = Map.get_room(room_id)
    if not r then
        print("[MapLoader] Room " .. tostring(room_id) .. " not found.")
        return
    end
    print("[" .. r.title .. "]")
    print(r.description)
    print(Map.exits_text(room_id))
end

-- ─── zone_name(room_id) ──────────────────────────────────────────────────────
-- Returns the location_name string stored with the room (GS4 area label).
function Map.zone_name(room_id)
    local r = Map.get_room(room_id)
    return r and r.location_name or ""
end

return Map
