import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
import asyncio

# Intencje bota
intents = discord.Intents.default()
intents.message_content = True

# Ustawienia bota
bot = commands.Bot(command_prefix="!", intents=intents, help_command=commands.DefaultHelpCommand())
# Ścieżka do FFmpeg
FFMPEG_PATH = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")

# Kolejka odtwarzania (zmieniamy nazwę zmiennej, aby uniknąć kolizji z komendą)
music_queue = []

# Funkcja do wyszukiwania filmów na YouTube
def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return info['entries'][0]['url'] if 'entries' in info else None

# Połączenie z voice channel i odtwarzanie muzyki
@bot.command()
async def play(ctx, *, query: str):
    global music_queue

    if not ctx.author.voice:
        await ctx.send("Dołącz do kanału głosowego, zanim wpiszesz komendę!")
        return

    voice_channel = ctx.author.voice.channel

    # Jeśli bot nie jest na kanale, dołącz
    if ctx.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = ctx.voice_client

    def play_next(_):
        if music_queue:
            next_url = music_queue.pop(0)
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(next_url, download=False)
                vc.play(discord.FFmpegPCMAudio(source=info['url'], executable=FFMPEG_PATH), after=play_next)
                bot.loop.create_task(ctx.send(f"Odtwarzam: {info['title']}"))
        else:
            bot.loop.create_task(vc.disconnect())

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    # Sprawdzanie, czy podano pełny URL, czy zapytanie do wyszukania
    if query.startswith("http"):
        url = query
    else:
        url = search_youtube(query)
        if url is None:
            await ctx.send("Nie znaleziono wyników dla tego zapytania.")
            return

    if vc.is_playing():
        music_queue.append(url)
        await ctx.send("Dodano do kolejki.")
    else:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            vc.play(discord.FFmpegPCMAudio(source=info['url'], executable=FFMPEG_PATH), after=play_next)
            await ctx.send(f"Odtwarzam: {info['title']}")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Pominięto utwór.")
    else:
        await ctx.send("Nie ma żadnego utworu do pominięcia.")

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Muzyka została zatrzymana.")
    else:
        await ctx.send("Aktualnie nie odtwarzam muzyki.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Wznawiam odtwarzanie.")
    else:
        await ctx.send("Muzyka już jest odtwarzana.")

@bot.command()
async def quit(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Rozłączyłem się z kanału głosowego.")
    else:
        await ctx.send("Nie jestem na żadnym kanale głosowym.")

@bot.command()
async def queue(ctx):
    global music_queue

    if not music_queue:
        await ctx.send("Kolejka jest pusta!")
    else:
        queue_list = "\n".join([f"{i+1}. {url}" for i, url in enumerate(music_queue)])
        await ctx.send(f"**Aktualna kolejka:**\n{queue_list}")

@bot.command()
async def myhelp(ctx):
    help_message = """
**Dostępne komendy:**
- `!play <URL>` - Odtwarza utwór z podanego linku YouTube lub nazwy utworu.
- `!pause` - Zatrzymuje odtwarzanie muzyki.
- `!resume` - Wznawia odtwarzanie muzyki.
- `!skip` - Pomija aktualnie odtwarzany utwór.
- `!queue` - Wyświetla aktualną kolejkę utworów.
- `!quit` - Bot opuszcza kanał głosowy.
"""
    await ctx.send(help_message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and not after.channel:
        return

    vc = discord.utils.get(bot.voice_clients, guild=member.guild)
    if vc and len(vc.channel.members) == 1:  # Tylko bot jest na kanale
        await asyncio.sleep(300)  # Czeka 5 minut
        if len(vc.channel.members) == 1:  # Nadal tylko bot
            await vc.disconnect()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Nie rozpoznano komendy. Wpisz `!myhelp`, aby zobaczyć dostępne komendy.")
@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel is None:
        print("Bot opuścił kanał głosowy, próba ponownego połączenia...")
        await asyncio.sleep(5)  # Poczekaj chwilę przed próbą połączenia
        if after.channel is None:  # Jeśli bot nadal nie jest połączony
            voice_channel = discord.utils.get(member.guild.voice_channels, name="NazwaTwojegoKanału")
            if voice_channel:
                await voice_channel.connect()
@bot.event
async def on_voice_state_update(member, before, after):
    print(f"Voice state update: {member} - Before: {before} - After: {after}")
# Uruchamianie bota
bot.run("YOUR DC TOKEN")
