#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest

# ========== استرینگ سشن شما ==========
STRING_SESSION = "1BJWap1wBu8BogZKyA7NsQolk9q6BhEHfWFwkjRhMGOmas_jLJmcmtATDDzQ0tGs_1hLc43hIOT5TTAYsUaKB865wHCfb3CaSyOfbled0g9nnLwkXgXFbxWI8K2v7Sd7MXqqXV7HjmjiF41UqfNhQLiDmEdqXx-B8qv6s5seNDTTfFb1rqIvifNj_loX32kn5flwZHNfycLuafHmVrpDVWr8ISZhihWKRE9mdCSKvBqpPrkqQ0gTpOgUbPNm0vCnQkyi59SkQdUopUAMk2sdcZvxfFgBHvAyeWwO7PjXxNSevdZnbFkc-TQhS7ZV7vv6Yhggo7oqvtOpKAuMDZMcE5RooEqGFUXk="
# ====================================

# ========== لیست فحش‌های رکیک ==========
BAD_WORDS = [
    "کص ننت", "کیرم دهنت", "جنده", "کونی", "لاشی",
    "کص کش", "حرومزاده", "گاییدمت", "ننه جنده",
    "کصخل", "خارکصه", "تخم سگ", "پدر سوخته",
    "مادر جنده", "کیر تو کص ننت", "بی ناموس",
    "برو گمشو کصخل", "جاکش", "پدرسگ", "ننتو گاییدم",
    "کیر تو زندگی کصشعرت", "مادر سگ", "کص ننش"
]

class SelfBot:
    def __init__(self):
        self.enemy_id = None
        self.enemy_name = None
        self.enemy_mode = False
        self.client = None
        self.me = None
        self.original_bio = ""
        
    async def start(self):
        print("=" * 60)
        print("🔥 سلف بات فارسی - ورود با String Session")
        print("=" * 60)
        
        try:
            # اتصال با استرینگ سشن - بدون نیاز به کد تایید!
            self.client = TelegramClient(
                StringSession(STRING_SESSION),
                API_ID,
                API_HASH
            )
            
            print("📡 در حال اتصال به تلگرام...")
            await self.client.start()
            
            self.me = await self.client.get_me()
            print(f"✅ متصل شدیم به: {self.me.first_name}")
            print(f"👤 یوزرنیم: @{self.me.username}")
            print(f"🆔 آیدی: {self.me.id}")
            
            # ذخیره بیوگرافی
            self.original_bio = self.me.about or ""
            print(f"📝 بیوگرافی ذخیره شد")
            
            # شروع آپدیت ساعت (فقط عدد)
            asyncio.create_task(self.update_time())
            
            # تنظیم هندلرها
            await self.setup_handlers()
            
            print("\n" + "=" * 50)
            print("✅ سلف بات فعال شد!")
            print("📌 دستورات:")
            print("   • تنظیم دشمن (روی پیام ریپلای کن)")
            print("   • خاموش دشمن")
            print("   • وضعیت")
            print("=" * 50 + "\n")
            
            await self.client.run_until_disconnected()
            
        except Exception as e:
            print(f"❌ خطا: {e}")
            await asyncio.sleep(5)
    
    async def update_time(self):
        """آپدیت ساعت - فقط عدد، بدون ایموجی"""
        while True:
            try:
                iran_tz = pytz.timezone('Asia/Tehran')
                now = datetime.now(iran_tz)
                time_str = now.strftime('%H:%M')  # فقط ۱۴:۳۰
                
                await self.client(UpdateProfileRequest(
                    first_name=time_str,
                    last_name='',
                    about=self.original_bio
                ))
                
                print(f"🕒 ساعت: {time_str}")
                
            except:
                pass
            await asyncio.sleep(300)  # 5 دقیقه
    
    async def setup_handlers(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            if event.sender_id == self.me.id:
                return
            
            # تنظیم دشمن
            if event.raw_text == 'تنظیم دشمن' and event.is_reply:
                reply = await event.get_reply_message()
                target = await reply.get_sender()
                
                self.enemy_id = target.id
                self.enemy_name = target.first_name or "کاربر"
                self.enemy_mode = True
                
                await event.reply(f"✅ دشمن تنظیم شد: {self.enemy_name}")
                return
            
            # خاموش دشمن
            if event.raw_text == 'خاموش دشمن':
                self.enemy_mode = False
                await event.reply("✅ دشمن خاموش شد")
                return
            
            # وضعیت
            if event.raw_text == 'وضعیت':
                status = "فعال" if self.enemy_mode else "غیرفعال"
                enemy = self.enemy_name if self.enemy_mode else "ندارد"
                await event.reply(f"📊 وضعیت:\n🔥 دشمن: {enemy}\n⚡ حالت: {status}")
                return
            
            # پاسخ به دشمن
            if self.enemy_mode and event.sender_id == self.enemy_id:
                word = random.choice(BAD_WORDS)
                await event.reply(word)
                return
            
            # پاسخ خودکار
            if event.is_private:
                await asyncio.sleep(2)
                await event.reply("🔺به دلیل مشغله کاری ممکنه با تاخیر جواب بدم")

# اجرا
API_ID = 31266351
API_HASH = '0c86dc56c8937015b96c0f306e91fa05'

bot = SelfBot()
asyncio.run(bot.start())
