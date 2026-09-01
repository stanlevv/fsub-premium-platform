#Kymang

import sys
import traceback
import asyncio  # noqa: F401 — tersedia di eval() scope
import os  # noqa: F401 — tersedia di eval() scope
import subprocess
import time  # noqa: F401 — tersedia di eval() scope
from io import BytesIO, StringIO
from os import execvp
from sys import executable
from subprocess import Popen, PIPE, TimeoutExpired  # noqa: F401 — tersedia di eval() scope

from hydrogram import filters

from Kymang import bot
from Kymang.config import ADMINS


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "\n chat = message.chat"
        + "\n r = message.reply_to_message"
        + "\n c = client"
        + "\n m = message"
        + "\n p = print"
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def restart():
    execvp(executable, [executable, "-m", "Kymang"])


@bot.on_message(filters.command("update"))
async def _(_, message):
    try:
        out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
        if "Already up to date." in str(out):
            return await message.reply_text("Its already up-to date!")
        await message.reply_text(f"```{out}```")
    except Exception as e:
        return await message.reply_text(str(e))
    await message.reply_text("**Updated with default branch, restarting now.**")
    await restart()


@bot.on_message(filters.user(ADMINS) & filters.command("eval"))
async def _(client, message):
    cmd = message.text.split(" ", maxsplit=1)[1]
    if len(message.command) < 2:
        return await message.reply("Silahkan kombinasikan dengan kode")
    status_message = await message.reply_text("Processing ...")
    reply_to_ = message.reply_to_message if message.reply_to_message else message
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "**EVAL**: "
    final_output += f"`{cmd}`\n\n"
    final_output += "**OUTPUT**:\n"
    final_output += f"`{evaluation.strip()}` \n"

    if len(final_output) > 4096:
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[: 4096 // 4 - 1],
                disable_notification=True,
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, quote=True)
    await status_message.delete()
