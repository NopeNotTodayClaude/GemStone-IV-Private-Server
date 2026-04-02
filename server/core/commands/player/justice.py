"""
Justice commands - JUSTICE, INQUIRE, ACCUSE, and community-service verbs.
"""

from __future__ import annotations


async def cmd_justice(session, cmd, args, server):
    mgr = getattr(server, "justice", None)
    if not mgr:
        await session.send_line("The justice system is unavailable right now.")
        return
    await mgr.justice(session, args)


async def cmd_inquire(session, cmd, args, server):
    del cmd, args
    mgr = getattr(server, "justice", None)
    if not mgr:
        await session.send_line("The justice system is unavailable right now.")
        return
    await mgr.inquire(session)


async def cmd_accuse(session, cmd, args, server):
    del cmd
    mgr = getattr(server, "justice", None)
    if not mgr:
        await session.send_line("The justice system is unavailable right now.")
        return
    await mgr.accuse(session, args)


async def cmd_justice_service(session, cmd, args, server):
    mgr = getattr(server, "justice", None)
    if not mgr:
        await session.send_line("Nothing happens.")
        return
    handled = await mgr.maybe_handle_service_verb(session, cmd, args)
    if not handled:
        await session.send_line("Nothing about your current justice sentence calls for that.")
