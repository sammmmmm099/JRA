import asyncio 
from pyrogram import Client, filters, enums
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

@Client.on_message(filters.command('start'))
async def start_message(c,m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
    await m.reply_photo(
        "https://envs.sh/ARa.jpg",
        caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Requests.</b>",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('- Mᴀɪɴ Cʜᴀɴɴᴇʟ -', url='https://t.me/Animes2u')],
                [InlineKeyboardButton('- Oɴɢᴏɪɴɢ Aɴɪᴍᴇ -', url='https://t.me/Animes3u')],
                [InlineKeyboardButton("◇ ᴘᴀɪᴅ ᴘʀᴏᴍᴏᴛɪᴏɴs ◇", url='https://t.me/Animes2u_Professor_Bot')],
                [
                    InlineKeyboardButton("⚡ ᴀʙᴏᴜᴛ ᴍᴇ", callback_data="about"),
                    InlineKeyboardButton("🍁 ᴄʟᴏꜱᴇ", callback_data="close")
                ]
            ]
        )
    )

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**To Accept Pending Requests, You Need To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. Please /logout First, Then Login Again With /login**")
    
    await show.edit(
        "**Now Forward A Message From Your Channel Or Group With Forward Tag\n\n"
        "Make Sure Your Logged-In Account Is Admin In That Channel Or Group With Full Rights.**"
    )
    
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and vj.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            await show.edit("**Error - Ensure Your Logged-In Account Is Admin In This Channel Or Group With The Necessary Rights.**")
            return
    else:
        return await message.reply("**Message Not Forwarded From A Channel Or Group.**")
    
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")

    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")
        
@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return 
    try:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id, m.from_user.first_name)
            await client.send_message(LOG_CHANNEL, LOG_TEXT.format(m.from_user.id, m.from_user.mention))
        
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        
        try:
            await client.send_message(
                m.from_user.id, 
                "**Hello {}!\nWelcome To {}\n\n__Powered By : @Animes2u __**".format(
                    m.from_user.mention, m.chat.title
                )
            )
            
            await m.reply_photo(
                "https://envs.sh/ARa.jpg",
                caption=f"<b>Hello {m.from_user.mention} 👋\n\nI Am Join Request Acceptor Bot. I Can Accept All Old Pending Join Requests.</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton('- Mᴀɪɴ Cʜᴀɴɴᴇʟ -', url='https://t.me/Animes2u')],
                        [InlineKeyboardButton('- Oɴɢᴏɪɴɢ Aɴɪᴍᴇ -', url='https://t.me/Animes3u')],
                        [InlineKeyboardButton("◇ ᴘᴀɪᴅ ᴘʀᴏᴍᴏᴛɪᴏɴs ◇", url='https://t.me/Animes2u_Professor_Bot')],
                        [
                            InlineKeyboardButton("⚡ ᴀʙᴏᴜᴛ ᴍᴇ", callback_data="about"),
                            InlineKeyboardButton("🍁 ᴄʟᴏꜱᴇ", callback_data="close")
                        ]
                    ]
                )
            )
        except:
            pass
    except Exception as e:
        print(str(e))
