import discord
from discord.ext import commands
import random
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file!")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=['!', '-', 'afgm '], intents=intents, help_command=commands.DefaultHelpCommand())

start_time = time.time()
last_seen = {}

@bot.event
async def on_ready():
    print(f"🟢 Bot is ready as {bot.user}")

@bot.event
async def on_message(message):
    if not message.author.bot:
        last_seen[message.author.id] = (message.content, datetime.utcnow())

        content_lower = message.content.lower()
        if any(trigger in content_lower for trigger in ["afgm", "efmg"]) or content_lower.startswith("-"):
            await message.add_reaction("🔥")

        if "afk" in content_lower:
            await message.channel.send(f"🚨 {message.author.mention} is marked as AFK. Others will be notified if they mention you.")

    await bot.process_commands(message)

@bot.command(help="Check if the bot is active and responsive.")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {ctx.author.mention}")

@bot.command(name="_8ball", help="Ask the magic 8 ball a question.")
async def _8ball(ctx, *, question=None):
    responses = ["Yes", "No", "Maybe", "Ask again later"]
    if question is None:
        await ctx.send(f"{ctx.author.mention}, you must ask a question!")
    else:
        await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command(help="Show basic system info about the bot.")
async def systeminfo(ctx):
    await ctx.send("🖥 This bot is running on Python with discord.py. Contact the admin for more info.")

@bot.command(help="Notify tournament players to finish their games.")
async def play(ctx):
    channel_id = 1166970462094503936
    role = discord.utils.get(ctx.guild.roles, name="League Member - AFGM")
    channel = bot.get_channel(channel_id)
    if role and channel:
        await channel.send(f"{role.mention} – 🔔 Reminder to finish your games 2 hours before the tournament ends!")
    else:
        await ctx.send("⚠️ Role or channel not found.")

@bot.command(help="Create a new role.")
@commands.has_permissions(manage_roles=True)
async def makerole(ctx, *, role_name):
    guild = ctx.guild
    existing = discord.utils.get(guild.roles, name=role_name)
    if existing:
        await ctx.send(f"The role `{role_name}` already exists.")
        return
    await guild.create_role(name=role_name)
    await ctx.send(f"The role `{role_name}` has been created!")

@bot.command(help="Add a role to a member.")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"The role `{role_name}` does not exist.")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} has been given the `{role_name}` role.")

@bot.command(help="Remove all roles from a member.")
@commands.has_permissions(manage_roles=True)
async def removeallroles(ctx, member: discord.Member):
    roles_to_remove = [role for role in member.roles if role != ctx.guild.default_role]
    if not roles_to_remove:
        await ctx.send(f"⚠️ {member.mention} has no extra roles.")
        return
    await member.remove_roles(*roles_to_remove)
    await ctx.send(f"🧹 All roles have been removed from {member.mention}.")
    try:
        await member.send(f"⚠️ All your roles on **{ctx.guild.name}** were removed by **{ctx.author.display_name}**.")
    except discord.Forbidden:
        await ctx.send("❌ Could not send a DM to the user.")

@bot.command(help="Show how long the bot has been running.")
async def uptime(ctx):
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"⏱ Bot uptime: {hours}h {minutes}m {seconds}s")

@bot.command(help="Show info about a user.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.name for role in member.roles if role.name != "@everyone"]
    joined = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
    created = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    embed = discord.Embed(title=f"User Info: {member}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Display Name", value=member.display_name, inline=True)
    embed.add_field(name="Account Created", value=created, inline=False)
    embed.add_field(name="Joined Server", value=joined, inline=False)
    embed.add_field(name="Roles", value=", ".join(roles) if roles else "None", inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Get a user's avatar.")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🖼 Avatar of {member.mention}: {member.avatar.url if member.avatar else 'No avatar set.'}")

@bot.command(help="Show information about the server.")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 Server Info: {guild.name}", color=discord.Color.blurple())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
    embed.add_field(name="ID", value=guild.id)
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Channels", value=len(guild.channels))
    await ctx.send(embed=embed)

@bot.command(help="Roll dice in NdM format (e.g., 2d6, 1d20).")
async def roll(ctx, dice: str = "1d6"):
    try:
        rolls, limit = map(int, dice.lower().split("d"))
    except Exception:
        await ctx.send("❌ Format must be NdM (e.g., `2d6`, `1d20`)")
        return

    results = [random.randint(1, limit) for _ in range(rolls)]
    await ctx.send(f"🎲 Results: {', '.join(str(r) for r in results)} | Total: {sum(results)}")

@bot.command(help="Choose randomly between given options.")
async def choose(ctx, *choices: str):
    if len(choices) < 2:
        await ctx.send("❗ You must provide at least two choices (e.g., `!choose pizza pasta`).")
    else:
        await ctx.send(f"🤔 I choose: **{random.choice(choices)}**")

@bot.command(help="Check the last message a user sent.")
async def lastseen(ctx, member: discord.Member = None):
    member = member or ctx.author
    info = last_seen.get(member.id)
    if info:
        message, time_seen = info
        formatted_time = time_seen.strftime("%Y-%m-%d %H:%M:%S")
        await ctx.send(f"🕵️ Last message from {member.display_name}: \"{message}\" at {formatted_time} UTC")
    else:
        await ctx.send(f"❓ No data found for {member.display_name}.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required argument!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Unknown command.")
    else:
        await ctx.send(f"⚠️ Error: {error}")

bot.run(TOKEN)
