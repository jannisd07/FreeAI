# FreeAI

Discord bot for free AI image generation (2023). Members request images with a slash command; the bot runs Stable Diffusion (Realistic Vision V2.0, `diffusers`) on my own GPU and works through requests in a queue. Credits and invite rewards are stored per user.

**Status:** discontinued, kept as an archive.

## Stack

Python, nextcord, PyTorch, diffusers

## Run

```bash
pip install nextcord diffusers transformers torch python-dotenv
cp .env.example .env   # add DISCORD_BOT_TOKEN
python dc.py
```

More projects: [jannisdietrich.com](https://jannisdietrich.com)
