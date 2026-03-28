"""
pets.py
-------
Player-facing PET command surface and companion interaction verbs.
"""

from server.core.protocol.colors import colorize, TextPresets


async def cmd_pet(session, cmd, args, server):
    """PET verb root and petting interaction fallback."""
    mgr = getattr(server, "pets", None)
    if not mgr:
        await session.send_line("The companion system is unavailable right now.")
        return

    raw = (args or "").strip()
    if not raw:
        await mgr.cmd_status(session)
        return

    parts = raw.split(None, 1)
    sub = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""

    if sub == "help":
        await session.send_line(colorize("PET HELP", TextPresets.SYSTEM))
        await session.send_line("  PET STATUS        - Show your active companion and its abilities.")
        await session.send_line("  PET CALL          - Call your active companion back into view.")
        await session.send_line("  PET DISMISS       - Ask your companion to drift out of sight for now.")
        await session.send_line("  PET RELEASE       - Send your active companion back to Moonwhisker Menagerie.")
        await session.send_line("  PET FEED <item>   - Feed a carried training treat to your active companion.")
        await session.send_line("  PET GEAR          - Show the current gear slots on your active companion.")
        await session.send_line("  PET SHOP          - Open the Moonwhisker catalogue while inside the shop.")
        await session.send_line("  PET <target>      - Pet a visible companion or Twillip.")
        return

    if sub == "status":
        await mgr.cmd_status(session)
        return

    if sub == "call":
        await mgr.call_active_pet(session)
        return

    if sub == "dismiss":
        await mgr.dismiss_active_pet(session)
        return

    if sub == "release":
        await mgr.release_active_pet(session)
        return

    if sub == "feed":
        await mgr.feed_active_pet(session, rest)
        return

    if sub == "gear":
        pet = getattr(session, "active_pet", None)
        if not pet:
            await session.send_line("You do not currently have an active companion.")
            return
        await session.send_line(f"{pet.get('pet_name')}'s gear:")
        slots = mgr.cfg.get("pet_slots") or []
        equipment = pet.get("equipment") or {}
        for slot in slots:
            row = equipment.get(slot)
            if row and row.get("item_snapshot"):
                item_name = (row.get("item_snapshot") or {}).get("short_name") or "something"
                await session.send_line(f"  {slot.capitalize()}: {item_name}")
            else:
                await session.send_line(f"  {slot.capitalize()}: (empty)")
        return

    if sub == "shop":
        await mgr.cmd_shop(session)
        return

    if sub == "active":
        await session.send_line("Companion swapping is handled from the Moonwhisker Menagerie website while you are inside the shop.")
        return

    handled = await mgr.interact_with_visible_companion(session, "pet", raw)
    if not handled:
        await session.send_line("You don't see that companion here.")


async def cmd_touch_companion(session, cmd, args, server):
    mgr = getattr(server, "pets", None)
    if not mgr:
        await session.send_line("The companion system is unavailable right now.")
        return
    raw = (args or "").strip()
    if not raw:
        await session.send_line("Touch what?")
        return
    if not await mgr.interact_with_visible_companion(session, "touch", raw):
        await session.send_line("You don't see that here.")


async def cmd_kick_companion(session, cmd, args, server):
    mgr = getattr(server, "pets", None)
    if not mgr:
        await session.send_line("The companion system is unavailable right now.")
        return
    raw = (args or "").strip()
    if not raw:
        await session.send_line("Kick what?")
        return
    if not await mgr.interact_with_visible_companion(session, "kick", raw):
        await session.send_line("You don't see that here.")
