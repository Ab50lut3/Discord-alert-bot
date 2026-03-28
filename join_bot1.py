


import os
import discord
from discord.ext import commands

# ============================================
# CONFIGURATION - READ FROM ENVIRONMENT VARIABLES
# ============================================
# The token and user ID are stored SAFELY in:
# - Cyclic/Railway Dashboard → Variables
# - OR in a .env file for local testing
# ============================================

# Get token from environment variables (NEVER hardcode this!)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Get your Discord user ID from environment variables
YOUR_DISCORD_USER_ID = int(os.environ.get('YOUR_DISCORD_USER_ID', '0'))

# Optional: Set a channel ID for public alerts
ALERT_CHANNEL_ID = os.environ.get('ALERT_CHANNEL_ID', None)
if ALERT_CHANNEL_ID:
    ALERT_CHANNEL_ID = int(ALERT_CHANNEL_ID)

# Check if token is set (prevents bot from starting without token)
if not BOT_TOKEN:
    print("=" * 50)
    print("❌ ERROR: BOT_TOKEN not found!")
    print("=" * 50)
    print("Please set your bot token in environment variables:")
    print("  - On Cyclic: Dashboard → Variables → Add BOT_TOKEN")
    print("  - On Railway: Dashboard → Variables → Add BOT_TOKEN")
    print("  - For local testing: Create a .env file")
    print("=" * 50)
    exit(1)

if YOUR_DISCORD_USER_ID == 0:
    print("=" * 50)
    print("❌ ERROR: YOUR_DISCORD_USER_ID not found!")
    print("=" * 50)
    print("Please set your Discord User ID in environment variables:")
    print("  - On Cyclic: Dashboard → Variables → Add YOUR_DISCORD_USER_ID")
    print("  - On Railway: Dashboard → Variables → Add YOUR_DISCORD_USER_ID")
    print("=" * 50)
    exit(1)

# ============================================
# BOT SETUP
# ============================================

# Enable necessary intents (required for member join events)
intents = discord.Intents.default()
intents.members = True  # CRITICAL: Allows bot to detect new members
intents.message_content = True  # Optional for future features

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# ============================================
# EVENT: BOT IS READY
# ============================================
@bot.event
async def on_ready():
    """Prints bot status when online"""
    print(f'✅ Bot is online! Logged in as {bot.user}')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for new members 👀"
        )
    )
    
    # Send you a test DM to confirm everything works
    try:
        you = await bot.fetch_user(YOUR_DISCORD_USER_ID)
        await you.send(
            "✅ **Bot is online and ready!**\n\n"
            "I'll notify you whenever someone joins your server.\n"
            f"Currently watching: **{len(bot.guilds)}** server(s)\n\n"
            "Type `!test` in any channel to verify I'm working."
        )
        print("📨 Test message sent to your Discord DM!")
    except Exception as e:
        print(f"⚠️ Couldn't send test DM: {e}")

# ============================================
# EVENT: NEW MEMBER JOINS - MAIN FUNCTION!
# ============================================
@bot.event
async def on_member_join(member):
    """Triggered when someone joins your Discord server"""
    
    # Skip if it's a bot
    if member.bot:
        print(f"🤖 Bot joined: {member.name} (ignored)")
        return
    
    print(f"🔔 New member detected: {member.name} (ID: {member.id})")
    
    # Send alert to YOU via DM
    try:
        # Get the user you want to notify (you!)
        you = await bot.fetch_user(YOUR_DISCORD_USER_ID)
        
        if you:
            # Get server name
            server_name = member.guild.name
            
            # Build the alert message with Embed (fancy formatting)
            embed = discord.Embed(
                title="🟢 NEW MEMBER ALERT!",
                description=f"**{member.name}** just joined **{server_name}**!",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add member info
            embed.add_field(
                name="Username", 
                value=f"{member.name}#{member.discriminator}" if member.discriminator != "0" else member.name, 
                inline=True
            )
            embed.add_field(name="User ID", value=member.id, inline=True)
            embed.add_field(
                name="Account Created", 
                value=member.created_at.strftime("%Y-%m-%d"), 
                inline=True
            )
            
            # Add clickable link to message them
            embed.add_field(
                name="🎯 Quick Action",
                value=f"[Click Here to DM {member.name}](https://discord.com/users/{member.id})",
                inline=False
            )
            
            # Add instructions
            embed.set_footer(text="Click the link above to DM them instantly!")
            
            # Send DM to YOU
            await you.send(embed=embed)
            print(f"📨 Alert sent for new member: {member.name}")
    
    except discord.Forbidden:
        print(f"❌ Can't DM you - check your Discord privacy settings")
    except Exception as e:
        print(f"⚠️ Error sending alert: {e}")
    
    # OPTIONAL: Also send public alert to a specific channel
    if ALERT_CHANNEL_ID:
        channel = bot.get_channel(ALERT_CHANNEL_ID)
        if channel:
            await channel.send(
                f"🔔 **{member.mention}** just joined! "
                f"Go say hi! 👋"
            )
            print(f"📢 Public alert sent to channel {ALERT_CHANNEL_ID}")

# ============================================
# SIMPLE COMMAND: Test the bot
# ============================================
@bot.command()
async def test(ctx):
    """Type !test in Discord to check if bot is working"""
    await ctx.send("✅ Bot is working! I'll alert you when new members join.")
    print("📊 Test command used by user")

# ============================================
# SLASH COMMAND: Test your bot
# ============================================
@bot.tree.command(name="test", description="Test if the bot is working")
async def test_slash(interaction: discord.Interaction):
    """Simple test command"""
    await interaction.response.send_message("✅ Bot is online and working!", ephemeral=True)
    print("📊 Slash test command used")

# ============================================
# RUN THE BOT
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Starting Discord Bot...")
    print("=" * 50)
    bot.run(BOT_TOKEN)
