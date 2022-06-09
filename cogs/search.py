from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context, hybrid_command

from bot import MyClient
from views.pages import Pages


class Search(commands.Cog):
    def __init__(self, client: MyClient):
        self.client = client

    def make_page(self, hit) -> dict[str, discord.Embed | str]:
        if hit["type"] != "song":
            return
        hit = hit["result"]
        embed = discord.Embed(
            title=f"{hit['title']} - {hit['artist_names']}", url=hit["url"]
        )
        embed.set_image(url=hit["song_art_image_url"])
        embed.set_footer(text=f"Lyrics Bot by cde")
        embed.set_author(
            name=hit["primary_artist"]["name"],
            icon_url=hit["primary_artist"]["image_url"],
        )
        rd = hit["release_date_components"]
        if rd:
            embed.add_field(
                name="Release Date", value=f"{rd['day']}/{rd['month']}/{rd['year']}"
            )
        return {
            "embed": embed,
            "song_id": hit["id"],
            "hit": hit,
            "song_url": hit["url"],
        }

    @hybrid_command()
    async def search(self, ctx: Context, *, query: str):
        """Search for a given query"""
        query = quote(query)
        headers = {"Authorization": "Bearer " + self.client.config.GENIUS_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f"https://api.genius.com/search?q={query}"
            ) as response:
                jres = await response.json()

                # TEMPORARY
                # with open("data.json", "w") as f:
                #     json.dump(jres, f, indent=4)
                # await ctx.send(file=discord.File("data.json"))
                # END TEMPORARY

                if jres["meta"]["status"] != 200:
                    return await ctx.send("Something went wrong!")

                if not jres["response"]["hits"]:
                    return await ctx.send("No results found!")

                pages = [self.make_page(hit) for hit in jres["response"]["hits"]]

                e = pages[0]["embed"]
                e.set_footer(text=f"Page 1/{len(pages)} - Lyrics Bot by cde")
                await ctx.send(view=Pages(self.client, pages), embed=e)


async def setup(client: MyClient):
    await client.add_cog(Search(client))
