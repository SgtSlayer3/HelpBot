import discord
import asyncio

TOKEN = 'MTM2NTIwOTI1Mjg0Njc2ODE5OQ.GvuRug.29i44GSnTbBO0gBQo4reWO7UyWI2ioanjl2tTo'
CHANNEL_ID = 1364582455436378213  # Replace this with your target channel ID
QUESTIONS_FILE = 'questions.txt'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Only respond in the specified channel
    if message.channel.id != CHANNEL_ID:
        return

    if message.content.strip() == "run.test":
        try:
            with open(QUESTIONS_FILE, 'r') as file:
                questions = file.readlines()

            for question in questions:
                question = question.strip()
                if question:
                    await message.channel.send(question)
                    await asyncio.sleep(5)

        except FileNotFoundError:
            await message.channel.send("Error: `questions.txt` not found.")
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

client.run(TOKEN)
