-- 027_finish_core_magic_guilds.sql
-- Magic support items plus core profession guild skill tracks.

INSERT INTO items (
    name, short_name, noun, article, item_type, is_template, is_stackable,
    weight, value, description, examine_text
)
SELECT
    'a loaf of manna bread',
    'manna bread',
    'bread',
    'a',
    'consumable',
    1,
    0,
    0.2,
    75,
    'A warm loaf of blessed bread glows faintly with spiritual energy.',
    'The bread carries the clean, sustaining scent of summoned manna.'
FROM DUAL
WHERE NOT EXISTS (
    SELECT 1 FROM items WHERE short_name = 'manna bread' AND item_type = 'consumable'
);

UPDATE guild_definitions
SET support_level = 'complete', has_skill_training = 1, has_guildmaster = 1
WHERE guild_id IN ('wizard', 'cleric', 'empath', 'sorcerer', 'bard', 'ranger');

DELETE FROM guild_skill_definitions
WHERE guild_id IN ('wizard', 'cleric', 'empath', 'sorcerer', 'bard', 'ranger');

INSERT INTO guild_skill_definitions (
    guild_id, skill_name, display_name, skill_order, max_rank, points_per_rank, practice_only, is_active
) VALUES
    ('wizard',   'Spell Aiming', 'Spell Aiming', 1, 63, 100, 0, 1),
    ('wizard',   'Arcane Symbols', 'Arcane Symbols', 2, 63, 100, 0, 1),
    ('wizard',   'Chargecraft', 'Chargecraft', 3, 63, 100, 0, 1),
    ('cleric',   'Liturgy', 'Liturgy', 1, 63, 100, 0, 1),
    ('cleric',   'Benedictions', 'Benedictions', 2, 63, 100, 0, 1),
    ('cleric',   'Channeling', 'Channeling', 3, 63, 100, 0, 1),
    ('empath',   'Healing Arts', 'Healing Arts', 1, 63, 100, 0, 1),
    ('empath',   'Attunement', 'Attunement', 2, 63, 100, 0, 1),
    ('empath',   'Transference', 'Transference', 3, 63, 100, 0, 1),
    ('bard',     'Performance', 'Performance', 1, 63, 100, 0, 1),
    ('bard',     'Songcraft', 'Songcraft', 2, 63, 100, 0, 1),
    ('bard',     'Bardic Lore', 'Bardic Lore', 3, 63, 100, 1, 1),
    ('ranger',   'Stealth', 'Stealth', 1, 63, 100, 0, 1),
    ('ranger',   'Nature Lore', 'Nature Lore', 2, 63, 100, 0, 1),
    ('ranger',   'Trailcraft', 'Trailcraft', 3, 63, 100, 1, 1),
    ('sorcerer', 'Shadowcraft', 'Shadowcraft', 1, 63, 100, 0, 1),
    ('sorcerer', 'Demonology', 'Demonology', 2, 63, 100, 0, 1),
    ('sorcerer', 'Necromancy', 'Necromancy', 3, 63, 100, 0, 1);

DELETE FROM guild_task_definitions
WHERE guild_id IN ('wizard', 'cleric', 'empath', 'sorcerer', 'bard', 'ranger');

INSERT INTO guild_task_definitions (
    guild_id, skill_name, task_code, title, description, objective_event,
    required_count, base_points, min_rank, max_rank, practice_room_id,
    requires_guild_authority, is_active
) VALUES
    ('wizard', 'Spell Aiming', 'wiz_cast', 'Directed Casting', 'Cast offensive or utility spells successfully.', 'spell_cast_success', 4, 45, 0, NULL, NULL, 0, 1),
    ('wizard', 'Spell Aiming', 'wiz_focus', 'Aiming Drill', 'Work a precision spellcasting drill inside the guild.', 'guild_practice', 3, 40, 0, NULL, 18041, 0, 1),
    ('wizard', 'Arcane Symbols', 'wiz_scroll_read', 'Rune Study', 'Read and decipher guild-sanctioned scrollwork.', 'scroll_read_success', 3, 40, 0, NULL, NULL, 0, 1),
    ('wizard', 'Arcane Symbols', 'wiz_scroll_invoke', 'Scroll Invocation', 'Successfully invoke scroll magic.', 'scroll_invoke_success', 3, 45, 0, NULL, NULL, 0, 1),
    ('wizard', 'Chargecraft', 'wiz_charge', 'Chargecraft', 'Operate or recharge magical items safely.', 'magic_item_success', 3, 50, 0, NULL, NULL, 0, 1),
    ('wizard', 'Chargecraft', 'wiz_charge_drill', 'Resonance Drill', 'Practice stabilizing charged matrices in the guild.', 'guild_practice', 3, 40, 0, NULL, 18041, 0, 1),

    ('cleric', 'Liturgy', 'cleric_cast', 'Formal Invocation', 'Cast spiritual magic in keeping with guild liturgy.', 'spell_cast_success', 4, 45, 0, NULL, NULL, 0, 1),
    ('cleric', 'Liturgy', 'cleric_prayer', 'Prayer Circle', 'Recite and practice the guild''s formal rites.', 'guild_practice', 3, 40, 0, NULL, 10376, 0, 1),
    ('cleric', 'Benedictions', 'cleric_bless', 'Benediction Drill', 'Practice the measured rhythm of blessings.', 'guild_practice', 3, 45, 0, NULL, 10376, 0, 1),
    ('cleric', 'Channeling', 'cleric_share', 'Shared Grace', 'Transfer mana to allies through spiritual discipline.', 'mana_share_success', 3, 50, 0, NULL, NULL, 0, 1),

    ('empath', 'Healing Arts', 'empath_cast', 'Healing Resonance', 'Cast empathic spells with clean control.', 'spell_cast_success', 4, 45, 0, NULL, NULL, 0, 1),
    ('empath', 'Healing Arts', 'empath_focus', 'Calming Focus', 'Practice the stillness required for guild healing.', 'guild_practice', 3, 40, 0, NULL, 10759, 0, 1),
    ('empath', 'Attunement', 'empath_attune', 'Attunement Drill', 'Refine your empathic attunement in the guildhall.', 'guild_practice', 3, 45, 0, NULL, 10759, 0, 1),
    ('empath', 'Transference', 'empath_share', 'Shared Vitality', 'Transfer mana to others without waste.', 'mana_share_success', 3, 50, 0, NULL, NULL, 0, 1),

    ('bard', 'Performance', 'bard_song', 'Performance Piece', 'Weave a successful song or spell before an audience.', 'spell_cast_success', 4, 45, 0, NULL, NULL, 0, 1),
    ('bard', 'Performance', 'bard_rehearse', 'Hall Rehearsal', 'Practice posture, timing, and breath in the guild hall.', 'guild_practice', 3, 40, 0, NULL, 10438, 0, 1),
    ('bard', 'Songcraft', 'bard_compose', 'Songcraft Study', 'Work through the structure and cadence of bardic compositions.', 'guild_practice', 3, 45, 0, NULL, 10438, 0, 1),
    ('bard', 'Bardic Lore', 'bard_scroll', 'Annotated Scores', 'Study magical notation and invoke prepared scores cleanly.', 'scroll_invoke_success', 3, 50, 0, NULL, NULL, 0, 1),

    ('ranger', 'Stealth', 'ranger_hide', 'Woodland Vanish', 'Slip cleanly from sight as a ranger should.', 'hide_success', 3, 45, 0, NULL, NULL, 0, 1),
    ('ranger', 'Stealth', 'ranger_ambush', 'Hunter''s Strike', 'Ambush a target from concealment.', 'ambush_success', 2, 50, 0, NULL, NULL, 0, 1),
    ('ranger', 'Nature Lore', 'ranger_forage', 'Wildcraft', 'Forage useful plants and signs from the wild.', 'forage_success', 3, 45, 0, NULL, NULL, 0, 1),
    ('ranger', 'Trailcraft', 'ranger_trail', 'Trail Lesson', 'Work through routecraft and field drills inside the guild.', 'guild_practice', 3, 40, 0, NULL, 24367, 0, 1),

    ('sorcerer', 'Shadowcraft', 'sorc_cast', 'Shadowcraft', 'Shape sorcerous power successfully in live casting.', 'spell_cast_success', 4, 45, 0, NULL, NULL, 0, 1),
    ('sorcerer', 'Shadowcraft', 'sorc_scroll', 'Infused Texts', 'Invoke or awaken infused magical items.', 'scroll_invoke_success', 3, 45, 0, NULL, NULL, 0, 1),
    ('sorcerer', 'Demonology', 'sorc_demon', 'Demonological Practice', 'Practice the bindings and sigils of demonology.', 'guild_practice', 3, 45, 0, NULL, 10886, 0, 1),
    ('sorcerer', 'Necromancy', 'sorc_necro', 'Necromantic Practice', 'Refine your necromantic focus inside the guild.', 'guild_practice', 3, 45, 0, NULL, 10886, 0, 1),
    ('sorcerer', 'Necromancy', 'sorc_item', 'Dark Matrices', 'Manipulate charged or infused items without collapse.', 'magic_item_success', 3, 50, 0, NULL, NULL, 0, 1);

DELETE FROM guild_master_registry
WHERE guild_id IN ('wizard', 'cleric', 'sorcerer', 'bard', 'ranger', 'empath')
  AND npc_template_id IN ('kalciusa', 'cleric_garntek', 'vorenus_faendryl', 'bard_master', 'zl_ranger_guide', 'empath_healer');

INSERT INTO guild_master_registry (
    guild_id, npc_template_id, role_type, room_id, lich_room_id, city_name, is_active, notes
) VALUES
    ('wizard', 'kalciusa', 'administrator', 18041, 687001, 'Ta''Vaalor', 1, 'Wizard guild administrator for the live guild system.'),
    ('cleric', 'cleric_garntek', 'administrator', 10376, 675001, 'Ta''Vaalor', 1, 'Cleric guild administrator for the live guild system.'),
    ('empath', 'empath_healer', 'administrator', 10759, 657001, 'Ta''Vaalor', 1, 'Empath guild authority using the placed guild healer.'),
    ('bard', 'bard_master', 'master', 10438, 287001, 'Ta''Vaalor', 1, 'Bard guild authority in the Ta''Vaalor bard guild entry.'),
    ('ranger', 'zl_ranger_guide', 'administrator', 24367, 278001, 'Zul Logoth', 1, 'Ranger guild authority using the placed Zul Logoth ranger guide.'),
    ('sorcerer', 'vorenus_faendryl', 'administrator', 10886, 663001, 'Ta''Illistim', 1, 'Sorcerer guild administrator for the live guild system.');
