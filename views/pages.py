import io
from typing import Optional

import discord

from bot import MyClient


class Button(discord.ui.Button):
    def __init__(self, callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback


class Pages(discord.ui.View):
    def __init__(self, client: MyClient, data: list[dict[str, discord.Embed | str]]):
        super().__init__()
        self.data = data
        self.index = 0
        self.client = client

        self.add_item(
            Button(
                label="≪",
                style=discord.ButtonStyle.grey,
                callback=self.go_to_first_page,
            )
        )
        self.add_item(
            Button(
                label="Back", style=discord.ButtonStyle.blurple, callback=self.go_back
            )
        )
        self.add_item(
            discord.ui.Button(
                label=f"1/{len(self.data)}",
                custom_id="current:page",
                disabled=True,
                style=discord.ButtonStyle.grey,
            )
        )
        self.add_item(
            Button(
                label="Next", style=discord.ButtonStyle.blurple, callback=self.go_next
            )
        )
        self.add_item(
            Button(
                label="≫", style=discord.ButtonStyle.grey, callback=self.go_to_last_page
            )
        )
        self.add_item(
            Button(
                label="Lyrics",
                style=discord.ButtonStyle.green,
                callback=self.get_lyrics_page,
                custom_id="lyrics:main",
            )
        )
        self.add_item(
            Button(label="Close", style=discord.ButtonStyle.red, callback=self.close)
        )

    async def on_timeout(self) -> None:
        if hasattr(self, "message"):
            await self.message.edit(view=None)

    async def update_page(
        self,
        interaction: discord.Interaction,
        etype: Optional[str] = None,
        file: Optional[discord.File] = None,
    ):
        for item in self.children:
            if item.custom_id and item.custom_id == "current:page":
                item.label = f"{self.index + 1}/{len(self.data)}"
                break
        if interaction.response.is_done():
            if hasattr(self, "message"):
                e = (
                    self.data[self.index]["embed"]
                    if etype != "lyrics"
                    else self.data[self.index]["lyrics"]
                )
                await self.message.edit(
                    embed=e, view=self, attachments=[file] if file else []
                )
            else:
                e = (
                    self.data[self.index]["embed"]
                    if etype != "lyrics"
                    else self.data[self.index]["lyrics"]
                )
                await interaction.followup.edit_message(
                    embed=e,
                    view=self,
                    message_id=interaction.message.id,
                    attachments=[file] if file else [],
                )
        else:
            e = (
                self.data[self.index]["embed"]
                if etype != "lyrics"
                else self.data[self.index]["lyrics"]
            )
            await interaction.response.edit_message(
                embed=e, view=self, attachments=[file] if file else []
            )

    async def go_to_first_page(self, interaction: discord.Interaction):
        self.index = 0
        await self.update_page(interaction)

    async def go_back(self, interaction: discord.Interaction):
        if self.index > 0:
            self.index -= 1
            await self.update_page(interaction)

    async def go_next(self, interaction: discord.Interaction):
        if self.index < len(self.data) - 1:
            self.index += 1
            await self.update_page(interaction)

    async def go_to_last_page(self, interaction: discord.Interaction):
        self.index = len(self.data) - 1
        await self.update_page(interaction)

    async def get_lyrics_page(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if "lyrics" in self.data[self.index] and "lyrics_file" in self.data[self.index]:
            await self.update_page(
                interaction, "lyrics", self.data[self.index]["lyrics_file"]
            )

        song_url = self.data[self.index]["song_url"]
        lyrics = self.client.get_lyrics(song_url)
        fp = io.StringIO(lyrics)
        file = discord.File(fp, filename="lyrics.txt")
        lyrics = "\n".join(lyrics.split("\n")[1:])
        if len(lyrics) > 500:
            lyrics = lyrics[:500] + "..."
        hit = self.data[self.index]["hit"]

        embed = discord.Embed(
            title=f"{hit['title']} - {hit['artist_names']}", url=hit["url"]
        )
        embed.set_thumbnail(url=hit["song_art_image_url"])
        embed.set_footer(text=f"Lyrics Bot by cde")
        embed.set_author(
            name=hit["primary_artist"]["name"],
            icon_url=hit["primary_artist"]["image_url"],
        )
        embed.add_field(name="Lyrics", value=f"```{lyrics}```")

        self.data[self.index]["lyrics"] = embed
        self.data[self.index]["lyrics_file"] = file

        await self.update_page(interaction, "lyrics", file)

    async def close(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_message()
        self.stop()
