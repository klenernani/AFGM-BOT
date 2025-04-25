import os 
import sys
import time
import random
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file!")

# Flask server to keep the bot alive on Railway
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# Bot setup (disable default help)
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=['-', 'afgm '], 
    intents=intents,
    help_command=None
)

start_time = time.time()
last_seen = {}

#  EVENTS
@bot.event
async def on_ready():
    print(f"🟢 Bot is ready as {bot.user}")

@bot.event
async def on_message(message):
    if not message.author.bot:
        last_seen[message.author.id] = (message.content, datetime.utcnow())
        content = message.content.lower()
        if any(trigger in content for trigger in ["afgm", "efmg"]) or content.startswith("-"):
            await message.add_reaction("🔥")
        if "afk" in content:
            await message.channel.send(f"🚨 {message.author.mention} is marked as AFK.")
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="⚠️ Error Occurred", color=discord.Color.red())
    if isinstance(error, commands.MissingPermissions):
        embed.add_field(name="❌ Missing Permissions",
                        value="You do not have permission to use this command.", inline=False)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.add_field(name="❓ Missing Argument",
                        value="A required argument is missing! Check the usage.", inline=False)
    elif isinstance(error, commands.CommandNotFound):
        embed.add_field(name="❓ Unknown Command",
                        value="This command does not exist. Use `-help` to see valid commands.", inline=False)
    elif isinstance(error, commands.NotOwner):
        embed.add_field(name="🚫 Not Owner",
                        value="Only the bot owner can perform this action.", inline=False)
    else:
        embed.add_field(name="⚠️ General Error", value=f"{error}", inline=False)
    await ctx.send(embed=embed)

#  HELP COMMAND
@bot.command(name="help", help="Show this help message.")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Bot Commands",
        description="List of available commands, arguments & examples:",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="-help",
        value="Show this help message.\n**Usage:** `-help`",
        inline=False
    )
    embed.add_field(
        name="-ping",
        value="Check if the bot is responsive.\n**Usage:** `-ping`",
        inline=False
    )
    embed.add_field(
        name="-8ball <question>",
        value="Ask the magic 8 ball a question.\n**Example:** `-8ball Will we win?`",
        inline=False
    )
    embed.add_field(
        name="-systeminfo",
        value="Show basic system info.\n**Usage:** `-systeminfo`",
        inline=False
    )
    embed.add_field(
        name="-play",
        value="Remind tournament players to play.\n**Usage:** `-play`",
        inline=False
    )
    embed.add_field(
        name="-makerole <role_name>",
        value="Create a new role.\n**Argument:** role_name — name of the role\n**Example:** `-makerole Admin`",
        inline=False
    )
    embed.add_field(
        name="-addrole <member> <role_name>",
        value="Assign a role to a user.\n**Example:** `-addrole @John Admin`",
        inline=False
    )
    embed.add_field(
        name="-removeallroles <member>",
        value="Remove all roles from a member.\n**Example:** `-removeallroles @John`",
        inline=False
    )
    embed.add_field(
        name="-userinfo [member]",
        value="Show user info (or yourself).\n**Example:** `-userinfo @Nani`",
        inline=False
    )
    embed.add_field(
        name="-avatar [member]",
        value="Show a user's avatar.\n**Example:** `-avatar @Nani`",
        inline=False
    )
    embed.add_field(
        name="-serverinfo",
        value="Display server information.\n**Usage:** `-serverinfo`",
        inline=False
    )
    embed.add_field(
        name="-roll [NdM]",
        value="Roll dice (NdM format).\n**Example:** `-roll 2d6`",
        inline=False
    )
    embed.add_field(
        name="-choose <opt1> <opt2> [...optN]",
        value="Choose one option at random.\n**Example:** `-choose tea coffee`",
        inline=False
    )
    embed.add_field(
        name="-lastseen [member]",
        value="Show last message from a user.\n**Example:** `-lastseen @Nani`",
        inline=False
    )
    embed.add_field(
        name="-uptime",
        value="Show bot uptime.\n**Usage:** `-uptime`",
        inline=False
    )
    embed.add_field(
        name="-reboot",
        value="Reboot the bot (owner only).\n**Usage:** `-reboot`",
        inline=False
    )
    await ctx.send(embed=embed)

#  COMMANDS
@bot.command(help="Check bot responsiveness.")
async def ping(ctx):
    await ctx.send(f"Wonna play🏓 Pong! {ctx.author.mention}") 

@bot.command(name="8ball", help="Ask the magic 8 ball a question.")
async def _8ball(ctx, *, question=None):
    responses = ["Yes", "No", "Maybe", "Ask again later"]
    if not question:
        await ctx.send(f"{ctx.author.mention}, you must ask a question!")
    else:
        await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command(help="Get basic system info.")
async def systeminfo(ctx):
    await ctx.send("🖥 Running on Python + discord.py")

@bot.command(help="Remind members to play their matches.")
async def play(ctx):
    channel_id = 1166970462094503936
    role = discord.utils.get(ctx.guild.roles, name="League Member - AFGM")
    channel = bot.get_channel(channel_id)
    if role and channel:
        await channel.send(f"{role.mention} – 🔔 Reminder to play your matches!")
    else:
        await ctx.send("⚠️ Role or channel not found.")

@bot.command(help="Create a new role.")
@commands.has_permissions(manage_roles=True)
async def makerole(ctx, *, role_name):
    embed = discord.Embed(
        title="🛠 Create a New Role",
        description=f"Processing `{role_name}`...",
        color=discord.Color.green()
    )
    if discord.utils.get(ctx.guild.roles, name=role_name):
        embed.clear_fields()
        embed.add_field(name="⚠️ Error", value=f"Role `{role_name}` already exists.", inline=False)
    else:
        await ctx.guild.create_role(name=role_name)
        embed.clear_fields()
        embed.add_field(name="✅ Success", value=f"Role `{role_name}` created.", inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Assign a role to a member.")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name):
    embed = discord.Embed(
        title="🔧 Assign Role",
        description=f"Assigning `{role_name}` to {member.mention}...",
        color=discord.Color.blue()
    )
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        embed.clear_fields()
        embed.add_field(name="⚠️ Error", value=f"Role `{role_name}` not found.", inline=False)
    else:
        await member.add_roles(role)
        embed.clear_fields()
        embed.add_field(name="✅ Success", value=f"Assigned `{role_name}` to {member.mention}.", inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Remove all roles from a member.")
@commands.has_permissions(manage_roles=True)
async def removeallroles(ctx, member: discord.Member):
    roles = [r for r in member.roles if r != ctx.guild.default_role]
    if not roles:
        return await ctx.send(f"⚠️ {member.mention} has no roles to remove.")
    await member.remove_roles(*roles)
    await ctx.send(f"🧹 Removed all roles from {member.mention}.")
    try:
        await member.send(f"⚠️ All your roles have been removed in {ctx.guild.name}.")
    except discord.Forbidden:
        pass

@bot.command(help="Show user info.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(
        title="User Information",
        color=discord.Color.blue(),
        description=f"Information for {member.mention}"
    )
    embed.add_field(name="Username", value=member.name, inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role != ctx.guild.default_role]), inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Show a user's avatar.")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.green()
    )
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command(help="Display server information.")
async def serverinfo(ctx):
    embed = discord.Embed(
        title="Server Information",
        description=f"Details about {ctx.guild.name}",
        color=discord.Color.orange()
    )
    embed.add_field(name="Server Name", value=ctx.guild.name, inline=False)
    embed.add_field(name="Server ID", value=ctx.guild.id, inline=False)
    embed.add_field(name="Members", value=len(ctx.guild.members), inline=False)
    embed.add_field(name="Created On", value=ctx.guild.created_at.strftime("%b %d, %Y"), inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Roll dice.")
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
        result = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 You rolled: {', '.join(map(str, result))}")
    except ValueError:
        await ctx.send("⚠️ Invalid dice format. Use NdM format (e.g., 2d6).")

@bot.command(help="Choose one option randomly.")
async def choose(ctx, *choices: str):
    await ctx.send(f"🎉 I choose: {random.choice(choices)}")

@bot.command(help="Show last seen messages.")
async def lastseen(ctx, member: discord.Member = None):
    member = member or ctx.author
    last_message, last_time = last_seen.get(member.id, ("No messages", "Never"))
    embed = discord.Embed(
        title=f"Last seen message for {member.name}",
        description=f"Message: {last_message}\nTime: {last_time}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command(help="Show bot uptime.")
async def uptime(ctx):
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"⏱ Bot uptime: {hours}h {minutes}m {seconds}s")

#  OWNER ONLY COMMAND
@bot.command(help="Reboot the bot.")
@commands.is_owner()
async def reboot(ctx):
    await ctx.send("🔄 Rebooting bot...")
    await bot.close()

bot.run(TOKEN)
