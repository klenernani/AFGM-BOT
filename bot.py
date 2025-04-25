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
PRIVATE_CHANNEL_ID = 1166970390900383754  # zameni sa ID-jem tvog kanala

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the .env file!")

# Flask “keep alive”
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    Thread(target=run).start()
keep_alive()

# Load persisted last_seen
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

# Bot setup
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
        embed.add_field(name="❌ Missing Permissions",
                        value="You do not have permission to use this command.",
                        inline=False)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.add_field(name="❓ Missing Argument",
                        value="A required argument is missing! Check `-help`.",
                        inline=False)
    elif isinstance(error, commands.CommandNotFound):
        embed.add_field(name="❓ Unknown Command",
                        value="This command does not exist. Use `-help`.",
                        inline=False)
    elif isinstance(error, commands.NotOwner):
        embed.add_field(name="🚫 Not Owner",
                        value="Only the bot owner can perform this action.",
                        inline=False)
    else:
        embed.add_field(name="⚠️ General Error",
                        value=str(error),
                        inline=False)
    await ctx.send(embed=embed)

# HELP
@bot.command(name="help", help="Show this help message.")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Bot Commands",
        description="List of available commands, arguments & examples:",
        color=discord.Color.gold()
    )
    cmds = [
        ("-help", "Show this help message.\nUsage: `-help`"),
        ("-ping", "Check if the bot is responsive.\nUsage: `-ping`"),
        ("-8ball <question>", "Ask the magic 8 ball.\nExample: `-8ball Will I win?`"),
        ("-systeminfo", "Show basic system info.\nUsage: `-systeminfo`"),
        ("-play", "Remind tournament players.\nUsage: `-play`"),
        ("-makerole <role_name>", "Create a new role.\nExample: `-makerole Admin`"),
        ("-addrole <member> <role_name>", "Assign a role.\nExample: `-addrole @User Admin`"),
        ("-removeallroles <member>", "Remove all roles.\nExample: `-removeallroles @User`"),
        ("-setowner <member>", "Grant Owner role.\nExample: `-setowner @User`"),
        ("-allow <member> [channel]", "Unlock private channel.\nExample: `-allow @User`"),
        ("-userinfo [member]", "Show user info.\nExample: `-userinfo @User`"),
        ("-avatar [member]", "Show avatar.\nExample: `-avatar @User`"),
        ("-serverinfo", "Display server info.\nUsage: `-serverinfo`"),
        ("-roll [NdM]", "Roll dice (NdM).\nExample: `-roll 2d6`"),
        ("-choose <opt1> <opt2> [...]", "Pick random option.\nExample: `-choose red blue`"),
        ("-lastseen [member]", "Show last message.\nExample: `-lastseen @User`"),
        ("-uptime", "Show bot uptime.\nUsage: `-uptime`"),
        ("-reboot", "Reboot the bot (owner only).\nUsage: `-reboot`"),
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
    choices = ["Yes", "No", "Maybe", "Ask again later"]
    if not question:
        return await ctx.send(f"{ctx.author.mention}, you must ask a question!")
    await ctx.send(f"🎱 {random.choice(choices)}")

@bot.command(help="Show basic system info.")
async def systeminfo(ctx):
    await ctx.send("🖥 Running on Python + discord.py")

@bot.command(help="Remind tournament players to play.")
async def play(ctx):
    ch = bot.get_channel(1166970462094503936)
    role = discord.utils.get(ctx.guild.roles, name="League Member - AFGM")
    if ch and role:
        await ch.send(f"{role.mention} – 🔔 Reminder to play your matches!")
    else:
        await ctx.send("⚠️ Role or channel not found.")

@bot.command(help="Create a new role.")
@commands.has_permissions(manage_roles=True)
async def makerole(ctx, *, role_name):
    if discord.utils.get(ctx.guild.roles, name=role_name):
        return await ctx.send(f"⚠️ Role `{role_name}` already exists.")
    await ctx.guild.create_role(name=role_name)
    await ctx.send(f"✅ Role `{role_name}` created.")

@bot.command(help="Assign a role to a member.")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.send(f"⚠️ Role `{role_name}` not found.")
    await member.add_roles(role)
    await ctx.send(f"✅ Assigned `{role_name}` to {member.mention}.")

@bot.command(help="Remove all roles from a member.")
@commands.has_permissions(manage_roles=True)
async def removeallroles(ctx, member: discord.Member):
    roles = [r for r in member.roles if r != ctx.guild.default_role]
    if not roles:
        return await ctx.send(f"⚠️ {member.mention} has no roles.")
    await member.remove_roles(*roles)
    await ctx.send(f"🧹 Removed all roles from {member.mention}.")

@bot.command(help="Grant the 'Owner' role to a member.")
@commands.has_permissions(manage_roles=True)
async def setowner(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Owner")
    if not role:
        role = await ctx.guild.create_role(name="Owner", permissions=discord.Permissions.all())
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} is now an Owner.")

@bot.command(help="Allow a member into a private channel.")
@commands.has_permissions(manage_channels=True)
async def allow(ctx, member: discord.Member, channel: discord.TextChannel = None):
    channel = channel or bot.get_channel(PRIVATE_CHANNEL_ID)
    await channel.set_permissions(member, read_messages=True, send_messages=True)
    await ctx.send(f"✅ {member.mention} can now see {channel.mention}.")

@bot.command(help="Show user info.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [r.name for r in member.roles if r.name != "@everyone"]
    embed = discord.Embed(title=f"{member}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Name", value=member.display_name, inline=True)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Roles", value=", ".join(roles) or "None", inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Show a user's avatar.")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=discord.Color.purple())
    embed.set_image(url=member.avatar.url if member.avatar else discord.Embed.Empty)
    await ctx.send(embed=embed)

@bot.command(help="Display server info.")
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"Server Info: {g.name}", color=discord.Color.blurple())
    embed.add_field(name="ID", value=g.id, inline=False)
    embed.add_field(name="Owner", value=g.owner, inline=False)
    embed.add_field(name="Created", value=g.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Members", value=g.member_count, inline=False)
    embed.add_field(name="Roles", value=len(g.roles), inline=False)
    embed.add_field(name="Channels", value=len(g.channels), inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Roll dice in NdM format.")
async def roll(ctx, dice: str = "1d6"):
    try:
        rolls, limit = map(int, dice.lower().split("d"))
        results = [random.randint(1, limit) for _ in range(rolls)]
        await ctx.send(f"🎲 You rolled: {', '.join(map(str, results))}")
    except:
        await ctx.send("⚠️ Use NdM format (e.g. `-roll 2d6`)")

@bot.command(help="Choose one option at random.")
async def choose(ctx, *options: str):
    if len(options) < 2:
        return await ctx.send("❗ Provide at least two options.")
    await ctx.send(f"🤔 I choose: **{random.choice(options)}**")

@bot.command(help="Show last message from a user.")
async def lastseen(ctx, member: discord.Member = None):
    member = member or ctx.author
    msg, ts = last_seen.get(member.id, ("No messages", "Never"))
    await ctx.send(f"🕵️ Last seen for {member.display_name}: \"{msg}\" at {ts}")

@bot.command(help="Show bot uptime.")
async def uptime(ctx):
    delta = int(time.time() - start_time)
    h, rem = divmod(delta, 3600)
    m, s = divmod(rem, 60)
    await ctx.send(f"⏱ Uptime: {h}h {m}m {s}s")

@bot.command(help="Reboot the bot (owner only).")
@commands.is_owner()
async def reboot(ctx):
    await ctx.send("🔄 Rebooting...")
    await bot.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# Start the bot
bot.run(TOKEN)
