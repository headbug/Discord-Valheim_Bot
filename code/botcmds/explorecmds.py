import discord
import logging
from discord import app_commands
from discord.ext import commands
from config import (
    LOG_LEVEL,
    LOGCHAN_ID,
    PLOC_CMD,
    DISCORD_SERVER,
)


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class Explored(commands.Cog):
    """
    Explored commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_app_command_error(self, interaction, error) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            logger.error(f"MissingPermissions from command {interaction.command.name}, User: {interaction.user.name}, {error}")
            await interaction.response.send_message(
                f'Command "{interaction.command.name}" gave error {error}',
                ephemeral=True,
            )
        if isinstance(error, app_commands.errors.CheckFailure):
            logger.error(f"CheckFailure from command {interaction.command.name}, User: {interaction.user.name}, {error}")
            await interaction.response.send_message(
                f'Command "{interaction.command.name}" gave error {error}',
                ephemeral=True,
            )
        else:
            logger.error(f"An error occurred! User: {interaction.user.name}, {error}")
            await interaction.response.send_message(
                "An error occurred!", ephemeral=True
            )

    async def chancheck(interaction: discord.Integration):
        if interaction.channel.id == LOGCHAN_ID or commands.is_owner():
            return True

    @app_commands.command(
        name="explored",
        description="Shows total world locations and how many have be explored.",
    )
    @app_commands.checks.has_any_role(PLOC_CMD)
    @app_commands.check(chancheck)
    async def explored(self, interaction: discord.Integration):
        ldrembed = discord.Embed(title="World Explored Stats", color=0x33A163)
        botsql = self.bot.get_cog("BotSQL")
        mycursor = await botsql.get_cursor()
        sql = """SELECT COUNT(*) FROM plocinfo WHERE locations IS NULL"""
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        sql1 = """SELECT locations FROM plocinfo WHERE locations IS NOT NULL LIMIT 1"""
        mycursor.execute(sql1)
        Info1 = mycursor.fetchall()
        mycursor.close()
        Info = Info[0]
        Info1 = Info1[0]
        ldrembed.add_field(
            name="Total Locations", value="{}".format(Info1[0]), inline=True
        )
        ldrembed.add_field(
            name="Locations Explored", value="{}".format(Info[0]), inline=True
        )
        ldrembed.add_field(
            name="Percent of World Explored",
            value="{}%".format(format(Info[0] / int(Info1[0]) * 100, ".2f")),
            inline=True,
        )
        await interaction.response.send_message(embed=ldrembed)


async def setup(bot):
    await bot.add_cog(Explored(bot), guilds=[discord.Object(id=DISCORD_SERVER)])
