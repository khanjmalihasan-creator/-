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

# ========== استرینگ سشن شما ==========
STRING_SESSION = "1BJWap1wBu8BogZKyA7NsQolk9q6BhEHfWFwkjRhMGOmas_jLJmcmtATDDzQ0tGs_1hLc43hIOT5TTAYsUaKB865wHCfb3CaSyOfbled0g9nnLwkXgXFbxWI8K2v7Sd7MXqqXV7HjmjiF41UqfNhQLiDmEdqXx-B8qv6s5seNDTTfFb1rqIvifNj_loX32kn5flwZHNfycLuafHmVrpDVWr8ISZhihWKRE9mdCSKvBqpPrkqQ0gTpOgUbPNm0vCnQkyi59SkQdUopUAMk2sdcZvxfFgBHvAyeWwO7PjXxNSevdZnbFkc-TQhS7ZV7vv6Yhggo7oqvtOpKAuMDZMcE5RooEqGFUXk="
# ====================================

API_ID = 31266351
API_HASH = '0c86dc56c8937015b96c0f306e91fa05'

# ========== لیست پیشفرض فحش‌ها ==========
DEFAULT_BAD_WORDS = [
    "کص ننت", "کیرم دهنت", "جنده", "کونی", "لاشی",
    "کص کش", "حرومزاده", "گاییدمت", "ننه جنده",
    "کصخل", "خارکصه", "تخم سگ", "پدر سوخته",
    "مادر جنده", "کیر تو کص ننت", "بی ناموس"
]

# ========== لیست پیشفرض جوک‌ها ==========
DEFAULT_JOKES = [
    "به به چه روز قشنگی!",
    "دوستت دارم رفیق! 🤗",
    "چطوری؟ خوبی؟",
    "خوشحالم که رفیقمی!",
    "بهترین دوست دنیا!"
]

class SelfBot:
    def __init__(self):
        # ===== متغیرهای دشمن =====
        self.enemy_id = None
        self.enemy_name = None
        self.enemy_chat_id = None
        self.enemy_mode = False
        
        # ===== متغیرهای دوست =====
        self.friend_id = None
        self.friend_name = None
        self.friend_chat_id = None
        self.friend_mode = False
        
        # ===== متغیرهای ساعت =====
        self.clock_enabled = True
        self.original_name = ""
        
        # ===== لیست فحش‌ها و جوک‌ها =====
        self.bad_words = []
        self.jokes = []
        self.load_data()
        
        # ===== متغیرهای بات =====
        self.client = None
        self.me = None
        self.my_id = None
        self.running = True
    
    def load_data(self):
        """لود کردن لیست فحش‌ها و جوک‌ها از فایل"""
        try:
            # لود فحش‌ها
            if os.path.exists('bad_words.json'):
                with open('bad_words.json', 'r', encoding='utf-8') as f:
                    self.bad_words = json.load(f)
                print(f"📚 {len(self.bad_words)} فحش از فایل لود شد")
            else:
                self.bad_words = DEFAULT_BAD_WORDS.copy()
                self.save_data('bad_words.json', self.bad_words)
                print(f"📚 {len(self.bad_words)} فحش پیشفرض لود شد")
            
            # لود جوک‌ها
            if os.path.exists('jokes.json'):
                with open('jokes.json', 'r', encoding='utf-8') as f:
                    self.jokes = json.load(f)
                print(f"😄 {len(self.jokes)} جوک از فایل لود شد")
            else:
                self.jokes = DEFAULT_JOKES.copy()
                self.save_data('jokes.json', self.jokes)
                print(f"😄 {len(self.jokes)} جوک پیشفرض لود شد")
                
        except Exception as e:
            print(f"⚠️ خطا در لود: {e}")
            self.bad_words = DEFAULT_BAD_WORDS.copy()
            self.jokes = DEFAULT_JOKES.copy()
    
    def save_data(self, filename, data):
        """ذخیره داده در فایل"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    async def start(self):
        """شروع بات با String Session - بدون نیاز به شماره"""
        print("=" * 60)
        print("🔥 سلف بات فارسی - ورود با String Session")
        print("✅ فقط با سشن - بدون نیاز به کد تایید")
        print("=" * 60)
        
        while self.running:
            try:
                # اتصال با String Session - نیازی به شماره نیست!
                self.client = TelegramClient(
                    StringSession(STRING_SESSION),
                    API_ID,
                    API_HASH,
                    connection_retries=999,
                    retry_delay=3
                )
                
                print("📡 در حال اتصال به تلگرام با سشن...")
                await self.client.start()  # بدون phone!
                
                self.me = await self.client.get_me()
                self.my_id = self.me.id
                self.original_name = self.me.first_name or "کاربر"
                
                print(f"✅ متصل شدیم به: {self.original_name}")
                print(f"🆔 آیدی من: {self.my_id}")
                print(f"📚 فحش‌ها: {len(self.bad_words)}")
                print(f"😄 جوک‌ها: {len(self.jokes)}")
                
                await self.update_clock()
                asyncio.create_task(self.clock_loop())
                await self.setup_handlers()
                
                print("\n" + "=" * 50)
                print("✅ سلف بات فعال شد!")
                print(f"👤 نام: {self.original_name}")
                print("🕒 ساعت: کنار اسم")
                print(f"📚 فحش‌ها: {len(self.bad_words)}")
                print(f"😄 جوک‌ها: {len(self.jokes)}")
                print("\n📌 دستورات:")
                print("   • تنظیم دوست (ریپلای کن)")
                print("   • خاموش دوست")
                print("   • تنظیم دشمن (ریپلای)")
                print("   • خاموش دشمن")
                print("   • ساعت روشن/خاموش")
                print("   • وضعیت")
                print("   • افزودن فحش [متن]")
                print("   • افزودن جوک [متن]")
                print("=" * 50 + "\n")
                
                await self.client.run_until_disconnected()
                
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(5)
    
    async def update_clock(self):
        """آپدیت ساعت روی پروفایل"""
        try:
            if self.clock_enabled:
                iran_tz = pytz.timezone('Asia/Tehran')
                now = datetime.now(iran_tz)
                time_str = now.strftime('%H:%M')
                full_name = f"{self.original_name} {time_str}"
                
                await self.client(UpdateProfileRequest(
                    first_name=full_name,
                    last_name=''
                ))
                print(f"🕒 پروفایل: {full_name}")
            else:
                await self.client(UpdateProfileRequest(
                    first_name=self.original_name,
                    last_name=''
                ))
            return True
        except:
            return False
    
    async def clock_loop(self):
        """لوپ آپدیت ساعت"""
        while self.running:
            try:
                await self.update_clock()
                await asyncio.sleep(10)  # هر ۱۰ ثانیه
            except:
                await asyncio.sleep(30)
    
    async def setup_handlers(self):
        """تنظیم هندلرها"""
        
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                # ========== فقط خودم میتونم دستور بدم ==========
                if event.sender_id != self.my_id:
                    return
                
                chat = await event.get_chat()
                chat_id = event.chat_id
                chat_title = getattr(chat, 'title', 'خصوصی')
                text = event.raw_text or ""
                
                print(f"📨 دستور از خودم در {chat_title}: {text[:30]}")
                
                # ========== تنظیم دوست ==========
                if text == "تنظیم دوست":
                    if not event.is_reply:
                        await event.reply("❌ لطفاً روی پیام کاربر ریپلای کن!")
                        return
                    
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                    
                    if target.bot:
                        await event.reply("❌ نمیتونی بات رو دوست کنی!")
                        return
                    
                    self.friend_id = target.id
                    self.friend_name = target.first_name or "کاربر"
                    self.friend_chat_id = chat_id
                    self.friend_mode = True
                    
                    await event.reply(
                        f"✅ **دوست تنظیم شد!**\n\n"
                        f"👤 **کاربر:** {self.friend_name}\n"
                        f"📍 **گروه:** {chat_title}\n"
                        f"😄 بهش جوک میدم!\n"
                        f"📚 **جوک‌ها:** {len(self.jokes)}"
                    )
                    print(f"😄 دوست جدید: {self.friend_name}")
                    return
                
                # ========== خاموش دوست ==========
                if text == "خاموش دوست":
                    if self.friend_mode:
                        old_name = self.friend_name
                        self.friend_mode = False
                        self.friend_id = None
                        self.friend_name = None
                        self.friend_chat_id = None
                        await event.reply(f"✅ دوست {old_name} خاموش شد!")
                    else:
                        await event.reply("⚠️ دوستی تنظیم نشده!")
                    return
                
                # ========== تنظیم دشمن ==========
                if text == "تنظیم دشمن":
                    if not event.is_reply:
                        await event.reply("❌ لطفاً روی پیام کاربر ریپلای کن!")
                        return
                    
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                    
                    if target.bot:
                        await event.reply("❌ نمیتونی بات رو دشمن کنی!")
                        return
                    
                    self.enemy_id = target.id
                    self.enemy_name = target.first_name or "کاربر"
                    self.enemy_chat_id = chat_id
                    self.enemy_mode = True
                    
                    await event.reply(
                        f"✅ **دشمن تنظیم شد!**\n\n"
                        f"👤 **کاربر:** {self.enemy_name}\n"
                        f"📍 **گروه:** {chat_title}\n"
                        f"🔥 فقط همینجا فحش میخوره!\n"
                        f"📚 **فحش‌ها:** {len(self.bad_words)}"
                    )
                    print(f"🎯 دشمن: {self.enemy_name}")
                    return
                
                # ========== خاموش دشمن ==========
                if text == "خاموش دشمن":
                    if self.enemy_mode:
                        old_name = self.enemy_name
                        self.enemy_mode = False
                        self.enemy_id = None
                        self.enemy_name = None
                        self.enemy_chat_id = None
                        await event.reply(f"✅ دشمن {old_name} خاموش شد!")
                    else:
                        await event.reply("⚠️ دشمنی تنظیم نشده!")
                    return
                
                # ========== وضعیت ==========
                if text == "وضعیت":
                    enemy_status = "🔥 فعال" if self.enemy_mode else "⭕ غیرفعال"
                    enemy_name = self.enemy_name if self.enemy_mode else "ندارد"
                    friend_status = "😄 فعال" if self.friend_mode else "⭕ غیرفعال"
                    friend_name = self.friend_name if self.friend_mode else "ندارد"
                    clock_status = "🟢 روشن" if self.clock_enabled else "🔴 خاموش"
                    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S')
                    
                    await event.reply(
                        f"📊 **وضعیت سلف بات**\n\n"
                        f"👤 **دوست:** {friend_name}\n"
                        f"😄 **حالت دوست:** {friend_status}\n"
                        f"👤 **دشمن:** {enemy_name}\n"
                        f"🔥 **حالت دشمن:** {enemy_status}\n"
                        f"⏰ **ساعت:** {clock_status}\n"
                        f"🕒 **زمان:** {now}\n"
                        f"📚 **فحش‌ها:** {len(self.bad_words)}\n"
                        f"😄 **جوک‌ها:** {len(self.jokes)}"
                    )
                    return
                
                # ========== دستورات ساعت ==========
                if text == "ساعت روشن":
                    self.clock_enabled = True
                    await self.update_clock()
                    await event.reply("✅ ساعت روشن شد!")
                    return
                
                if text == "ساعت خاموش":
                    self.clock_enabled = False
                    await self.update_clock()
                    await event.reply("⏹️ ساعت خاموش شد!")
                    return
                
                # ========== مدیریت فحش‌ها ==========
                if text.startswith("افزودن فحش"):
                    word = text[11:].strip()
                    if word and word not in self.bad_words:
                        self.bad_words.append(word)
                        self.save_data('bad_words.json', self.bad_words)
                        await event.reply(f"✅ فحش اضافه شد: {word}\n📊 تعداد: {len(self.bad_words)}")
                    return
                
                if text.startswith("حذف فحش"):
                    word = text[9:].strip()
                    if word in self.bad_words:
                        self.bad_words.remove(word)
                        self.save_data('bad_words.json', self.bad_words)
                        await event.reply(f"✅ فحش حذف شد: {word}")
                    return
                
                # ========== مدیریت جوک‌ها ==========
                if text.startswith("افزودن جوک"):
                    joke = text[11:].strip()
                    if joke and joke not in self.jokes:
                        self.jokes.append(joke)
                        self.save_data('jokes.json', self.jokes)
                        await event.reply(f"✅ جوک اضافه شد\n📊 تعداد: {len(self.jokes)}")
                    return
                
                if text.startswith("حذف جوک"):
                    joke = text[9:].strip()
                    if joke in self.jokes:
                        self.jokes.remove(joke)
                        self.save_data('jokes.json', self.jokes)
                        await event.reply(f"✅ جوک حذف شد")
                    return
                
            except Exception as e:
                print(f"⚠️ خطا: {e}")
        
        # ========== هندلر پاسخ به دوست و دشمن ==========
        @self.client.on(events.NewMessage)
        async def reply_handler(event):
            try:
                # فحش به دشمن
                if (self.enemy_mode and 
                    self.enemy_id and 
                    self.enemy_chat_id and
                    event.sender_id == self.enemy_id and 
                    event.chat_id == self.enemy_chat_id):
                    
                    if random.random() < 0.9 and self.bad_words:
                        word = random.choice(self.bad_words)
                        await asyncio.sleep(random.uniform(0.3, 1))
                        await event.reply(word)
                        print(f"🔥 فحش به {self.enemy_name}")
                
                # جوک به دوست
                if (self.friend_mode and 
                    self.friend_id and 
                    self.friend_chat_id and
                    event.sender_id == self.friend_id and 
                    event.chat_id == self.friend_chat_id):
                    
                    if random.random() < 0.7 and self.jokes:
                        joke = random.choice(self.jokes)
                        await asyncio.sleep(random.uniform(0.3, 1))
                        await event.reply(joke)
                        print(f"😄 جوک به {self.friend_name}")
                        
            except Exception as e:
                print(f"⚠️ خطا در پاسخ: {e}")

# ========== اجرا ==========
if __name__ == "__main__":
    bot = SelfBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n\n🛑 سلف بات متوقف شد.")
        bot.running = False
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        time.sleep(5)
        asyncio.run(bot.start())
