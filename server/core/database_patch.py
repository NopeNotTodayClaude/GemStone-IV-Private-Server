"""
DATABASE PATCH — apply to server/core/database.py
===================================================
Two methods need updating.  Find each one and replace entirely.

CHANGE 1: create_character  — add culture_key, age, skin_tone to INSERT
CHANGE 2: get_professions   — column renamed type -> profession_type
"""


# ── CHANGE 1: replace create_character() ──────────────────────────────────────
# Find the existing create_character method and replace it with this one.
# The only changes are:
#   • culture_key, age, skin_tone added to INSERT column list
#   • corresponding %(...)s placeholders added
#   • default values supplied so callers that don't pass them still work

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
                    current_room_id, height, hair_color, hair_style, eye_color, skin_tone,
                    age
                ) VALUES (
                    %(account_id)s, %(name)s, %(race_id)s, %(profession_id)s, %(gender)s,
                    %(culture_key)s,
                    %(strength)s, %(constitution)s, %(dexterity)s, %(agility)s,
                    %(discipline)s, %(aura)s, %(logic)s, %(intuition)s,
                    %(wisdom)s, %(influence)s,
                    %(health_max)s, %(health_max)s, %(mana_max)s, %(mana_max)s,
                    %(spirit_max)s, %(spirit_max)s, %(stamina_max)s, %(stamina_max)s,
                    %(starting_room)s, %(height)s, %(hair_color)s, %(hair_style)s,
                    %(eye_color)s, %(skin_tone)s,
                    %(age)s
                )
            """, {
                **char_data,
                "account_id":  account_id,
                "culture_key": char_data.get("culture_key"),   # None = no culture chosen
                "skin_tone":   char_data.get("skin_tone", "fair"),
                "age":         char_data.get("age"),            # None = not set yet
            })
            char_id = cur.lastrowid
            log.info("Character created: %s (id=%d)", char_data.get("name"), char_id)
            return char_id
        except mysql.connector.IntegrityError as e:
            log.warning("Character creation failed: %s", e)
            return None
        finally:
            conn.close()


# ── CHANGE 2: replace get_professions() ───────────────────────────────────────
# The column was renamed from `type` to `profession_type` to avoid MySQL
# reserved-word conflicts.  Any code that uses the returned dicts still
# gets a key called "type" — we alias it here so nothing else breaks.

    def get_professions(self):
        """Get all professions. Returns list of dicts with key 'type' (aliased from profession_type)."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, name, profession_type AS `type`, description, "
                "hp_per_level, mana_per_level FROM professions ORDER BY id"
            )
            return cur.fetchall()
        finally:
            conn.close()
