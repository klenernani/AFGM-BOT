# 📦 Imports
import os
import sys
import time
import random
import json
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# 📁 Constants
DATA_FILE = 'data.json'
PRIVATE_CHANNEL_ID = 1166970390900383754  # change if needed

# 🔑 Loading token
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file!")

# 🌐 Flask keep_alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

# 💾 Loading last user activity
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        raw = json.load(f)
    last_seen = {
        int(uid): (msg, datetime.fromisoformat(ts))
        for uid, (msg, ts) in raw.get('last_seen', {}).items()
    }
else:
    last_seen = {}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({
            'last_seen': {
                str(uid): [msg, ts.isoformat()]
                for uid, (msg, ts) in last_seen.items()
            }
        }, f, indent=2)

# 🤖 Setting up the bot
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=['-', 'afgm '],
    intents=intents,
    help_command=None
)
start_time = time.time()

# 🎯 EVENTS
@bot.event
async def on_ready():
    print(f"🟢 Bot is ready as {bot.user}")

@bot.event
async def on_message(message):
    if not message.author.bot:
        last_seen[message.author.id] = (message.content, datetime.utcnow())
        save_data()
        content = message.content.lower()

        if any(trigger in content for trigger in ["afgm", "efmg"]) or content.startswith("-"):
            await message.add_reaction("🔥")
        
        if "afk" in content:
            await message.channel.send(f"🚨 {message.author.mention} has been marked as AFK.")
    
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="⚠️ Error", color=discord.Color.red())

    if isinstance(error, commands.MissingPermissions):
        embed.add_field(name="❌ Missing Permissions", value="You do not have permission for this command.", inline=False)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.add_field(name="❓ Missing Argument", value="You did not provide the required argument. Check -help.", inline=False)
    elif isinstance(error, commands.CommandNotFound):
        embed.add_field(name="❓ Unknown Command", value="This command does not exist. Check -help.", inline=False)
    elif isinstance(error, commands.NotOwner):
        embed.add_field(name="🚫 Not the Owner", value="Only the bot owner can use this.", inline=False)
    else:
        embed.add_field(name="⚠️ General Error", value=str(error), inline=False)

    await ctx.send(embed=embed)

# 📚 Command: HELP
@bot.command(name="help", help="Show help.")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Commands",
        description="List of available commands:",
        color=discord.Color.gold()
    )
    commands_list = [
        ("-help", "Displays this help message."),
        ("-ping", "Checks if the bot is responsive."),
        ("-8ball <question>", "Ask the magic 8-ball a question."),
        ("-systeminfo", "Shows basic system information."),
        ("-play", "Reminds tournament members to play."),
        ("-makerole <name>", "Creates a new role."),
        ("-addrole <member> <role>", "Assigns a role to a member."),
        ("-removeallroles <member>", "Removes all roles from a member."),
        ("-setowner <member>", "Assigns an owner role."),
        ("-allow <member> [channel]", "Grants access to a private channel."),
        ("-userinfo [member]", "Shows user information."),
        ("-avatar [member]", "Shows user avatar."),
        ("-serverinfo", "Shows server information."),
        ("-roll [NdM]", "Rolls dice (e.g., 2d6)."),
        ("-choose <option1> <option2> [...]", "Randomly chooses an option."),
        ("-lastseen [member]", "Shows last activity of a user."),
        ("-uptime", "Shows how long the bot has been running."),
        ("-reboot", "Reboots the bot (owner only)."),
    ]
    for name, description in commands_list:
        embed.add_field(name=name, value=description, inline=False)
    
    await ctx.send(embed=embed)

# 🛠️ COMMANDS
@bot.command(help="Checks bot's response time.")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {ctx.author.mention}")

@bot.command(name="8ball", help="Ask the 8-ball a question.")
async def _8ball(ctx, *, question=None):
    if not question:
        await ctx.send(f"{ctx.author.mention}, you need to ask a question!")
    else:
        answer = random.choice(["Yes.", "No.", "Maybe.", "Ask later."])
        await ctx.send(f"🎱 {answer}")

@bot.command(help="Shows system information.")
async def systeminfo(ctx):
    await ctx.send("🖥 Running on Python + discord.py")

@bot.command(help="Reminds tournament players to play their matches.")
async def play(ctx):
    channel = bot.get_channel(1166970462094503936)
    role = discord.utils.get(ctx.guild.roles, name="League Member - AFGM")
    if channel and role:
        await channel.send(f"{role.mention} – 🔔 Reminder to play your matches!")
    else:
        await ctx.send("⚠️ Role or channel not found.")

@bot.command(help="Creates a new role.")
@commands.has_permissions(manage_roles=True)
async def makerole(ctx, *, role_name):
    if discord.utils.get(ctx.guild.roles, name=role_name):
        return await ctx.send(f"⚠️ Role {role_name} already exists.")
    await ctx.guild.create_role(name=role_name)
    await ctx.send(f"✅ Role {role_name} has been created.")

@bot.command(help="Assigns a role to a member.")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send(f"⚠️ Role {role_name} not found.")
    await member.add_roles(role)
    await ctx.send(f"✅ Role {role_name} assigned to {member.mention}.")

@bot.command(help="Removes all roles from a member.")
@commands.has_permissions(manage_roles=True)
async def removeallroles(ctx, member: discord.Member):
    roles = [r for r in member.roles if r != ctx.guild.default_role]
    if not roles:
        return await ctx.send(f"⚠️ {member.mention} has no roles.")
    await member.remove_roles(*roles)
    await ctx.send(f"🧹 All roles removed from {member.mention}.")

@bot.command(help="Assigns the owner role to a member.")
@commands.has_permissions(manage_roles=True)
async def setowner(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Owner")
    if not role:
        role = await ctx.guild.create_role(name="Owner", permissions=discord.Permissions.all())
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} is now the owner!")

@bot.command(help="Grants access to a private channel.")
@commands.has_permissions(manage_channels=True)
async def allow(ctx, member: discord.Member, channel: discord.TextChannel = None):
    channel = channel or bot.get_channel(PRIVATE_CHANNEL_ID)
    if channel:
        await channel.set_permissions(member, read_messages=True, send_messages=True)
        await ctx.send(f"✅ {member.mention} now has access to the channel {channel.mention}.")
    else:
        await ctx.send("⚠️ Channel not found.")

@bot.command(help="Shows user information.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = ', '.join([r.name for r in member.roles if r.name != "@everyone"])
    embed = discord.Embed(title=f"👤 Information about {member}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="Roles", value=roles or "No special roles", inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Shows user avatar.")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.avatar.url)

@bot.command(help="Shows server information.")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"🌍 {guild.name}", color=discord.Color.green())
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    await ctx.send(embed=embed)

@bot.command(help="Rolls dice.")
async def roll(ctx, dice: str):
    try:
        rolls, limit = map(int, dice.split('d'))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 Roll results: {', '.join(map(str, results))}")
    except ValueError:
        await ctx.send("⚠️ Invalid dice format. Use NdM (e.g., 2d6).")

@bot.command(help="Randomly selects an option.")
async def choose(ctx, *options):
    if options:
        await ctx.send(f"🎉 I choose: {random.choice(options)}")
    else:
        await ctx.send("⚠️ You need to provide options.")

@bot.command(help="Shows last seen time of a user.")
async def lastseen(ctx, member: discord.Member):
    last_msg, timestamp = last_seen.get(member.id, (None, None))
    if timestamp:
        await ctx.send(f"⏳ {member.mention} was last seen: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        await ctx.send(f"⚠️ No activity found for {member.mention}.")

@bot.command(help="Shows bot uptime.")
async def uptime(ctx):
    uptime_seconds = time.time() - start_time
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    await ctx.send(f"💻 Bot uptime: {hours} hours, {minutes} minutes.")

@bot.command(help="Reboots the bot (owner only).")
@commands.is_owner()
async def reboot(ctx):
    await ctx.send("🔄 Rebooting bot...")
    await bot.close()
    os.system("python3 bot.py")  # Change with your actual bot restart command
    sys.exit(0)

# 🔑 Running the bot
bot.run(TOKEN)
