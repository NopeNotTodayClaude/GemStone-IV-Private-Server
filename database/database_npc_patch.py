"""
DATABASE PATCH — NPC system additions
======================================
Add these methods to server/core/database.py  (inside the Database class).

These are standalone additions — nothing existing needs to change.
"""

    # ──────────────────────────────────────────────────────────────────────────
    # NPC shop inventory
    # ──────────────────────────────────────────────────────────────────────────

    def get_npc_shop_inventory(self, template_id: str) -> list:
        """
        Return all inventory rows for an NPC shop.
        Each row: {id, item_id, quantity, price, restock_at}
        quantity = -1 means unlimited.
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, item_id, quantity, price, restock_at "
                "FROM npc_shop_inventory "
                "WHERE template_id = %s",
                (template_id,)
            )
            return cur.fetchall()
        except Exception as e:
            log.warning("get_npc_shop_inventory failed (%s): %s", template_id, e)
            return []
        finally:
            conn.close()

    def npc_shop_buy(self, template_id: str, inv_id: int) -> bool:
        """
        Decrement stock by 1 for a finite-stock item (quantity >= 0).
        Returns True if the purchase went through, False if out of stock.
        No-op for unlimited stock (quantity = -1).
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT quantity FROM npc_shop_inventory WHERE id = %s AND template_id = %s",
                (inv_id, template_id)
            )
            row = cur.fetchone()
            if not row:
                return False
            if row["quantity"] == -1:
                return True          # unlimited
            if row["quantity"] <= 0:
                return False         # out of stock
            cur.execute(
                "UPDATE npc_shop_inventory SET quantity = quantity - 1 WHERE id = %s",
                (inv_id,)
            )
            conn.commit()
            return True
        except Exception as e:
            log.warning("npc_shop_buy failed: %s", e)
            return False
        finally:
            conn.close()

    def npc_shop_restock(self, template_id: str, inv_id: int, quantity: int):
        """Set a shop item back to a specific quantity and clear restock_at."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE npc_shop_inventory SET quantity = %s, restock_at = 0 "
                "WHERE id = %s AND template_id = %s",
                (quantity, inv_id, template_id)
            )
            conn.commit()
        except Exception as e:
            log.warning("npc_shop_restock failed: %s", e)
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────────────────────
    # NPC guild membership
    # ──────────────────────────────────────────────────────────────────────────

    def get_guild_membership(self, guild_id: str, character_id: int) -> dict:
        """
        Return the player's guild membership row, or None if not a member.
        Row: {id, guild_id, character_id, rank_level, guild_xp, joined_at}
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM npc_guild_membership "
                "WHERE guild_id = %s AND character_id = %s",
                (guild_id, character_id)
            )
            return cur.fetchone()
        except Exception as e:
            log.warning("get_guild_membership failed: %s", e)
            return None
        finally:
            conn.close()

    def join_guild(self, guild_id: str, character_id: int):
        """Add a player to a guild at rank 1 with 0 xp."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT IGNORE INTO npc_guild_membership "
                "(guild_id, character_id, rank_level, guild_xp) "
                "VALUES (%s, %s, 1, 0)",
                (guild_id, character_id)
            )
            conn.commit()
        except Exception as e:
            log.warning("join_guild failed: %s", e)
        finally:
            conn.close()

    def add_guild_xp(self, guild_id: str, character_id: int, xp: int) -> int:
        """
        Add XP to a player's guild standing.
        Returns the new total guild_xp.
        """
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE npc_guild_membership SET guild_xp = guild_xp + %s "
                "WHERE guild_id = %s AND character_id = %s",
                (xp, guild_id, character_id)
            )
            conn.commit()
            cur.execute(
                "SELECT guild_xp FROM npc_guild_membership "
                "WHERE guild_id = %s AND character_id = %s",
                (guild_id, character_id)
            )
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception as e:
            log.warning("add_guild_xp failed: %s", e)
            return 0
        finally:
            conn.close()

    def set_guild_rank(self, guild_id: str, character_id: int, rank_level: int):
        """Advance (or reduce) a player's rank in a guild."""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE npc_guild_membership SET rank_level = %s "
                "WHERE guild_id = %s AND character_id = %s",
                (rank_level, guild_id, character_id)
            )
            conn.commit()
        except Exception as e:
            log.warning("set_guild_rank failed: %s", e)
        finally:
            conn.close()

    def get_guild_ranks(self, guild_id: str) -> list:
        """Return all rank definitions for a guild, ordered by rank_level."""
        conn = self._get_conn()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT rank_level, rank_name, rank_title, "
                "min_xp_required, min_skill_ranks, unlock_abilities "
                "FROM npc_guild_ranks WHERE guild_id = %s "
                "ORDER BY rank_level ASC",
                (guild_id,)
            )
            return cur.fetchall()
        except Exception as e:
            log.warning("get_guild_ranks failed: %s", e)
            return []
        finally:
            conn.close()
