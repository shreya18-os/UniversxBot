# Universx MC Discord Bot

A custom Discord bot for Universx MC Minecraft server with moderation, automation, and role management features.

## Features

### Moderation Commands
- `u!kick` - Kick a member
- `u!ban` - Ban a member
- `u!unban` - Unban a member
- `u!clear` - Clear messages
- `u!warn` - Warn a member

### Auto-role System
- Automatically assigns roles to new members
- `u!setautorole` - Set the auto-role for new members

### Application System
- `u!apply` - Start the server application process
- `u!reviewapp` - Review pending applications (Admin only)

### Utility Commands
- `u!ping` - Check bot latency
- `u!serverinfo` - Display server information
- `u!userinfo` - Display user information

## Setup

### Local Development
1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a Discord bot and get the token:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the Bot section
   - Create a bot and copy the token
4. Create a `.env` file from `.env.example` and add your bot token
5. Run the bot:
   ```bash
   python bot.py
   ```

### Railway Deployment
1. Fork this repository to your GitHub account
2. Create a new project in Railway
3. Connect your GitHub repository
4. Add the following environment variable in Railway:
   - `DISCORD_BOT_TOKEN`: Your Discord bot token
5. Railway will automatically deploy your bot using the Dockerfile

## Bot Configuration

- Default prefix is `u!`
- Bot owner ID is set to: 1101467683083530331
- The bot uses all intents for full functionality

### No-Prefix Commands (Owner Only)
- `u!grant_no_prefix @user` - Grant no-prefix permission to a user
- `u!revoke_no_prefix @user` - Revoke no-prefix permission from a user
- `u!list_no_prefix` - List all users with no-prefix permission

Users with no-prefix permission can use commands without the `u!` prefix.

## Security Note

Never share your bot token with anyone. Keep it private and secure.

## Support

For support or questions, please contact the server administrators.