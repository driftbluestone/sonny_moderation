import discord, datetime, typing
import time as tm
from discord import app_commands
from discord.ext import commands
from api import users
from utils import config

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot=bot))

times = {
    "s": 1,
    "m": 60,
    "h": 60 * 60,
    "d": 60 * 60 * 24,
    "w": 60 * 60 * 24 * 7
}

class ModerationCommands(app_commands.Group):
    async def interaction_check(self, interaction: discord.Interaction):
        permission =  users.has_permission(interaction.user.id, "moderation")
        if not permission:
            await interaction.response.send_message(":warning: No permission", ephemeral=True)
        return permission

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    moderation = ModerationCommands(name="moderation", description=".")

    @moderation.command(name = "timeout", description = "Timeout member")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, time: str, reason: typing.Optional[str] = "No reason provided."):
        try:
            num = int(time)
            value = "m"
        except:
            try:
                num = int(time[:-1])
                value = time[-1]
            except:
                return await interaction.response.send_message("Invalid time input")
        if value not in times:
            return await interaction.response.send_message("Invalid time input")
        num *= times[value]
        if interaction.user.id == user.id:
            return await interaction.response.send_message("Cannot timeout yourself!")
        if num > (60 * 60 * 24 * 7 * 4):
            return await interaction.response.send_message("Duration too long, max 28 days.")
        if (user.id not in config.server_config["bot_admins"]) or (interaction.guild.roles.index(interaction.user.roles[-1]) <= interaction.guild.roles.index(user.roles[-1])):
            return await interaction.response.send_message("Cannot timeout user: user has role(s) above or equal")
        
        duration = datetime.timedelta(seconds=num)
        await user.timeout(duration, reason=reason)
        embed = discord.Embed(description = f"{user.mention} timed out until <t:{int(tm.time()) + num}:S>\nReason: `{reason}`")
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @timeout.error
    async def command_error(self, interaction: discord.Interaction, error: Exception):
        return await interaction.response.send_message(str(error))