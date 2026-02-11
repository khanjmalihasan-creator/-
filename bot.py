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
from telethon.errors import FloodWaitError

# ========== استرینگ سشن شما ==========
STRING_SESSION = "1BJWap1wBu8BogZKyA7NsQolk9q6BhEHfWFwkjRhMGOmas_jLJmcmtATDDzQ0tGs_1hLc43hIOT5TTAYsUaKB865wHCfb3CaSyOfbled0g9nnLwkXgXFbxWI8K2v7Sd7MXqqXV7HjmjiF41UqfNhQLiDmEdqXx-B8qv6s5seNDTTfFb1rqIvifNj_loX32kn5flwZHNfycLuafHmVrpDVWr8ISZhihWKRE9mdCSKvBqpPrkqQ0gTpOgUbPNm0vCnQkyi59SkQdUopUAMk2sdcZvxfFgBHvAyeWwO7PjXxNSevdZnbFkc-TQhS7ZV7vv6Yhggo7oqvtOpKAuMDZMcE5RooEqGFUXk="
# ====================================

API_ID = 31266351
API_HASH = '0c86dc56c8937015b96c0f306e91fa05'

# ========== لیست فحش‌های رکیک ==========
BAD_WORDS = [
    "کص ننت", "کیرم دهنت", "جنده", "کونی", "لاشی",
    "کص کش", "حرومزاده", "گاییدمت", "ننه جنده",
    "کصخل", "خارکصه", "تخم سگ", "پدر سوخته",
    "مادر جنده", "کیر تو کص ننت", "بی ناموس"
]

class SelfBot:
    def __init__(self):
        self.enemy_id = None
        self.enemy_name = None
        self.enemy_mode = False
        self.client = None
        self.me = None
        self.running = True
        
    async def start(self):
        print("=" * 60)
        print("🔥 سلف بات فارسی - فعال در گروه و خصوصی")
        print("=" * 60)
        
        while self.running:
            try:
                self.client = TelegramClient(
                    StringSession(STRING_SESSION),
                    API_ID,
                    API_HASH,
                    connection_retries=10,
                    retry_delay=2
                )
                
                print("📡 در حال اتصال به تلگرام...")
                await self.client.start()
                
                self.me = await self.client.get_me()
                print(f"✅ متصل شدیم به: {self.me.first_name}")
                print(f"🆔 آیدی من: {self.me.id}")
                
                # آپدیت اولیه ساعت
                await self.update_time_now()
                
                # شروع تسک آپدیت ساعت
                asyncio.create_task(self.time_updater_every_minute())
                
                # تنظیم هندلرها
                await self.setup_handlers()
                
                print("\n" + "=" * 50)
                print("✅ سلف بات فعال شد!")
                print("📍 فعال در: گروه‌ها + خصوصی")
                print("🕒 آپدیت ساعت: هر ۱ دقیقه")
                print("📌 دستورات:")
                print("   • تنظیم دشمن (روی پیام ریپلای کن)")
                print("   • خاموش دشمن")
                print("   • وضعیت")
                print("=" * 50 + "\n")
                
                await self.client.run_until_disconnected()
                
            except FloodWaitError as e:
                print(f"⚠️ محدودیت تلگرام: {e.seconds} ثانیه صبر...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"❌ خطا: {e}")
                print("🔄 تلاش مجدد در ۵ ثانیه...")
                await asyncio.sleep(5)
    
    async def update_time_now(self):
        """آپدیت ساعت پروفایل"""
        try:
            iran_tz = pytz.timezone('Asia/Tehran')
            now = datetime.now(iran_tz)
            time_str = now.strftime('%H:%M')
            
            await self.client(UpdateProfileRequest(
                first_name=time_str,
                last_name=''
            ))
            
            print(f"🕒 ساعت: {time_str}")
            return True
        except Exception as e:
            return False
    
    async def time_updater_every_minute(self):
        """آپدیت هر ۱ دقیقه"""
        while self.running:
            try:
                await self.update_time_now()
                await asyncio.sleep(60)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except:
                await asyncio.sleep(30)
    
    async def setup_handlers(self):
        """تنظیم هندلرها - کار در گروه و خصوصی"""
        
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                # ========== خودم نباشم ==========
                if event.sender_id == self.me.id:
                    return
                
                # ========== لاگ کردن همه پیامها ==========
                sender = await event.get_sender()
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', 'خصوصی')
                sender_name = sender.first_name or "کاربر"
                
                print(f"📨 [{chat_title}] {sender_name}: {event.raw_text[:30]}...")
                
                # ========== تنظیم دشمن (با ریپلای) ==========
                if event.raw_text == 'تنظیم دشمن':
                    if event.is_reply:
                        reply = await event.get_reply_message()
                        target = await reply.get_sender()
                        
                        self.enemy_id = target.id
                        self.enemy_name = target.first_name or "کاربر"
                        self.enemy_mode = True
                        
                        await event.reply(f"✅ دشمن تنظیم شد!\n👤 {self.enemy_name}\n🔥 از این به بعد فحش میخوری!")
                        print(f"🎯 دشمن جدید: {self.enemy_name} (ID: {self.enemy_id})")
                    else:
                        await event.reply("⚠️ لطفاً روی پیام کاربر ریپلای کن!")
                    return
                
                # ========== خاموش دشمن ==========
                if event.raw_text == 'خاموش دشمن':
                    if self.enemy_mode:
                        self.enemy_mode = False
                        self.enemy_id = None
                        self.enemy_name = None
                        await event.reply("✅ حالت دشمن خاموش شد!")
                        print("🟢 دشمن خاموش شد")
                    else:
                        await event.reply("⚠️ دشمنی تنظیم نشده!")
                    return
                
                # ========== وضعیت ==========
                if event.raw_text == 'وضعیت':
                    status = "🔥 فعال" if self.enemy_mode else "⭕ غیرفعال"
                    enemy = self.enemy_name if self.enemy_mode else "ندارد"
                    now = datetime.now(pytz.timezone('Asia/Tehran'))
                    time_str = now.strftime('%H:%M:%S')
                    
                    await event.reply(
                        f"📊 **وضعیت سلف بات**\n\n"
                        f"👤 **دشمن:** {enemy}\n"
                        f"🔥 **حالت:** {status}\n"
                        f"🕒 **ساعت:** {time_str}\n"
                        f"📍 **موقعیت:** گروه + خصوصی"
                    )
                    return
                
                # ========== پاسخ به دشمن (فحش رکیک) ==========
                if self.enemy_mode and self.enemy_id:
                    if event.sender_id == self.enemy_id:
                        # 85% شانس پاسخ
                        if random.random() < 0.85:
                            word = random.choice(BAD_WORDS)
                            
                            # تأخیر کوتاه برای طبیعی بودن
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                            await event.reply(word)
                            
                            print(f"🔥 فحش به {self.enemy_name}: {word[:20]}...")
                        else:
                            print(f"⏭️ فحش نداد به {self.enemy_name} (شانس)")
                    return
                
                # ========== پاسخ خودکار به پیام خصوصی ==========
                if event.is_private:
                    await asyncio.sleep(random.uniform(2, 4))
                    await event.reply("🔺به دلیل مشغله کاری ممکنه با تاخیر جواب بدم")
                    print(f"🤖 پاسخ خودکار به {sender_name}")
                    
            except Exception as e:
                print(f"⚠️ خطا در هندلر: {e}")

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
        print(f"\n❌ خطای اصلی: {e}")
        time.sleep(5)
        asyncio.run(main())
