"""
Database manager - handles all MariaDB operations.
Character persistence, account management, auto-save.
"""

import logging
import json
import datetime
from decimal import Decimal
import mysql.connector
from mysql.connector import pooling
import bcrypt
import time

log = logging.getLogger(__name__)


def _json_safe_snapshot(value):
    """Normalize common DB/python values before storing item snapshots as JSON."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, dict):
        return {str(k): _json_safe_snapshot(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe_snapshot(v) for v in value]
    return value


class Database:
    """Manages all database connections and queries."""

    def __init__(self, config):
        self.config = config
        self._pool = None

    def connect(self):
        """Initialize the connection pool."""
        try:
            db_config = {
                "host": self.config.get("database.development.host", "127.0.0.1"),
                "port": self.config.get("database.development.port", 3306),
                "database": self.config.get("database.development.database", "gemstone_dev"),
                "user": self.config.get("database.development.username", "gemstone"),
                "password": self.config.get("database.development.password", "gemstone_dev"),
                "charset": "utf8mb4",
                "autocommit": True,
            }
            self._pool = pooling.MySQLConnectionPool(
                pool_name="gemstone_pool",
                pool_size=10,
                **db_config
            )
            log.info("Database connection pool established.")
            return True
        except Exception as e:
            # Fallback: try root with no password (dev mode)
            try:
                db_config = {
                    "host": "127.0.0.1",
                    "port": 3306,
                    "database": "gemstone_dev",
                    "user": "root",
                    "password": "",
                    "charset": "utf8mb4",
                    "autocommit": True,
                }
                self._pool = pooling.MySQLConnectionPool(
                    pool_name="gemstone_pool",
                    pool_size=10,
                    **db_config
                )
                log.info("Database connected (root fallback mode).")
                return True
            except Exception as e2:
                log.error("Database connection failed: %s", e2)
                return False

    def _get_conn(self):
        return self._pool.get_connection()

    # =========================================================
    # ACCOUNT OPERATIONS
    # =========================================================

    def create_account(self, username, password, email=None):
        """Create a new account. Returns account_id or None."""
        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO accounts (username, password_hash, email) VALUES (%s, %s, %s)",
                (username, pw_hash, email)
            )
            account_id = cur.lastrowid
            log.info("Account created: %s (id=%d)", username, account_id)
            return account_id
        except mysql.connector.IntegrityError:
            log.warning("Account creation failed: username '%s' already exists", username)
            return None
        finally:
            conn.close()

    def authenticate(self, username, password):
        """Authenticate login. Returns account dict or None."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM accounts WHERE username = %s", (username,))
            account = cur.fetchone()
            if not account:
                return None
            if account.get("is_banned"):
                return "banned"
            if bcrypt.checkpw(password.encode("utf-8"), account["password_hash"].encode("utf-8")):
                # Update last login
                cur.execute("UPDATE accounts SET last_login = NOW() WHERE id = %s", (account["id"],))
                return account
            return None
        finally:
            conn.close()

    def get_characters_for_account(self, account_id):
        """Get all characters belonging to an account."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, name, race_id, profession_id, level, current_room_id "
                "FROM characters WHERE account_id = %s ORDER BY name",
                (account_id,)
            )
            return cur.fetchall()
        finally:
            conn.close()

    # =========================================================
    # CHARACTER OPERATIONS
    # =========================================================

    def create_character(self, account_id, char_data):
        """
        Create a new character. char_data is a dict with all fields.
        Returns character_id or None.
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO characters (
                    account_id, name, race_id, profession_id, gender,
                    culture_key,
                    stat_strength, stat_constitution, stat_dexterity, stat_agility,
                    stat_discipline, stat_aura, stat_logic, stat_intuition,
                    stat_wisdom, stat_influence,
                    health_max, health_current, mana_max, mana_current,
                    spirit_max, spirit_current, stamina_max, stamina_current,
                    current_room_id, starting_room_id, height, hair_color, hair_style, eye_color,
                    skin_tone, age
                ) VALUES (
                    %(account_id)s, %(name)s, %(race_id)s, %(profession_id)s, %(gender)s,
                    %(culture_key)s,
                    %(strength)s, %(constitution)s, %(dexterity)s, %(agility)s,
                    %(discipline)s, %(aura)s, %(logic)s, %(intuition)s,
                    %(wisdom)s, %(influence)s,
                    %(health_max)s, %(health_max)s, %(mana_max)s, %(mana_max)s,
                    %(spirit_max)s, %(spirit_max)s, %(stamina_max)s, %(stamina_max)s,
                    %(starting_room)s, %(starting_room)s, %(height)s, %(hair_color)s, %(hair_style)s,
                    %(eye_color)s, %(skin_tone)s, %(age)s
                )
            """, {
                **char_data,
                "account_id":  account_id,
                "culture_key": char_data.get("culture_key"),
                "skin_tone":   char_data.get("skin_tone", "fair"),
                "age":         char_data.get("age"),
            })
            char_id = cur.lastrowid
            log.info("Character created: %s (id=%d)", char_data.get("name"), char_id)
            return char_id
        except mysql.connector.IntegrityError as e:
            log.warning("Character creation failed: %s", e)
            return None
        finally:
            conn.close()

    def load_character(self, character_id):
        """Load full character data from DB."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM characters WHERE id = %s", (character_id,))
            char = cur.fetchone()
            if char:
                # Also load skills
                cur.execute(
                    "SELECT skill_id, ranks, bonus, ranks_this_level FROM character_skills WHERE character_id = %s",
                    (character_id,)
                )
                char["skills"] = {row["skill_id"]: row for row in cur.fetchall()}
                cur.execute(
                    "SELECT spell_id, duration_remaining FROM character_spells_active WHERE character_id = %s",
                    (character_id,)
                )
                char["active_spells"] = {row["spell_id"]: row["duration_remaining"] for row in cur.fetchall()}
                cur.execute("""
                    SELECT cgm.*, gd.name AS guild_name, gd.profession_id AS guild_profession_id,
                           gd.support_level, gd.monthly_dues, gd.initiation_fee,
                           gd.join_level, gd.max_prepay_months, gd.has_skill_training,
                           gd.progression_multiplier,
                           gd.has_guildmaster, grd.rank_name
                    FROM character_guild_membership cgm
                    JOIN guild_definitions gd ON gd.guild_id = cgm.guild_id
                    LEFT JOIN guild_rank_definitions grd
                      ON grd.guild_id = cgm.guild_id AND grd.rank_level = cgm.rank_level
                    WHERE cgm.character_id = %s AND cgm.status = 'active'
                    ORDER BY cgm.joined_at DESC
                    LIMIT 1
                """, (character_id,))
                membership = cur.fetchone()
                char["guild_membership"] = membership

                if membership:
                    guild_id = membership["guild_id"]
                    cur.execute("""
                        SELECT skill_name, ranks, training_points, is_mastered, last_trained_at
                        FROM character_guild_skills
                        WHERE character_id = %s AND guild_id = %s
                        ORDER BY skill_name
                    """, (character_id, guild_id))
                    char["guild_skills"] = {
                        row["skill_name"]: row for row in cur.fetchall()
                    }
                    cur.execute("""
                        SELECT id, skill_name, task_code, task_type, task_text,
                               objective_event, target_count, progress_count, award_points,
                               repetitions_remaining, task_data, status,
                               assigned_at, completed_at
                        FROM character_guild_tasks
                        WHERE character_id = %s AND guild_id = %s AND status IN ('assigned', 'ready')
                        ORDER BY assigned_at DESC
                    """, (character_id, guild_id))
                    char["guild_tasks"] = cur.fetchall()
                else:
                    char["guild_skills"] = {}
                    char["guild_tasks"] = []

            return char
        finally:
            conn.close()

    def load_character_by_name(self, name):
        """Load character by name."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM characters WHERE name = %s", (name,))
            char = cur.fetchone()
            if char:
                cur.execute(
                    "SELECT skill_id, ranks, bonus, ranks_this_level FROM character_skills WHERE character_id = %s",
                    (char["id"],)
                )
                char["skills"] = {row["skill_id"]: row for row in cur.fetchall()}
            return char
        finally:
            conn.close()

    def save_character(self, session):
        """
        Save character state to database.
        Called on auto-save, logout, and server shutdown.
        """
        if not session.character_id:
            return False

        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE characters SET
                    level = %(level)s,
                    experience = %(experience)s,
                    field_experience = %(field_experience)s,
                    health_current = %(health_current)s,
                    health_max = %(health_max)s,
                    mana_current = %(mana_current)s,
                    mana_max = %(mana_max)s,
                    spirit_current = %(spirit_current)s,
                    spirit_max = %(spirit_max)s,
                    stamina_current = %(stamina_current)s,
                    stamina_max = %(stamina_max)s,
                    physical_tp = %(physical_tp)s,
                    mental_tp = %(mental_tp)s,
                    silver = %(silver)s,
                    bank_silver = %(bank_silver)s,
                    fame = %(fame)s,
                    fame_list_opt_in = %(fame_list_opt_in)s,
                    current_room_id = %(current_room_id)s,
                    starting_room_id = COALESCE(%(starting_room_id)s, starting_room_id),
                    position = %(position)s,
                    stance = %(stance)s,
                    tutorial_stage = %(tutorial_stage)s,
                    tutorial_complete = %(tutorial_complete)s,
                    aimed_location = %(aimed_location)s,
                    total_playtime = total_playtime + %(session_time)s,
                    last_login = NOW()
                WHERE id = %(character_id)s
            """, {
                "level": getattr(session, "level", 1),
                "experience": getattr(session, "experience", 0),
                "field_experience": getattr(session, "field_experience", 0),
                "health_current": getattr(session, "health_current", 100),
                "health_max": getattr(session, "health_max", 100),
                "mana_current": getattr(session, "mana_current", 0),
                "mana_max": getattr(session, "mana_max", 0),
                "spirit_current": getattr(session, "spirit_current", 10),
                "spirit_max": getattr(session, "spirit_max", 10),
                "stamina_current": getattr(session, "stamina_current", 100),
                "stamina_max": getattr(session, "stamina_max", 100),
                "physical_tp": getattr(session, "physical_tp", 0),
                "mental_tp": getattr(session, "mental_tp", 0),
                "silver": getattr(session, "silver", 0),
                "bank_silver": getattr(session, "bank_silver", 0),
                "fame": getattr(session, "fame", 0),
                "fame_list_opt_in": 1 if getattr(session, "fame_list_opt_in", False) else 0,
                "current_room_id": session.current_room.id if session.current_room else 100,
                "starting_room_id": getattr(session, "starting_room_id", None),
                "position": session.position,
                "stance": getattr(session, "stance", "neutral"),
                "tutorial_stage": getattr(session, "tutorial_stage", 0),
                "tutorial_complete": 1 if getattr(session, "tutorial_complete", False) else 0,
                "aimed_location": getattr(session, "aimed_location", None),
                "session_time": int(time.time() - session.connect_time),
                "character_id": session.character_id,
            })
            return True
        except Exception as e:
            log.error("Failed to save character %s: %s", session.character_name, e)
            return False
        finally:
            conn.close()

    def save_all_characters(self, sessions):
        """Save all playing sessions. Used for auto-save and shutdown."""
        saved = 0
        for session in sessions:
            if session.state == "playing" and session.character_id:
                if self.save_character(session):
                    saved += 1
        return saved

    def character_name_exists(self, name):
        """Check if a character name is already taken."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM characters WHERE name = %s", (name,))
            return cur.fetchone()[0] > 0
        finally:
            conn.close()

    # =========================================================
    # REAL-TIME SAVE METHODS
    # =========================================================

    def save_quest_progress(self, character_id, tutorial_stage, tutorial_complete):
        """Save tutorial/quest progress immediately to database."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE characters SET
                    tutorial_stage = %s,
                    tutorial_complete = %s
                WHERE id = %s
            """, (tutorial_stage, 1 if tutorial_complete else 0, character_id))
            return True
        except Exception as e:
            log.error("Failed to save quest progress for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_character_room(self, character_id, room_id):
        """Save character's current room immediately to database."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE characters SET current_room_id = %s WHERE id = %s",
                (room_id, character_id)
            )
            return True
        except Exception as e:
            log.error("Failed to save room for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_character_resources(self, character_id, health, mana, spirit, stamina, silver):
        """Save character resources immediately to database."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE characters SET
                    health_current = %s, mana_current = %s,
                    spirit_current = %s, stamina_current = %s,
                    silver = %s
                WHERE id = %s
            """, (health, mana, spirit, stamina, silver, character_id))
            return True
        except Exception as e:
            log.error("Failed to save resources for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_character_experience(self, character_id, level, experience, field_experience):
        """Save character experience/level immediately to database."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE characters SET
                    level = %s, experience = %s, field_experience = %s
                WHERE id = %s
            """, (level, experience, field_experience, character_id))
            return True
        except Exception as e:
            log.error("Failed to save experience for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_character_fame(self, character_id, fame, fame_list_opt_in=None):
        """Save character fame and optional fame-list preference immediately."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if fame_list_opt_in is None:
                cur.execute(
                    "UPDATE characters SET fame = %s WHERE id = %s",
                    (fame, character_id)
                )
            else:
                cur.execute(
                    "UPDATE characters SET fame = %s, fame_list_opt_in = %s WHERE id = %s",
                    (fame, 1 if fame_list_opt_in else 0, character_id)
                )
            return True
        except Exception as e:
            log.error("Failed to save fame for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def add_character_fame(self, character_id, amount, source_key, detail_text=None):
        """Increment fame and append a ledger row. Returns new fame total or None."""
        if amount == 0:
            return self.get_character_fame(character_id)
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE characters SET fame = GREATEST(0, fame + %s) WHERE id = %s",
                (amount, character_id)
            )
            cur.execute(
                "INSERT INTO character_fame_ledger (character_id, amount, source_key, detail_text) VALUES (%s, %s, %s, %s)",
                (character_id, amount, source_key, detail_text)
            )
            cur.execute("SELECT fame FROM characters WHERE id = %s", (character_id,))
            row = cur.fetchone()
            conn.commit()
            return int(row[0]) if row else None
        except Exception as e:
            log.error("Failed to add fame for char %s: %s", character_id, e)
            return None
        finally:
            conn.close()

    def get_character_fame(self, character_id):
        """Return one character's current fame total."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT fame FROM characters WHERE id = %s", (character_id,))
            row = cur.fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()

    def get_character_by_name_basic(self, name):
        """Return lightweight row for fame/lookups by character name."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT id, name, level, race_id, profession_id, fame, fame_list_opt_in
                FROM characters
                WHERE name = %s
                LIMIT 1
            """, (name,))
            return cur.fetchone()
        finally:
            conn.close()

    def get_visible_fame_rows(self):
        """Return the top 1000 public fame rows in retail-style sort order."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT id, name, fame, level, gender, race_id, profession_id
                FROM characters
                WHERE fame_list_opt_in = 1
                ORDER BY fame DESC, level DESC, name ASC
                LIMIT 1000
            """)
            return cur.fetchall()
        finally:
            conn.close()

    # =========================================================
    # ADVENTURER'S GUILD / BOUNTIES
    # =========================================================

    def get_character_adventurer_guild(self, character_id):
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT *
                FROM character_adventurer_guild
                WHERE character_id = %s
                LIMIT 1
                """,
                (character_id,),
            )
            return cur.fetchone()
        except Exception as e:
            log.error("Failed to load Adventurer's Guild profile for char %s: %s", character_id, e)
            return None
        finally:
            conn.close()

    def ensure_character_adventurer_guild(self, character_id, town_name=None):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO character_adventurer_guild (
                    character_id, registered_town_name, rank_level, rank_title, rank_points, lifetime_bounties
                ) VALUES (%s, %s, 1, 'Associate', 0, 0)
                ON DUPLICATE KEY UPDATE
                    registered_town_name = COALESCE(registered_town_name, VALUES(registered_town_name)),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (character_id, town_name),
            )
            conn.commit()
        except Exception as e:
            log.error("Failed to ensure Adventurer's Guild profile for char %s: %s", character_id, e)
            return None
        finally:
            conn.close()
        return self.get_character_adventurer_guild(character_id)

    def update_character_adventurer_guild(self, character_id, *, town_name=None, rank_level=None,
                                          rank_title=None, rank_points=None, lifetime_bounties=None):
        profile = self.ensure_character_adventurer_guild(character_id, town_name=town_name)
        if not profile:
            return None
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_adventurer_guild
                SET registered_town_name = COALESCE(%s, registered_town_name),
                    rank_level = COALESCE(%s, rank_level),
                    rank_title = COALESCE(%s, rank_title),
                    rank_points = COALESCE(%s, rank_points),
                    lifetime_bounties = COALESCE(%s, lifetime_bounties),
                    updated_at = CURRENT_TIMESTAMP
                WHERE character_id = %s
                """,
                (town_name, rank_level, rank_title, rank_points, lifetime_bounties, character_id),
            )
            if rank_points is not None:
                try:
                    cur.execute(
                        "UPDATE characters SET bounty_points = %s WHERE id = %s",
                        (int(rank_points), character_id),
                    )
                except Exception:
                    pass
            conn.commit()
        except Exception as e:
            log.error("Failed to update Adventurer's Guild profile for char %s: %s", character_id, e)
            return None
        finally:
            conn.close()
        return self.get_character_adventurer_guild(character_id)

    def get_character_bounty(self, character_id, *, include_completed=True):
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            statuses = ("active", "completed") if include_completed else ("active",)
            placeholders = ", ".join(["%s"] * len(statuses))
            cur.execute(
                f"""
                SELECT *
                FROM character_bounties
                WHERE character_id = %s
                  AND status IN ({placeholders})
                  AND (expires_at IS NULL OR expires_at >= NOW())
                ORDER BY id DESC
                LIMIT 1
                """,
                (character_id, *statuses),
            )
            return cur.fetchone()
        except Exception as e:
            log.error("Failed to load active bounty for char %s: %s", character_id, e)
            return None
        finally:
            conn.close()

    def expire_character_bounties(self, character_id):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_bounties
                SET status = 'expired'
                WHERE character_id = %s
                  AND status IN ('active', 'completed')
                """,
                (character_id,),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to expire bounty rows for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def assign_character_bounty(self, character_id, bounty_row, *, town_name=None,
                                taskmaster_template_id=None, taskmaster_room_id=None, expires_hours=72):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_bounties
                SET status = 'expired'
                WHERE character_id = %s
                  AND status IN ('active', 'completed')
                """,
                (character_id,),
            )
            cur.execute(
                """
                INSERT INTO character_bounties (
                    character_id, bounty_type, target, target_count, current_count, zone_id,
                    town_name, taskmaster_template_id, taskmaster_room_id, target_template_id,
                    target_display_name, status, assigned_at, expires_at,
                    reward_silver, reward_experience, reward_fame, reward_points
                ) VALUES (
                    %s, %s, %s, %s, 0, NULL,
                    %s, %s, %s, %s,
                    %s, 'active', NOW(), DATE_ADD(NOW(), INTERVAL %s HOUR),
                    %s, %s, %s, %s
                )
                """,
                (
                    character_id,
                    str(bounty_row.get("type") or "cull"),
                    str(bounty_row.get("target_name") or bounty_row.get("target_template_id") or "target"),
                    int(bounty_row.get("target_count") or 1),
                    town_name,
                    taskmaster_template_id,
                    taskmaster_room_id,
                    str(bounty_row.get("target_template_id") or ""),
                    str(bounty_row.get("target_name") or ""),
                    int(expires_hours),
                    int(bounty_row.get("reward_silver") or 0),
                    int(bounty_row.get("reward_experience") or 0),
                    int(bounty_row.get("reward_fame") or 0),
                    int(bounty_row.get("reward_points") or 0),
                ),
            )
            conn.commit()
            bounty_id = cur.lastrowid
        except Exception as e:
            log.error("Failed to assign bounty for char %s: %s", character_id, e)
            return None
        finally:
            conn.close()

        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM character_bounties WHERE id = %s LIMIT 1", (bounty_id,))
            return cur.fetchone()
        except Exception:
            return None
        finally:
            conn.close()

    def record_character_bounty_kill(self, bounty_id, increment=1):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_bounties
                SET current_count = LEAST(target_count, current_count + %s),
                    status = CASE
                        WHEN LEAST(target_count, current_count + %s) >= target_count THEN 'completed'
                        ELSE 'active'
                    END,
                    completed_at = CASE
                        WHEN LEAST(target_count, current_count + %s) >= target_count THEN COALESCE(completed_at, NOW())
                        ELSE completed_at
                    END
                WHERE id = %s
                  AND status IN ('active', 'completed')
                """,
                (increment, increment, increment, bounty_id),
            )
            conn.commit()
        except Exception as e:
            log.error("Failed to record bounty progress for bounty %s: %s", bounty_id, e)
            return None
        finally:
            conn.close()

        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM character_bounties WHERE id = %s LIMIT 1", (bounty_id,))
            return cur.fetchone()
        except Exception:
            return None
        finally:
            conn.close()

    def close_character_bounty(self, bounty_id):
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE character_bounties
                SET status = 'expired',
                    completed_at = COALESCE(completed_at, NOW())
                WHERE id = %s
                """,
                (bounty_id,),
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to close bounty %s: %s", bounty_id, e)
            return False
        finally:
            conn.close()

    def get_fame_leaderboard(self, scope="all", rank=1, limit=25):
        """Return public fame leaderboard rows for all/race/profession scopes."""
        rows = self.get_visible_fame_rows() or []
        scope_l = str(scope or "all").strip().lower()
        if scope_l.startswith("race:"):
            race_id = int(scope_l.split(":", 1)[1])
            rows = [row for row in rows if int(row.get("race_id") or 0) == race_id]
        elif scope_l.startswith("profession:"):
            prof_id = int(scope_l.split(":", 1)[1])
            rows = [row for row in rows if int(row.get("profession_id") or 0) == prof_id]
        start = max(0, int(rank) - 1)
        return rows[start:start + max(1, int(limit))]

    def get_fame_stats(self, character_id=None):
        """Return summary statistics for the public fame list and optional character ranks."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM characters WHERE fame_list_opt_in = 1")
            total_opted_in = int((cur.fetchone() or [0])[0] or 0)
        finally:
            conn.close()

        visible = self.get_visible_fame_rows() or []
        visible_count = len(visible)
        top_fame = int(visible[0].get("fame") or 0) if visible else 0
        cutoff_fame = int(visible[-1].get("fame") or 0) if visible else 0

        stats = {
            "total_opted_in": total_opted_in,
            "visible_count": visible_count,
            "visible_cap": 1000,
            "top_fame": top_fame,
            "cutoff_fame": cutoff_fame,
            "character_visible": False,
            "overall_rank": None,
            "race_rank": None,
            "profession_rank": None,
        }

        if not character_id:
            return stats

        char_row = None
        for idx, row in enumerate(visible, start=1):
            if int(row.get("id") or 0) == int(character_id):
                char_row = row
                stats["character_visible"] = True
                stats["overall_rank"] = idx
                break

        if not char_row:
            return stats

        race_id = int(char_row.get("race_id") or 0)
        prof_id = int(char_row.get("profession_id") or 0)
        race_rank = 0
        prof_rank = 0
        for row in visible:
            if int(row.get("race_id") or 0) == race_id:
                race_rank += 1
                if int(row.get("id") or 0) == int(character_id):
                    stats["race_rank"] = race_rank
            if int(row.get("profession_id") or 0) == prof_id:
                prof_rank += 1
                if int(row.get("id") or 0) == int(character_id):
                    stats["profession_rank"] = prof_rank
        return stats

    def save_character_tps(self, character_id, physical_tp, mental_tp):
        """Save training points immediately to database."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE characters SET physical_tp = %s, mental_tp = %s WHERE id = %s",
                (physical_tp, mental_tp, character_id)
            )
            return True
        except Exception as e:
            log.error("Failed to save TPs for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()


    def save_character_stats(self, character_id, session):
        """Save the 10 core stat values after a FIXSTATS reallocation."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE characters SET
                    stat_strength     = %(stat_strength)s,
                    stat_constitution = %(stat_constitution)s,
                    stat_dexterity    = %(stat_dexterity)s,
                    stat_agility      = %(stat_agility)s,
                    stat_discipline   = %(stat_discipline)s,
                    stat_aura         = %(stat_aura)s,
                    stat_logic        = %(stat_logic)s,
                    stat_intuition    = %(stat_intuition)s,
                    stat_wisdom       = %(stat_wisdom)s,
                    stat_influence    = %(stat_influence)s
                WHERE id = %(id)s
            """, {
                "stat_strength":     getattr(session, "stat_strength",     50),
                "stat_constitution": getattr(session, "stat_constitution", 50),
                "stat_dexterity":    getattr(session, "stat_dexterity",    50),
                "stat_agility":      getattr(session, "stat_agility",      50),
                "stat_discipline":   getattr(session, "stat_discipline",   50),
                "stat_aura":         getattr(session, "stat_aura",         50),
                "stat_logic":        getattr(session, "stat_logic",        50),
                "stat_intuition":    getattr(session, "stat_intuition",    50),
                "stat_wisdom":       getattr(session, "stat_wisdom",       50),
                "stat_influence":    getattr(session, "stat_influence",    50),
                "id":                character_id,
            })
            return True
        except Exception as e:
            log.error("Failed to save stats for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_convert_loans(self, character_id, ptp_loaned, mtp_loaned):
        """Persist conversion loan balances after a CONVERT or CONVERT REFUND."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE characters SET ptp_loaned = %s, mtp_loaned = %s WHERE id = %s",
                (max(0, ptp_loaned), max(0, mtp_loaned), character_id)
            )
            return True
        except Exception as e:
            log.error("Failed to save convert loans for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_fixstat_data(self, character_id, uses_remaining, uses_total, last_free_ts):
        """Persist fixstat use tracking columns."""
        import datetime
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            last_free = None
            if last_free_ts:
                last_free = datetime.datetime.fromtimestamp(float(last_free_ts))
            cur.execute("""
                UPDATE characters SET
                    fixstat_uses_remaining = %s,
                    fixstat_uses_total     = %s,
                    fixstat_last_free      = %s
                WHERE id = %s
            """, (uses_remaining, uses_total, last_free, character_id))
            return True
        except Exception as e:
            log.error("Failed to save fixstat data for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def save_character_skill(self, character_id, skill_id, ranks, bonus, ranks_this_level=0):
        """Insert or update a single skill rank for a character."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO character_skills (character_id, skill_id, ranks, bonus, ranks_this_level)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE ranks = %s, bonus = %s, ranks_this_level = %s
            """, (character_id, skill_id, ranks, bonus, ranks_this_level,
                  ranks, bonus, ranks_this_level))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to save skill %s for char %s: %s", skill_id, character_id, e)
            return False
        finally:
            conn.close()

    def reset_skill_level_caps(self, character_id):
        """Reset ranks_this_level to 0 for all skills on level-up."""
        conn = self._get_conn()
        cur  = None
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE character_skills SET ranks_this_level = 0 WHERE character_id = %s",
                (character_id,)
            )
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            log.error("Failed to reset skill level caps for char %s: %s", character_id, e)
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass
            return False
        finally:
            conn.close()

    def get_character_artisan_skills(self, character_id):
        """Return artisan skill progress keyed by skill_key."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT skill_key, ranks, projects_completed, last_worked_at
                FROM character_artisan_skills
                WHERE character_id = %s
                ORDER BY skill_key
            """, (character_id,))
            return {row["skill_key"]: row for row in cur.fetchall()}
        finally:
            conn.close()

    def save_character_artisan_skill(self, character_id, skill_key, ranks, projects_completed=0, last_worked_at=None):
        """Insert or update artisan progress for one skill."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO character_artisan_skills
                    (character_id, skill_key, ranks, projects_completed, last_worked_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    ranks = VALUES(ranks),
                    projects_completed = VALUES(projects_completed),
                    last_worked_at = VALUES(last_worked_at)
            """, (character_id, skill_key, ranks, projects_completed, last_worked_at))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to save artisan skill %s for char %s: %s", skill_key, character_id, e)
            return False
        finally:
            conn.close()

    def get_character_artisan_settings(self, character_id):
        """Return artisan settings for a character, or defaults if none exist."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT character_id, unlearn_preference_key, updated_at
                FROM character_artisan_settings
                WHERE character_id = %s
                LIMIT 1
            """, (character_id,))
            row = cur.fetchone()
            if row:
                return row
            return {"character_id": character_id, "unlearn_preference_key": None}
        finally:
            conn.close()

    def set_character_artisan_unlearn_preference(self, character_id, skill_key):
        """Persist the current ARTISAN UNLEARN preference."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO character_artisan_settings (character_id, unlearn_preference_key)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE unlearn_preference_key = VALUES(unlearn_preference_key)
            """, (character_id, skill_key))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to save artisan settings for char %s: %s", character_id, e)
            return False
        finally:
            conn.close()

    def get_character_artisan_projects(self, character_id, status=None):
        """Return artisan projects for a character."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            if status:
                cur.execute("""
                    SELECT *
                    FROM artisan_projects
                    WHERE character_id = %s AND status = %s
                    ORDER BY updated_at DESC, id DESC
                """, (character_id, status))
            else:
                cur.execute("""
                    SELECT *
                    FROM artisan_projects
                    WHERE character_id = %s
                    ORDER BY updated_at DESC, id DESC
                """, (character_id,))
            rows = cur.fetchall()
            for row in rows:
                for key in ("recipe_snapshot", "progress_data"):
                    raw = row.get(key)
                    if isinstance(raw, str):
                        try:
                            row[key] = json.loads(raw)
                        except Exception:
                            pass
            return rows
        finally:
            conn.close()

    def get_character_active_artisan_project(self, character_id, skill_key=None):
        """Return the current active artisan project for a character."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            if skill_key:
                cur.execute("""
                    SELECT *
                    FROM artisan_projects
                    WHERE character_id = %s AND skill_key = %s AND status = 'active'
                    ORDER BY updated_at DESC, id DESC
                    LIMIT 1
                """, (character_id, skill_key))
            else:
                cur.execute("""
                    SELECT *
                    FROM artisan_projects
                    WHERE character_id = %s AND status = 'active'
                    ORDER BY updated_at DESC, id DESC
                    LIMIT 1
                """, (character_id,))
            row = cur.fetchone()
            if not row:
                return None
            for key in ("recipe_snapshot", "progress_data"):
                raw = row.get(key)
                if isinstance(raw, str):
                    try:
                        row[key] = json.loads(raw)
                    except Exception:
                        pass
            return row
        finally:
            conn.close()

    def upsert_active_artisan_project(
        self,
        character_id,
        skill_key,
        recipe_key,
        *,
        station_key=None,
        stage_index=0,
        quality_tier=None,
        recipe_snapshot=None,
        progress_data=None,
    ):
        """Create or update the active project for one artisan skill."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id
                FROM artisan_projects
                WHERE character_id = %s AND skill_key = %s AND status = 'active'
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
            """, (character_id, skill_key))
            row = cur.fetchone()
            recipe_json = json.dumps(recipe_snapshot) if recipe_snapshot is not None else None
            progress_json = json.dumps(progress_data) if progress_data is not None else None
            if row:
                project_id = int(row[0])
                cur.execute("""
                    UPDATE artisan_projects
                    SET recipe_key = %s,
                        station_key = %s,
                        stage_index = %s,
                        quality_tier = %s,
                        recipe_snapshot = %s,
                        progress_data = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (
                    recipe_key, station_key, stage_index, quality_tier,
                    recipe_json, progress_json, project_id,
                ))
                conn.commit()
                return project_id

            cur.execute("""
                INSERT INTO artisan_projects (
                    character_id, skill_key, recipe_key, station_key, status,
                    stage_index, quality_tier, recipe_snapshot, progress_data
                ) VALUES (%s, %s, %s, %s, 'active', %s, %s, %s, %s)
            """, (
                character_id, skill_key, recipe_key, station_key,
                stage_index, quality_tier, recipe_json, progress_json,
            ))
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            log.error("Failed to upsert artisan project for char %s skill %s: %s", character_id, skill_key, e)
            return None
        finally:
            conn.close()

    def complete_character_artisan_project(self, character_id, skill_key, *, progress_data=None, quality_tier=None):
        """Mark the current active artisan project complete."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            progress_json = json.dumps(progress_data) if progress_data is not None else None
            cur.execute("""
                UPDATE artisan_projects
                SET status = 'complete',
                    completed_at = NOW(),
                    progress_data = COALESCE(%s, progress_data),
                    quality_tier = COALESCE(%s, quality_tier),
                    updated_at = NOW()
                WHERE character_id = %s AND skill_key = %s AND status = 'active'
            """, (progress_json, quality_tier, character_id, skill_key))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            log.error("Failed to complete artisan project for char %s skill %s: %s", character_id, skill_key, e)
            return False
        finally:
            conn.close()

    def get_item_template_by_short_name(self, short_name):
        """Return one item template row by short_name."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT *
                FROM items
                WHERE short_name = %s AND is_template = 1
                ORDER BY id
                LIMIT 1
            """, (short_name,))
            return cur.fetchone()
        finally:
            conn.close()

    # =========================================================
    # INVENTORY OPERATIONS
    # =========================================================

    def get_character_inventory(self, character_id):
        """Load all inventory items for a character."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT ci.id as inv_id, ci.item_id, ci.container_id, ci.slot, ci.quantity,
                       ci.extra_data,
                       i.name, i.short_name, i.noun, i.article, i.item_type,
                       i.weight, i.value, i.weapon_type, i.weapon_category,
                       i.attack_bonus, i.damage_bonus, i.damage_factor, i.weapon_speed,
                       i.damage_type, i.level_required,
                       i.armor_group, i.armor_asg, i.defense_bonus, i.enchant_bonus,
                       i.spell_hindrance, i.action_penalty,
                       i.shield_ds, i.shield_size, i.shield_evade_penalty,
                       i.container_capacity,
                       i.lockpick_modifier,
                       i.worn_location, i.description, i.examine_text, i.lore_text,
                       i.material, i.color,
                       i.herb_heal_type, i.herb_heal_amount,
                       i.heal_type, i.heal_rank, i.heal_amount, i.herb_roundtime
                FROM character_inventory ci
                JOIN items i ON ci.item_id = i.id
                WHERE ci.character_id = %s
                ORDER BY ci.slot, i.name
            """, (character_id,))
            rows = cur.fetchall()
            # Merge extra_data JSON into the item dict, then reconstruct
            # any customized display name and stat overrides so that items
            # customized via the shop ORDER system survive server reboots.
            import json as _json
            for row in rows:
                extra = row.pop("extra_data", None)
                if not extra:
                    continue
                try:
                    parsed = _json.loads(extra) if isinstance(extra, str) else extra
                    if not isinstance(parsed, dict):
                        continue
                    row.update(parsed)

                    # ── Restore customized display name ───────────────────
                    # custom_name holds the fully-built name string saved at
                    # delivery time (e.g. "an invar silvery falchion").
                    if parsed.get("custom_name"):
                        row["name"] = parsed["custom_name"]
                        # Rebuild short_name: strip leading article
                        cn = parsed["custom_name"]
                        words = cn.split(" ", 1)
                        if len(words) == 2 and words[0].lower() in ("a", "an", "the"):
                            row["short_name"] = words[1]
                        else:
                            row["short_name"] = cn

                    # ── Restore material-based stat overrides ─────────────
                    # enchant_bonus, attack_bonus, defense_bonus may have been
                    # raised by the chosen material.  extra_data values win
                    # over whatever the base items table row says.
                    for stat in ("enchant_bonus", "attack_bonus", "defense_bonus"):
                        if stat in parsed:
                            row[stat] = parsed[stat]

                    # ── Restore material display field ────────────────────
                    if parsed.get("material"):
                        row["material"] = parsed["material"]

                    # ── Restore color field ───────────────────────────────
                    if parsed.get("color"):
                        row["color"] = parsed["color"]

                except Exception:
                    pass
            return rows
        finally:
            conn.close()

    def save_item_extra_data(self, inv_id, extra_data: dict):
        """
        Persist per-instance item state (lockpick condition, charges, etc.)
        into the extra_data JSON column of character_inventory.
        """
        import json as _json
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE character_inventory SET extra_data = %s WHERE id = %s",
                (_json.dumps(extra_data), inv_id)
            )
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to save item extra_data (inv_id=%s): %s", inv_id, e)
            return False
        finally:
            conn.close()

    def save_ground_item(self, room_id, item_snapshot: dict, dropped_by_character_id=None, dropped_by_name=None, source="drop"):
        """Persist an item as a room-ground object with an expiry timer."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            snapshot = {
                key: value for key, value in dict(item_snapshot or {}).items()
                if key not in {"inv_id", "slot", "container_id", "ground_id", "created_at", "expires_at"}
            }
            item_value = max(0, int(snapshot.get("value") or 0))
            ttl_seconds = 3600 if item_value >= 5000 else 1800
            expires_at = datetime.datetime.fromtimestamp(time.time() + ttl_seconds)
            cur.execute(
                """
                INSERT INTO room_ground_items
                    (room_id, item_id, item_name, item_short_name, item_noun, item_type,
                     base_value, item_data, dropped_by_character_id, dropped_by_name, source, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    int(room_id),
                    int(snapshot.get("item_id") or 0),
                    snapshot.get("name") or snapshot.get("short_name") or "something",
                    snapshot.get("short_name") or snapshot.get("name") or "something",
                    snapshot.get("noun"),
                    snapshot.get("item_type"),
                    item_value,
                    json.dumps(snapshot),
                    dropped_by_character_id,
                    dropped_by_name,
                    source,
                    expires_at,
                )
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            log.error("Failed to save ground item in room %s: %s", room_id, e)
            return None
        finally:
            conn.close()

    def get_room_ground_items(self, room_id):
        """Load all unexpired ground items for a room."""
        self.cleanup_expired_ground_items(room_id=room_id)
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, room_id, item_id, item_name, item_short_name, item_noun, item_type,
                       base_value, item_data, dropped_by_character_id, dropped_by_name, source,
                       created_at, expires_at
                FROM room_ground_items
                WHERE room_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (int(room_id),)
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        items = []
        for row in rows:
            try:
                snapshot = json.loads(row.get("item_data") or "{}")
                if not isinstance(snapshot, dict):
                    snapshot = {}
            except Exception:
                snapshot = {}
            snapshot.setdefault("item_id", row.get("item_id"))
            snapshot.setdefault("name", row.get("item_name"))
            snapshot.setdefault("short_name", row.get("item_short_name"))
            snapshot.setdefault("noun", row.get("item_noun"))
            snapshot.setdefault("item_type", row.get("item_type"))
            snapshot.setdefault("value", row.get("base_value"))
            snapshot["ground_id"] = int(row["id"])
            snapshot["room_id"] = int(row["room_id"])
            snapshot["dropped_source"] = row.get("source")
            snapshot["created_at"] = row.get("created_at")
            snapshot["expires_at"] = row.get("expires_at")
            items.append(snapshot)
        return items

    def remove_ground_item(self, ground_id):
        """Remove one persisted ground item by id."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM room_ground_items WHERE id = %s", (int(ground_id),))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to remove ground item %s: %s", ground_id, e)
            return False
        finally:
            conn.close()

    def cleanup_expired_ground_items(self, room_id=None):
        """Delete expired room-ground items, optionally scoped to one room."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if room_id is None:
                cur.execute("DELETE FROM room_ground_items WHERE expires_at <= NOW()")
            else:
                cur.execute(
                    "DELETE FROM room_ground_items WHERE room_id = %s AND expires_at <= NOW()",
                    (int(room_id),)
                )
            removed = int(cur.rowcount or 0)
            conn.commit()
            return removed
        except Exception as e:
            log.error("Failed to cleanup expired ground items: %s", e)
            return 0
        finally:
            conn.close()

    def get_public_locker_location_for_room(self, room_id):
        """Return locker location metadata plus room roles for the given room."""
        if not room_id:
            return None
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT pll.id, pll.town_name, pll.capacity, plr.room_role
                FROM public_locker_locations pll
                JOIN public_locker_rooms plr ON plr.location_id = pll.id
                WHERE plr.room_id = %s
                ORDER BY FIELD(plr.room_role, 'locker', 'access', 'bank')
                """,
                (int(room_id),)
            )
            rows = cur.fetchall()
            if not rows:
                return None
            location = {
                "id": int(rows[0]["id"]),
                "town_name": rows[0]["town_name"],
                "capacity": int(rows[0]["capacity"] or 50),
                "roles": sorted({(row.get("room_role") or "").lower() for row in rows if row.get("room_role")}),
            }
            return location
        finally:
            conn.close()

    def get_public_locker_room_ids(self, location_id, room_role=None):
        """Return room ids for a public locker location, optionally filtered by role."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if room_role:
                cur.execute(
                    """
                    SELECT room_id
                    FROM public_locker_rooms
                    WHERE location_id = %s AND room_role = %s
                    ORDER BY room_id
                    """,
                    (int(location_id), str(room_role)),
                )
            else:
                cur.execute(
                    """
                    SELECT room_id
                    FROM public_locker_rooms
                    WHERE location_id = %s
                    ORDER BY room_role, room_id
                    """,
                    (int(location_id),),
                )
            return [int(row[0]) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_public_locker_locations(self):
        """Return all public locker locations."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, town_name, capacity
                FROM public_locker_locations
                ORDER BY town_name
                """
            )
            return cur.fetchall()
        finally:
            conn.close()

    def get_character_locker_items(self, character_id, location_id):
        """Load all locker items for a character/location."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, character_id, location_id, item_id, item_name, item_short_name,
                       item_noun, item_type, base_value, item_data, stored_at
                FROM character_locker_items
                WHERE character_id = %s AND location_id = %s
                ORDER BY stored_at ASC, id ASC
                """,
                (int(character_id), int(location_id)),
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        items = []
        for row in rows:
            try:
                snapshot = json.loads(row.get("item_data") or "{}")
                if not isinstance(snapshot, dict):
                    snapshot = {}
            except Exception:
                snapshot = {}
            snapshot.setdefault("item_id", row.get("item_id"))
            snapshot.setdefault("name", row.get("item_name"))
            snapshot.setdefault("short_name", row.get("item_short_name"))
            snapshot.setdefault("noun", row.get("item_noun"))
            snapshot.setdefault("item_type", row.get("item_type"))
            snapshot.setdefault("value", row.get("base_value"))
            snapshot["locker_item_id"] = int(row["id"])
            snapshot["stored_at"] = row.get("stored_at")
            items.append(snapshot)
        return items

    def count_character_locker_items(self, character_id, location_id):
        """Count locker items for a character/location."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT COUNT(*)
                FROM character_locker_items
                WHERE character_id = %s AND location_id = %s
                """,
                (int(character_id), int(location_id)),
            )
            row = cur.fetchone()
            return int(row[0] or 0) if row else 0
        finally:
            conn.close()

    def save_character_locker_item(self, character_id, location_id, item_snapshot: dict):
        """Persist one item snapshot into a character's public locker."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            snapshot = _json_safe_snapshot({
                key: value for key, value in dict(item_snapshot or {}).items()
                if key not in {"inv_id", "slot", "container_id", "locker_item_id", "stored_at"}
            })
            cur.execute(
                """
                INSERT INTO character_locker_items
                    (character_id, location_id, item_id, item_name, item_short_name,
                     item_noun, item_type, base_value, item_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    int(character_id),
                    int(location_id),
                    int(snapshot.get("item_id") or 0),
                    snapshot.get("name") or snapshot.get("short_name") or "something",
                    snapshot.get("short_name") or snapshot.get("name") or "something",
                    snapshot.get("noun"),
                    snapshot.get("item_type"),
                    max(0, int(snapshot.get("value") or 0)),
                    json.dumps(snapshot),
                ),
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            log.error("Failed to save locker item for char %s loc %s: %s", character_id, location_id, e)
            return None
        finally:
            conn.close()

    def remove_character_locker_item(self, locker_item_id):
        """Delete one locker item row."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM character_locker_items WHERE id = %s", (int(locker_item_id),))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            log.error("Failed to remove locker item %s: %s", locker_item_id, e)
            return False
        finally:
            conn.close()

    def add_item_to_inventory(self, character_id, item_id, slot=None, quantity=1):
        """Add an item to a character's inventory. Returns inventory row id."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if slot in ("right_hand", "left_hand"):
                cur.execute(
                    "UPDATE character_inventory SET slot = NULL "
                    "WHERE character_id = %s AND slot = %s",
                    (character_id, slot)
                )
            # Check if stackable item already exists
            cur.execute("""
                SELECT ci.id, ci.quantity FROM character_inventory ci
                JOIN items i ON ci.item_id = i.id
                WHERE ci.character_id = %s AND ci.item_id = %s AND i.is_stackable = TRUE
            """, (character_id, item_id))
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    "UPDATE character_inventory SET quantity = quantity + %s WHERE id = %s",
                    (quantity, existing[0])
                )
                return existing[0]
            else:
                cur.execute(
                    "INSERT INTO character_inventory (character_id, item_id, slot, quantity) VALUES (%s, %s, %s, %s)",
                    (character_id, item_id, slot, quantity)
                )
                return cur.lastrowid
        except Exception as e:
            log.error("Failed to add item to inventory: %s", e)
            return None
        finally:
            conn.close()

    def insert_inventory_item_instance(self, character_id, item_id, slot=None, quantity=1, container_id=None):
        """Insert a distinct inventory row without stack-merging."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if slot in ("right_hand", "left_hand"):
                cur.execute(
                    "UPDATE character_inventory SET slot = NULL WHERE character_id = %s AND slot = %s",
                    (character_id, slot),
                )
            cur.execute(
                """
                INSERT INTO character_inventory (character_id, item_id, slot, quantity, container_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (character_id, item_id, slot, quantity, container_id),
            )
            conn.commit()
            return cur.lastrowid
        except Exception as e:
            log.error("Failed to insert inventory item instance: %s", e)
            return None
        finally:
            conn.close()

    def set_inventory_slot(self, inv_id, slot):
        """Move an inventory row into a slot, enforcing unique hand occupancy."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT character_id FROM character_inventory WHERE id = %s", (inv_id,))
            row = cur.fetchone()
            if not row:
                return False

            character_id = row[0]
            if slot in ("right_hand", "left_hand"):
                cur.execute(
                    "UPDATE character_inventory SET slot = NULL "
                    "WHERE character_id = %s AND slot = %s AND id <> %s",
                    (character_id, slot, inv_id)
                )

            cur.execute(
                "UPDATE character_inventory SET slot = %s, container_id = NULL WHERE id = %s",
                (slot, inv_id)
            )
            return True
        except Exception as e:
            log.error("Failed to set inventory slot: %s", e)
            return False
        finally:
            conn.close()

    def remove_item_from_inventory(self, inv_id):
        """Remove an item from inventory by inventory row id."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM character_inventory WHERE id = %s", (inv_id,))
            return True
        except Exception as e:
            log.error("Failed to remove inventory item: %s", e)
            return False
        finally:
            conn.close()

    def get_or_create_item(self, name, short_name, noun, item_type="misc", article="a", value=0, description=""):
        """Get an item by short_name or create it if it doesn't exist. Returns item_id."""
        conn = self._get_conn()
        cur  = None
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id FROM items WHERE short_name = %s", (short_name,))
            row = cur.fetchone()
            # Consume any remaining rows so the cursor is clean before close
            cur.fetchall()
            if row:
                cur.close()
                return row["id"]
            cur.execute("""
                INSERT INTO items (name, short_name, noun, item_type, article, value, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, short_name, noun, item_type, article, value, description))
            new_id = cur.lastrowid
            conn.commit()
            cur.close()
            return new_id
        except Exception as e:
            log.error("Failed to get/create item: %s", e)
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass
            return None
        finally:
            conn.close()


    def execute_query(self, query, params=None):
        """Execute a raw SQL query and return all rows as tuples."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            log.error("Failed to execute query: %s", e)
            return []
        finally:
            conn.close()

    def execute_update(self, query, params=None):
        """Execute a raw SQL INSERT/UPDATE/DELETE and commit. Returns rows affected."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            conn.commit()
            return cur.rowcount
        except Exception as e:
            log.error("Failed to execute update: %s", e)
            return 0
        finally:
            conn.close()
    # =========================================================
    # REFERENCE DATA
    # =========================================================

    def get_races(self):
        """Get all races."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM races ORDER BY id")
            return cur.fetchall()
        finally:
            conn.close()

    def get_professions(self):
        """Get all professions. Returns list of dicts with key 'type' (aliased from profession_type)."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, name, profession_type AS type, description, "
                "hp_per_level, mana_per_level FROM professions ORDER BY id"
            )
            return cur.fetchall()
        finally:
            conn.close()

    def get_skills(self):
        """Get all skills."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM skills ORDER BY id")
            return cur.fetchall()
        finally:
            conn.close()

    # =========================================================
    # GUILDS
    # =========================================================

    def get_guild_definition(self, guild_id):
        """Get an active guild definition by id."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT *
                FROM guild_definitions
                WHERE guild_id = %s AND is_active = 1
                LIMIT 1
            """, (guild_id,))
            return cur.fetchone()
        finally:
            conn.close()

    def get_guild_definition_for_profession(self, profession_id):
        """Get the active profession guild for a profession."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT *
                FROM guild_definitions
                WHERE profession_id = %s AND is_active = 1
                LIMIT 1
            """, (profession_id,))
            return cur.fetchone()
        finally:
            conn.close()

    def get_character_guild_membership(self, character_id):
        """Get the active guild membership row for a character."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT cgm.*, gd.name AS guild_name, gd.profession_id AS guild_profession_id,
                       gd.support_level, gd.monthly_dues, gd.initiation_fee,
                       gd.join_level, gd.max_prepay_months, gd.has_skill_training,
                       gd.progression_multiplier,
                       gd.has_guildmaster, grd.rank_name
                FROM character_guild_membership cgm
                JOIN guild_definitions gd ON gd.guild_id = cgm.guild_id
                LEFT JOIN guild_rank_definitions grd
                  ON grd.guild_id = cgm.guild_id AND grd.rank_level = cgm.rank_level
                WHERE cgm.character_id = %s AND cgm.status = 'active'
                ORDER BY cgm.joined_at DESC
                LIMIT 1
            """, (character_id,))
            return cur.fetchone()
        finally:
            conn.close()

    def get_character_guild_skills(self, character_id, guild_id):
        """Get guild skill rows keyed by skill name."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT skill_name, ranks, training_points, is_mastered, last_trained_at
                FROM character_guild_skills
                WHERE character_id = %s AND guild_id = %s
                ORDER BY skill_name
            """, (character_id, guild_id))
            return {row["skill_name"]: row for row in cur.fetchall()}
        finally:
            conn.close()

    def get_character_guild_tasks(self, character_id, guild_id):
        """Get active guild tasks for a character."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT id, skill_name, task_code, task_type, task_text,
                       objective_event, target_count, progress_count, award_points,
                       repetitions_remaining, task_data, status,
                       assigned_at, completed_at
                FROM character_guild_tasks
                WHERE character_id = %s AND guild_id = %s AND status IN ('assigned', 'ready')
                ORDER BY assigned_at DESC
            """, (character_id, guild_id))
            return cur.fetchall()
        finally:
            conn.close()

    def get_guild_skill_definitions(self, guild_id):
        """Get the configured guild skill definitions for a guild."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT guild_id, skill_name, display_name, skill_order,
                       max_rank, points_per_rank, practice_only, is_active
                FROM guild_skill_definitions
                WHERE guild_id = %s AND is_active = 1
                ORDER BY skill_order, skill_name
            """, (guild_id,))
            return cur.fetchall()
        finally:
            conn.close()

    def get_guild_registry_for_room(self, room_id):
        """Get active guild registry rows for a room."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT gmr.*, gd.name AS guild_name, gd.profession_id, gd.support_level,
                       gd.monthly_dues, gd.initiation_fee, gd.join_level,
                       gd.max_prepay_months, gd.has_skill_training, gd.has_guildmaster
                FROM guild_master_registry gmr
                JOIN guild_definitions gd ON gd.guild_id = gmr.guild_id
                WHERE gmr.room_id = %s AND gmr.is_active = 1 AND gd.is_active = 1
                ORDER BY FIELD(gmr.role_type, 'master', 'administrator', 'trainer', 'contact'), gmr.id
            """, (room_id,))
            return cur.fetchall()
        finally:
            conn.close()

    def join_guild_member(self, character_id, guild_id, *, actor_template_id=None, notes=None):
        """Join or reactivate a guild membership."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO character_guild_membership (
                    character_id, guild_id, status, rank_level, joined_at,
                    dues_paid_through, last_checkin_at, next_checkin_due_at, resigned_at
                ) VALUES (%s, %s, 'active', 1, NOW(), NULL, NULL, NULL, NULL)
                ON DUPLICATE KEY UPDATE
                    status = 'active',
                    rank_level = 1,
                    joined_at = NOW(),
                    dues_paid_through = NULL,
                    last_checkin_at = NULL,
                    next_checkin_due_at = NULL,
                    resigned_at = NULL
            """, (character_id, guild_id))
            cur.execute("""
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'join', 0, %s, %s)
            """, (character_id, guild_id, actor_template_id, notes))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to join guild %s for char %s: %s", guild_id, character_id, e)
            return False
        finally:
            conn.close()

    def pay_guild_dues(self, character_id, guild_id, dues_paid_through, amount, months_paid,
                       *, actor_template_id=None, notes=None):
        """Update dues paid-through date and append a ledger row."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE character_guild_membership
                SET dues_paid_through = %s
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
            """, (dues_paid_through, character_id, guild_id))
            cur.execute("""
                INSERT INTO guild_ledger (
                    character_id, guild_id, entry_type, amount, months_paid, actor_template_id, notes
                ) VALUES (%s, %s, 'dues', %s, %s, %s, %s)
            """, (character_id, guild_id, amount, months_paid, actor_template_id, notes))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to pay guild dues for char %s in %s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def checkin_guild_member(self, character_id, guild_id, next_checkin_due_at,
                             *, actor_template_id=None, notes=None):
        """Record a guild check-in and append a ledger row."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE character_guild_membership
                SET last_checkin_at = NOW(), next_checkin_due_at = %s
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
            """, (next_checkin_due_at, character_id, guild_id))
            cur.execute("""
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'checkin', 0, %s, %s)
            """, (character_id, guild_id, actor_template_id, notes))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to check in guild member char %s in %s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()

    def resign_guild_member(self, character_id, guild_id, *, actor_template_id=None, notes=None):
        """Resign an active guild membership."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE character_guild_membership
                SET status = 'resigned', resigned_at = NOW()
                WHERE character_id = %s AND guild_id = %s AND status = 'active'
            """, (character_id, guild_id))
            cur.execute("""
                INSERT INTO guild_ledger (character_id, guild_id, entry_type, amount, actor_template_id, notes)
                VALUES (%s, %s, 'resign', 0, %s, %s)
            """, (character_id, guild_id, actor_template_id, notes))
            conn.commit()
            return True
        except Exception as e:
            log.error("Failed to resign guild member char %s in %s: %s", character_id, guild_id, e)
            return False
        finally:
            conn.close()
