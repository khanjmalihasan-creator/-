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
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import FloodWaitError

# ========== سشن شما ==========
STRING_SESSION = "1BJWap1wBu0b7sSFAfVaBYk7OXk921RBlaDUfGFqfT25C1d3VqzuhPg3p_UlK5gScKmaL7Srbjk4KcYAirFtTfw_p1a33j10mdWiEaYps8xNo1SV4WfgS6d5PIj1jKSZJ0llGMvIp1gYks7QiKeiY-vhtZB53SPED6MJgWXb7sc0pyg2uGqmR0I2l1K1Xq_KaDC076h4ePuleNCF7yEz9YWDa5qP6lHlp-c7cXcf5gkcEvoW21NC9NhWK21vsrlvKh4NGAjMsVfcr5-IB8XXYKrp2Jf-1TINyR4diYyc-b_vzruDeUxQ7oGkuQ0_P8srVgDUQl0neaYmRvYU56wOZ2t1zbozOPcs="
# ====================================

API_ID = 31266351
API_HASH = '0c86dc56c8937015b96c0f306e91fa05'

class SelfBot:
    def __init__(self):
        # ===== کاربران خاص =====
        self.special_users = {}  # {user_id: {"name": "توماس", "replies": ["سلام", "خوبی"]}}
        
        # ===== دشمنان =====
        self.enemies = {}  # {user_id: {"name": "علی", "chat_id": 123, "bad_words": ["فحش1", "فحش2"]}}
        
        # ===== ساعت =====
        self.clock_enabled = True
        self.original_name = ""
        
        # ===== حالت بولد =====
        self.bold_mode = False
        
        # ===== تشخیص پیام حذف شده =====
        self.deleted_msg_tracking = {}  # {chat_id: {msg_id: {"text": "...", "user_id": 123, "name": "..."}}}
        self.delete_detection_enabled = False
        
        # ===== لیست فحش‌های پیشفرض =====
        self.default_bad_words = [
            "کص ننت", "کیرم دهنت", "جنده", "کونی", "لاشی",
            "کص کش", "حرومزاده", "گاییدمت", "ننه جنده"
        ]
        
        # ===== متغیرهای بات =====
        self.client = None
        self.me = None
        self.my_id = None
        self.running = True
        self.tasks = []
        
        self.load_data()
    
    def load_data(self):
        """لود اطلاعات از فایل"""
        try:
            if os.path.exists('special_users.json'):
                with open('special_users.json', 'r', encoding='utf-8') as f:
                    self.special_users = json.load(f)
                print(f"👥 {len(self.special_users)} کاربر خاص لود شد")
            
            if os.path.exists('enemies.json'):
                with open('enemies.json', 'r', encoding='utf-8') as f:
                    self.enemies = json.load(f)
                print(f"👤 {len(self.enemies)} دشمن لود شد")
                
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.bold_mode = settings.get('bold_mode', False)
                    self.delete_detection_enabled = settings.get('delete_detection', False)
                    self.clock_enabled = settings.get('clock_enabled', True)
                
        except Exception as e:
            print(f"⚠️ خطا در لود: {e}")
    
    def save_data(self):
        """ذخیره اطلاعات در فایل"""
        try:
            with open('special_users.json', 'w', encoding='utf-8') as f:
                json.dump(self.special_users, f, ensure_ascii=False, indent=2)
            
            with open('enemies.json', 'w', encoding='utf-8') as f:
                json.dump(self.enemies, f, ensure_ascii=False, indent=2)
            
            settings = {
                'bold_mode': self.bold_mode,
                'delete_detection': self.delete_detection_enabled,
                'clock_enabled': self.clock_enabled
            }
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    async def start(self):
        print("=" * 60)
        print("🔥 سلف بات - نسخه کامل با همه قابلیت‌ها")
        print("=" * 60)
        
        while self.running:
            try:
                self.client = TelegramClient(
                    StringSession(STRING_SESSION),
                    API_ID,
                    API_HASH,
                    connection_retries=5,
                    retry_delay=1
                )
                
                print("📡 در حال اتصال به تلگرام...")
                await self.client.start()
                
                self.me = await self.client.get_me()
                self.my_id = self.me.id
                self.original_name = self.me.first_name or "کاربر"
                
                print(f"✅ متصل شدیم به: {self.original_name}")
                print(f"🆔 آیدی من: {self.my_id}")
                print(f"👥 کاربران خاص: {len(self.special_users)}")
                print(f"👤 دشمنان: {len(self.enemies)}")
                print(f"⚡ حالت بولد: {'روشن' if self.bold_mode else 'خاموش'}")
                print(f"🚨 تشخیص حذف: {'روشن' if self.delete_detection_enabled else 'خاموش'}")
                
                await self.update_clock()
                clock_task = asyncio.create_task(self.clock_loop())
                self.tasks.append(clock_task)
                
                if self.delete_detection_enabled:
                    delete_task = asyncio.create_task(self.deleted_message_detector())
                    self.tasks.append(delete_task)
                
                await self.setup_handlers()
                
                print("\n" + "=" * 50)
                print("✅ سلف بات فعال شد!")
                self.show_commands()
                print("=" * 50 + "\n")
                
                await self.client.run_until_disconnected()
                
            except Exception as e:
                print(f"❌ خطا: {e}")
                await asyncio.sleep(5)
    
    def show_commands(self):
        """نمایش دستورات"""
        print("📌 **دستورات جدید:**")
        print("   • بولد روشن - فعال کردن حالت بولد")
        print("   • بولد خاموش - غیرفعال کردن حالت بولد")
        print("   • تشخیص حذف روشن - فعال کردن تشخیص پیام حذف شده")
        print("   • تشخیص حذف خاموش - غیرفعال کردن")
        print("   • پیگیری [آیدی] - شروع پیگیری پیام‌های یک کاربر")
        print("   • توقف پیگیری - توقف پیگیری")
        print("\n📌 **دستورات کاربران خاص:**")
        print("   • تنظیم کاربر [نام] (ریپلای) - مثال: تنظیم کاربر توماس")
        print("   • افزودن پاسخ [آیدی] => [متن]")
        print("   • حذف کاربر [آیدی]")
        print("   • لیست کاربران")
        print("\n📌 **دستورات دشمنان:**")
        print("   • تنظیم دشمن (ریپلای)")
        print("   • افزودن فحش [آیدی] => [متن]")
        print("   • حذف دشمن [آیدی]")
        print("   • لیست دشمنان")
        print("\n📌 **سایر:**")
        print("   • ساعت روشن/خاموش")
        print("   • وضعیت")
    
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
            else:
                await self.client(UpdateProfileRequest(
                    first_name=self.original_name,
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
    
    async def deleted_message_detector(self):
        """تشخیص پیام‌های حذف شده"""
        print("👀 شروع نظارت بر پیام‌های حذف شده...")
        
        while self.running and self.delete_detection_enabled:
            try:
                for chat_id, messages in list(self.deleted_msg_tracking.items()):
                    try:
                        # دریافت پیام‌های جدید
                        history = await self.client(GetHistoryRequest(
                            peer=chat_id,
                            limit=20,
                            offset_date=None,
                            offset_id=0,
                            max_id=0,
                            min_id=0,
                            add_offset=0,
                            hash=0
                        ))
                        
                        existing_ids = [msg.id for msg in history.messages]
                        
                        # بررسی پیام‌های حذف شده
                        for msg_id, msg_data in list(messages.items()):
                            if msg_id not in existing_ids:
                                # پیام حذف شده
                                alert = (
                                    f"🚨 **پیام حذف شد!**\n\n"
                                    f"👤 از: {msg_data['name']}\n"
                                    f"🆔 آیدی: {msg_data['user_id']}\n"
                                    f"📝 متن: {msg_data['text']}\n"
                                    f"🕒 زمان حذف: {datetime.now().strftime('%H:%M:%S')}"
                                )
                                await self.client.send_message(self.my_id, alert)
                                del self.deleted_msg_tracking[chat_id][msg_id]
                                
                    except Exception as e:
                        print(f"⚠️ خطا در بررسی چت {chat_id}: {e}")
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"⚠️ خطا در تشخیص حذف: {e}")
                await asyncio.sleep(5)
    
    async def setup_handlers(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            try:
                if event.sender_id != self.my_id:
                    return
                
                chat_id = event.chat_id
                text = event.raw_text or ""
                
                # ========== حالت بولد ==========
                if text == "بولد روشن":
                    self.bold_mode = True
                    self.save_data()
                    await event.reply("✅ حالت بولد فعال شد!")
                    return
                
                if text == "بولد خاموش":
                    self.bold_mode = False
                    self.save_data()
                    await event.reply("⏹️ حالت بولد غیرفعال شد!")
                    return
                
                # ========== تشخیص حذف ==========
                if text == "تشخیص حذف روشن":
                    self.delete_detection_enabled = True
                    self.save_data()
                    await event.reply("✅ تشخیص پیام حذف شده فعال شد!")
                    
                    # راه‌اندازی مجدد تسک
                    for task in self.tasks:
                        if task.get_name() == "delete_detector":
                            task.cancel()
                    delete_task = asyncio.create_task(self.deleted_message_detector(), name="delete_detector")
                    self.tasks.append(delete_task)
                    return
                
                if text == "تشخیص حذف خاموش":
                    self.delete_detection_enabled = False
                    self.save_data()
                    await event.reply("⏹️ تشخیص پیام حذف شده غیرفعال شد!")
                    return
                
                # ========== پیگیری کاربر ==========
                if text.startswith("پیگیری "):
                    try:
                        user_id = int(text[7:].strip())
                        
                        # دریافت اطلاعات کاربر
                        try:
                            user = await self.client.get_entity(user_id)
                            user_name = user.first_name or "کاربر"
                        except:
                            user_name = "کاربر ناشناس"
                        
                        # ذخیره برای پیگیری
                        if chat_id not in self.deleted_msg_tracking:
                            self.deleted_msg_tracking[chat_id] = {}
                        
                        await event.reply(
                            f"✅ پیگیری پیام‌های {user_name} فعال شد!\n"
                            f"🆔 آیدی: {user_id}\n"
                            f"📍 در این گروه"
                        )
                        
                    except Exception as e:
                        await event.reply(f"❌ خطا: {e}")
                    return
                
                if text == "توقف پیگیری":
                    if chat_id in self.deleted_msg_tracking:
                        del self.deleted_msg_tracking[chat_id]
                        await event.reply("✅ پیگیری متوقف شد")
                    else:
                        await event.reply("❌ پیگیری فعال نیست")
                    return
                
                # ========== تنظیم کاربر خاص ==========
                if text.startswith("تنظیم کاربر ") and event.is_reply:
                    try:
                        name = text[12:].strip()
                        reply = await event.get_reply_message()
                        target = await reply.get_sender()
                        
                        user_id = str(target.id)
                        self.special_users[user_id] = {
                            "name": name,
                            "replies": []
                        }
                        self.save_data()
                        
                        msg = f"✅ **کاربر خاص تنظیم شد!**\n👤 نام: {name}\n🆔 آیدی: {user_id}"
                        if self.bold_mode:
                            await event.reply(f"**{msg}**")
                        else:
                            await event.reply(msg)
                    except:
                        await event.reply("❌ خطا")
                    return
                
                # ========== افزودن پاسخ ==========
                if text.startswith("افزودن پاسخ "):
                    try:
                        parts = text[12:].split("=>")
                        if len(parts) == 2:
                            user_id = parts[0].strip()
                            reply_text = parts[1].strip()
                            
                            if user_id in self.special_users:
                                self.special_users[user_id]["replies"].append(reply_text)
                                self.save_data()
                                
                                msg = f"✅ پاسخ برای {self.special_users[user_id]['name']} اضافه شد:\n💬 {reply_text}"
                                if self.bold_mode:
                                    await event.reply(f"**{msg}**")
                                else:
                                    await event.reply(msg)
                            else:
                                await event.reply("❌ این کاربر وجود ندارد")
                        else:
                            await event.reply("❌ فرمت صحیح: افزودن پاسخ آیدی => متن")
                    except:
                        await event.reply("❌ خطا")
                    return
                
                # ========== تنظیم دشمن ==========
                if text == "تنظیم دشمن" and event.is_reply:
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                    
                    user_id = str(target.id)
                    self.enemies[user_id] = {
                        "name": target.first_name or "کاربر",
                        "chat_id": chat_id,
                        "bad_words": self.default_bad_words.copy()
                    }
                    self.save_data()
                    
                    msg = f"✅ **دشمن تنظیم شد!**\n👤 نام: {target.first_name}\n🆔 آیدی: {user_id}"
                    if self.bold_mode:
                        await event.reply(f"**{msg}**")
                    else:
                        await event.reply(msg)
                    return
                
                # ========== افزودن فحش ==========
                if text.startswith("افزودن فحش "):
                    try:
                        parts = text[11:].split("=>")
                        if len(parts) == 2:
                            user_id = parts[0].strip()
                            bad_word = parts[1].strip()
                            
                            if user_id in self.enemies:
                                self.enemies[user_id]["bad_words"].append(bad_word)
                                self.save_data()
                                
                                msg = f"✅ فحش برای {self.enemies[user_id]['name']} اضافه شد"
                                if self.bold_mode:
                                    await event.reply(f"**{msg}**")
                                else:
                                    await event.reply(msg)
                            else:
                                await event.reply("❌ این دشمن وجود ندارد")
                        else:
                            await event.reply("❌ فرمت صحیح: افزودن فحش آیدی => متن")
                    except:
                        await event.reply("❌ خطا")
                    return
                
                # ========== لیست‌ها ==========
                if text == "لیست کاربران":
                    if self.special_users:
                        msg = "📋 **لیست کاربران خاص:**\n\n"
                        for uid, data in self.special_users.items():
                            msg += f"👤 **{data['name']}** (آیدی: {uid})\n💬 {len(data['replies'])} پاسخ\n\n"
                        if self.bold_mode:
                            await event.reply(f"**{msg}**")
                        else:
                            await event.reply(msg)
                    else:
                        await event.reply("📭 هیچ کاربر خاصی وجود ندارد")
                    return
                
                if text == "لیست دشمنان":
                    if self.enemies:
                        msg = "👤 **لیست دشمنان:**\n\n"
                        for uid, data in self.enemies.items():
                            msg += f"🔥 {data['name']} (آیدی: {uid})\n💬 {len(data['bad_words'])} فحش\n\n"
                        if self.bold_mode:
                            await event.reply(f"**{msg}**")
                        else:
                            await event.reply(msg)
                    else:
                        await event.reply("✅ هیچ دشمنی وجود ندارد")
                    return
                
                # ========== ساعت ==========
                if text == "ساعت روشن":
                    self.clock_enabled = True
                    self.save_data()
                    await self.update_clock()
                    await event.reply("✅ ساعت روشن شد!")
                    return
                
                if text == "ساعت خاموش":
                    self.clock_enabled = False
                    self.save_data()
                    await self.update_clock()
                    await event.reply("⏹️ ساعت خاموش شد!")
                    return
                
                # ========== وضعیت ==========
                if text == "وضعیت":
                    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M:%S')
                    msg = (
                        f"📊 **وضعیت سلف بات**\n\n"
                        f"👥 کاربران خاص: {len(self.special_users)}\n"
                        f"👤 دشمنان: {len(self.enemies)}\n"
                        f"⚡ حالت بولد: {'🟢 روشن' if self.bold_mode else '🔴 خاموش'}\n"
        
