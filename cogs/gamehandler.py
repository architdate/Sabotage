import discord, json
from discord.ext import commands, tasks
from gameapi import AmongUsGame


class GameHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('config.json') as c:
            self.config = json.load(c)
        self.ongoing = False
        self.game = None

    def get_discord_members(self, playerinfos, guild):
        with open('registered.json') as r:
            registered = json.load(r)
        names = [self.game.ProcessMemory.ReadString(p.PlayerName) for p in playerinfos]
        retval = []
        for k, v in registered.items():
            if v in names:
                retval.append(discord.utils.get(guild.members, id=int(k)))
        return retval

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        with open("registered.json") as c:
            registered = json.load(c)
        if before.channel == None and after.channel == discord.utils.get(self.bot.main_server.voice_channels, id=self.config["GAME_CHANNEL"]):
            if not self.ongoing and member.voice.mute and str(member.id) in registered.keys():
                await member.edit(mute=False)
            elif self.ongoing and member in self.get_discord_members(self.game.getDeadPlayers(), self.bot.main_server):
                await member.edit(mute=True)
            elif self.ongoing and str(member.id) in registered.keys() and self.game.getState() == AmongUsGame.GameState.TASKS:
                await member.edit(mute=True)
            elif self.ongoing and member not in self.get_discord_members(self.game.getDeadPlayers(), self.bot.main_server) and self.game.getState() != AmongUsGame.GameState.TASKS:
                await member.edit(mute=False)

    @commands.command()
    @commands.guild_only()
    async def monitor(self, ctx):
        self.game = AmongUsGame()
        if not self.game.isHooked():
            self.game = None
        if self.game != None:
            self.ongoing = True
            self.gameloop.start()
            await ctx.send("Hooked to Among Us! Started monitoring!")

    @commands.command()
    @commands.guild_only()
    async def stopmonitor(self, ctx):
        if self.ongoing:
            self.game = None
            self.ongoing = False
            self.gameloop.cancel()
            vc = discord.utils.get(self.bot.main_server.voice_channels, id=self.config["GAME_CHANNEL"])
            vcm = vc.members
            vcm_ids = [m.id for m in vcm]
            with open("registered.json") as c:
                registered = json.load(c)
            for k in registered.keys():
                if int(k) in vcm_ids:
                    try:
                        await discord.utils.get(self.bot.main_server.members, id=int(k)).edit(mute=False)
                    except:
                        pass
            await ctx.send("Stopped monitoring!")
        else:
            await ctx.send("I was not monitoring anyway!")

    @commands.command()
    @commands.guild_only()
    async def register(self, ctx, *, gamename: str):
        """Registers your game name to you"""
        author = ctx.author
        crewmate_role = discord.utils.get(ctx.guild.roles, id=self.config["CREWMATE_ROLE"])
        try:
            with open("registered.json") as c:
                registered = json.load(c)
            if gamename not in registered.values():
                registered[str(author.id)] = gamename
                await author.add_roles(crewmate_role, reason="Registered with Sabotage!")
                with open("registered.json", 'w') as c:
                    c.write(json.dumps(registered, indent=4))
                await ctx.send("Registration successful!")
            else:
                await ctx.send("That name is already registered! Please choose something else!")
        except FileNotFoundError:
            await ctx.send("Registration file not found! Creating a new one!")
            registered = {}
            registered[str(author.id)] = gamename
            await author.add_roles(crewmate_role, reason="Registered with Sabotage!")
            with open("registered.json", 'w') as c:
                c.write(json.dumps(registered, indent=4))
            await ctx.send("Registration successful!")

    @commands.command()
    @commands.guild_only()
    async def unregister(self, ctx):
        """Unegisters your game name to you"""
        author = ctx.author
        crewmate_role = discord.utils.get(ctx.guild.roles, id=self.config["CREWMATE_ROLE"])
        try:
            with open("registered.json") as c:
                registered = json.load(c)
            if str(author.id) not in registered.keys():
                await ctx.send("You are not registered anyway!")
            else:
                del registered[str(author.id)]
                await author.remove_roles(crewmate_role, reason="Removed registration with Sabotage!")
                with open("registered.json", 'w') as c:
                    c.write(json.dumps(registered, indent=4))
                await ctx.send("Removed you from registered users!")
        except FileNotFoundError:
            pass

    @tasks.loop(seconds=0.25)
    async def gameloop(self):
        vc = discord.utils.get(self.bot.main_server.voice_channels, id=self.config["GAME_CHANNEL"])
        vcm = vc.members
        vcm_ids = [m.id for m in vcm]
        state = self.game.getState()
        if state != self.game.oldState:
            with open("registered.json") as r:
                registered = json.load(r)
            if state == AmongUsGame.GameState.DISCUSSION:
                dead = self.get_discord_members(self.game.getDeadPlayers(), self.bot.main_server)
                dead_ids = [d.id for d in dead]
                for k in registered.keys():
                    if int(k) in dead_ids and int(k) in vcm_ids:
                        try:
                            await discord.utils.get(self.bot.main_server.members, id=int(k)).edit(mute=True)
                        except:
                            pass
                    elif int(k) in vcm_ids:
                        try:
                            await discord.utils.get(self.bot.main_server.members, id=int(k)).edit(mute=False)
                        except:
                            pass
            if state == AmongUsGame.GameState.TASKS:
                for k in registered.keys():
                    if int(k) in vcm_ids:
                        try:
                            await discord.utils.get(self.bot.main_server.members, id=int(k)).edit(mute=True)
                        except:
                            pass
            if state == AmongUsGame.GameState.LOBBY:
                for k in registered.keys():
                    if int(k) in vcm_ids:
                        try:
                            await discord.utils.get(self.bot.main_server.members, id=int(k)).edit(mute=False)
                        except:
                            pass
        self.game.oldState = state

    @commands.command()
    @commands.guild_only()
    async def joined(self, ctx, *, member: discord.Member):
        """Says when a member joined."""
        await ctx.send(f'{member.display_name} joined on {member.joined_at}')

    @commands.command(name='hook')
    async def get_hooked(self, ctx):
        """Is the bot cool?"""
        game = AmongUsGame()
        await ctx.send(f'Hook value: {game.isHooked()}')

    @commands.command(name='top_role', aliases=['toprole'])
    @commands.guild_only()
    async def show_toprole(self, ctx, *, member: discord.Member=None):
        """Simple command which shows the members Top Role."""

        if member is None:
            member = ctx.author

        await ctx.send(f'The top role for {member.display_name} is {member.top_role.name}')
    
    @commands.command(name='perms', aliases=['perms_for', 'permissions'])
    @commands.guild_only()
    async def check_permissions(self, ctx, *, member: discord.Member=None):
        """A simple command which checks a members Guild Permissions.
        If member is not provided, the author will be checked."""

        if not member:
            member = ctx.author

        # Here we check if the value of each permission is True.
        perms = '\n'.join(perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
        embed.set_author(icon_url=member.avatar_url, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name='\uFEFF', value=perms)

        await ctx.send(content=None, embed=embed)
        # Thanks to Gio for the Command.

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case MembersCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(GameHandler(bot))