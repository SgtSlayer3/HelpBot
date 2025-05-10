File Sturctue:
.
├── bot.py (or main.py)
├── channelIDs.txt
├── giftCodes.txt
├── tcReqirements.txt
├── .env

A .env File in the root directory with the bots token must be made:
  DISCORD_TOKEN=your_token

Data Files:
- List of channel IDs bot is present in
- tcRequirements.txt contains the following Level|Prerequisites|Bread|Wood|Coal|Iron|Upgrade Time
- giftCodes.txt: Gift codes with expiration dates

How to compile/run:
- git clone https://github.com/SgtSlayer3/HelpBot.git
- pip install -r requirements.txt
- Create the .env, channelIDs.txt, and giftCodes.txt
- Run the bot

If you would like to run tests please see the test bot directory.
For a quick demo see: https://youtu.be/Q-Vmq03-QRA
