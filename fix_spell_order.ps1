$file = 'C:\Gemstone 4 Server\server\core\commands\player\spellcasting.py'
$lines = [System.IO.File]::ReadAllLines($file)
$src = $lines -join "`n"
$changes = 0

# PATH 1 - prepared cast block
$old1 = "        if ok:`n            _clear_prepared_scroll_state(session)`n            result_dict = _lua_result_to_dict(engine, values)`n            await _apply_spell_damage(session, server, target, result_dict)`n            message = f`"{message}{await _apply_post_cast_side_effects(session, server, spell_number, target, verb)}`"`n            _apply_lua_char_updates(engine, raw_char, session)`n            _refresh_post_spell_state(session, server, target)`n            if _is_healing_spell(session, spell_number):`n                await session.send_line(healing_msg(f`"  {message}`"))`n                await _broadcast_healing_spell(session, server, spell_number, target, message)`n            else:`n                _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM`n                await session.send_line(colorize(f`"  {message}`", _spell_color))"

$new1 = "        if ok:`n            _clear_prepared_scroll_state(session)`n            result_dict = _lua_result_to_dict(engine, values)`n            _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM`n            if _is_healing_spell(session, spell_number):`n                await session.send_line(healing_msg(f`"  {message}`"))`n                await _broadcast_healing_spell(session, server, spell_number, target, message)`n            else:`n                await session.send_line(colorize(f`"  {message}`", _spell_color))`n            await _apply_spell_damage(session, server, target, result_dict)`n            side_fx = await _apply_post_cast_side_effects(session, server, spell_number, target, verb)`n            _apply_lua_char_updates(engine, raw_char, session)`n            _refresh_post_spell_state(session, server, target)`n            if side_fx:`n                for _fx in side_fx.strip().splitlines():`n                    if _fx.strip():`n                        await session.send_line(colorize(f`"  {_fx.strip()}`", _spell_color))"

if ($src.Contains($old1)) {
    $src = $src.Replace($old1, $new1)
    $changes++
    Write-Host "PATH 1 replaced"
} else {
    Write-Host "PATH 1 NOT FOUND"
}

# PATH 2 - unprepared cast block
$old2 = "    if ok:`n        await _apply_spell_damage(session, server, target, result_dict)`n        message = f`"{message}{await _apply_post_cast_side_effects(session, server, spell_number, target, verb)}`"`n        _refresh_post_spell_state(session, server, target)`n        session._prepared_lua_spell_number = None`n        if _is_healing_spell(session, spell_number):`n            await session.send_line(healing_msg(f`"  {message}`"))`n            await _broadcast_healing_spell(session, server, spell_number, target, message)`n        else:`n            _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM`n            await session.send_line(colorize(f`"  {message}`", _spell_color))"

$new2 = "    if ok:`n        _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM`n        if _is_healing_spell(session, spell_number):`n            await session.send_line(healing_msg(f`"  {message}`"))`n            await _broadcast_healing_spell(session, server, spell_number, target, message)`n        else:`n            await session.send_line(colorize(f`"  {message}`", _spell_color))`n        await _apply_spell_damage(session, server, target, result_dict)`n        side_fx = await _apply_post_cast_side_effects(session, server, spell_number, target, verb)`n        _refresh_post_spell_state(session, server, target)`n        session._prepared_lua_spell_number = None`n        if side_fx:`n            for _fx in side_fx.strip().splitlines():`n                if _fx.strip():`n                    await session.send_line(colorize(f`"  {_fx.strip()}`", _spell_color))"

if ($src.Contains($old2)) {
    $src = $src.Replace($old2, $new2)
    $changes++
    Write-Host "PATH 2 replaced"
} else {
    Write-Host "PATH 2 NOT FOUND"
}

# PATH 3 - incant block
$old3 = "    if ok:`n        await _apply_spell_damage(session, server, target_obj, result_dict)`n        _clear_prepared_scroll_state(session)`n        message = f`"{message}{await _apply_post_cast_side_effects(session, server, spell_number, target_obj, 'cast')}`"`n        _refresh_post_spell_state(session, server, target_obj)`n        if _is_healing_spell(session, spell_number):`n            await session.send_line(healing_msg(f`"  {message}`"))`n            await _broadcast_healing_spell(session, server, spell_number, target_obj, message)`n        else:`n            _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM`n            await session.send_line(colorize(f`"  {message}`", _spell_color))"

$new3 = "    if ok:`n        _spell_color = TextPresets.COMBAT_HIT if (result_dict.get('damage') or result_dict.get('room_damage')) else TextPresets.SYSTEM`n        if _is_healing_spell(session, spell_number):`n            await session.send_line(healing_msg(f`"  {message}`"))`n            await _broadcast_healing_spell(session, server, spell_number, target_obj, message)`n        else:`n            await session.send_line(colorize(f`"  {message}`", _spell_color))`n        await _apply_spell_damage(session, server, target_obj, result_dict)`n        _clear_prepared_scroll_state(session)`n        side_fx = await _apply_post_cast_side_effects(session, server, spell_number, target_obj, 'cast')`n        _refresh_post_spell_state(session, server, target_obj)`n        if side_fx:`n            for _fx in side_fx.strip().splitlines():`n                if _fx.strip():`n                    await session.send_line(colorize(f`"  {_fx.strip()}`", _spell_color))"

if ($src.Contains($old3)) {
    $src = $src.Replace($old3, $new3)
    $changes++
    Write-Host "PATH 3 replaced"
} else {
    Write-Host "PATH 3 NOT FOUND"
}

[System.IO.File]::WriteAllText($file, $src, [System.Text.Encoding]::UTF8)
Write-Host "Done. Total changes: $changes/3"
