#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import asyncio
import json
from datetime import datetime
import pytz
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import FloodWaitError

# ========== سشن جدیدتو اینجا بذار ==========
STRING_SESSION = "1BJWap1wBu8BogZKyA7NsQolk9q6BhEHfWFwkjRhMGOmas_jLJmcmtATDDzQ0tGs_1hLc43hIOT5TTAYsUaKB865wHCfb3CaSyOfbled0g9nnLwkXgXFbxWI8K2v7Sd7MXqqXV7HjmjiF41UqfNhQLiDmEdqXx-B8qv6s5seNDTTfFb1rqIvifNj_loX32kn5flwZHNfycLuafHmVrpDVWr8ISZhihWKRE9mdCSKvBqpPrkqQ0gTpOgUbPNm0vCnQkyi59SkQdUopUAMk2sdcZvxfFgBHvAyeWwO7PjXxNSevdZnbFkc-TQhS7ZV7vv6Yhggo7oqvtOpKAuMDZMcE5RooEqGFUXk="
# ============================================

API_ID = 31266351
API_HASH = '0c86dc56c8937015b96c0f306e91fa05'

# ========== لیست پیشفرض ==========
DEFAULT_BAD_WORDS = ["کص ننت", "کیرم دهنت", "جنده"]
DEFAULT_JOKES = ["دوستت دارم رفیق!", "به به چه روز قشنگی!"]

class SelfBot:
    def __init__(self):
        self.enemy_id = None
        self.enemy_name = None
        self.enemy_chat_id = None
        self.enemy_mode = False
        self.friend_id = None
        self.friend_name = None
        self.friend_chat_id = None
        self.friend_mode = False
        self.clock_enabled = True
        self.original_name = ""
        self.bad_words = []
        self.jokes = []
        self.load_data()
        self.client = None
        self.me = None
        self.my_id = None
        self.running = True
    
    def load_data(self):
        try:
            if os.path.exists('bad_words.json'):
                with open('bad_words.json', 'r', encoding='utf-8') as f:
                    self.bad_words = json.load(f)
            else:
                self.bad_words = DEFAULT_BAD_WORDS.copy()
            
            if os.path.exists('jokes.json'):
                with open('jokes.json', 'r', encoding='utf-8') as f:
                    self.jokes = json.load(f)
            else:
                self.jokes = DEFAULT_JOKES.copy()
        except:
            self.bad_words = DEFAULT_BAD_WORDS.copy()
            self.jokes = DEFAULT_JOKES.copy()
    
    def save_data(self, filename, data):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    async def start(self):
        print("=" * 60)
        print("🔥 سلف بات - ورود با سشن")
        print("=" * 60)
        
        while self.running:
            try:
                # اتصال با سشن
                self.client = TelegramClient(
                    StringSession(STRING_SESSION),
                    API_ID,
                    API_HASH
                )
                
                print("📡 در حال اتصال...")
                await self.client.start()
                
                self.me = await self.client.get_me()
                self.my_id = self.me.id
                self.original_name = self.me.first_name or "کاربر"
                
                print(f"✅ متصل شدیم به: {self.original_name}")
                
                await self.update_clock()
                asyncio.create_task(self.clock_loop())
                await self.setup_handlers()
                
                print("\n✅ سلف بات فعال شد!")
                print("📌 دستورات: تنظیم دوست, تنظیم دشمن, خاموش دوست, خاموش دشمن, وضعیت, ساعت روشن, ساعت خاموش")
                
                await self.client.run_until_disconnected()
                
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(5)
    
    async def update_clock(self):
        try:
            if self.clock_enabled:
                now = datetime.now(pytz.timezone('Asia/Tehran'))
                time_str = now.strftime('%H:%M')
                await self.client(UpdateProfileRequest(
                    first_name=f"{self.original_name} {time_str}",
                    last_name=''
                ))
        except:
            pass
    
    async def clock_loop(self):
        while self.running:
            try:
                await self.update_clock()
                await asyncio.sleep(10)
            except:
                await asyncio.sleep(30)
    
    async def setup_handlers(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                if event.sender_id != self.my_id:
                    return
                
                text = event.raw_text or ""
                
                if text == "تنظیم دوست" and event.is_reply:
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                    self.friend_id = target.id
                    self.friend_name = target.first_name or "کاربر"
                    self.friend_chat_id = event.chat_id
                    self.friend_mode = True
                    await event.reply(f"✅ دوست شد: {self.friend_name}")
                
                elif text == "تنظیم دشمن" and event.is_reply:
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                    self.enemy_id = target.id
                    self.enemy_name = target.first_name or "کاربر"
                    self.enemy_chat_id = event.chat_id
                    self.enemy_mode = True
                    await event.reply(f"✅ دشمن شد: {self.enemy_name}")
                
                elif text == "خاموش دوست":
                    self.friend_mode = False
                    await event.reply("✅ دوست خاموش شد")
                
                elif text == "خاموش دشمن":
                    self.enemy_mode = False
                    await event.reply("✅ دشمن خاموش شد")
                
                elif text == "وضعیت":
                    await event.reply(
                        f"دوست: {self.friend_name if self.friend_mode else 'ندارد'}\n"
                        f"دشمن: {self.enemy_name if self.enemy_mode else 'ندارد'}\n"
                        f"ساعت: {'روشن' if self.clock_enabled else 'خاموش'}"
                    )
                
                elif text == "ساعت روشن":
                    self.clock_enabled = True
                    await self.update_clock()
                    await event.reply("✅ ساعت روشن شد")
                
                elif text == "ساعت خاموش":
                    self.clock_enabled = False
                    await self.update_clock()
                    await event.reply("⏹️ ساعت خاموش شد")
                
            except Exception as e:
                print(f"⚠️ خطا: {e}")
        
        @self.client.on(events.NewMessage)
        async def reply_handler(event):
            try:
                if self.friend_mode and event.sender_id == self.friend_id and event.chat_id == self.friend_chat_id:
                    if self.jokes and random.random() < 0.7:
                        await event.reply(random.choice(self.jokes))
                
                if self.enemy_mode and event.sender_id == self.enemy_id and event.chat_id == self.enemy_chat_id:
                    if self.bad_words and random.random() < 0.9:
                        await event.reply(random.choice(self.bad_words))
                        
            except:
                pass

# ========== اجرا ==========
if __name__ == "__main__":
    bot = SelfBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n🛑 بات متوقف شد")
