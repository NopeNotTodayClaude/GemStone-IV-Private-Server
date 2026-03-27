"""Apply tutorial wiring patches to the codebase."""
import pathlib

# ====== PATCH 1: character_creation.py ======
f = pathlib.Path(r'N:\GemStoneIVServer\server\core\character_creation.py')
content = f.read_text(encoding='utf-8')

old_block = '        # Enter the world\n        session.state = "playing"\n        room = self.server.world.get_room(start_room)\n        if not room:\n            room = self.server.world.get_room(100)\n\n        town = room.zone.name if room and room.zone else "the world"\n\n        await session.send_line(f"\\r\\n{\'=\'*55}")\n        await session.send_line(f"  {d[\'name\']} the {d[\'race_name\']} {d[\'profession_name\']} enters the world...")\n        await session.send_line(f"  Location: {town}")\n        await session.send_line(f"{\'=\'*55}\\r\\n")\n\n        if room:\n            session.current_room = room\n            self.server.world.add_player_to_room(session, room.id)\n            await self.server.commands.handle(session, "look")\n        else:\n            await session.send("(Warning: starting room not found!)\\r\\n>")'

new_block = '        # Start the tutorial for new characters\n        await session.send_line(f"\\r\\n{\'=\'*55}")\n        await session.send_line(f"  {d[\'name\']} the {d[\'race_name\']} {d[\'profession_name\']} enters the world...")\n        await session.send_line(f"{\'=\'*55}\\r\\n")\n\n        # Route through tutorial system\n        if hasattr(self.server, \'tutorial\'):\n            await self.server.tutorial.start_tutorial(session)\n        else:\n            # Fallback: place directly in starting town\n            session.state = "playing"\n            room = self.server.world.get_room(start_room)\n            if not room:\n                room = self.server.world.get_room(100)\n            if room:\n                session.current_room = room\n                self.server.world.add_player_to_room(session, room.id)\n                await self.server.commands.handle(session, "look")\n            else:\n                await session.send("(Warning: starting room not found!)\\r\\n>")'

if old_block in content:
    content = content.replace(old_block, new_block)
    f.write_text(content, encoding='utf-8')
    print("PATCH 1 OK: character_creation.py updated")
else:
    print("PATCH 1 SKIP: old block not found in character_creation.py")
    # Find what's there
    if '# Enter the world' in content:
        print("  (marker exists but text differs)")
    else:
        print("  (marker not found - may already be patched)")
    if 'start_tutorial' in content:
        print("  (already contains start_tutorial - probably already patched)")

# ====== PATCH 2: command_router.py ======
f2 = pathlib.Path(r'N:\GemStoneIVServer\server\core\commands\command_router.py')
content2 = f2.read_text(encoding='utf-8')

# Insert tutorial interception before "# Find handler"
old2 = '        # Find handler\n        handler = self._commands.get(cmd)'
new2 = '''        # Tutorial interception - let tutorial handle commands first
        if hasattr(session, 'tutorial_complete') and not session.tutorial_complete:
            if hasattr(self.server, 'tutorial'):
                try:
                    handled = await self.server.tutorial.on_command(session, cmd, args)
                    if handled:
                        await session.send_prompt()
                        return
                except Exception as e:
                    log.error("Tutorial command error (%s): %s", raw_input, e, exc_info=True)

        # Find handler
        handler = self._commands.get(cmd)'''

if old2 in content2:
    content2 = content2.replace(old2, new2, 1)
    f2.write_text(content2, encoding='utf-8')
    print("PATCH 2 OK: command_router.py updated")
elif 'tutorial_complete' in content2:
    print("PATCH 2 SKIP: already patched")
else:
    print("PATCH 2 FAIL: marker not found")

# ====== PATCH 3: movement.py ======
f3 = pathlib.Path(r'N:\GemStoneIVServer\server\core\commands\player\movement.py')
content3 = f3.read_text(encoding='utf-8')

old3 = '    # Show the new room\n    await cmd_look(session, "look", "", server)\n'
new3 = '''    # Show the new room
    await cmd_look(session, "look", "", server)

    # Tutorial hook - trigger sprite dialogue on room enter
    if hasattr(session, 'tutorial_complete') and not session.tutorial_complete:
        if hasattr(server, 'tutorial'):
            await server.tutorial.on_room_enter(session, to_room.id)
'''

if old3 in content3:
    content3 = content3.replace(old3, new3, 1)
    f3.write_text(content3, encoding='utf-8')
    print("PATCH 3 OK: movement.py updated")
elif 'tutorial_complete' in content3:
    print("PATCH 3 SKIP: already patched")
else:
    print("PATCH 3 FAIL: marker not found")
    # Debug
    if 'cmd_look(session' in content3:
        idx = content3.index('cmd_look(session')
        print("  Near cmd_look:", repr(content3[idx:idx+80]))
