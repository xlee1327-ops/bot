import discord
from discord.ext import commands
import json
import os
from datetime import datetime

VIOLATION_FILE = "data/violations.json"

def load_violations():
    if not os.path.exists(VIOLATION_FILE):
        with open(VIOLATION_FILE, 'w') as f:
            json.dump({}, f)
    with open(VIOLATION_FILE, 'r') as f:
        return json.load(f)

def save_violations(data):
    with open(VIOLATION_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class Pelanggaran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Auto detect kata toxic
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        badwords = ["anjing", "bangsat", "kontol", "memek"]  # bisa load dari json
        for word in badwords:
            if word in message.content.lower():
                data = load_violations()
                uid = str(message.author.id)
                if uid not in data:
                    data[uid] = []
                data[uid].append({
                    "kata": word,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": message.content
                })
                save_violations(data)
                await message.delete()
                await message.channel.send(f"{message.author.mention} ⚠️ kata tidak pantas terdeteksi!")
                break

    # Command lihat rekap pelanggaran pribadi
    @commands.command()
    async def pelanggaranku(self, ctx):
        data = load_violations()
        uid = str(ctx.author.id)

        if uid not in data or len(data[uid]) == 0:
            await ctx.send("✅ Kamu belum memiliki pelanggaran.")
            return

        message = f"**📄 Rekap pelanggaran {ctx.author.mention}:**\n"
        for i, pel in enumerate(data[uid][-10:], start=1):
            waktu = datetime.fromisoformat(pel['timestamp']).strftime('%Y-%m-%d %H:%M')
            message += f"{i}. `{pel['kata']}` pada {waktu}\n"
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Pelanggaran(bot))
