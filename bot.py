import asyncio
import discord
from discord.ext import commands
import lyricsgenius
import os
import re

import config


class MyClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config.Config()
        self.genius = lyricsgenius.Genius(self.config.GENIUS_KEY)
        self.genius.verbose = False
        self.genius.remove_section_headers = True

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    def get_lyrics(self, song_url):
        lrc = self.genius.lyrics(song_url=song_url)
        lrc = lrc.removesuffix("Embed")
        lrc = re.sub(r"\d+$", "", lrc)
        return lrc


async def main():

    intents = discord.Intents.default()

    client = MyClient(intents=intents, command_prefix=commands.when_mentioned_or("!"))
    client.remove_command("help")

    async with client:

        for filename in os.listdir("cogs"):
            if filename.endswith(".py"):
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename[:-3]}")

        await client.start(client.config.BOT_TOKEN)


if __name__ == "__main__":

    asyncio.run(main())
