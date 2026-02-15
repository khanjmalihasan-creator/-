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

class SelfBot:
    def __init__(self):
        # ===== متغیرهای دشمن =====
        self.enemy_id = None
        self.enemy_name = None
        self.enemy_chat_id = None  # آیدی گروهی که توش تنظیم شده
        self.enemy_mode = False
        
        # ===== متغیرهای ساعت =====
        self.clock_enabled = True
        self.original_name = ""
        
        # ===== لیست فحش‌ها =====
        self.bad_words = []
        self.load_bad_words()
        
        # ===== متغیرهای بات =====
        self.client = None
        self.me = None
        self.my_id = None
        self.running = True
    
    def load_bad_words(self):
        """لود کردن لیست فحش‌ها از فایل"""
        try:
            if os.path.exists('bad_words.json'):
                with open('bad_words.json', 'r', encoding='utf-8') as f:
                    self.bad_words = json.load(f)
                print(f"📚 {len(self.bad_words)} فحش از فایل لود شد")
            else:
                self.bad_words = DEFAULT_BAD_WORDS.copy()
                self.save_bad_words()
                print(f"📚 {len(self.bad_words)} فحش پیشفرض لود شد")
        except Exception as e:
            print(f"⚠️ خطا: {e}")
            self.bad_words = DEFAULT_BAD_WORDS.copy()
    
    def save_bad_words(self):
        try:
            with open('bad_words.json', 'w', encoding='utf-8') as f:
                json.dump(self.bad_words, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    async def start(self):
        print("=" * 60)
        print("🔥 سلف بات فارسی - نسخه نهایی")
        print("✅ فقط خودت | فقط همون گروه | فقط کاربر واقعی")
        print("=" * 60)
        
        while self.running:
            try:
                self.client = TelegramClient(
                    StringSession(STRING_SESSION),
                    API_ID,
                    API_HASH,
                    connection_retries=999,
                    retry_delay=3
                )
                
                print("📡 در حال اتصال به تلگرام...")
                await self.client.start()
                
                self.me = await self.client.get_me()
                self.my_id = self.me.id
                self.original_name = self.me.first_name or "کاربر"
                
                print(f"✅ متصل شدیم به: {self.original_name}")
                print(f"🆔 آیدی من: {self.my_id}")
                print(f"📚 فحش‌ها: {len(self.bad_words)}")
                
                await self.update_clock()
                asyncio.create_task(self.clock_loop())
                await self.setup_handlers()
                
                print("\n" + "=" * 50)
                print("✅ سلف بات فعال شد!")
                print(f"👤 نام: {self.original_name}")
                print("🕒 ساعت: کنار اسم")
                print(f"📚 فحش‌ها: {len(self.bad_words)}")
                print("\n📌 قوانین:")
                print("   1️⃣ فقط خودت میتونی دستور بدی")
                print("   2️⃣ دشمن فقط تو همون گروه فحش میخوره")
                print("   3️⃣ به بات فحش داده نمیشه")
                print("=" * 50 + "\n")
                
                await self.client.run_until_disconnected()
                
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(5)
    
    async def update_clock(self):
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
                # ========== فقط خودم میتونم دستور بدم ==========
                if event.sender_id != self.my_id:
                    return  # ❌ هیچکس غیر از خودم
                
                chat = await event.get_chat()
                chat_id = event.chat_id
                chat_title = getattr(chat, 'title', 'خصوصی')
                text = event.raw_text or ""
                
                print(f"📨 دستور از خودم در {chat_title}: {text[:30]}")
                
                # ========== تنظیم دشمن ==========
                if text == "تنظیم دشمن":
                    if not event.is_reply:
                        await event.reply("❌ لطفاً روی پیام کاربر ریپلای کن!")
                        return
                    
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                    
                    # ✅ چک کردن بات بودن
                    if target.bot:
                        await event.reply("❌ نمیتونی بات رو دشمن کنی!")
                        return
                    
                    # ✅ ذخیره آیدی کاربر + آیدی گروه
                    self.enemy_id = target.id
                    self.enemy_name = target.first_name or "کاربر"
                    self.enemy_chat_id = chat_id  # آیدی همون گروه
                    self.enemy_mode = True
                    
                    await event.reply(
                        f"✅ **دشمن تنظیم شد!**\n\n"
                        f"👤 **کاربر:** {self.enemy_name}\n"
                        f"📍 **گروه:** {chat_title}\n"
                        f"🔥 فقط همینجا فحش میخوره!\n"
                        f"📚 **فحش‌ها:** {len(self.bad_words)}"
                    )
                    print(f"🎯 دشمن: {self.enemy_name} در {chat_title}")
                    return
                
                # ========== خاموش دشمن ==========
                if text == "خاموش دشمن":
                    if self.enemy_mode:
                        old_name = self.enemy_name
                        old_chat = "گروه"  # منبع
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
                    chat_name = "ندارد"
                    
                    # اگه دشمن فعاله، گروهش رو نشون بده
                    if self.enemy_mode and self.enemy_chat_id:
                        try:
                            chat_entity = await self.client.get_entity(self.enemy_chat_id)
                            chat_name = getattr(chat_entity, 'title', 'گروه')
                        except:
                            chat_name = "نامشخص"
                    
                    clock_status = "🟢 روشن" if self.clock_enabled else "🔴 خاموش"
                    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S')
                    
                    await event.reply(
                        f"📊 **وضعیت سلف بات**\n\n"
                        f"👤 **دشمن:** {enemy_name}\n"
                        f"📍 **مکان:** {chat_name}\n"
                        f"🔥 **حالت:** {enemy_status}\n"
                        f"⏰ **ساعت:** {clock_status}\n"
                        f"🕒 **زمان:** {now}\n"
                        f"📚 **فحش‌ها:** {len(self.bad_words)}"
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
                        self.save_bad_words()
                        await event.reply(f"✅ فحش اضافه شد: {word}\n📊 تعداد: {len(self.bad_words)}")
                    return
                
                if text.startswith("حذف فحش"):
                    word = text[9:].strip()
                    if word in self.bad_words:
                        self.bad_words.remove(word)
                        self.save_bad_words()
                        await event.reply(f"✅ فحش حذف شد: {word}")
                    return
                
                if text == "لیست فحش‌ها":
                    if not self.bad_words:
                        await event.reply("📭 لیست فحش‌ها خالی است!")
                        return
                    
                    words_list = "\n".join([f"{i+1}. {w}" for i, w in enumerate(self.bad_words[:20])])
                    more = f"\n... و {len(self.bad_words)-20} فحش دیگه" if len(self.bad_words) > 20 else ""
                    await event.reply(f"📋 **لیست فحش‌ها:**\n\n{words_list}{more}")
                    return
                
            except Exception as e:
                print(f"⚠️ خطا: {e}")
        
        # ========== هندلر فحش دادن به دشمن ==========
        @self.client.on(events.NewMessage)
        async def enemy_handler(event):
            try:
                # ✅ فقط اگه دشمن فعاله
                # ✅ فقط اگه فرستنده همون دشمنه
                # ✅ فقط اگه چت جاری همون گروهیه که توش تنظیم شده
                if (self.enemy_mode and 
                    self.enemy_id and 
                    self.enemy_chat_id and
                    event.sender_id == self.enemy_id and 
                    event.chat_id == self.enemy_chat_id):
                    
                    # 90% شانس فحش دادن
                    if random.random() < 0.9 and self.bad_words:
                        word = random.choice(self.bad_words)
                        await asyncio.sleep(random.uniform(0.3, 1))
                        await event.reply(word)
                        print(f"🔥 فحش به {self.enemy_name} در گروه: {word[:20]}")
                        
            except Exception as e:
                print(f"⚠️ خطا در فحش: {e}")

# ========== اجرا ==========
bot = SelfBot()

async def main():
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 سلف بات متوقف شد.")
        bot.running = False
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        time.sleep(5)
        asyncio.run(main())
