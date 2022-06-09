from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context

from bot import MyClient


class Sync(commands.Cog):
    def __init__(self, client: MyClient):
        self.client = client

    @commands.command()
    async def sync(self, ctx: Context, guild_id: Optional[int] = None):
        """Syncronise the bot with the guild"""
        await ctx.reply("Syncing commands...")
        if guild_id:
            guild = discord.Object(id=guild_id)
            self.client.tree.copy_global_to(guild=guild)
            await self.client.tree.sync(guild=guild)
        else:
            await self.client.tree.sync()
        await ctx.send("Done!")


async def setup(client: MyClient):
    await client.add_cog(Sync(client))
