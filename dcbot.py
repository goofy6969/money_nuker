import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def create_channels(guild, base_name, num_channels, message):
    tasks = []
    for i in range(1, num_channels + 1):
        channel_name = f"{base_name}_{i}"
        tasks.append(create_channel(guild, channel_name, message))
    await asyncio.gather(*tasks)

async def create_channel(guild, channel_name, message):
    while True:
        try:
            channel = await guild.create_text_channel(channel_name)
            await channel.send(f"@everyone {message}")
            print(f"Created and pinged: {channel_name}")
            break
        except discord.errors.HTTPException as e:
            if e.status == 429:  
                retry_after = int(e.headers.get('Retry-After', 1))
                print(f"Rate limited. Waiting {retry_after} seconds before retrying.")
                await asyncio.sleep(retry_after)
            else:
                print(f"Failed to create channel {channel_name}: {e}")
                break

async def delete_non_matching_channels(guild, base_name):
    tasks = []
    for channel in guild.text_channels + guild.voice_channels:
        if base_name not in channel.name:
            tasks.append(delete_channel(channel))
    await asyncio.gather(*tasks)

async def delete_channel(channel):
    while True:
        try:
            await channel.delete()
            print(f"Deleted: {channel.name}")
            break
        except discord.errors.HTTPException as e:
            if e.status == 429:  
                retry_after = int(e.headers.get('Retry-After', 1))
                print(f"Rate limited. Waiting {retry_after} seconds before retrying.")
                await asyncio.sleep(retry_after)
            else:
                print(f"Failed to delete channel {channel.name}: {e}")
                break

@bot.event
async def on_ready():
    print("\033[32m" + r"""

███╗░░░███╗░█████╗░███╗░░██╗███████╗██╗░░░██╗  ███╗░░██╗██╗░░░██╗██╗░░██╗███████╗██████╗░
████╗░████║██╔══██╗████╗░██║██╔════╝╚██╗░██╔╝  ████╗░██║██║░░░██║██║░██╔╝██╔════╝██╔══██╗
██╔████╔██║██║░░██║██╔██╗██║█████╗░░░╚████╔╝░  ██╔██╗██║██║░░░██║█████═╝░█████╗░░██████╔╝
██║╚██╔╝██║██║░░██║██║╚████║██╔══╝░░░░╚██╔╝░░  ██║╚████║██║░░░██║██╔═██╗░██╔══╝░░██╔══██╗
██║░╚═╝░██║╚█████╔╝██║░╚███║███████╗░░░██║░░░  ██║░╚███║╚██████╔╝██║░╚██╗███████╗██║░░██║
╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚══╝╚══════╝░░░╚═╝░░░  ╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
""")
    print("\033[0m")  

    guild_name = input("What server do you want to create channels in? ")

    guild = discord.utils.get(bot.guilds, name=guild_name)

    if guild is None:
        print("Server not found. Please make sure you entered the correct server name.")
        return

    while True:
        base_name = input("What do you want the base name of the channels to be? ")

        while True:
            try:
                num_channels = int(input("How many channels do you want to create? "))
                break
            except ValueError:
                print("Invalid number. Please enter a valid integer.")

        message = input("What do you want the bot to say in every channel? ")

        
        await delete_non_matching_channels(guild, base_name)

        
        await create_channels(guild, base_name, num_channels, message)

        cont = input("Do you want to create more channels? (yes/no) ")
        if cont.lower() != 'yes':
            break

async def run_bot():
    while True:
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            token_path = os.path.join(script_dir, 'bot_token.txt')  
            
            with open(token_path, 'r') as token_file:
                token = token_file.read().strip()

            await bot.start(token)
        except Exception as e:
            print(f"Bot disconnected due to {e}. Restarting...")
            await asyncio.sleep(5)  

if __name__ == "__main__":
    asyncio.run(run_bot())

