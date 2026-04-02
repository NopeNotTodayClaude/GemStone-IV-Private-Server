"""
Inn commands.
"""


async def cmd_check_in(session, cmd, args, server):
    inns = getattr(server, "inns", None)
    if not inns:
        await session.send_line("Inn services are unavailable right now.")
        return
    await inns.check_in(session)


async def cmd_check_out(session, cmd, args, server):
    inns = getattr(server, "inns", None)
    if not inns:
        await session.send_line("Inn services are unavailable right now.")
        return
    await inns.check_out(session)


async def cmd_check_room(session, cmd, args, server):
    inns = getattr(server, "inns", None)
    if not inns:
        await session.send_line("Inn services are unavailable right now.")
        return
    await inns.check_room(session)


async def cmd_latch(session, cmd, args, server):
    inns = getattr(server, "inns", None)
    if not inns:
        await session.send_line("Inn services are unavailable right now.")
        return
    await inns.latch(session, True)


async def cmd_unlatch(session, cmd, args, server):
    inns = getattr(server, "inns", None)
    if not inns:
        await session.send_line("Inn services are unavailable right now.")
        return
    await inns.latch(session, False)


async def cmd_invite(session, cmd, args, server):
    inns = getattr(server, "inns", None)
    if not inns:
        await session.send_line("Inn services are unavailable right now.")
        return
    await inns.invite(session, args)
