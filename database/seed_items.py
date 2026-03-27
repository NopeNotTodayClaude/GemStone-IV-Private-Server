"""
GemStone IV Item Seeder

Reads all item data files and inserts them into the items table as templates.
Run this script to populate the database with all GS4 items.

Usage: python seed_items.py
"""

import sys
import os
import importlib.util

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

try:
    import mariadb
except ImportError:
    try:
        import mysql.connector as mariadb
    except ImportError:
        import pymysql as mariadb
        mariadb.connect = mariadb.connect


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "gemstone_dev",
}


def get_connection():
    """Get a database connection."""
    try:
        conn = mariadb.connect(**DB_CONFIG)
    except Exception:
        # Try without password
        cfg = dict(DB_CONFIG)
        cfg.pop("password", None)
        conn = mariadb.connect(**cfg)
    return conn


def load_module(filepath):
    """Dynamically load a Python module from a filepath."""
    spec = importlib.util.spec_from_file_location("mod", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_noun(name):
    """Extract the noun (last word) from an item name."""
    parts = name.strip().split()
    return parts[-1] if parts else name


def extract_article(description):
    """Extract the article from a description like 'a longsword' or 'an emerald'."""
    if not description:
        return "a"
    desc = description.strip().lower()
    if desc.startswith("an "):
        return "an"
    if desc.startswith("a "):
        return "a"
    if desc.startswith("some "):
        return "some"
    if desc.startswith("the "):
        return "the"
    return "a"


def map_item_type(item_data):
    """Map the item's 'type' field to the DB item_type enum."""
    t = item_data.get("type", "misc").lower()
    type_map = {
        "weapon": "weapon",
        "armor": "armor",
        "shield": "shield",
        "gem": "gem",
        "herb": "herb",
        "container": "container",
        "lockpick": "misc",
        "tool": "misc",
        "light": "misc",
        "scroll": "scroll",
        "runestone": "wand",
        "wand": "wand",
        "food": "consumable",
        "drink": "consumable",
        "ore": "misc",
        "skin": "skin",
        "jewelry": "jewelry",
        "trinket": "misc",
        "currency": "misc",
    }
    return type_map.get(t, "misc")


def insert_item(cursor, item_name, item_data, category=None):
    """Insert a single item template into the items table."""
    base_name = item_data.get("base_name", item_name)
    description = item_data.get("description", f"a {item_name}")
    article = extract_article(description)
    noun = extract_noun(base_name)
    item_type = map_item_type(item_data)
    material = item_data.get("material", "steel" if item_type in ("weapon", "armor", "shield") else None)

    # Build the INSERT
    sql = """
    INSERT INTO items (
        name, short_name, noun, base_name, article, item_type, material, material_bonus,
        weight, value, is_template,
        weapon_type, weapon_category, damage_factor, damage_type, crit_divisor,
        attack_bonus, damage_bonus, weapon_speed,
        armor_group, armor_asg, cva, spell_hindrance, defense_bonus, action_penalty,
        shield_size, shield_ds, shield_evade_penalty,
        container_capacity, herb_heal_type, herb_heal_amount,
        gem_family, lockpick_modifier, enchant_bonus,
        description, is_stackable
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s, %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s, %s,
        %s, %s
    )
    ON DUPLICATE KEY UPDATE
        base_name = VALUES(base_name),
        material = VALUES(material),
        weight = VALUES(weight),
        value = VALUES(value),
        is_template = 1
    """

    # Weapon fields
    weapon_type = item_data.get("weapon_type", None)
    weapon_category = item_data.get("weapon_category", category)
    if weapon_category and weapon_category not in ("edged", "blunt", "twohanded", "polearm", "ranged", "thrown", "brawling"):
        weapon_category = None
    damage_factor = item_data.get("damage_factor", 0)
    damage_type = item_data.get("damage_type", None)
    crit_divisor = item_data.get("crit_divisor", 1)
    attack_bonus = item_data.get("attack_bonus", 0)
    damage_bonus = item_data.get("damage_bonus", 0)
    weapon_speed = item_data.get("roundtime", item_data.get("weapon_speed", 5))

    # Armor fields
    armor_group = item_data.get("armor_group", item_data.get("asg", 0))
    armor_asg = item_data.get("armor_asg", item_data.get("asg", 1))
    cva = item_data.get("cva", 25)
    spell_hindrance = item_data.get("spell_hindrance", 0)
    defense_bonus = item_data.get("defense_bonus", 0)
    action_penalty = item_data.get("action_penalty", 0)

    # Shield fields
    shield_size = item_data.get("shield_type", item_data.get("shield_size", None))
    if shield_size and shield_size not in ("small", "medium", "large", "tower"):
        shield_size = None
    shield_ds = item_data.get("shield_ds", 0)
    shield_evade_penalty = item_data.get("shield_evade_penalty", 0)

    # Other fields
    container_capacity = item_data.get("capacity", item_data.get("container_capacity", 0))
    herb_heal_type = item_data.get("herb_heal_type", None)
    herb_heal_amount = item_data.get("herb_heal_amount", 0)
    gem_family = item_data.get("gem_family", None)
    lockpick_modifier = item_data.get("lockpick_modifier", 1.0)
    enchant_bonus = item_data.get("enchant_bonus", 0)
    weight = item_data.get("weight", 1)
    value = item_data.get("value", 0)
    is_stackable = 1 if item_type in ("consumable", "gem", "herb") else 0

    params = (
        base_name, base_name[:64], noun, base_name, article, item_type, material, 0,
        weight, value, 1,
        weapon_type, weapon_category, damage_factor, damage_type, crit_divisor,
        attack_bonus, damage_bonus, weapon_speed,
        armor_group, armor_asg, cva, spell_hindrance, defense_bonus, action_penalty,
        shield_size, shield_ds, shield_evade_penalty,
        container_capacity, herb_heal_type, herb_heal_amount,
        gem_family, lockpick_modifier, enchant_bonus,
        description, is_stackable,
    )

    cursor.execute(sql, params)


def seed_weapons(cursor):
    """Seed all weapon data files."""
    weapons_dir = os.path.join(PROJECT_ROOT, "server", "data", "items", "weapons")
    count = 0
    for filename in os.listdir(weapons_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            filepath = os.path.join(weapons_dir, filename)
            mod = load_module(filepath)
            category = filename.replace(".py", "")

            # Each weapons file has a dict constant (EDGED_WEAPONS, BLUNT_WEAPONS, etc.)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, dict) and attr and not attr_name.startswith("_"):
                    # Check if it looks like an item dict (has nested dicts with 'base_name')
                    first_val = next(iter(attr.values()), None)
                    if isinstance(first_val, dict) and "base_name" in first_val:
                        for name, data in attr.items():
                            insert_item(cursor, name, data, category=category)
                            count += 1
                        break
    print(f"  Weapons: {count} items seeded")
    return count


def seed_from_file(cursor, filepath, label):
    """Seed items from a single data file. Returns count."""
    mod = load_module(filepath)
    count = 0
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if isinstance(attr, dict) and attr and not attr_name.startswith("_"):
            first_val = next(iter(attr.values()), None)
            if isinstance(first_val, dict) and ("base_name" in first_val or "type" in first_val or "name" in first_val):
                for name, data in attr.items():
                    if isinstance(data, dict) and ("base_name" in data or "type" in data):
                        insert_item(cursor, name, data)
                        count += 1
    print(f"  {label}: {count} items seeded")
    return count


def main():
    """Main seeder function."""
    print("GemStone IV Item Seeder")
    print("=" * 40)

    conn = get_connection()
    cursor = conn.cursor()
    total = 0

    try:
        # Seed weapons
        total += seed_weapons(cursor)

        # Seed armor
        armor_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "armor", "armor.py")
        if os.path.exists(armor_file):
            total += seed_from_file(cursor, armor_file, "Armor")

        # Seed shields
        shields_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "shields", "shields.py")
        if os.path.exists(shields_file):
            total += seed_from_file(cursor, shields_file, "Shields")

        # Seed gems
        gems_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "gems", "gems.py")
        if os.path.exists(gems_file):
            total += seed_from_file(cursor, gems_file, "Gems")

        # Seed herbs
        herbs_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "herbs", "herbs.py")
        if os.path.exists(herbs_file):
            total += seed_from_file(cursor, herbs_file, "Herbs")

        # Seed lockpicks
        lockpicks_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "lockpicks", "lockpicks.py")
        if os.path.exists(lockpicks_file):
            total += seed_from_file(cursor, lockpicks_file, "Lockpicks")

        # Seed containers
        containers_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "containers", "containers.py")
        if os.path.exists(containers_file):
            total += seed_from_file(cursor, containers_file, "Containers")

        # Seed misc items
        misc_file = os.path.join(PROJECT_ROOT, "server", "data", "items", "misc", "misc_items.py")
        if os.path.exists(misc_file):
            total += seed_from_file(cursor, misc_file, "Misc Items")

        conn.commit()
        print("=" * 40)
        print(f"Total: {total} item templates seeded successfully!")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
