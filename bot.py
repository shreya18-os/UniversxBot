import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

intents = discord.Intents.all()

# Store users with no-prefix permission
no_prefix_users = set()

# Custom prefix handler
def get_prefix(bot, message):
    if message.author.id in no_prefix_users:
        return commands.when_mentioned_or('')(bot, message)
    return commands.when_mentioned_or('u!')(bot, message)

bot = commands.Bot(command_prefix=get_prefix, intents=intents, owner_id=1101467683083530331)

# Store user data
user_data = {
    'warnings': {},
    'badges': {},
    'no_prefix': set()
}

# Available badges
BADGES = {
    'owner': '👑 Owner',
    'staff': '🛡️ Staff',
    'admin': '⚡ Admin',
    'no_badge': '❌ No Badge'
}

# No-prefix permission commands
@bot.command(name='grant_no_prefix')
@commands.is_owner()
async def grant_no_prefix(ctx, member: discord.Member):
    no_prefix_users.add(member.id)
    await ctx.send(f'Granted no-prefix permission to {member.mention}')

@bot.command(name='revoke_no_prefix')
@commands.is_owner()
async def revoke_no_prefix(ctx, member: discord.Member):
    if member.id in no_prefix_users:
        no_prefix_users.remove(member.id)
        await ctx.send(f'Revoked no-prefix permission from {member.mention}')
    else:
        await ctx.send(f'{member.mention} does not have no-prefix permission')

@bot.command(name='list_no_prefix')
@commands.is_owner()
async def list_no_prefix(ctx):
    if not no_prefix_users:
        await ctx.send('No users have no-prefix permission')
        return
    users = ['\n'.join([f'<@{user_id}>' for user_id in no_prefix_users])]
    await ctx.send(f'Users with no-prefix permission:\n{users}')

# Store auto-role configuration
auto_roles = {}

# Store user application data
applications = {}


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name='Universx MC | u!help'))

# Custom Help Command
class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f'{self.context.clean_prefix}{command.qualified_name} {command.signature}'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title='📚 Universx MC Bot Help Menu',
            description='Welcome to the help menu! Use `u!help <command>` for detailed information.',
            color=discord.Color.blue()
        )

        embed.add_field(
            name=':shield: Moderation',
            value=(
                '`kick` – Kick a member\n'
                '`ban` – Ban a member\n'
                '`unban` – Unban a user\n'
                '`clear` – Purge messages\n'
                '`warn` – Warn a user'
            ),
            inline=False
        )

        embed.add_field(
            name=':performing_arts: Auto-Role',
            value=(
                '`setautorole` – Set role for new members'
            ),
            inline=False
        )

        embed.add_field(
            name=':memo: Application',
            value=(
                '`apply` – Start an application\n'
                '`reviewapp` – Review a user\'s application'
            ),
            inline=False
        )

        embed.add_field(
            name=':wrench: Utility',
            value=(
                '`ping` – Show latency\n'
                '`serverinfo` – Server stats\n'
                '`userinfo` – User info'
            ),
            inline=False
        )

        embed.add_field(
            name=':bust_in_silhouette: Profile',
            value=(
                '`profile` / `p` – View profile\n'
                '`grant_badge` – Grant badge (Owner)\n'
                '`revoke_badge` – Revoke badge (Owner)'
            ),
            inline=False
        )

        embed.add_field(
            name=':crown: Owner Only',
            value=(
                '`grant_no_prefix` – Allow user to run commands without prefix\n'
                '`revoke_no_prefix` – Remove no-prefix permission\n'
                '`list_no_prefix` – List users with no-prefix access'
            ),
            inline=False
        )

        embed.set_footer(text='Use u!help <command> to view detailed help for a command.')
        await self.get_destination().send(embed=embed)

    
    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f'Command: {command.name}',
            description=command.help or 'No description available',
            color=discord.Color.green()
        )

        # Add command signature
        embed.add_field(
            name='Usage',
            value=f'`{self.get_command_signature(command)}`',
            inline=False
        )

        # Add aliases if they exist
        if command.aliases:
            embed.add_field(
                name='Aliases',
                value=', '.join(f'`{alias}`' for alias in command.aliases),
                inline=False
            )

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(
            title='❌ Error',
            description=error,
            color=discord.Color.red()
        )
        await self.get_destination().send(embed=embed)

# Set up custom help command
bot.help_command = CustomHelpCommand()

# Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Check if the message started with the real prefix (u!)
        if ctx.prefix == 'u!':
            embed = discord.Embed(
                title='❌ Command Not Found',
                description='Use `u!help` to see available commands.',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        return  # Do not show errors for no-prefix messages
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title='❌ Missing Permissions',
            description='You do not have the required permissions to use this command.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        raise error  # For development/debugging purposes

# Moderation Commands
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    __cog_name__ = "Moderation" 

    @commands.command(help='Kick a member from the server :boot:')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        embed = discord.Embed(
            title='👢 Member Kicked',
            description=f'{member.mention} has been kicked\nReason: {reason or "No reason provided"}',
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    @commands.command(help='Ban a member from the server :hammer:')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        embed = discord.Embed(
            title='🔨 Member Banned',
            description=f'{member.mention} has been banned\nReason: {reason or "No reason provided"}',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(help='Unban a member from the server :unlock:')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed = discord.Embed(
                    title='🔓 Member Unbanned',
                    description=f'{user.mention} has been unbanned',
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                return
        await ctx.send('Member not found in ban list')

    @commands.command(help='Clear a specified number of messages :broom:')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title='🧹 Messages Cleared',
            description=f'Cleared {amount} messages',
            color=discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command(help='Warn a member :warning:')
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        if member.id not in user_data['warnings']:
            user_data['warnings'][member.id] = []
        user_data['warnings'][member.id].append({
            'reason': reason,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        embed = discord.Embed(
            title='⚠️ Member Warned',
            description=f'{member.mention} has been warned\nReason: {reason or "No reason provided"}',
            color=discord.Color.yellow()
        )
        await ctx.send(embed=embed)

# Auto-role System
class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in auto_roles:
            role = member.guild.get_role(auto_roles[member.guild.id])
            if role:
                await member.add_roles(role)
                embed = discord.Embed(
                    title='🎭 Auto-Role Assigned',
                    description=f'Welcome {member.mention}! You have been assigned the {role.name} role.',
                    color=discord.Color.green()
                )
                # Send to system channel if it exists, otherwise first text channel
                channel = member.guild.system_channel or member.guild.text_channels[0]
                await channel.send(embed=embed)

    @commands.command(help='Set the auto-role for new members :performing_arts:')
    @commands.has_permissions(manage_roles=True)
    async def setautorole(self, ctx, role: discord.Role):
        auto_roles[ctx.guild.id] = role.id
        embed = discord.Embed(
            title='✅ Auto-Role Set',
            description=f'Auto-role has been set to {role.mention}',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

# Application System
class Application(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = [
            'What is your Minecraft username? :video_game:',
            'How old are you? :birthday:',
            'Why do you want to join our server? :thinking:',
            'Do you agree to follow our rules? :scroll:'
        ]

    @commands.command(help='Apply to join the Minecraft server :pencil:')
    async def apply(self, ctx):
        embed = discord.Embed(
            title='📝 Server Application',
            description='Please answer the following questions within 60 seconds each.',
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        answers = []
        for question in self.questions:
            question_embed = discord.Embed(
                description=question,
                color=discord.Color.blue()
            )
            await ctx.send(embed=question_embed)

            try:
                answer = await self.bot.wait_for(
                    'message',
                    timeout=60.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                answers.append(answer.content)
            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title='⏰ Timeout',
                    description='Application timed out. Please try again.',
                    color=discord.Color.red()
                )
                await ctx.send(embed=timeout_embed)
                return

        applications[ctx.author.id] = {
            'answers': answers,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        }

        success_embed = discord.Embed(
            title='✅ Application Submitted',
            description='Your application has been submitted for review!',
            color=discord.Color.green()
        )
        await ctx.send(embed=success_embed)

    @commands.command(help='Review a pending application :clipboard:')
    @commands.has_permissions(administrator=True)
    async def reviewapp(self, ctx, user: discord.Member, status: str):
        if user.id in applications:
            applications[user.id]['status'] = status.lower()
            
            # Embed for the reviewer
            review_embed = discord.Embed(
                title='📋 Application Review',
                description=f'Application for {user.mention} has been marked as {status}',
                color=discord.Color.blue()
            )
            await ctx.send(embed=review_embed)

            # Embed for the applicant
            status_color = discord.Color.green() if status.lower() == 'accepted' else \
                          discord.Color.red() if status.lower() == 'rejected' else \
                          discord.Color.orange()
            
            user_embed = discord.Embed(
                title='📬 Application Status Update',
                description=f'Your application has been {status}!',
                color=status_color
            )
            await user.send(embed=user_embed)
        else:
            error_embed = discord.Embed(
                title='❌ Error',
                description='No application found for this user.',
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)

# Utility Commands
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Check bot latency :ping_pong:')
    async def ping(self, ctx):
        embed = discord.Embed(
            title='🏓 Pong!',
            description=f'Latency: {round(self.bot.latency * 1000)}ms',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(help='Display server information :information_source:')
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title=f'📊 {guild.name} Server Information',
            color=discord.Color.blue()
        )
        embed.add_field(name='👑 Owner', value=guild.owner.mention)
        embed.add_field(name='👥 Members', value=guild.member_count)
        embed.add_field(name='📅 Created At', value=guild.created_at.strftime('%Y-%m-%d'))
        embed.add_field(name='💬 Text Channels', value=len(guild.text_channels))
        embed.add_field(name='🔊 Voice Channels', value=len(guild.voice_channels))
        embed.add_field(name='🎭 Roles', value=len(guild.roles))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        await ctx.send(embed=embed)

    @commands.command(help='Display user information :bust_in_silhouette:')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.mention for role in member.roles[1:]]
        embed = discord.Embed(
            title=f'👤 User Information - {member}',
            color=member.color
        )
        embed.add_field(name='🆔 ID', value=member.id)
        embed.add_field(name='📅 Joined', value=member.joined_at.strftime('%Y-%m-%d'))
        embed.add_field(name='📝 Created At', value=member.created_at.strftime('%Y-%m-%d'))
        embed.add_field(name='👑 Top Role', value=member.top_role.mention)
        embed.add_field(name='🎭 Roles', value=' '.join(roles) if roles else 'None')
        embed.add_field(name='🤖 Bot', value='Yes' if member.bot else 'No')
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)

# Profile System
class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='profile', aliases=['p'], help='View your or another user\'s profile 👤')
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f'Profile - {member}',
            color=member.color
        )
        
        # Add user info
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name='🆔 User ID', value=member.id, inline=True)
        embed.add_field(name='📅 Joined', value=member.joined_at.strftime('%Y-%m-%d'), inline=True)
        
        # Add badges (with custom emoji examples)
        badges = user_data['badges'].get(member.id, set())
        badge_display = '\n'.join([BADGES[badge] for badge in badges]) if badges else BADGES['no_badge']
        embed.add_field(
            name='<:BadgeIcon:123456789> Badges',  # Replace with your server's badge emoji ID
            value=badge_display.replace('👑', '<:OwnerBadge:123456789>')
                              .replace('🛡️', '<:StaffBadge:123456789>')
                              .replace('⚡', '<:AdminBadge:123456789>')
                              .replace('❌', '<:NoBadge:123456789>'),
            inline=False
        )
        
        # Add no-prefix status (with custom emoji examples)
        no_prefix_status = '<:Enabled:123456789> Enabled' if member.id in no_prefix_users else '<:Disabled:123456789> Disabled'
        embed.add_field(name='<:PrefixIcon:123456789> No-Prefix Status', value=no_prefix_status, inline=False)
        
        # Add custom emoji hint
        embed.set_footer(text='Replace <:EmojiName:123456789> with your server\'s custom emoji IDs')
        
        await ctx.send(embed=embed)

    @commands.command(help='Grant a badge to a user 🏅')
    @commands.is_owner()
    async def grant_badge(self, ctx, member: discord.Member, badge: str):
        if badge.lower() not in BADGES:
            await ctx.send(f'Invalid badge. Available badges: {", ".join(BADGES.keys())}')
            return
        
        if member.id not in user_data['badges']:
            user_data['badges'][member.id] = set()
        
        user_data['badges'][member.id].add(badge.lower())
        await ctx.send(f'Granted {BADGES[badge.lower()]} to {member.mention}')

    @commands.command(help='Revoke a badge from a user ❌')
    @commands.is_owner()
    async def revoke_badge(self, ctx, member: discord.Member, badge: str):
        if member.id not in user_data['badges'] or badge.lower() not in user_data['badges'][member.id]:
            await ctx.send(f'{member.mention} does not have this badge')
            return
        
        user_data['badges'][member.id].remove(badge.lower())
        await ctx.send(f'Revoked {BADGES[badge.lower()]} from {member.mention}')

# Add all cogs
async def setup_cogs():
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(AutoRole(bot))
    await bot.add_cog(Application(bot))
    await bot.add_cog(Utility(bot))
    await bot.add_cog(Profile(bot))

@bot.event
async def on_ready():
    await setup_cogs()
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name='Universx MC | u!help'))

# Setup cogs and run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
