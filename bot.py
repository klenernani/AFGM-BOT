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

# Constants
DATA_FILE = 'data.json'
PRIVATE_CHANNEL_ID = 1166970390900383754  # replace with your channel ID

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

# Load persisted data
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
    to_dump = {
        'last_seen': {
            str(uid): [msg, ts.isoformat()]
            for uid, (msg, ts) in last_seen.items()
        }
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(to_dump, f, indent=2)

# Bot setup (disable default help)
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=['-', 'afgm '],
    intents=intents,
    help_command=None
)

start_time = time.time()

# EVENTS
@bot.event
async def on_ready():
    print(f"🟢 Bot is ready as {bot.user}")

@bot.event
async def on_message(message):
    if not message.author.bot:
        # update last_seen and persist
        last_seen[message.author.id] = (message.content, datetime.utcnow())
        save_data()
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
        embed.add_field(name="❌ Missing Permissions", value="You do not have permission to use this command.", inline=False)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.add_field(name="❓ Missing Argument", value="A required argument is missing! Check `-help` for usage.", inline=False)
    elif isinstance(error, commands.CommandNotFound):
        embed.add_field(name="❓ Unknown Command", value="This command does not exist. Use `-help` to see valid commands.", inline=False)
    elif isinstance(error, commands.NotOwner):
        embed.add_field(name="🚫 Not Owner", value="Only the bot owner can perform this action.", inline=False)
    else:
        embed.add_field(name="⚠️ General Error", value=f"{error}", inline=False)
    await ctx.send(embed=embed)

# HELP COMMAND
@bot.command(name="help", help="Show this help message.")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Bot Commands",
        description="List of available commands, arguments & examples:",
        color=discord.Color.gold()
    )
    cmds = [
        ("-help", "Show this help message.\n**Usage:** `-help`"),
        ("-ping", "Check if the bot is responsive.\n**Usage:** `-ping`"),
        ("-8ball <question>", "Ask the magic 8 ball a question.\n**Example:** `-8ball Will we win?`"),
        ("-systeminfo", "Show basic system info.\n**Usage:** `-systeminfo`"),
        ("-play", "Remind tournament players to play.\n**Usage:** `-play`"),
        ("-makerole <role_name>", "Create a new role.\n**Example:** `-makerole Admin`"),
        ("-addrole <member> <role_name>", "Assign a role to a user.\n**Example:** `-addrole @John Admin`"),
        ("-removeallroles <member>", "Remove all roles from a member.\n**Example:** `-removeallroles @John`"),
        ("-setowner <member>", "Grant the 'Owner' role to a member.\n**Example:** `-setowner @Nani`"),
        ("-allow <member> [channel]", "Grant access to private channel.\n**Example:** `-allow @Nani`"),
        ("-userinfo [member]", "Show user info (or yourself).\n**Example:** `-userinfo @Nani`"),
        ("-avatar [member]", "Show a user's avatar.\n**Example:** `-avatar @Nani`"),
        ("-serverinfo", "Display server information.\n**Usage:** `-serverinfo`"),
        ("-roll [NdM]", "Roll dice (NdM format).\n**Example:** `-roll 2d6`"),
        ("-choose <opt1> <opt2> [...]", "Choose one option at random.\n**Example:** `-choose tea coffee`"),
        ("-lastseen [member]", "Show last message from a user.\n**Example:** `-lastseen @Nani`"),
        ("-uptime", "Show bot uptime.\n**Usage:** `-uptime`"),
        ("-reboot", "Reboot the bot (owner only).\n**Usage:** `-reboot`"),
    ]
    for name, desc in cmds:
        embed.add_field(name=name, value=desc, inline=False)
    await ctx.send(embed=embed)

# COMMANDS
@bot.command(help="Check bot responsiveness.")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {ctx.author.mention}")

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
    embed = discord.Embed(title="🛠 Create a New Role", color=discord.Color.green())
    if discord.utils.get(ctx.guild.roles, name=role_name):
        embed.add_field(name="⚠️ Error", value=f"Role `{role_name}` already exists.", inline=False)
    else:
        await ctx.guild.create_role(name=role_name)
        embed.add_field(name="✅ Success", value=f"Role `{role_name}` created.", inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Roll dice in NdM format.")
async def roll(ctx, dice: str = "1d6"):
    try:
        rolls, limit = map(int, dice.lower().split("d"))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 You rolled: {', '.join(map(str, results))}")
    except ValueError:
        await ctx.send("⚠️ Invalid dice format. Use NdM (e.g., 2d6)")

# Start the bot
bot.run(TOKEN)
