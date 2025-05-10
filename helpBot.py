import os
import re
import discord
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables
load_dotenv()

# Constants
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

def load_allowed_channel_ids(path="channelIDs.txt"):
    allowed_ids = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                try:
                    allowed_ids.add(int(parts[0]))
                except ValueError:
                    continue  # skip lines that don't start with an integer
    return allowed_ids

ALLOWED_CHANNEL_IDS = load_allowed_channel_ids()

intents = discord.Intents.default()
intents.message_content = True

def load_tc_requirements(path="tcReqirements.txt"):
    tc_data = {}
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split("|")
            if len(parts) == 7:
                level = int(parts[0])
                tc_data[level] = {
                    "Prerequisites": parts[1],
                    "Bread": parts[2],
                    "Wood": parts[3],
                    "Coal": parts[4],
                    "Iron": parts[5],
                    "Upgrade Time": parts[6]
                }
    return tc_data

tc_data = load_tc_requirements()

def load_gift_codes_and_expiration(path="giftCodes.txt"):
    gift_codes = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split()  # Split by whitespace to separate code and date
                if len(parts) == 2:
                    gift_code = parts[0]
                    expiration_date = parts[1]
                    gift_codes.append(f"{gift_code} (Expire {expiration_date} at 23:59 UTC)")
    return gift_codes

gift_codes = load_gift_codes_and_expiration()

bot = commands.Bot(command_prefix="!", intents=intents)

def parse_time_to_seconds(text: str) -> int:
    time_units = {
        "day": 86400,
        "hour": 3600,
        "minute": 60,
    }
    total_seconds = 0
    for unit, multiplier in time_units.items():
        match = re.search(rf"(\d+)\s*{unit}", text)
        if match:
            total_seconds += int(match.group(1)) * multiplier
    return total_seconds

def format_seconds_to_text(seconds: int) -> str:
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60

    parts = []
    if days: parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours: parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes: parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return ", ".join(parts) if parts else "0 minutes"

def get_tc_requirements_embed(level: int, percent: int = 0):
    if level in tc_data:
        data = tc_data[level]
        upgrade_time = data['Upgrade Time']

        if percent > 0:
            base_seconds = parse_time_to_seconds(upgrade_time)
            adjusted_seconds = round(base_seconds / (1 + float(percent) / 100))
            upgrade_time = format_seconds_to_text(adjusted_seconds)

        if percent != 0:
            return discord.Embed(
                    title=f"📋 Town Center Level **{level}** Requirements with **{percent}**% construction speed",
                description=(
                    f"• **Prerequisites**: {data['Prerequisites']}\n"
                    f"• **Base Bread**: {data['Bread']}\n"
                    f"• **Base Wood**: {data['Wood']}\n"
                    f"• **Base Coal**: {data['Coal']}\n"
                    f"• **Base Iron**: {data['Iron']}\n"
                    f"• **Upgrade Time**: {upgrade_time}"
                ),
                color=0x2ecc71
            )
        else:
            return discord.Embed(
                    title=f"📋 Town Center Level **{level}** Requirements",
                description=(
                    f"• **Prerequisites**: {data['Prerequisites']}\n"
                    f"• **Base Bread**: {data['Bread']}\n"
                    f"• **Base Wood**: {data['Wood']}\n"
                    f"• **Base Coal**: {data['Coal']}\n"
                    f"• **Base Iron**: {data['Iron']}\n"
                    f"• **Upgrade Time**: {upgrade_time}"
                ),
                color=0x2ecc71
            )
        
    else:
        return discord.Embed(
            title="❗ Invalid Town Center Level",
            description="Valid levels are between 2 and 30.",
            color=0xe74c3c
        )


def get_embed_response(content: str) -> discord.Embed | None:
    content = content.casefold()


    if ("requirements" in content or "prerequisites" in content or "cost" in content) and ("tc" in content or "town center" in content or "town centre" in content):
        # Use regex to find all digits
        numbers = re.findall(r"\d+(?:\.\d+)?", content)  # Find all sequences of digits
        print("Extracted Numbers:", numbers)
        if numbers:
            level = int(numbers[0])  # Extract the first number found
            percent = float(numbers[1]) if len(numbers) > 1 else 0
            #print(f"Level found: {level}")
            return get_tc_requirements_embed(level, percent)  # Return embed based on the first level found
    if "helpbotactive?" in content:
        return discord.Embed(
            title="Hello! 👋",
            color=0x000000
        )
    elif ("are" in content or "any" in content or "how" in content) and "code" in content:
        # Display gift codes or expiration message
        if gift_codes:
            description = "\n".join([f"• **{code}**" for code in gift_codes])
            description += "\n\n🔗 Redeem on Website: https://ks-giftcode.centurygame.com/"
            description += "\n🕹️ Redeem in-game(Android users only): Avatar(top-left on Main Interface) -> Settings -> Gift Code"
            return discord.Embed(
                title="🎁 Gift Codes:",
                description=description,
                color=0x00ff99
            )
        else:
            return discord.Embed(
                title="🎁 Gift Codes:",
                description="None currently active",
                color=0xe74c3c
            )
    elif (content.startswith("how") or content.startswith("can") or (content.startswith("is")) or content.startswith("does") or "?" in content) and ("change" in content or "move" in content or "teleport" in content or "transfer" in content ) and ("state" in content or "server" in content or "region" in content):
        return discord.Embed(
            title="📦 Can you move states?",
            description=("There's no way to move your city to another state.\n"
                         "👉 However, you can create a new character:\n"
                         "`Profile Pic > Settings > Characters > Create New Character`"),
            color=0x3498db
        )
    elif "does" in content and "auto" in content and ("bear" in content or "pitfall" in content):
        return discord.Embed(
            title="🐾 Does auto-rally work for bear trap?",
            description="No, you must be online and manually join rallies.",
            color=0xe74c3c
        )
    elif ("what" in content or "which" in content or "?" in content) and ("bear trap" in content or "bear" in content or "pitfall" in content) and ("heroes" in content or "use" in content):
        return discord.Embed(
            title="🐻 What heroes do you use for the bear trap?",
            description=("For the bear trap, use you three strongest attacking heroes when starting rallies.  When joining rallies use a lead hero that boosts rally lethality. During gen1 these heroes are only Amadaeus and Chenko"),
            color=0x3498db
        )
    elif "when" in content and "does" in content and ("fog" in content or "fertile land" in content or "plains" in content):
        return discord.Embed(
            title="🌫️ When does the fog move?",
            description=("• **Day 14** — Reveals the *Plains*\n"
                         "• **Day 39** — Reveals the *Fertile Land*"),
            color=0x9b59b6
        )
    elif ("should" in content or "?" in content) and "save" in content and "keys" in content:
        return discord.Embed(
            title="🔑 Should I save my keys?",
            description=("**No**, there are no standard events that require keys.\nHowever there may be special events in the future that take them.\n"),
            color=0x2ecc71
        )
    elif ("what" in content or "which" in content or "?" in content) and ("thing" in content or "way" in content or "should" in content or "spend gems" in content or "use gems" in content) and ("gems" in content):
        return discord.Embed(
            title="💎 What is the best thing to use gems on?",
            description=("• **Lucky wheel** - This is the primary thing you should use gems on.\n"
                         "• VIP, Hero Rally, Teleports and troop speedups can also be good depending on your situation.\n"),
            color=0x8e44ad
        )
    elif ("how to" in content or "how do" in content or "when" in content) and ("are" in content or "?" in content) and ("get" in content or "released" in content) and ("gen2" in content or "gen 2" in content or "generation 2" in content):
        return discord.Embed(
            title="🦸‍♂️ When are Gen 2 heroes released?",
            description=("Gen2 heroes are released between day 40 and 50 of your state with the third Hall of Governors"),
            color=0x2980b9
        )
    elif ("when are" in content) and ("gen2" in content or "gen 2" in content or "generation 2" in content) and ("released" in content or "available" in content):
        return discord.Embed(
            title="🦸‍♂️ When are Gen 2 heroes released?",
            description=("Gen2 heroes are released between day 40 and 50 of your state. With the third Hall of Governors"),
            color=0x2980b9
        )
    elif ("amadeus" in content) and ("or" in content) and ("zoe" in content):
        return discord.Embed(
            title="🦸‍♂️ Amadeus or Zoe?",
            description=("• **Amadeus** is better on attack.\n"
                         "• **Zoe** is better for defense.\n"),
            color=0x2980b9
        )
    elif ("which" in content or "who" in content or "what" in content) and ("hero" in content) and ("wheel" in content or "roulette" in content):
        return discord.Embed(
            title="🎡 Which heroes are in hero roulette?",
            description=("• gen1: Saul\n"
                         "• gen2: Zoe\n"),
            color=0x3498db
        )
    elif (content.startswith("when") or "time" in content or "?" in content) and ("pets" in content) and ("released" in content or "available" in content or "come" in content or "arrive" in content):
        return discord.Embed(
            title="🐾 When are pets released?",
            description=("Pets are released on day 55 of your state (The day after King's Castle). \n"),
            color=0x3498db
        )
    elif ("when" in content or "what day" in content or "how often" in content) and ("is" in content) and ("king's Castle" in content or "king Castle"):
        return discord.Embed(
            title="🏰 When is King's Castle?",
            description=("• The first King's Castle is on day 54 of your state.\n"
                         "• After that it will take place every 2 weeks on Saturdays.\n"
                         "• King's Castle always starts at 12:00 UTC.\n"),
            color=0xf1c40f
        )
    elif ("what" in content) and ("tc" in content or "town center" in content or "town centre" in content) and ("hero gear" in content):
        return discord.Embed(
            title="🏰 What TC level is required for hero gear?",
            description=("• **TC15** is required for hero gear.\n"
                         "• **TC20** is required for hero gear mastery foraging.\n"),
            color=0x3498db
        )
    elif ("what" in content) and ("tc" in content or "town center" in content or "town centre" in content) and ("governor gear" in content):
        return discord.Embed(
            title="🏰 What TC level is required for governor gear?",
            description=("• **TC22** is required for governor gear.\n"),
            color=0x3498db
        )
    elif ("what" in content) and ("tc" in content or "town center" in content or "town centre" in content) and ("charm" in content):
        return discord.Embed(
            title="🏰 What TC level is required for charms?",
            description=("• **TC25** is required for governor charms\n"),
            color=0x3498db
        )
    elif ((("how" in content) and ("often" in content)) or ("when" in content and "is" in content)) and "fishing" in content:
        return discord.Embed(
            title="🎣 How often is the fishing even?",
            description=("The fishing event is **monthly**\n"),
            color=0x3498db
        )
    elif ((("how" in content) and (("often" in content)) or ("when" in content and "is" in content)))  and ("hall of governors" in content or "hog" in content):
        return discord.Embed(
            title="🏰 How often is the Hall of Governors event?",
            description=("The Hall of Governors event is generally every **2 weeks**\n"),
            color=0x3498db
        )
    elif ((("how" in content) and (("often" in content)) or ("when" in content and "is" in content))) and ("swordland" in content):
        return discord.Embed(
            title="⚔️ How often is the Swordland Sowdown event?",
            description=("The Swordland event is generally every **2 weeks**\n"),
            color=0x3498db
        )
    elif ((content.startswith("what") or content.startswith("how")) and ("vip" in content) and ("cost" in content or "requirements" in content or ("much" in content and "xp" in content))):
        embed = discord.Embed(
            title="💎 What are the VIP requirements?",
            color=0x3498db
        )
        embed.set_image(url="https://i.imgur.com/YLhEDYv.png")
        return embed
    elif (("how" in content) and ("much" in content or "many" in content) and ("res" in content or "resources" in content) and ("banner" in content or "flag" in content) and ("destroy" in content or "dismantle" in content)):
        return discord.Embed(
            title="🏴 How many resources are refunded when you destroy a banner?",
            description=("You get **10%** of the resources back from destroying a banner.\n"),
            color=0x3498db
        )
    elif ("can" in content or "what" in content or "?" in content) and ("do" in content or "use" in content) and ("extra" in content or "leftover" in content) and ("hero shards" in content or "shards" in content):
        return discord.Embed(
            title="🦸‍♂️ Can I do anything with extra hero shards?",
            description=("Yes there is an event called **Champagne Fair** where you can exchange extra hero shards for tickets.\n"
                        "1 rare shard = 6 tickets\n"
                        "1 epic shard = 10 tickets\n"
                        "1 legendary shard = 200 tickets\n"),
            color=0x3498db
        )
    elif ("do" in content or "will" in content or "?" in content) and ("purchases" in content or "items" in content or "packs" in content) and ("transfer" in content or "move" in content) and ("account" in content or "server" in content or "state" in content):
        return discord.Embed(
            title="💰 Do purchases on account transfer to new servers?",
            description=("No, purchases made on an account do not transfer to new servers. Items and packs are tied to the state/character where they were purchased."),
            color=0xe74c3c
        )
    elif ("how many" in content or "?" in content or "how long" in content or "how often" in content) and ("dayz" in content or "days" in content or "long" in content) and ("ke" in content or "kill event" in content or "all out" in content or "allout" in content):
        return discord.Embed(
            title="⚔️ How many days is KE?",
            description=("The Kill Event (All Out), lasts for **2 days**.\n"
                         "It is generally every **2 weeks** and takes place onf Friday to Saturday.\n"),
            color=0xe74c3c
        )
    elif ("how" in content or "where" in content or "?" in content) and ("make" in content or "give" in content) and ("suggestion" in content or "feedback" in content):
        return discord.Embed(
            title="💡 How to make a suggestion?",
            description="See the **#feedback** channel to share your suggestions!",
            color=0x3498db
        )
    elif ("how" in content or "?" in content) and ("get" in content or "unlock" in content) and ("burst of life" in content or ("burst" in content and "life" in content)):
        return discord.Embed(
            title="🌟 How to get the Burst of Life skin?",
            description="Reach **4M power** during the **Rookies Growth** event in the first week of a state.",
            color=0x3498db
        )
    elif ("is there" in content or "?" in content) and ("event" in content) and ("charms" in content):
        return discord.Embed(
            title="🏰 Is there an event for upgrading charms?",
            description="The 4th Hall of Governors has a day for upgrading charms.",
            color=0x3498db
        )
    """
    elif "show.me" in content:
        import subprocess
        result = subprocess.run(["python", "showMe.py", content], capture_output=True, text=True)
        if result.stdout:
            import json
            response = json.loads(result.stdout)
            embed = discord.Embed(
                title=response.get("title", ""),
                description=response.get("description", None),
                color=response.get("color", 0x3498db)
            )
            if response.get("image_url"):
                embed.set_image(url=response["image_url"])
            return embed
        """

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user}.")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="!help"
    ))

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot and message.author.id != 1365209252846768199:
        return

    if message.channel.id not in ALLOWED_CHANNEL_IDS:
        return

    embed = get_embed_response(message.content)
    if embed:
        async with message.channel.typing():
            sent_message = await message.channel.send(embed=embed)
            await sent_message.add_reaction("👍")
            await sent_message.add_reaction("👎")

    await bot.process_commands(message)

if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("❌ Error: DISCORD_TOKEN is not set in environment variables.")
