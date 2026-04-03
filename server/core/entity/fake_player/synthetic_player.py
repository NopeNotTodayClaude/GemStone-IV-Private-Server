"""
synthetic_player.py
-------------------
Lightweight player-like actor used by the fake-player population manager.
These actors are visible in rooms and can use player-adjacent systems without
being real login sessions.
"""

from __future__ import annotations

import time


class SyntheticPlayer:
    def __init__(self, manager, row: dict):
        self.manager = manager
        self.server = manager.server
        self.is_synthetic_player = True

        self.synthetic_id = int(row.get("id") or 0)
        self.character_id = int(row.get("character_id") or 0)
        self.character_name = str(row.get("character_name") or "Someone")
        self.race_id = int(row.get("race_id") or 1)
        self.race = str(row.get("race_name") or "Human")
        self.profession_id = int(row.get("profession_id") or 1)
        self.profession = str(row.get("profession_name") or "Warrior")
        self.profession_name = self.profession
        self.gender = str(row.get("gender") or "male")
        self.age = int(row.get("age") or 20)
        self.level = int(row.get("level") or 1)

        self.mbti = str(row.get("mbti") or "ISTJ").upper()
        self.archetype = str(row.get("archetype") or "town_regular").strip().lower()
        self.home_region_key = str(row.get("home_region_key") or "").strip().lower()
        self.home_room_id = int(row.get("home_room_id") or 0)

        self.state = "playing"
        self.connected = True
        self.connect_time = time.time()
        self.last_input_time = self.connect_time
        self.last_save_time = self.connect_time

        self.current_room = None
        self.previous_room = None
        self.current_room_id = int(row.get("current_room_id") or 0)

        self.level_target = int(row.get("level_target") or self.level or 1)
        self.health_max = int(row.get("health_max") or max(35, 85 + self.level * 8))
        self.health_current = int(row.get("health_current") or self.health_max)
        self.mana_max = int(row.get("mana_max") or max(0, self.level * 2))
        self.mana_current = int(row.get("mana_current") or self.mana_max)
        self.spirit_max = int(row.get("spirit_max") or 10)
        self.spirit_current = int(row.get("spirit_current") or self.spirit_max)
        self.stamina_max = int(row.get("stamina_max") or max(70, 80 + self.level * 3))
        self.stamina_current = int(row.get("stamina_current") or self.stamina_max)

        self.silver = int(row.get("silver") or 0)
        self.bank_silver = 0
        self.experience = int(row.get("experience") or 0)
        self.field_experience = int(row.get("field_experience") or 0)

        self.position = str(row.get("position") or "standing")
        self.stance = str(row.get("stance") or "neutral").lower()
        self.hidden = bool(row.get("hidden") or False)
        self.sneaking = bool(row.get("sneaking") or False)
        self.invisible = False

        self.in_combat = bool(row.get("in_combat") or False)
        self.target = None
        self.roundtime_end = float(row.get("roundtime_end") or 0.0)
        self.aimed_location = row.get("aimed_location")

        self.is_dead = bool(row.get("is_dead") or False)
        self.death_choice_pending = False
        self.death_room_id = int(row.get("death_room_id") or 0)
        self.death_stat_mult = float(row.get("death_stat_mult") or 1.0)
        self.temporal_rift_room_id = None
        self.temporal_rift_release_at = 0

        self.inventory = list(row.get("inventory") or [])
        self.right_hand = row.get("right_hand")
        self.left_hand = row.get("left_hand")
        self.ready_ammo_inv_id = None
        self.ready_ammo_type = None
        self.ready_ammo_name = None

        self.skills = dict(row.get("skills") or {})
        self.injuries = dict(row.get("injuries") or {})
        self.status_effects = dict(row.get("status_effects") or {})
        self.wounds = dict(row.get("wounds") or {})

        self.synthetic_flags = dict(row.get("state_json") or {})
        self.stat_strength = int(row.get("stat_strength") or 70)
        self.stat_constitution = int(row.get("stat_constitution") or 70)
        self.stat_dexterity = int(row.get("stat_dexterity") or 70)
        self.stat_agility = int(row.get("stat_agility") or 70)
        self.stat_discipline = int(row.get("stat_discipline") or 70)
        self.stat_aura = int(row.get("stat_aura") or 70)
        self.stat_logic = int(row.get("stat_logic") or 70)
        self.stat_intuition = int(row.get("stat_intuition") or 70)
        self.stat_wisdom = int(row.get("stat_wisdom") or 70)
        self.stat_influence = int(row.get("stat_influence") or 70)
        self.reaction_triggers = {}
        self.hotbar_slots = {}
        self.guild_membership = None
        self.guild_skills = {}
        self.guild_tasks = []
        self.unlocks = {}
        self.active_spells = {}
        self.spell_ranks = {}
        self.spellbook = []
        self.tutorial_complete = True
        self.tutorial_stage = 999
        self.pet_progress = dict(self.synthetic_flags.get("pet_progress") or {})
        self.pets = list(self.synthetic_flags.get("pets") or [])
        self.active_pet = dict(self.synthetic_flags.get("active_pet") or {}) or None

    @property
    def display_name(self) -> str:
        return self.character_name

    async def send(self, text):
        del text
        return

    async def send_line(self, text=""):
        del text
        return

    async def send_prompt(self):
        return

    def get_roundtime(self):
        remaining = self.roundtime_end - time.time()
        return max(0, int(remaining))

    def set_roundtime(self, seconds):
        self.roundtime_end = time.time() + float(seconds or 0)

    def disconnect(self):
        self.connected = False

    def to_state_row(self) -> dict:
        room_id = int(getattr(getattr(self, "current_room", None), "id", 0) or self.current_room_id or 0)
        state_json = dict(self.synthetic_flags or {})
        state_json["pet_progress"] = dict(self.pet_progress or {})
        state_json["pets"] = list(self.pets or [])
        state_json["active_pet"] = dict(self.active_pet or {}) if self.active_pet else None
        return {
            "id": self.synthetic_id,
            "character_id": self.character_id,
            "character_name": self.character_name,
            "race_id": self.race_id,
            "race_name": self.race,
            "profession_id": self.profession_id,
            "profession_name": self.profession,
            "gender": self.gender,
            "age": self.age,
            "level": self.level,
            "level_target": self.level_target,
            "mbti": self.mbti,
            "archetype": self.archetype,
            "home_region_key": self.home_region_key,
            "home_room_id": self.home_room_id,
            "current_room_id": room_id,
            "health_current": self.health_current,
            "health_max": self.health_max,
            "mana_current": self.mana_current,
            "mana_max": self.mana_max,
            "spirit_current": self.spirit_current,
            "spirit_max": self.spirit_max,
            "stamina_current": self.stamina_current,
            "stamina_max": self.stamina_max,
            "silver": self.silver,
            "experience": self.experience,
            "field_experience": self.field_experience,
            "position": self.position,
            "stance": self.stance,
            "hidden": 1 if self.hidden else 0,
            "sneaking": 1 if self.sneaking else 0,
            "in_combat": 1 if self.in_combat else 0,
            "is_dead": 1 if self.is_dead else 0,
            "death_room_id": int(getattr(self, "death_room_id", 0) or 0),
            "death_stat_mult": self.death_stat_mult,
            "roundtime_end": self.roundtime_end,
            "stat_strength": self.stat_strength,
            "stat_constitution": self.stat_constitution,
            "stat_dexterity": self.stat_dexterity,
            "stat_agility": self.stat_agility,
            "stat_discipline": self.stat_discipline,
            "stat_aura": self.stat_aura,
            "stat_logic": self.stat_logic,
            "stat_intuition": self.stat_intuition,
            "stat_wisdom": self.stat_wisdom,
            "stat_influence": self.stat_influence,
            "inventory": list(self.inventory or []),
            "right_hand": self.right_hand,
            "left_hand": self.left_hand,
            "skills": dict(self.skills or {}),
            "injuries": dict(self.injuries or {}),
            "status_effects": dict(self.status_effects or {}),
            "wounds": dict(self.wounds or {}),
            "state_json": state_json,
        }

    def __repr__(self):
        return f"SyntheticPlayer({self.synthetic_id}, {self.character_name}, room={self.current_room_id})"
