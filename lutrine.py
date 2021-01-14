import discord
from discord.ext import commands
import random
import requests
import youtube_dl
import os
import traceback
import ctypes

# Client (bot)
token = ''

bot = commands.Bot(command_prefix='~')
bot.remove_command('help')
ctypes.util.find_library('lib')


@bot.event
async def on_ready():
    print('logged in as ' + bot.user.name)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=getActivity()))


async def downloadAttachment(url):
    r = requests.get(url, allow_redirects=False)
    open('attachment.png', 'wb').write(r.content)


def getActivity():
    activity = ["Peko Chan", "Gawr Gura", "Korone Chan", "Rushia"]
    return random.choice(activity)

@bot.command()
async def ping(ctx):
    await ctx.channel.send("pong")


@bot.command(aliases=['help'])
async def use(ctx):
    await ctx.channel.send(
        "```welcome! I don't have many commands right now! to issue a command, use '~'. Here's what I "
        "can do!\n\nping: issue this command to see if I'm alive!"
        "\n\ndownload: WIP, issue this command followed by a url to get a youtube"
        " clip sent to you!```")


@bot.command()
async def download(ctx, url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': 'True'
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.cache.remove()
            info_dict = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info_dict)
            ydl.download([url])
            file = discord.File(filename)
            await ctx.send(file=file, content="here's your video!")
            os.remove(filename)
    except Exception:
        await ctx.send("hmmm... I couldn't find that one. check the url and try again!")


def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


def get_voice_client(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client


@bot.command()
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send('wait for the song to end, or use the \'stop\' command')
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
    else:
        await ctx.send("please connect to a voice channel first!")
    if not is_connected(ctx):
        await channel.connect()
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    get_voice_client(ctx).play(discord.FFmpegPCMAudio("song.mp3"))


@bot.command()
async def disconnect(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("I'm not connected to a voice channel at the moment!")


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('no audio is playing right now!')


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('audio is not paused!')


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@bot.event
async def on_command_error(ctx, error):
    send_help = (commands.errors.MissingRequiredArgument, commands.errors.BadArgument,
                 commands.errors.TooManyArguments, commands.errors.UserInputError)
    if isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, send_help):
        _help = await commandHelp(ctx)
        await ctx.send(embed=_help)
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("sorry, you don't have the permissions to use this command!")
    else:
        print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))


async def commandHelp(ctx):
    cmd = ctx.command
    em = discord.Embed(title=f'Usage: {ctx.message.content} {cmd.signature}')
    em.color = discord.Color.blurple()
    em.description = cmd.help
    return em


# Run the client on the server
bot.run(token)
