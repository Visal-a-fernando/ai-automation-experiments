"""One-time helper: discover your Telegram chat_id.

1. In Telegram, message @BotFather -> /newbot -> follow prompts -> copy the token.
2. Open your new bot and send it any message (e.g. /start).
3. Run:  python telegram_setup.py <token>
It prints the chat_id to set as TELEGRAM_CHAT.
"""
import sys, json, urllib.request

token = (sys.argv[1] if len(sys.argv) > 1 else input("Bot token: ")).strip()
data = json.loads(urllib.request.urlopen(
    f"https://api.telegram.org/bot{token}/getUpdates", timeout=30).read())
if not data.get("ok"):
    sys.exit(f"Telegram error: {data.get('description')}")

chats = {}
for u in data.get("result", []):
    msg = u.get("message") or u.get("callback_query", {}).get("message") or {}
    chat = msg.get("chat")
    if chat:
        chats[chat["id"]] = chat.get("username") or chat.get("first_name") or chat.get("title")

if not chats:
    print("No messages yet. Send your bot a message in Telegram, then rerun this.")
else:
    for cid, name in chats.items():
        print(f"chat_id = {cid}   ({name})")
