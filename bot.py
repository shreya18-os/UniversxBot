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

# Store user warnings
warnings = {}

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

# Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found. Use `u!help` to see available commands.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have the required permissions to use this command.')

# Moderation Commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked. Reason: {reason}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned. Reason: {reason}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned.')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f'Cleared {amount} messages.')
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    if member.id not in warnings:
        warnings[member.id] = []
    warnings[member.id].append({
        'reason': reason,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    await ctx.send(f'{member.mention} has been warned. Reason: {reason}')

# Auto-role System
@bot.event
async def on_member_join(member):
    if member.guild.id in auto_roles:
        role = member.guild.get_role(auto_roles[member.guild.id])
        if role:
            await member.add_roles(role)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def setautorole(ctx, role: discord.Role):
    auto_roles[ctx.guild.id] = role.id
    await ctx.send(f'Auto-role has been set to {role.name}')

# Application System
@bot.command()
async def apply(ctx):
    await ctx.send('Please answer the following questions within 60 seconds each:')
    questions = [
        'What is your Minecraft username?',
        'How old are you?',
        'Why do you want to join our server?',
        'Do you agree to follow our rules?'
    ]
    answers = []

    for question in questions:
        await ctx.send(question)
        try:
            answer = await bot.wait_for(
                'message',
                timeout=60.0,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel
            )
            answers.append(answer.content)
        except asyncio.TimeoutError:
            await ctx.send('Application timed out. Please try again.')
            return

    applications[ctx.author.id] = {
        'answers': answers,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'pending'
    }

    await ctx.send('Your application has been submitted for review!')

@bot.command()
@commands.has_permissions(administrator=True)
async def reviewapp(ctx, user: discord.Member, status: str):
    if user.id in applications:
        applications[user.id]['status'] = status.lower()
        await ctx.send(f'Application for {user.mention} has been marked as {status}')
        await user.send(f'Your application has been {status}!')
    else:
        await ctx.send('No application found for this user.')

# Utility Commands
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f'{guild.name} Server Information',
        color=discord.Color.blue()
    )
    embed.add_field(name='Owner', value=guild.owner.mention)
    embed.add_field(name='Members', value=guild.member_count)
    embed.add_field(name='Created At', value=guild.created_at.strftime('%Y-%m-%d'))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles = [role.mention for role in member.roles[1:]]
    embed = discord.Embed(
        title=f'User Information - {member}',
        color=member.color
    )
    embed.add_field(name='ID', value=member.id)
    embed.add_field(name='Joined', value=member.joined_at.strftime('%Y-%m-%d'))
    embed.add_field(name='Roles', value=' '.join(roles) if roles else 'None')
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await ctx.send(embed=embed)

# Run the bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))