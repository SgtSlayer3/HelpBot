import sys
import json

def get_show_me_response(content: str):
    content = content.casefold()

    if "vip" in content and ("requirements" in content or "req" in content):
        return {
            "title": "💎 VIP requirements",
            "description": None,
            "image_url": "https://i.imgur.com/YLhEDYv.png",
            "color": 0x3498db
        }

    elif "example" in content:
        return {
            "title": "📘 Example Command",
            "description": "This is an example response for 'show me example'.",
            "image_url": None,
            "color": 0x3498db
        }

    return None

if __name__ == "__main__":
    # Accept content passed as arguments from helpBot.py
    content = " ".join(sys.argv[1:])
    response = get_show_me_response(content)

    if response:
        print(json.dumps(response))