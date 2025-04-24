import discord
from discord.ext import commands
import random
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Učitavanje .env fajla
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Provera da li je token učitan
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN nije postavljen u .env fajlu!")

# Inicijalizacija bota
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=['!', '-', 'afgm '], intents=intents)

start_time = time.time()
last_seen = {}

@bot.event
async def on_ready():
    print(f"🟢 Bot je spreman kao {bot.user}")

@bot.event
async def on_message(message):
    if not message.author.bot:
        last_seen[message.author.id] = (message.content, datetime.utcnow())

        content_lower = message.content.lower()

        # Trigger reči
        if any(trigger in content_lower for trigger in ["afgm", "efmg"]) or content_lower.startswith("-"):
            await message.add_reaction("🔥")

        # Detekcija AFK
        if "afk" in content_lower:
            await message.channel.send(
                f"🚨 {message.author.mention} je označen kao AFK. Obavestićemo druge ako te pomenu."
            )

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Bot je aktivan! {ctx.author.mention}")

@bot.command()
async def _8ball(ctx, *, question=None):
    responses = ["Yes", "No", "Maybe", "Ask again later"]
    if question is None:
        await ctx.send(f"{ctx.author.mention}, moraš da postaviš pitanje!")
    else:
        await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command()
async def systeminfo(ctx):
    await ctx.send("🖥 Bot radi na Python-u sa discord.py. Za više informacija, kontaktiraj admina.")

@bot.command()
async def play(ctx):
    channel_id = 1166970462094503936
    role = discord.utils.get(ctx.guild.roles, name="League Member - AFGM")
    channel = bot.get_channel(channel_id)
    if role and channel:
        await channel.send(f"{role.mention} – 🔔 Igrači koji još nisu igrali, završite do 2 sata pre kraja turnira!")
    else:
        await ctx.send("⚠️ Nije pronađen kanal ili uloga.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def makerole(ctx, *, role_name):
    guild = ctx.guild
    existing = discord.utils.get(guild.roles, name=role_name)
    if existing:
        await ctx.send(f"Uloga `{role_name}` već postoji!")
        return
    await guild.create_role(name=role_name)
    await ctx.send(f"Uloga `{role_name}` je uspešno napravljena!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"Uloga `{role_name}` ne postoji.")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} je dobio ulogu `{role_name}`.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removeallroles(ctx, member: discord.Member):
    roles_to_remove = [role for role in member.roles if role != ctx.guild.default_role]
    if not roles_to_remove:
        await ctx.send(f"⚠️ {member.mention} nema dodatne uloge.")
        return
    await member.remove_roles(*roles_to_remove)
    await ctx.send(f"🧹 Sve uloge su uklonjene sa {member.mention}.")
    try:
        await member.send(
            f"⚠️ Sve tvoje uloge na serveru **{ctx.guild.name}** su uklonjene od strane **{ctx.author.display_name}**."
        )
    except discord.Forbidden:
        await ctx.send("❌ Ne mogu da pošaljem DM korisniku – moguće da su mu isključene poruke.")

@bot.command()
async def uptime(ctx):
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"⏱ Bot je aktivan: {hours}h {minutes}m {seconds}s")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.name for role in member.roles if role.name != "@everyone"]
    joined = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
    created = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    embed = discord.Embed(title=f"Info za {member}", color=discord.Color.green())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Ime na serveru", value=member.display_name, inline=True)
    embed.add_field(name="Nalog kreiran", value=created, inline=False)
    embed.add_field(name="Pridružio se", value=joined, inline=False)
    embed.add_field(name="Uloge", value=", ".join(roles) if roles else "Nema", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🖼 Avatar korisnika {member.mention}: {member.avatar.url if member.avatar else 'Nema avatara.'}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Nemaš dozvolu za ovu komandu.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Nedostaje argument!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Nepoznata komanda.")
    else:
        await ctx.send(f"⚠️ Greška: {error}")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 Info o serveru: {guild.name}", color=discord.Color.blurple())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
    embed.add_field(name="ID", value=guild.id)
    embed.add_field(name="Vlasnik", value=guild.owner)
    embed.add_field(name="Kreiran", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Članova", value=guild.member_count)
    embed.add_field(name="Uloga", value=len(guild.roles))
    embed.add_field(name="Kanala", value=len(guild.channels))
    await ctx.send(embed=embed)

@bot.command()
async def roll(ctx, dice: str = "1d6"):
    try:
        rolls, limit = map(int, dice.lower().split("d"))
    except Exception:
        await ctx.send("❌ Format mora biti NdM (npr. `2d6`, `1d20`)")
        return

    results = [random.randint(1, limit) for _ in range(rolls)]
    await ctx.send(f"🎲 Rezultati: {', '.join(str(r) for r in results)} | Ukupno: {sum(results)}")

@bot.command()
async def choose(ctx, *choices: str):
    if len(choices) < 2:
        await ctx.send("❗ Moraš navesti bar dve opcije (npr. `!choose pizza pasta`).")
    else:
        await ctx.send(f"🤔 Biram: **{random.choice(choices)}**")

@bot.command()
async def lastseen(ctx, member: discord.Member = None):
    member = member or ctx.author
    info = last_seen.get(member.id)
    if info:
        message, time_seen = info
        formatted_time = time_seen.strftime("%Y-%m-%d %H:%M:%S")
        await ctx.send(f"🕵️ Poslednja poruka korisnika {member.display_name}: \"{message}\" u {formatted_time} UTC")
    else:
        await ctx.send(f"❓ Nema podataka za {member.display_name}.")

# Pokretanje bota
bot.run(TOKEN)
