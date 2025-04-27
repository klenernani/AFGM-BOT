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
ANNOUNCE_CHANNEL_ID = 1166970462094503936  # kanal za boot-up poruku

# 🔑 Loading TOKEN
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    raise ValueError('**❗ DISCORD_BOT_TOKEN is not set in `.env` file!**')

# 🌐 Flask server to keep bot alive
app = Flask('')

@app.route('/')
def home():
    return "**✅ Bot is active!**"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run, daemon=True).start()

keep_alive()

# 🤖 Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=['-', 'afgm '],
    intents=intents,
    help_command=None
)
start_time = time.time()

# 💾 Loading previous data
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
        json.dump({'last_seen': {
            str(uid): [msg, ts.isoformat()]
            for uid, (msg, ts) in last_seen.items()
        }}, f, indent=2)

# 🔍 Checking ROLE
def is_league_admin():
    async def predicate(ctx):
        role = discord.utils.get(ctx.guild.roles, name='League Admin - AFGM')
        return role in ctx.author.roles
    return commands.check(predicate)

# 🎯 Events
@bot.event
async def on_ready():
    print(f"🟢 Bot is ready as {bot.user}")

    # Izabrani kanal gde bot šalje poruku
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        await channel.send("🚀 **Bot is up and ready!!**")
    else:
        print("⚠️ Kanal nije pronađen!")

@bot.event
async def on_message(message):
    if not message.author.bot:
        last_seen[message.author.id] = (message.content, datetime.utcnow())
        save_data()
        content = message.content.lower()
        if any(trigger in content for trigger in ['afgm', 'efmg']) or content.startswith('-'):
            await message.add_reaction('🔥')
        if 'afk' in content:
            await message.channel.send(
                embed=discord.Embed(
                    description=f"🚨 **{message.author.mention}** has been marked as _AFK_.",
                    color=discord.Color.red()
                )
            )
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title='⚠️ Error', color=discord.Color.red())
    if isinstance(error, commands.MissingPermissions):
        embed.add_field(name='❌ Missing Permissions', value='_You do not have permission to use this command._', inline=False)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.add_field(name='❓ Missing Argument', value='_A required argument was not provided. Check `-help`._', inline=False)
    elif isinstance(error, commands.CommandNotFound):
        embed.add_field(name='❓ Unknown Command', value='_This command does not exist. Check `-help`._', inline=False)
    elif isinstance(error, commands.NotOwner):
        embed.add_field(name='🚫 Not Owner', value='_Only the bot owner can use this command._', inline=False)
    else:
        embed.add_field(name='⚠️ General Error', value=f'_{str(error)}_', inline=False)
    await ctx.send(embed=embed)

# 📚 HELP Command
@bot.command(name='help', help='Displays a list of all commands.')
async def help_command(ctx):
    embed = discord.Embed(
        title='📖 **Command List**',
        description='_Available commands:_',
        color=discord.Color.blue()
    )
    cmds = [
        ('-help', 'Displays this message.'),
        ('-ping', 'Checks if the bot is responding.'),
        ('-8ball <question>', 'Ask the magic ball a question.'),
        ('-systeminfo', 'Shows basic system information.'),
        ('-play', 'Motivational message for matches.'),
        ('-play1', 'Quick reminder for matches.'),
        ('-play2', 'Freestyle play reminder.'),
        ('-playmotiv', 'Ultra motivational reminder.'),
        ('-playrelax', 'Relaxed play reminder.'),
        ('-playurgent', 'Urgent match reminder.'),
        ('-makerole <role_name>', 'Create a new role.'),
        ('-addrole <member> <role>', 'Assign a role to a member.'),
        ('-removeallroles <member>', 'Remove all roles from a member.'),
        ('-setowner <member>', 'Assign ownership role.'),
        ('-allow <member> [channel]', 'Grant access to a private channel.'),
        ('-userinfo [member]', 'Displays user information.'),
        ('-avatar [member]', 'Displays user avatar.'),
        ('-serverinfo', 'Server information.'),
        ('-roll [NdM]', 'Rolls dice (example: 2d6).'),
        ('-choose <option1> <option2> ...', 'Randomly choose an option.'),
        ('-lastseen [member]', 'Shows last seen message.'),
        ('-uptime', 'Displays bot uptime.'),
        ('-reboot', 'Reboots the bot (owner only).'),
    ]
    for name, desc in cmds:
        embed.add_field(name=f'**{name}**', value=f'_{desc}_', inline=False)
    await ctx.send(embed=embed)

# 🛠️ Basic Commands
@bot.command(help='Ask bot if he is ready to serve.')
async def ping(ctx):
    await ctx.send(embed=discord.Embed(
        description=f" **I'm ready to serve** :saluting_face: {ctx.author.mention}",
        color=discord.Color.green()
    ))

@bot.command(name='8ball', help='Ask the magic ball a question.')
async def _8ball(ctx, *, question=None):
    if not question:
        return await ctx.send(embed=discord.Embed(
            description=f"🎱 {ctx.author.mention}, _you must ask a question!_",
            color=discord.Color.red()
        ))
    responses = ['Yes.', 'No.', 'Maybe.', 'Ask later.']
    await ctx.send(embed=discord.Embed(
        description=f"🎱 _{random.choice(responses)}_",
        color=discord.Color.purple()
    ))

@bot.command(help='Shows system information.')
async def systeminfo(ctx):
    await ctx.send(embed=discord.Embed(
        description='🖥 **Bot runs on Python + discord.py for any help ask @n00b **',
        color=discord.Color.teal()
    ))

# 🔥 Start the bot
if __name__ == '__main__':
    bot.run(TOKEN)
