"""
Commands for spell-created summons such as Floating Disk and Spirit Servant.
"""


async def cmd_dismiss(session, cmd, args, server):
    mgr = getattr(server, "spell_summons", None)
    if mgr and await mgr.handle_dismiss(session, args):
        return
    await session.send_line("Dismiss what?")


async def cmd_turn(session, cmd, args, server):
    mgr = getattr(server, "spell_summons", None)
    if mgr and await mgr.handle_turn(session, args):
        return
    await session.send_line("Turning that has no effect.")


async def cmd_recover(session, cmd, args, server):
    mgr = getattr(server, "spell_summons", None)
    if mgr and await mgr.handle_recover(session, args):
        return
    await session.send_line("Recover what?")
