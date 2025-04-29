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

# 💾 Save the data
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

# 🌐 Keep alive
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is UP!"

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

# 🚀 Bot Ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.get_channel(ANNOUNCE_CHANNEL_ID).send('Bot is now online and running!')

# 📥 On Message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    last_seen[message.author.id] = (message.content, datetime.now())
    save_data()

# 📖 Help Command
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Command List",
        description="Available commands:",
        color=discord.Color.green()
    )
    embed.add_field(name="-help", value="Displays this message.", inline=False)
    embed.add_field(name="-ping", value="Checks if the bot is responding.", inline=False)
    embed.add_field(name="-8ball <question>", value="Ask the magic ball a question.", inline=False)
    embed.add_field(name="-systeminfo", value="Shows basic system information.", inline=False)
    embed.add_field(name="-play", value="Motivational message for matches.", inline=False)
    embed.add_field(name="-play1", value="Quick reminder for matches.", inline=False)
    embed.add_field(name="-play2", value="Freestyle play reminder.", inline=False)
    embed.add_field(name="-playmotiv", value="Ultra motivational reminder.", inline=False)
    embed.add_field(name="-playrelax", value="Relaxed play reminder.", inline=False)
    embed.add_field(name="-playurgent", value="Urgent match reminder.", inline=False)
    embed.add_field(name="-makerole <role_name>", value="Create a new role.", inline=False)
    embed.add_field(name="-addrole <member> <role>", value="Assign a role to a member.", inline=False)
    embed.add_field(name="-removeallroles <member>", value="Remove all roles from a member.", inline=False)
    embed.add_field(name="-setowner <member>", value="Assign ownership role.", inline=False)
    embed.add_field(name="-allow <member> [channel]", value="Grant access to a private channel.", inline=False)
    embed.add_field(name="-userinfo [member]", value="Displays user information.", inline=False)
    embed.add_field(name="-avatar [member]", value="Displays user avatar.", inline=False)
    embed.add_field(name="-serverinfo", value="Server information.", inline=False)
    embed.add_field(name="-roll [NdM]", value="Rolls dice (example: 2d6).", inline=False)
    embed.add_field(name="-choose <option1> <option2> ...", value="Randomly choose an option.", inline=False)
    embed.add_field(name="-lastseen [member]", value="Shows last seen message.", inline=False)
    embed.add_field(name="-uptime", value="Displays bot uptime.", inline=False)
    embed.add_field(name="-reboot", value="Reboots the bot (owner only).", inline=False)

    await ctx.send(embed=embed)

# 🎲 Roll Command
@bot.command(name='roll')
async def roll_command(ctx):
    result = random.randint(1, 100)
    embed = discord.Embed(
        title="🎲 Dice Roll Result",
        description=f"You rolled: {result}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

# 🕹️ Uptime Command
@bot.command(name='uptime')
async def uptime_command(ctx):
    uptime_duration = time.time() - start_time
    days = uptime_duration // (24 * 3600)
    hours = (uptime_duration % (24 * 3600)) // 3600
    minutes = (uptime_duration % 3600) // 60
    seconds = uptime_duration % 60

    embed = discord.Embed(
        title="🕰️ Bot Uptime",
        description=f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

# 🏁 Play Commands
@bot.command(name='play')
async def play_command(ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    message = "<@&1166971437802864660> – 🔔 Players who haven't played yet, please finish before 2 hours before the tournament ends!"
    await tournament_channel.send(message)
    await ctx.send("Reminder message sent!")

@bot.command(name='play1')
async def play1_command(ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    message = "⏰ Don't forget to play your matches today!"
    await tournament_channel.send(message)
    await ctx.send("Quick reminder sent!")

@bot.command(name='play2')
async def play2_command(ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    message = "🎮 Freestyle! Play at your best pace and enjoy the matches!"
    await tournament_channel.send(message)
    await ctx.send("Freestyle reminder sent!")

@bot.command(name='playmotiv')
async def playmotiv_command(ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    message = "🔥 Push yourself! Show your best skills and make your team proud!"
    await tournament_channel.send(message)
    await ctx.send("Motivational reminder sent!")

@bot.command(name='playrelax')
async def playrelax_command(ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    message = "🌴 Relax and enjoy your matches. Have fun and stay calm!"
    await tournament_channel.send(message)
    await ctx.send("Relaxed reminder sent!")

@bot.command(name='playurgent')
async def playurgent_command(ctx):
    tournament_channel = bot.get_channel(TOURNAMENT_CHANNEL_ID)
    message = "🚨 URGENT: Play your match immediately! Deadline approaching!"
    await tournament_channel.send(message)
    await ctx.send("Urgent reminder sent!")

# 🖼️ Avatar
@bot.command(name='avatar')
async def avatar_command(ctx, user: discord.User = None):
    user = user or ctx.author
    embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=user.avatar.url)
    await ctx.send(embed=embed)

# 🔎 Google Search
@bot.command(name='google')
async def google_command(ctx, *, topic: str):
    search_url = f"https://www.google.com/search?q={topic}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_result = soup.find('h3')
    if search_result:
        link = search_result.find_parent('a')['href']
        await ctx.send(f"Top result for '{topic}': {link}")
    else:
        await ctx.send(f"No results found for '{topic}'.")

# 🛡️ Last Seen
@bot.command(name='lastseen')
async def last_seen_command(ctx, user: discord.User = None):
    user = user or ctx.author
    last_msg, last_ts = last_seen.get(user.id, (None, None))
    embed = discord.Embed(
        title=f"Last message from {user.name}",
        description=f"Message: '{last_msg}'\nTimestamp: {last_ts}",
        color=discord.Color.blue()
    )
    if last_msg:
        await ctx.send(embed=embed)
    else:
        embed.description = f"{user.mention} has not sent any messages yet."
        await ctx.send(embed=embed)

# 🏁 Start the bot
bot.run(TOKEN)
