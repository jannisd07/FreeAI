import nextcord
from nextcord.ext import commands
import asyncio
import json

class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            global invites
            guild = self.bot.get_guild(1125542724402167808)
            invites = await guild.invites()
            await asyncio.sleep(2)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        invites_before_join = invites
        invites_after_join = await guild.invites()
        for invite in invites_before_join:
            matching_invites = [inv for inv in invites_after_join if inv.code == invite.code and inv.uses > invite.uses]
            print(matching_invites)
            if matching_invites:
                inviter = matching_invites[0].inviter
                break
        else:
            return
        with open("invites.json", "r") as f:
            data = json.load(f)
        if str(member.id) in data:
            already_invited = True
        else:
            already_invited = False
        data[str(member.id)] = inviter.id
        with open('invites.json', 'w') as f:
            json.dump(data, f, indent=4)
        with open('accounts.json', 'r') as f:
            data = json.load(f)
        if str(inviter.id) not in data:
            data[str(inviter.id)] = {}
            data[str(inviter.id)]["credits"] = 0
        if already_invited == False:
            data[str(inviter.id)]["credits"] += 3
        if str(member.id) not in data:
            data[str(member.id)] = {}
            data[str(member.id)]["credits"] = 10
            data[str(member.id)]["account_type"] = "basic"
        with open('accounts.json', 'w') as f:
            json.dump(data, f, indent=4)
        try:
            await inviter.send(f'You got three credits for inviting {member.name} to the server!')
        except:
            print("could not DM this user")

def setup(bot):
    bot.add_cog(Invites(bot))
