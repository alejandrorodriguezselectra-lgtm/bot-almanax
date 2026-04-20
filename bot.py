import os
import requests
import discord
from discord.ext import commands
from datetime import datetime
import asyncio
from zoneinfo import ZoneInfo

TOKEN_BOT = os.getenv("TOKEN_BOT")

# Ahora sí en español
lang = "es"

# Canal para el envío automático diario
channel_name = "almanax"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_sent_date = None


def build_message():
    madrid_now = datetime.now(ZoneInfo("Europe/Madrid"))
    date_en = madrid_now.strftime("%Y-%m-%d")
    date_fr = madrid_now.strftime("%d/%m/%Y")

    url = f"https://api.dofusdu.de/dofus3/v1/{lang}/almanax/{date_en}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    response_data = response.json()

    daily_bonus = response_data["bonus"]["type"]["name"]
    daily_bonus_description = response_data["bonus"]["description"]
    item_name = response_data["tribute"]["item"]["name"]
    item_quantity = response_data["tribute"]["quantity"]

    message = (
        f"🔥 **Almanax - Guerreros Fénix** 🔥\n\n"
        f"📅 {date_fr}\n"
        f"✨ Bonus: {daily_bonus}\n"
        f"📜 Descripción: {daily_bonus_description}\n"
        f"🎁 Ofrenda: {item_quantity}x {item_name}\n\n"
        f"⚔️ ¡A por ello, gremio!"
    )

    return message

async def send_to_named_channel():
    channel = discord.utils.get(bot.get_all_channels(), name=channel_name)

    if not channel:
        print(f"No encontré el canal '{channel_name}'.")
        return False

    try:
        message = build_message()
        await channel.send(message)
        print(f"Mensaje enviado en #{channel_name}.")
        return True
    except Exception as error:
        print(f"Error al enviar en #{channel_name}: {error}")
        return False


async def send_to_channel(channel):
    try:
        message = build_message()
        await channel.send(message)
        print(f"Mensaje enviado en el canal actual: {channel.name}")
        return True
    except Exception as error:
        print(f"Error al enviar en el canal actual: {error}")
        return False


async def madrid_scheduler():
    global last_sent_date

    while True:
        now_madrid = datetime.now(ZoneInfo("Europe/Madrid"))
        current_date = now_madrid.strftime("%Y-%m-%d")
        current_time = now_madrid.strftime("%H:%M")

        if current_time == "00:01" and last_sent_date != current_date:
            ok = await send_to_named_channel()
            if ok:
                last_sent_date = current_date

        await asyncio.sleep(1)


@bot.event
async def on_ready():
    print(f"Bot listo como {bot.user}.")

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as error:
        print(f"Error sincronizando slash commands: {error}")

    bot.loop.create_task(madrid_scheduler())


@bot.tree.command(name="almanax", description="Publica el Almanax del día en este canal")
async def almanax(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    ok = await send_to_channel(interaction.channel)

    if ok:
        await interaction.followup.send("Almanax enviado en este canal.", ephemeral=True)
    else:
        await interaction.followup.send(
            "No pude enviarlo. Mira PowerShell para ver el error exacto.",
            ephemeral=True
        )


bot.run(TOKEN_BOT)
