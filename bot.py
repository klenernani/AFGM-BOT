# 📜 Import libraries
import os
import sys
import time
import random
import json
import discord
from discord.ext import commands
from discord import ui
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup

# 📁 Constant values
DATA_FILE = 'data.json'
ANNOUNCE_CHANNEL_ID = 1166970462094503936
TOURNAMENT_CHANNEL_ID = 1166970462094503936

# 💾 Function to save data
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({
            'last_seen': {
                str(uid): [msg, ts.isoformat()]
                for uid, (msg, ts) in last_seen.items()
            }
        }, f, indent=2)

# 🔑 Load token
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not TOKEN:
    raise ValueError('❗ DISCORD_BOT_TOKEN is not set in the .env file!')

# 🌐 Keep bot alive
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is active!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run, daemon=True).start()

keep_alive()

# 🤖 Bot setup
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=['-', 'afgm '],
    intents=intents,
    help_command=None
)
start_time = time.time()

# 💾 Load previous data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        raw = json.load(f)
    last_seen = {
        int(uid): (msg, datetime.fromisoformat(ts))
        for uid, (msg, ts) in raw.get('last_seen', {}).items()
    }
else:
    last_seen = {}

# 🚀 Bot is ready
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    await bot.get_channel(ANNOUNCE_CHANNEL_ID).send(
        embed=discord.Embed(
            title="✅ Bot is now online!",
            description="Everything is running perfectly!",
            color=discord.Color.green()
        )
    )

# 📥 Message listener
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    last_seen[message.author.id] = (message.content, datetime.now())
    save_data()

# 📖 Help command
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Command List",
        description="Here are all the available commands you can use:",
        color=discord.Color.blue()
    )
    commands_list = {
        "-help": "Displays this message.",
        "-ping": "Checks if the bot is responsive.",
        "-8ball <question>": "Ask the magic 8-ball a question.",
        "-systeminfo": "Shows basic system information.",
        "-play": "Reminder to play your matches.",
        "-play1, -play2, -playmotiv, -playrelax, -playurgent": "Different match reminders.",
        "-makerole <role_name>": "Creates a new role.",
        "-addrole <member> <role>": "Assigns a role to a member.",
        "-removeallroles <member>": "Removes all roles from a member.",
        "-setowner <member>": "Sets the server owner.",
        "-allow <member> [channel]": "Grants access to a private channel.",
        "-userinfo [member]": "Displays user info.",
        "-avatar [member]": "Displays the user's avatar.",
        "-serverinfo": "Server information.",
        "-roll [NdM]": "Rolls a dice.",
        "-choose <option1> <option2> ...": "Randomly picks an option.",
        "-lastseen [member]": "Shows user's last message.",
        "-uptime": "Displays bot uptime.",
        "-reboot": "Reboots the bot (owner only)."
    }
    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)

    await ctx.send(embed=embed)

# 🎲 Dice roll
@bot.command(name='roll')
async def roll_command(ctx):
    result = random.randint(1, 100)
    embed = discord.Embed(
        title="🎲 Dice Roll Result",
        description=f"🎯 You rolled: **{result}**",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

# 🕹️ Bot uptime
@bot.command(name='uptime')
async def uptime_command(ctx):
    uptime_duration = time.time() - start_time
    days = uptime_duration // (24 * 3600)
    hours = (uptime_duration % (24 * 3600)) // 3600
    minutes = (uptime_duration % 3600) // 60
    seconds = uptime_duration % 60

    embed = discord.Embed(
        title="🕰️ Bot Uptime:",
        description=f"**{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s**",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

# 🏁 Match reminders
@bot.command(name='play')
async def play_command(ctx):
    await send_tournament_message("🔔 Players who haven't played yet, finish your matches before the tournament ends!", ctx)

@bot.command(name='play1')
async def play1_command(ctx):
    await send_tournament_message("⏰ Don’t forget to play your matches today!", ctx)

@bot.command(name='play2')
async def play2_command(ctx):
    await send_tournament_message("🎮 Play casually! Enjoy your matches!", ctx)

@bot.command(name='playmotiv')
async def playmotiv_command(ctx):
    await send_tournament_message("🔥 Give it your all! Show your best skills!", ctx)

@bot.command(name='playrelax')
async def playrelax_command(ctx):
    await send_tournament_message("🌴 Relax and enjoy the game. No stress!", ctx)

@bot.command(name='playurgent')
async def playurgent_command(ctx):
    await send_tournament_message("🚨 URGENT: Play your match now! Deadline is approaching!", ctx)

async def send_tournament_message(message, ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    await tournament_channel.send(message)
    await ctx.send("✅ Message sent!")

# 🖼️ User avatar
@bot.command(name='avatar')
async def avatar_command(ctx, user: discord.User = None):
    user = user or ctx.author
    embed = discord.Embed(
        title=f"🖼️ {user.name}'s Avatar",
        color=discord.Color.blue()
    )
    embed.set_image(url=user.avatar.url)
    await ctx.send(embed=embed)

# 🔎 Google search
@bot.command(name='google')
async def google_command(ctx, *, topic: str):
    search_url = f"https://www.google.com/search?q={topic}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_result = soup.find('h3')
    if search_result:
        link = search_result.find_parent('a')['href']
        await ctx.send(f"🔎 Top result for **{topic}**: {link}")
    else:
        await ctx.send(f"❗ No results found for **{topic}**.")

# 🛡️ Last user activity
@bot.command(name='lastseen')
async def last_seen_command(ctx, user: discord.User = None):
    user = user or ctx.author
    last_msg, last_ts = last_seen.get(user.id, (None, None))
    if last_msg and last_ts:
        embed = discord.Embed(
            title=f"🕵️ Last activity of {user.name}",
            description=f"**Message:** {last_msg}\n**Time:** {last_ts.strftime('%d.%m.%Y. %H:%M:%S')}",
            color=discord.Color.teal()
        )
    else:
        embed = discord.Embed(
            title="📭 No data",
            description=f"No recorded messages for {user.name}.",
            color=discord.Color.red()
        )
    await ctx.send(embed=embed)
