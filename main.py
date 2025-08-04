import dotenv import load_dotenv
import os

load_dotenv()
import discord
from discord.ext import commands
import json, os, re
from datetime import datetime, timedelta
from keep_alive import keep_alive

TOKEN ="os.getenv("DISCORD_TOKEN")
DONATE_CHANNEL_ID = 1396728149798289519
LEVI_ID = 854982878869717002
HUNTER_ROLE_NAME = "Hunters"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

DONASI_FILE = 'donasi.json'
BANNED_WORDS_FILE = 'banned_words.txt'
PELANGGARAN_FILE = 'pelanggaran.json'
MOD_ROLE = "Marshall"

def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def normalize(text):
    replacements = {
        '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '0': 'o', '@': 'a',
        '$': 's', '!': 'i', '|': 'i', '+': 't'
    }
    text = text.lower()
    for key, val in replacements.items():
        text = text.replace(key, val)
    return re.sub(r'[^a-z\s]', '', text)

def is_toxic(text):
    if not os.path.exists(BANNED_WORDS_FILE):
        return False
    with open(BANNED_WORDS_FILE, 'r') as f:
        banned = [line.strip().lower() for line in f]
    normalized = normalize(text)
    return any(word in normalized.split() for word in banned)

@bot.event
async def on_ready():
    print(f'🤖 Bot {bot.user} sudah online!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # ✅ Balas jika disebut "Ares" atau "Ashborn"
    if "ashborn" in content or "ares" in content:
        await message.channel.send(f"KEINGINANMU ADALAH PERINTAH BAGIKU TUAN {message.author.mention}")

    # ✅ Balas jika disuruh beri semangat
    if "beri" in content and "semangat deh" in content and message.mentions:
        target = message.mentions[0]
        semangat_quote = (
            f"💥 SEMANGAT SELALU {target.mention}!\n"
            f"JANGAN PERNAH RAGU UNTUK MELANGKAH MAJU. 🔥 HIDUP INI MILIKMU, KUATKAN LANGKAHMU, TAKLUKKAN DUNIA! 💪"
        )
        await message.channel.send(semangat_quote)

    # ✅ Balas kalau nama Levi disebut
    levi_keywords = ["leps", "lepps", "levi", "lep"]
    if any(keyword in content for keyword in levi_keywords):
        user = await bot.fetch_user(LEVI_ID)
        await message.channel.send(f" JIKA {user.mention} TIDAK MENJAWAB SAAT DI PANGGIL  ARTINYA SEDANG BEKERJA ATAU BERMAIN BLOOD STRIKE")

    # ✅ Lockdown
    if "lockdown" in content:
        overwrite = discord.PermissionOverwrite(send_messages=False)
        for channel in message.guild.text_channels:
            await channel.set_permissions(message.guild.default_role, overwrite=overwrite)
        await message.channel.send("🔒 Semua channel telah di-lockdown tuanku.")

    # ✅ Buka lockdown
    if "sudahi" in content:
        overwrite = discord.PermissionOverwrite(send_messages=True)
        for channel in message.guild.text_channels:
            await channel.set_permissions(message.guild.default_role, overwrite=overwrite)
        await message.channel.send("✅ Lockdown telah dihentikan, semua channel dibuka kembali tuanku.")

    # ✅ Filter kata kasar
    if is_toxic(message.content):
        pelanggaran = load_json(PELANGGARAN_FILE, {})
        user_id = str(message.author.id)
        pelanggaran[user_id] = pelanggaran.get(user_id, 0) + 1
        save_json(PELANGGARAN_FILE, pelanggaran)

        role = discord.utils.get(message.guild.roles, name=MOD_ROLE)
        if role:
            await message.channel.send(f"⚠ {message.author.mention} berkata kasar! {role.mention} mohon ditindak.")
        else:
            await message.channel.send(f"{message.author.mention} berkata kasar! (Role {MOD_ROLE} tidak ditemukan)")

    # ✅ Donasi terdeteksi
    if message.channel.id == DONATE_CHANNEL_ID and "DONATE:" in message.content.upper():
        match = re.search(r'DONATE:\s*(\S+)', message.content, re.IGNORECASE)
        if match:
            jumlah = match.group(1).strip()
            now = datetime.utcnow()
            data = load_json(DONASI_FILE, [])
            data.append({
                "user_id": message.author.id,
                "username": str(message.author),
                "amount": jumlah,
                "timestamp": now.isoformat()
            })
            save_json(DONASI_FILE, data)
            await message.channel.send(
                f"💎 {message.author.mention} TELAH DONASI SEJUMLAH {jumlah} gems KE guild!\n🔥 GUILD AKAN BERTAMBAH KUAT DENGAN BANTUAN MU SALAM DESTROYER!!."
            )

    # ✅ Deteksi kata "inf" atau "desert"
    if "inf" in content or "ds" in content:
        hunter_role = discord.utils.get(message.guild.roles, name=HUNTER_ROLE_NAME)
        if hunter_role:
            await message.channel.send(
                f"BAIKLAH TUAN {message.author.mention}, AKU AKAN MEMANGGIL PARA {hunter_role.mention} UNTUK MEMBANTU ANDA SALAM DESTROYER!"
            )
        else:
            await message.channel.send(
                f"BAIKLAH TUAN {message.author.mention}, NAMUN ROLE 'HUNTERS' TIDAK DITEMUKAN!"
            )

    await bot.process_commands(message)

@bot.command(name="dailycheck")
async def daily_check(ctx):
    now = datetime.utcnow()
    batas = now - timedelta(days=1)
    data = load_json(DONASI_FILE, [])
    recent = [d for d in data if datetime.fromisoformat(d["timestamp"]) > batas]

    if not recent:
        await ctx.send("💤 Belum ada donasi dalam 24 jam terakhir.")
        return

    msg = "📊 Donasi 24 Jam Terakhir:\n"
    for d in recent:
        jam = datetime.fromisoformat(d["timestamp"]).strftime('%H:%M')
        msg += f"🔹 {d['username']} - {d['amount']} gems (jam {jam} UTC)\n"
    await ctx.send(msg)

@bot.command(name="topdonatur")
async def top_donatur(ctx):
    data = load_json(DONASI_FILE, [])
    now = datetime.utcnow()
    batas = now - timedelta(days=7)

    filtered = [d for d in data if datetime.fromisoformat(d["timestamp"]) > batas]
    user_total = {}

    for d in filtered:
        user_total[d['username']] = user_total.get(d['username'], 0)
        try:
            angka = int(re.sub(r'\D', '', d['amount']))
            user_total[d['username']] += angka
        except:
            continue

    if not user_total:
        await ctx.send("Belum ada donatur minggu ini.")
        return

    sorted_data = sorted(user_total.items(), key=lambda x: x[1], reverse=True)[:5]
    msg = "🏆 TOP DONATUR MINGGU INI ADALAH :\n"
    for i, (user, total) in enumerate(sorted_data, 1):
        msg += f"{i}. {user} - {total} gems\n"
    await ctx.send(msg)

@bot.command(name="rekap")
async def rekap_pelanggaran(ctx, member: discord.Member):
    pelanggaran = load_json(PELANGGARAN_FILE, {})
    user_id = str(member.id)
    jumlah = pelanggaran.get(user_id, 0)
    await ctx.send(f"📛 REKAP PELANGGARAN YANG TELAH DILAKUKAN OLEH {member.mention}: SEBANYAK {jumlah} PELANGGARAN TERDETEKSI.")

keep_alive()
bot.run(TOKEN)
