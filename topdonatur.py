import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

DONATUR_FILE = "data/donatur.json"

def load_donatur():
    if not os.path.exists(DONATUR_FILE):
        with open(DONATUR_FILE, 'w') as f:
            json.dump({}, f)
    with open(DONATUR_FILE, 'r') as f:
        return json.load(f)

def save_donatur(data):
    with open(DONATUR_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class TopDonatur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def donasi(self, ctx, amount: int):
        user_id = str(ctx.author.id)
        data = load_donatur()
        now = datetime.utcnow().isoformat()

        if user_id not in data:
            data[user_id] = []
        data[user_id].append({"amount": amount, "timestamp": now})
        save_donatur(data)

        await ctx.send(f"✅ {ctx.author.mention} berhasil mencatat donasi sebesar **Rp{amount:,}**!")

    @commands.command()
    async def topdonatur(self, ctx):
        data = load_donatur()
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)

        ranking = []
        for user_id, entries in data.items():
            total = sum(entry['amount'] for entry in entries if datetime.fromisoformat(entry['timestamp']) > one_week_ago)
            if total > 0:
                ranking.append((int(user_id), total))

        if not ranking:
            return await ctx.send("⚠️ Belum ada donasi minggu ini.")

        ranking.sort(key=lambda x: x[1], reverse=True)
        message = "**🏆 Top Donatur Minggu Ini:**\n\n"
        for i, (uid, amount) in enumerate(ranking[:10], start=1):
            user = await self.bot.fetch_user(uid)
            message += f"**{i}. {user.name}** - Rp{amount:,}\n"

        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(TopDonatur(bot))
