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
    "مادر جنده", "کیر تو کص ننت", "بی ناموس",
    "پدرسگ", "ننتو گاییدم", "جاکش", "کونده",
    "گاییده شده", "کثافت", "حیوان", "الاغ"
]

class SelfBot:
    def __init__(self):
        # ===== متغیرهای دشمن =====
        self.enemy_id = None
        self.enemy_name = None
        self.enemy_mode = False
        
        # ===== متغیرهای ساعت =====
        self.clock_enabled = True  # ساعت روشن
        self.original_name = ""    # اسم اصلی
        self.clock_running = False
        
        # ===== متغیرهای بات =====
        self.client = None
        self.me = None
        self.running = True
        
    async def start(self):
        print("=" * 60)
        print("🔥 سلف بات فارسی - نسخه نهایی")
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
                self.original_name = self.me.first_name or "کاربر"
                
                print(f"✅ متصل شدیم به: {self.original_name}")
                print(f"🆔 آیدی من: {self.me.id}")
                print(f"🕒 وضعیت ساعت: روشن")
                
                # آپدیت اولیه ساعت
                await self.update_clock()
                
                # شروع تسک‌ها
                asyncio.create_task(self.clock_loop())
                asyncio.create_task(self.keep_alive())
                
                # تنظیم هندلرها
                await self.setup_handlers()
                
                print("\n" + "=" * 50)
                print("✅ سلف بات فعال شد!")
                print("📌 دستورات ساعت:")
                print("   • ساعت روشن - فعال کردن ساعت روی پروفایل")
                print("   • ساعت خاموش - غیرفعال کردن ساعت")
                print("   • ساعت وضعیت - بررسی وضعیت ساعت")
                print("\n📌 دستورات دشمن:")
                print("   • تنظیم دشمن (روی پیام ریپلای کن)")
                print("   • خاموش دشمن")
                print("   • وضعیت")
                print("=" * 50 + "\n")
                
                await self.client.run_until_disconnected()
                
            except FloodWaitError as e:
                print(f"⚠️ محدودیت: {e.seconds} ثانیه صبر...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"❌ خطا: {e}")
                print("🔄 تلاش مجدد در ۵ ثانیه...")
                await asyncio.sleep(5)
    
    async def update_clock(self):
        """آپدیت ساعت روی پروفایل"""
        try:
            if self.clock_enabled:
                iran_tz = pytz.timezone('Asia/Tehran')
                now = datetime.now(iran_tz)
                time_str = now.strftime('%H:%M')
                
                await self.client(UpdateProfileRequest(
                    first_name=time_str,
                    last_name=''
                ))
                print(f"🕒 ساعت روشن: {time_str}")
            else:
                # برگشت به اسم اصلی
                await self.client(UpdateProfileRequest(
                    first_name=self.original_name,
                    last_name=''
                ))
                print(f"⏹️ ساعت خاموش: {self.original_name}")
            return True
        except Exception as e:
            print(f"⚠️ خطای ساعت: {e}")
            return False
    
    async def clock_loop(self):
        """لوپ اصلی ساعت - هر ۱ دقیقه"""
        while self.running:
            try:
                await self.update_clock()
                await asyncio.sleep(60)  # ۱ دقیقه
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except:
                await asyncio.sleep(30)
    
    async def keep_alive(self):
        """زنده نگه داشتن بات"""
        while self.running:
            try:
                await asyncio.sleep(30)
                await self.client.get_me()
            except:
                pass
    
    async def setup_handlers(self):
        """هندلر اصلی پیام‌ها"""
        
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                # ===== خودم نباشم =====
                if event.sender_id == self.me.id:
                    return
                
                sender = await event.get_sender()
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', 'پیام خصوصی')
                sender_name = sender.first_name or "کاربر"
                text = event.raw_text or ""
                
                print(f"📨 [{chat_title}] {sender_name}: {text[:30]}")
                
                # ========== دستورات ساعت ==========
                if text == "ساعت روشن":
                    if not self.clock_enabled:
                        self.clock_enabled = True
                        await self.update_clock()
                        await event.reply("✅ ساعت روشن شد!")
                    else:
                        await event.reply("⚠️ ساعت در حال حاضر روشنه!")
                    return
                
                if text == "ساعت خاموش":
                    if self.clock_enabled:
                        self.clock_enabled = False
                        await self.update_clock()
                        await event.reply("⏹️ ساعت خاموش شد!")
                    else:
                        await event.reply("⚠️ ساعت در حال حاضر خاموشه!")
                    return
                
                if text == "ساعت وضعیت":
                    status = "🟢 روشن" if self.clock_enabled else "🔴 خاموش"
                    current = "فعال" if self.clock_enabled else "غیرفعال"
                    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M')
                    await event.reply(
                        f"⏰ **وضعیت ساعت**\n\n"
                        f"📊 وضعیت: {status}\n"
                        f"🕒 ساعت فعلی: {now}\n"
                        f"⚡ آپدیت: هر ۱ دقیقه"
                    )
                    return
                
                # ========== دستورات دشمن ==========
                if text == "تنظیم دشمن":
                    if event.is_reply:
                        reply = await event.get_reply_message()
                        target = await reply.get_sender()
                        
                        self.enemy_id = target.id
                        self.enemy_name = target.first_name or "کاربر"
                        self.enemy_mode = True
                        
                        await event.reply(
                            f"✅ **دشمن تنظیم شد!**\n\n"
                            f"👤 کاربر: {self.enemy_name}\n"
                            f"🆔 آیدی: {self.enemy_id}\n"
                            f"🔥 از این به بعد فحش میخوره!"
                        )
                        print(f"🎯 دشمن جدید: {self.enemy_name}")
                    else:
                        await event.reply("❌ لطفاً روی پیام کاربر ریپلای کنید!")
                    return
                
                if text == "خاموش دشمن":
                    if self.enemy_mode:
                        self.enemy_mode = False
                        self.enemy_id = None
                        self.enemy_name = None
                        await event.reply("✅ حالت دشمن خاموش شد!")
                        print("🟢 دشمن خاموش شد")
                    else:
                        await event.reply("⚠️ دشمنی تنظیم نشده!")
                    return
                
                if text == "وضعیت":
                    # وضعیت دشمن
                    enemy_status = "🔥 فعال" if self.enemy_mode else "⭕ غیرفعال"
                    enemy_name = self.enemy_name if self.enemy_mode else "ندارد"
                    
                    # وضعیت ساعت
                    clock_status = "🟢 روشن" if self.clock_enabled else "🔴 خاموش"
                    
                    # زمان فعلی
                    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S')
                    
                    await event.reply(
                        f"📊 **وضعیت سلف بات**\n\n"
                        f"⏰ **ساعت:** {clock_status}\n"
                        f"🕒 **زمان:** {now}\n"
                        f"👤 **دشمن:** {enemy_name}\n"
                        f"🔥 **حالت دشمن:** {enemy_status}\n"
                        f"📍 **موقعیت:** {chat_title}"
                    )
                    return
                
                # ========== پاسخ به دشمن (فحش) ==========
                if self.enemy_mode and self.enemy_id and event.sender_id == self.enemy_id:
                    # 90% شانس فحش دادن
                    if random.random() < 0.9:
                        word = random.choice(BAD_WORDS)
                        await asyncio.sleep(random.uniform(0.3, 1))
                        await event.reply(word)
                        print(f"🔥 فحش به {self.enemy_name}: {word[:20]}")
                    return
                
                # ========== پاسخ خودکار به پیام خصوصی ==========
                if event.is_private:
                    await asyncio.sleep(random.uniform(2, 4))
                    await event.reply("🔺به دلیل مشغله کاری ممکنه با تاخیر جواب بدم")
                    print(f"🤖 پاسخ خودکار به {sender_name}")
                    
            except Exception as e:
                print(f"⚠️ خطا: {e}")

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
