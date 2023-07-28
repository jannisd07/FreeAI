import nextcord
from nextcord.ext import commands
import json
import os
import torch
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands, tasks
import nextcord
from io import BytesIO
import concurrent.futures
import asyncio
from collections import deque
import threading
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import transformers

client = commands.Bot(command_prefix='!', intents=nextcord.Intents.all())
# SG161222/Realistic_Vision_V2.0
# SG161222/Realistic_Vision_V3.0_VAE
transformers.utils.move_cache()
scheduler = EulerDiscreteScheduler.from_pretrained("SG161222/Realistic_Vision_V3.0_VAE", subfolder="scheduler")
pipe1 = StableDiffusionPipeline.from_pretrained("SG161222/Realistic_Vision_V2.0", torch_dtype=torch.float16)
pipe1 = pipe1.to("cuda")

queue = deque()

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.channel.id in [1125823077268336722, 1125823101503016980, 1125823123275649044, 1125823145299939338, 1125823166191767653, 1125884252576301067]:
        if not message.author.bot:
            if not message.content.startswith("!clear"):
                with open("accounts.json", "r") as f:
                    data = json.load(f)
                if data[str(message.author.id)]["credits"] >= 1:
                    if data[str(message.author.id)]["account_type"] == "basic":
                        with open("accounts.json", "r") as f:
                            data = json.load(f)
                        if data[str(message.author.id)]["account_type"] == "basic":
                            data[str(message.author.id)]["credits"] -= 1
                        with open("accounts.json", "w") as f:
                            json.dump(data, f, indent=4)
                        queue.append([message.author.id, message.content, "pipe1", message.channel.id, "basic"])
                    else:
                        queue.append([message.author.id, message.content, "pipe1", message.channel.id, "premium"])
                else:
                    if data[str(message.author.id)]["account_type"] == "basic":
                        await message.channel.send(f"<@{message.author.id}> You don't have any credits left. Invite friends to FreeAI to get more credits. Each invite will give you **3 image generation credits**")
                    else:
                        queue.append([message.author.id, message.content, "pipe1", message.channel.id, "premium"])
    elif message.channel.id == 1126110884436127876:
        await message.add_reaction("🏆")


@tasks.loop(seconds=3)
async def process_queue():
    if queue:
        user_id, prompt, model, channel_id, account_type = queue[0]
        member = await client.fetch_user(user_id)
        channel = client.get_channel(channel_id)
        await channel.send(f"Processing image generation request for {member.mention}...")
        tasks = [generate_images(prompt, channel_id, account_type, user_id) for _ in range(3)]
        generated_images = await asyncio.gather(*tasks)
        files = [nextcord.File(generated_image, filename=f"FreeAI_{i+1}.png") for i, generated_image in enumerate(generated_images)]
        message = await channel.send(f"{member.mention}\n**{prompt}**", files=files)
        try:
            await member.send(f"**Version: V2**\nYour generated images are ready!\n**{prompt}**\n\nhttps://discord.com/channels/1125542724402167808/{channel.id}/{message.id}")
        except:
            print("Could not dm this user")
        queue.popleft()


async def get_type(prompt, channel_id):
    if channel_id == 1125823145299939338:
        text = f"RAW photo, subject, {prompt} (high detailed skin:1.2), 8k uhd, dslr, soft lighting, high quality, film grain, Fujifilm XT3"
    elif channel_id in [1125823077268336722, 1125823101503016980]:
        text = prompt
    elif channel_id == 1125823123275649044:
        text = f"{prompt} (high detailed), 8k uhd, soft lighting, high quality"
    elif channel_id in [1125823166191767653, 1125884252576301067]:
        text = f"RAW photo, {prompt} (high detailed), 8k uhd, dslr, soft lighting, high quality, realistic, nsfw, porn"
    print(text)
    return text

async def generate_images(prompt: str, channel_id, account_type, user_id):
    if user_id == 990380208383221760:
        steps = 100
    else:
        steps = 50
    if channel_id == 1125823166191767653:
        pipe1.safety_checker = None 
        pipe1.requires_safety_checker = False
        text = await get_type(prompt, channel_id)
        image = pipe1(text, num_inference_steps=steps, num_images_per_prompt=1).images[0]
    else:
        text = await get_type(prompt, channel_id)
        image = pipe1(text, num_inference_steps=steps, num_images_per_prompt=1).images[0]
    image_data = BytesIO()
    image.save(image_data, 'PNG')
    image_data.seek(0)
    return image_data

@client.event
async def on_ready():
    print("Bot is ready.")
    process_queue.start()

@client.command()
async def credits(ctx):
    with open("accounts.json", "r") as f:
        data = json.load(f)
    if str(ctx.author.id) in data:
        credits = data[str(ctx.author.id)]["credits"]
        account_type = data[str(ctx.author.id)]["account_type"]
        if account_type == "basic":
            await ctx.channel.send(f"You have {credits} credits left. One credit = one image generation.")
        elif account_type == "premium":
            await ctx.channel.send(f"You are a premium member. You can generate as many images as you like.")
    else:
        await ctx.channel.send("You are not in our database. Please rejoin this server to fix this error.")


def is_admin_or_specific_channel(ctx):
    return ctx.author.guild_permissions.administrator or ctx.channel.id == 1125884252576301067

@client.command()
@commands.check(is_admin_or_specific_channel)
async def clear(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please enter a positive number of messages to delete.")
        return
    try:
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Successfully deleted {len(deleted)} messages.", delete_after=5)
    except nextcord.Forbidden:
        await ctx.send("I do not have the required permissions to delete messages.")
    except nextcord.HTTPException as e:
        await ctx.send(f"An error occurred: {e}")


for file in os.listdir("./cogs"):
    if file.endswith(".py") and not file.startswith("_"):
        client.load_extension(f"cogs.{file[:-3]}")

client.run('ENTFERNT', reconnect=True)
