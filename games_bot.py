#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import base64
import xml.etree.ElementTree as ET
import requests
import sys
import os
import random
import json
import time
from datetime import datetime
from flask import Flask
from threading import Thread

# --- إعدادات Flask ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

@app.route('/home')
def home():
    return "مرافق ماسة شغّال وعم يلعب 🎮"

def run_flask():
    app.run(host='0.0.0.0', port=5001, debug=False)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- إعدادات اللوغ ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger("games_bot")

# --- الإعدادات الأساسية ---
SERVER   = "syriatalk.info"
PORT     = 5222
JID      = "shoq-hanen@syriatalk.info"
PASSWORD = "shoq-hanen"
NICK      = "مـرافـق مـآإسـة"
MY_NICK   = "ابن سـ☆☆☆ـوريـــا"
MASA_NICK = "عطـ❃⊰ـرـر آإليـ❃⊰ـآإسميـن"  # أدمن ثابتة
ROOMS = [
    "شمس@conference.syriatalk.info",
    "راقيات@conference.syriatalk.info"
]
MEMORY_FILE = "games_memory.json"

# ============================================================
# أسئلة ثقافية
# ============================================================
TRIVIA_QUESTIONS = [
    {"q": "🧠 شو عاصمة اليابان؟", "a": "طوكيو"},
    {"q": "🧠 كم يوم بالسنة؟", "a": "365"},
    {"q": "🧠 مين رسم الموناليزا؟", "a": "ليوناردو دافنشي"},
    {"q": "🧠 شو أكبر كوكب بالمجموعة الشمسية؟", "a": "المشتري"},
    {"q": "🧠 كم لون بقوس قزح؟", "a": "7"},
    {"q": "🧠 شو عاصمة فرنسا؟", "a": "باريس"},
    {"q": "🧠 مين كتب روميو وجولييت؟", "a": "شكسبير"},
    {"q": "🧠 كم ضلع بالمثلث؟", "a": "3"},
    {"q": "🧠 شو أسرع حيوان بالعالم؟", "a": "الفهد"},
    {"q": "🧠 كم قارة بالعالم؟", "a": "7"},
    {"q": "🧠 شو أكبر محيط بالعالم؟", "a": "الهادئ"},
    {"q": "🧠 مين اخترع التلفون؟", "a": "غراهام بيل"},
    {"q": "🧠 شو عاصمة ألمانيا؟", "a": "برلين"},
    {"q": "🧠 كم نجمة بعلم أمريكا؟", "a": "50"},
    {"q": "🧠 شو أطول نهر بالعالم؟", "a": "النيل"},
    {"q": "🧠 شو عاصمة البرازيل؟", "a": "برازيليا"},
    {"q": "🧠 كم ساعة باليوم؟", "a": "24"},
    {"q": "🧠 شو أصغر دولة بالعالم؟", "a": "الفاتيكان"},
    {"q": "🧠 مين اخترع الكهرباء؟", "a": "إديسون"},
    {"q": "🧠 شو عاصمة إيطاليا؟", "a": "روما"},
    {"q": "🧠 شو أعمق بحيرة بالعالم؟", "a": "بايكال"},
    {"q": "🧠 كم عظمة بجسم الإنسان؟", "a": "206"},
    {"q": "🧠 مين اخترع المصباح الكهربائي؟", "a": "إديسون"},
    {"q": "🧠 شو أكبر حيوان بالعالم؟", "a": "الحوت الأزرق"},
    {"q": "🧠 كم ساق للأخطبوط؟", "a": "8"},
    {"q": "🧠 شو عاصمة كندا؟", "a": "أوتاوا"},
    {"q": "🧠 كم دولة بالعالم تقريباً؟", "a": "195"},
    {"q": "🧠 شو أطول جبل بالعالم؟", "a": "إيفرست"},
    {"q": "🧠 مين كتب ألف ليلة وليلة؟", "a": "مجهول"},
    {"q": "🧠 كم دقيقة بالساعة؟", "a": "60"},
    {"q": "🧠 شو عاصمة الصين؟", "a": "بكين"},
    {"q": "🧠 كم ضلع بالمسدس؟", "a": "6"},
    {"q": "🧠 شو أكبر صحراء بالعالم؟", "a": "الصحراء الكبرى"},
    {"q": "🧠 شو عاصمة أستراليا؟", "a": "كانبيرا"},
    {"q": "🧠 كم كوكب بالمجموعة الشمسية؟", "a": "8"},
]

# ============================================================
# أسئلة رياضية
# ============================================================
SPORTS_QUESTIONS = [
    {"q": "⚽ كم لاعب بفريق كرة القدم؟", "a": "11"},
    {"q": "⚽ كم دقيقة مباراة كرة القدم العادية؟", "a": "90"},
    {"q": "⚽ مين أكثر فريق فاز بكأس العالم؟", "a": "البرازيل"},
    {"q": "⚽ بأي بلد أُقيمت كأس العالم 2022؟", "a": "قطر"},
    {"q": "⚽ شو اسم ملعب برشلونة؟", "a": "كامب نو"},
    {"q": "⚽ كم ضربة جزاء بضربات الترجيح لكل فريق؟", "a": "5"},
    {"q": "🏀 كم نقطة تساوي رمية الثلاثة ببسكتبول؟", "a": "3"},
    {"q": "🎾 شو اسم أشهر بطولة تنس عالمية؟", "a": "ويمبلدون"},
    {"q": "⚽ مين سجل هدف اليد الشهير بكأس العالم؟", "a": "مارادونا"},
    {"q": "🏋️ شو الرياضة اللي بتشيل أوزان؟", "a": "رفع الأثقال"},
    {"q": "⚽ شو اسم كأس الأندية الأوروبية؟", "a": "دوري أبطال أوروبا"},
    {"q": "🏃 كم كيلو بسباق الماراثون؟", "a": "42"},
    {"q": "⚽ مين فاز بكأس العالم 2018؟", "a": "فرنسا"},
    {"q": "⚽ كم بوابة بملعب كرة القدم؟", "a": "2"},
    {"q": "🏀 كم لاعب بفريق كرة السلة؟", "a": "5"},
    {"q": "⚽ شو اسم ملعب ريال مدريد؟", "a": "سانتياغو برنابيو"},
    {"q": "🎱 كم كرة بالبلياردو؟", "a": "16"},
    {"q": "⚽ مين فاز بكأس العالم 2014؟", "a": "ألمانيا"},
    {"q": "⚽ كم مرة فازت الأرجنتين بكأس العالم؟", "a": "3"},
    {"q": "🏊 كم متر بالسباحة القصيرة أولمبياً؟", "a": "100"},
    {"q": "⚽ مين أكثر لاعب سجل أهداف بكأس العالم؟", "a": "كلوزة"},
    {"q": "🎾 كم ست بمباراة التنس للرجال في غراند سلام؟", "a": "5"},
    {"q": "⚽ شو لون بطاقة الإنذار بكرة القدم؟", "a": "أصفر"},
    {"q": "🏐 كم لاعب بفريق الكرة الطائرة؟", "a": "6"},
]

# ============================================================
# أسئلة دينية
# ============================================================
RELIGIOUS_QUESTIONS = [
    {"q": "☪️ كم ركن للإسلام؟", "a": "5"},
    {"q": "☪️ شو أول سورة بالقرآن الكريم؟", "a": "الفاتحة"},
    {"q": "☪️ كم آية بسورة الفاتحة؟", "a": "7"},
    {"q": "☪️ شو آخر سورة بالقرآن الكريم؟", "a": "الناس"},
    {"q": "☪️ كم جزء بالقرآن الكريم؟", "a": "30"},
    {"q": "☪️ شو اسم جبل الوحي؟", "a": "حراء"},
    {"q": "☪️ بأي شهر نزل القرآن؟", "a": "رمضان"},
    {"q": "☪️ كم سنة عاش النبي محمد ﷺ؟", "a": "63"},
    {"q": "☪️ شو اسم زوجة النبي الأولى؟", "a": "خديجة"},
    {"q": "☪️ كم مرة يصلي المسلم باليوم؟", "a": "5"},
    {"q": "☪️ شو اسم المدينة اللي هاجر إليها النبي ﷺ؟", "a": "المدينة"},
    {"q": "☪️ كم سنة استغرق نزول القرآن؟", "a": "23"},
    {"q": "☪️ شو أطول سورة بالقرآن؟", "a": "البقرة"},
    {"q": "☪️ شو أقصر سورة بالقرآن؟", "a": "الكوثر"},
    {"q": "☪️ كم شهر بالسنة الهجرية؟", "a": "12"},
    {"q": "☪️ شو اسم ملك الموت؟", "a": "عزرائيل"},
    {"q": "☪️ كم ملك مقرب ذُكروا بالقرآن؟", "a": "3"},
    {"q": "☪️ شو المسجد الأقصى موجود بأي مدينة؟", "a": "القدس"},
    {"q": "☪️ كم سورة بالقرآن الكريم؟", "a": "114"},
    {"q": "☪️ شو اسم أول نبي بالإسلام؟", "a": "آدم"},
]

# ============================================================
# أسئلة نسوانية
# ============================================================
WOMEN_QUESTIONS = [
    {"q": "👸 شو أشهر عطر نسائي بالعالم؟", "a": "شانيل"},
    {"q": "👸 شو أول لون مسكارا اخترع؟", "a": "أسود"},
    {"q": "👸 مين مصممة الأزياء كوكو شانيل؟", "a": "غابرييل"},
    {"q": "👸 شو اسم أشهر عارضة أزياء بالتسعينيات؟", "a": "ناعومي كامبل"},
    {"q": "👸 شو أكثر حجم حذاء مبيع للنساء عالمياً؟", "a": "37"},
    {"q": "👸 شو أصل كلمة سبا؟", "a": "لاتيني"},
    {"q": "👸 مين رسامة الشارب المكسيكية الشهيرة؟", "a": "فريدا كالو"},
    {"q": "👸 شو أشهر عملية تجميل بالعالم؟", "a": "الأنف"},
    {"q": "👸 شو اسم أول ملكة جمال كون؟", "a": "فينيسا وليامز"},
    {"q": "👸 كم شهر فترة الحمل؟", "a": "9"},
    {"q": "👸 شو أكثر لون يحبه النساء بالملابس؟", "a": "أسود"},
    {"q": "👸 مين اخترعت الميني جيب؟", "a": "ماري كوانت"},
    {"q": "👸 شو أغلى عطر نسائي بالعالم؟", "a": "كلايف كريستيان"},
    {"q": "👸 شو اسم حقيبة هيرميس الشهيرة؟", "a": "بيركين"},
    {"q": "👸 كم طبقة بالبشرة؟", "a": "3"},
]

# ============================================================
# أسئلة رجالية
# ============================================================
MEN_QUESTIONS = [
    {"q": "💪 شو أقوى سيارة بالعالم من حيث الحصان؟", "a": "بوغاتي"},
    {"q": "💪 شو أشهر ماركة ساعات رجالية؟", "a": "رولكس"},
    {"q": "💪 كم سيلندر بمحرك V8؟", "a": "8"},
    {"q": "💪 شو أشهر ماركة موتوسيكل؟", "a": "هارلي ديفيدسون"},
    {"q": "💪 شو أكثر رياضة يمارسها الرجال عالمياً؟", "a": "كرة القدم"},
    {"q": "💪 شو اسم أشهر لعبة فيديو بالتاريخ؟", "a": "ماريو"},
    {"q": "💪 كم لتر بالدم ببدن الرجل تقريباً؟", "a": "5"},
    {"q": "💪 شو أشهر ماركة جينز بالعالم؟", "a": "ليفايز"},
    {"q": "💪 شو اسم أشهر عطر رجالي؟", "a": "بلو دو شانيل"},
    {"q": "💪 كم كيلو وزن الملاكم الثقيل أكثر؟", "a": "90"},
    {"q": "💪 شو اسم أول لعبة إلكترونية بالتاريخ؟", "a": "بونج"},
    {"q": "💪 شو أغلى سيارة بالعالم؟", "a": "رولز رويس"},
    {"q": "💪 شو اسم أشهر بندقية بالعالم؟", "a": "كلاشنكوف"},
    {"q": "💪 كم رصاصة بمجلة AK47؟", "a": "30"},
    {"q": "💪 شو أسرع سيارة إنتاج بالعالم؟", "a": "بوغاتي"},
]

# ============================================================
# أسئلة فنية (ممثلين ومسلسلات)
# ============================================================
ACTORS_QUESTIONS = [
    {"q": "🎬 مين لعب دور أبو عصام بمسلسل باب الحارة؟", "a": "بسام كوسا"},
    {"q": "🎬 مين لعب دور أبو النار بباب الحارة؟", "a": "فارس الحلو"},
    {"q": "🎬 مين بطل مسلسل عصي الدمع؟", "a": "تيم حسن"},
    {"q": "🎬 مين لعبت دور نور بمسلسل نور التركي؟", "a": "فريحة جنير"},
    {"q": "🎬 مين لعب دور الملك عبدالعزيز بمسلسل العاصوف؟", "a": "عبدالمحسن النمر"},
    {"q": "🎬 مين بطل مسلسل الهيبة؟", "a": "تيم حسن"},
    {"q": "🎬 مين لعبت دور أم كلثوم بالمسلسل الشهير؟", "a": "صباح الجزائري"},
    {"q": "🎬 مين لعب دور مختار بمسلسل مختار الثقفي؟", "a": "عباس السماكي"},
    {"q": "🎬 شو اسم الممثل السوري صاحب مسلسل ضيعة ضايعة؟", "a": "ياسر العظمة"},
    {"q": "🎬 مين لعب دور وطفة بباب الحارة؟", "a": "ديمة قندلفت"},
    {"q": "🎬 مين بطل مسلسل زنديق السوري؟", "a": "ماكسيم خليل"},
    {"q": "🎬 مين لعب دور الغندور بباب الحارة؟", "a": "محمد خير جراح"},
    {"q": "🎬 شو اسم الممثلة السورية بطلة مسلسل حرائر؟", "a": "نادين تحسين"},
    {"q": "🎬 مين لعب دور أبو بدر بمسلسل الخربة؟", "a": "عباد فهد"},
    {"q": "🎬 شو اسم بطل مسلسل قيامة أرطغرل التركي؟", "a": "أنجين آلتان"},
    {"q": "🎬 مين لعبت دور شهرزاد بالمسلسل الإيراني؟", "a": "ترانه عليدوستي"},
    {"q": "🎬 شو اسم الممثل السوري صاحب مسرح الشوك؟", "a": "دريد لحام"},
    {"q": "🎬 مين لعب دور الشيخ متعب بمسلسل العاصوف؟", "a": "محمد المنصور"},
    {"q": "🎬 شو اسم بطل مسلسل قيامة عثمان؟", "a": "بوراك أوزجيفيت"},
    {"q": "🎬 مين لعب دور أبو حاتم بباب الحارة؟", "a": "رفيق سبيعي"},
]

# (الصراحة: الأسئلة من اللاعبين أنفسهم)

# ============================================================
# دوال مساعدة
# ============================================================
def escape_xml(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;")) if text else ""

def strip_ns(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag

def render_xo_board(board):
    symbols = {0: "⬜", 1: "❌", 2: "⭕"}
    rows = []
    for r in range(3):
        rows.append(" ".join(symbols[board[r * 3 + c]] for c in range(3)))
    return "\n".join(rows)

def check_xo_winner(board):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != 0:
            return board[combo[0]]
    if all(c != 0 for c in board):
        return -1  # تعادل
    return 0  # ما في فائز بعد

# ============================================================
# كلاس الاتصال XMPP
# ============================================================
class XMPPConnection:
    def __init__(self, jid, password, server, port):
        self.jid, self.password, self.server, self.port = jid, password, server, port
        self.domain = jid.split("@")[1]
        self.reader = self.writer = None
        self.connected = False
        self.buffer = ""

    async def connect(self):
        try:
            log.info(f"🔌 جاري الاتصال بـ {self.server}:{self.port} ...")
            self.reader, self.writer = await asyncio.open_connection(self.server, self.port)
            self.connected = True
            log.info("✅ تم الاتصال!")
            return True
        except Exception as e:
            log.error(f"❌ فشل الاتصال: {e}")
            return False

    async def send_raw(self, data):
        if self.writer:
            self.writer.write(data.encode())
            await self.writer.drain()

    async def recv_raw(self):
        if not self.reader:
            return ""
        try:
            data = await self.reader.read(4096)
            decoded = data.decode(errors="ignore") if data else ""
            if decoded:
                log.info(f"📥 RECV: {decoded[:300]}")
            return decoded
        except Exception as e:
            log.error(f"❌ recv error: {e}")
            return ""

    async def open_stream(self):
        await self.send_raw(f"<?xml version='1.0'?><stream:stream to='{self.domain}' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>")

    async def sasl_plain_auth(self):
        await self.open_stream()
        attempts = 0
        while True:
            data = await self.recv_raw()
            if "mechanisms" in data:
                break
            attempts += 1
            if attempts > 20:
                return False
        auth_str = f"\0{self.jid.split('@')[0]}\0{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        await self.send_raw(f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{auth_b64}</auth>")
        resp = await self.recv_raw()
        if "failure" in resp:
            return False
        if "success" in resp:
            await self.open_stream()
            await self.recv_raw()
            await self.send_raw("<iq type='set' id='bind1'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>GamesBot_1.0</resource></bind></iq>")
            await self.recv_raw()
            await self.send_raw("<presence/>")
            await self.recv_raw()
            return True

    async def send_message(self, to_jid, body, mtype="groupchat"):
        await self.send_raw(f"<message to='{to_jid}' type='{mtype}'><body>{escape_xml(body)}</body></message>")

# ============================================================
# كلاس البوت
# ============================================================
class GamesBot:
    def __init__(self, conn, nick):
        self.conn = conn
        self.nick = nick
        self.rooms = list(ROOMS)
        self.memory = self.load_memory()
        self.memory.setdefault("points", {})   # {room: {nick: points}}
        self.memory.setdefault("admins", [])
        self.memory.setdefault("room_nicks", {})

        # حالة الألعاب الجارية — مفتاح: room_jid
        self.active_game    = {}   # نوع اللعبة الجارية
        self.guess_games    = {}   # تخمين رقم
        self.trivia_games   = {}   # أسئلة ثقافية/رياضية
        self.riddle_games   = {}   # فوازير
        self.blackjack_games = {}  # بلاك جاك
        self.xo_games       = {}  # أكس أو
        self.dare_games     = {}   # الصراحة

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_memory(self):
        try:
            tmp = MEMORY_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
            os.replace(tmp, MEMORY_FILE)
        except Exception as e:
            log.error(f"Save error: {e}")

    def is_owner(self, nick):
        return nick == MY_NICK

    def is_admin(self, nick):
        return self.is_owner(nick) or nick == MASA_NICK or nick in self.memory.get("admins", [])

    def add_points(self, room, nick, pts):
        self.memory["points"].setdefault(room, {})
        self.memory["points"][room].setdefault(nick, 0)
        self.memory["points"][room][nick] += pts
        self.save_memory()

    def get_points(self, room, nick):
        return self.memory.get("points", {}).get(room, {}).get(nick, 0)

    # ============================================================
    # التشغيل
    # ============================================================
    async def start(self):
        if not await self.conn.sasl_plain_auth():
            return False
        asyncio.create_task(self._recv_loop())
        await asyncio.sleep(2)
        await self.conn.send_raw("<presence><show>chat</show><status>🎮 مـرافـق مـآإسـة | بوت الألعاب</status></presence>")
        await asyncio.sleep(1)
        for room in ROOMS:
            log.info(f"📥 جاري الدخول لروم: {room}")
            default_nick = "مـرافـق مـآإسـة" if room == "شمس@conference.syriatalk.info" else "Tasaly_MØHΛMΣD"
            room_nick = self.memory.get("room_nicks", {}).get(room, default_nick)
            await self.conn.send_raw(f"<presence to='{room}/{room_nick}'><x xmlns='http://jabber.org/protocol/muc'/></presence>")
            if room not in self.rooms:
                self.rooms.append(room)
            await asyncio.sleep(1)
        await asyncio.sleep(3)
        banner = (
            "┏━━━━━━━ 🎮 ━━━━━━━┓\n"
            "   مـرافـق مـآإسـة جاهز! 💎\n"
            "   بوت الألعاب الترفيهي\n"
            "  ᴘᴏᴡᴇʀᴇᴅ ʙʏ ابن سـ☆☆☆ـوريـــا\n"
            "┗━━━━━━━ 🎮 ━━━━━━━┛"
        )
        for room in ROOMS:
            await self.conn.send_message(room, banner)
            await asyncio.sleep(1)
        log.info("✅ البوت شغال!")
        return True

    async def join_room(self, room_jid):
        default_nick = "مـرافـق مـآإسـة" if room_jid == "شمس@conference.syriatalk.info" else "Tasaly_MØHΛMΣD"
        room_nick = self.memory.get("room_nicks", {}).get(room_jid, default_nick)
        await self.conn.send_raw(f"<presence to='{room_jid}/{room_nick}'><x xmlns='http://jabber.org/protocol/muc'/></presence>")
        if room_jid not in self.rooms:
            self.rooms.append(room_jid)
        await asyncio.sleep(1)
        await self.conn.send_message(room_jid,
            "┏━━━━━━━ 🎮 ━━━━━━━┓\n"
            "   مـرافـق مـآإسـة جاهز! 💎\n"
            "   بوت الألعاب الترفيهي\n"
            "  ᴘᴏᴡᴇʀᴇᴅ ʙʏ ابن سـ☆☆☆ـوريـــا\n"
            "┗━━━━━━━ 🎮 ━━━━━━━┛"
        )

    # ============================================================
    # حلقة الاستقبال
    # ============================================================
    async def _recv_loop(self):
        while self.conn.connected:
            data = await self.conn.recv_raw()
            if not data:
                break
            self.conn.buffer += data
            while True:
                end_msg = self.conn.buffer.find("</message>")
                end_pre = self.conn.buffer.find("</presence>")
                end_iq  = self.conn.buffer.find("</iq>")
                candidates = [(i, t) for i, t in [(end_msg, "</message>"), (end_pre, "</presence>"), (end_iq, "</iq>")] if i != -1]
                if not candidates:
                    break
                idx, tag = min(candidates, key=lambda x: x[0])
                end = idx + len(tag)
                stanza_str = self.conn.buffer[:end]
                self.conn.buffer = self.conn.buffer[end:]
                start = stanza_str.find("<")
                if start > 0:
                    stanza_str = stanza_str[start:]
                if stanza_str.strip():
                    await self._handle_stanza(stanza_str)

    async def _handle_stanza(self, xml_str):
        try:
            xml_str = xml_str.strip()
            s = xml_str.find("<")
            e = xml_str.rfind(">")
            if s == -1 or e == -1:
                return
            xml_str = xml_str[s:e+1]
            root = ET.fromstring(xml_str)
            tag  = strip_ns(root.tag)
            frm  = root.attrib.get("from", "")
            if "/" in frm:
                room        = frm.split("/")[0]
                sender_nick = frm.split("/")[1]
            else:
                room        = frm
                sender_nick = ""

            if sender_nick == self.nick:
                return

            # --- presence: دخول روم ---
            if tag == "presence":
                ptype = root.attrib.get("type", "")
                if sender_nick == "ماسة" and ptype != "unavailable" and room:
                    await asyncio.sleep(1)
                    await asyncio.sleep(1)
                    await self.conn.send_message(
                        room,
                        "💎 أنا هون يا ماسة 🌹\nمرافقك الخاص عطـ❃⊰ـرـر آإليـ❃⊰ـآإسميـن جاهز! ✨"
                    )

            elif tag == "message":
                body_elem = root.find("{jabber:client}body") or root.find("body")
                if body_elem is None or not body_elem.text:
                    return
                body  = body_elem.text.strip()
                mtype = root.attrib.get("type", "chat")

                if mtype == "groupchat" and sender_nick:
                    await self._handle_group_message(room, sender_nick, body)
                elif mtype == "chat" and sender_nick:
                    # خاص
                    target = frm.split("/")[0] if "@conference." in frm else frm.split("/")[0]
                    await self._handle_private(target, sender_nick, body, frm)

        except Exception as e:
            log.error(f"stanza error: {e}")

    # ============================================================
    # معالجة رسائل الجروب
    # ============================================================
    async def _handle_group_message(self, room, nick, body):
        def reply(msg):
            asyncio.create_task(self.conn.send_message(room, msg))

        body = body.strip()

        # --- تحقق من الإجابات الجارية أولاً ---
        # تخمين رقم
        if room in self.guess_games:
            try:
                guess = int(body)
                game  = self.guess_games[room]
                target_num = game["number"]
                attempts   = game["attempts"]
                game["attempts"] += 1
                if guess == target_num:
                    pts = max(10, 50 - attempts * 5)
                    self.add_points(room, nick, pts)
                    del self.guess_games[room]
                    if room in self.active_game:
                        del self.active_game[room]
                    reply(f"🎯 صح يا {nick}! الرقم كان {target_num} 🎉\nربحت {pts} نقطة! ⭐")
                elif guess < target_num:
                    reply(f"📈 أكبر من {guess}!")
                else:
                    reply(f"📉 أصغر من {guess}!")
                return
            except ValueError:
                pass

        # أسئلة ثقافية/رياضية
        if room in self.trivia_games:
            game   = self.trivia_games[room]
            answer = game["answer"].strip().lower()
            if body.strip().lower() == answer or answer in body.strip().lower():
                self.add_points(room, nick, 30)
                del self.trivia_games[room]
                if room in self.active_game:
                    del self.active_game[room]
                reply(f"✅ صح يا {nick}! الجواب: {game['answer']} 🎉\nربحت 30 نقطة! ⭐")
                return

        # فوازير
        if room in self.riddle_games:
            game   = self.riddle_games[room]
            answer = game["answer"].strip().lower()
            if body.strip().lower() == answer or answer in body.strip().lower():
                self.add_points(room, nick, 20)
                del self.riddle_games[room]
                if room in self.active_game:
                    del self.active_game[room]
                reply(f"🧩 صح يا {nick}! الجواب: {game['answer']} 🎉\nربحت 20 نقطة! ⭐")
                return

        # أكس أو — إدخال رقم الخلية
        if room in self.xo_games:
            game = self.xo_games[room]
            current_player = game["players"][game["turn"]]
            if nick == current_player:
                try:
                    cell = int(body) - 1
                    if 0 <= cell <= 8 and game["board"][cell] == 0:
                        game["board"][cell] = game["turn"] + 1
                        winner = check_xo_winner(game["board"])
                        board_str = render_xo_board(game["board"])
                        if winner == 1 or winner == 2:
                            w_nick = game["players"][winner - 1]
                            self.add_points(room, w_nick, 50)
                            del self.xo_games[room]
                            if room in self.active_game:
                                del self.active_game[room]
                            reply(f"{board_str}\n\n🏆 {w_nick} فاز بلعبة أكس أو! +50 نقطة ⭐")
                        elif winner == -1:
                            del self.xo_games[room]
                            if room in self.active_game:
                                del self.active_game[room]
                            reply(f"{board_str}\n\n🤝 تعادل!")
                        else:
                            game["turn"] = 1 - game["turn"]
                            next_player = game["players"][game["turn"]]
                            symbol = "❌" if game["turn"] == 0 else "⭕"
                            reply(f"{board_str}\n\n{symbol} دور {next_player}، اختار رقم (1-9):")
                    else:
                        reply(f"❗ خلية غلط أو مشغولة، جرب رقم تاني (1-9)")
                    return
                except ValueError:
                    pass

        # بلاك جاك
        if room in self.blackjack_games:
            game = self.blackjack_games[room]
            if nick == game["player"]:
                if body in ["اسحب", "hit"]:
                    card = random.randint(1, 11)
                    game["player_cards"].append(card)
                    total = sum(game["player_cards"])
                    if total > 21:
                        del self.blackjack_games[room]
                        if room in self.active_game:
                            del self.active_game[room]
                        reply(f"💥 طارت عليك! مجموعك {total} - خسرت 😅\nأوراقك: {game['player_cards']}")
                    else:
                        reply(f"🃏 أوراقك: {game['player_cards']} = {total}\nاكتب 'اسحب' للورقة التالية أو 'وقف' للوقوف")
                    return
                elif body in ["وقف", "stand"]:
                    player_total = sum(game["player_cards"])
                    dealer_total = sum(game["dealer_cards"])
                    # البوت يسحب حتى 17
                    while dealer_total < 17:
                        game["dealer_cards"].append(random.randint(1, 10))
                        dealer_total = sum(game["dealer_cards"])
                    del self.blackjack_games[room]
                    if room in self.active_game:
                        del self.active_game[room]
                    result = (
                        f"🃏 أوراقك: {game['player_cards']} = {player_total}\n"
                        f"🤖 أوراق البوت: {game['dealer_cards']} = {dealer_total}\n"
                    )
                    if dealer_total > 21 or player_total > dealer_total:
                        self.add_points(room, nick, 40)
                        reply(result + f"🎉 {nick} فاز! +40 نقطة ⭐")
                    elif player_total == dealer_total:
                        reply(result + "🤝 تعادل!")
                    else:
                        reply(result + "😅 البوت فاز هالمرة!")
                    return

        # الصراحة — منطق الأدوار
        if room in self.dare_games:
            game = self.dare_games[room]
            phase = game.get("phase")

            # المرحلة 1: اللي بيسأل يكتب سؤاله
            if phase == "waiting_question" and nick == game.get("asker"):
                game["question"] = body
                game["phase"] = "waiting_answer"
                answerer = game["answerer"]
                reply(
                    f"❓ سؤال {nick} لـ {answerer}:\n"
                    f"« {body} »\n\n"
                    f"💬 {answerer}، شو جوابك؟"
                )
                return

            # المرحلة 2: اللي بيجاوب يكتب جوابه
            if phase == "waiting_answer" and nick == game.get("answerer"):
                game["phase"] = "done"
                asker = game["asker"]
                reply(
                    f"✅ جواب {nick}:\n"
                    f"« {body} »\n\n"
                    f"اكتب 'دور جديد' لجولة ثانية أو 'إنهاء الصراحة' للوقف."
                )
                return

            # دور جديد
            if body in ["دور جديد", "كمّل"] and game.get("phase") == "done":
                players = game["players"]
                asker, answerer = random.sample(players, 2)
                game["asker"]    = asker
                game["answerer"] = answerer
                game["phase"]    = "waiting_question"
                game["question"] = ""
                reply(
                    f"🎲 دور جديد!\n\n"
                    f"🎤 {asker} يسأل {answerer}\n"
                    f"يلا {asker}، اكتب سؤالك هلق! 👇"
                )
                return

            # إنهاء الصراحة
            if body in ["إنهاء الصراحة", "انهاء الصراحة"]:
                del self.dare_games[room]
                if room in self.active_game:
                    del self.active_game[room]
                reply("🔚 انتهت لعبة الصراحة. شكراً للكل! 🙏")
                return

        # ============================================================
        # أوامر جديدة
        # ============================================================
        b = body

        # --- قائمة الألعاب ---
        if b in ["العاب", "الألعاب", "العاب🎮", "اوامر"]:
            reply(
                "🎮 ━━━ قائمة الألعاب ━━━ 🎮\n\n"
                "🎯 تخمين رقم\n"
                "❓ سؤال ثقافي\n"
                "⚽ سؤال رياضي\n"
                "☪️ سؤال ديني\n"
                "👸 سؤال نسواني\n"
                "💪 سؤال رجالي\n"
                "🎬 سؤال فني\n"
                "🧩 فزورة\n"
                "🎲 نرد\n"
                "🎲 نرد [اسم] — نرد ضد شخص\n"
                "🃏 بلاك جاك\n"
                "🎰 سلوت\n"
                "❌⭕ أكس أو [اسم] — ضد شخص\n"
                "🗣️ صراحة — لعبة جماعية\n\n"
                "📊 نقاطي | توب\n"
                "🔚 إنهاء اللعبة (للأدمن)\n"
                "📡 فوت [روم] | اطلع [روم]"
            )
            return

        # --- إدارة الرومات (للأدمن فقط) ---
        if b.startswith("فوت ") and self.is_admin(nick):
            room_name = b.replace("فوت", "").strip()
            room_jid  = f"{room_name}@conference.syriatalk.info"
            await self.join_room(room_jid)
            reply(f"✅ دخلت روم {room_name}.")
            return

        if b.startswith("اطلع ") and self.is_admin(nick):
            room_name = b.replace("اطلع", "").strip()
            room_jid  = f"{room_name}@conference.syriatalk.info" if "@" not in room_name else room_name
            await self.conn.send_raw(f"<presence to='{room_jid}/{self.nick}' type='unavailable'/>")
            if room_jid in self.rooms:
                self.rooms.remove(room_jid)
            reply(f"👋 طلعت من روم {room_name}.")
            return

        # --- إنهاء اللعبة ---
        if b in ["إنهاء اللعبة", "انهاء اللعبة", "🔚 إنهاء اللعبة"] and self.is_admin(nick):
            cleared = False
            for d in [self.active_game, self.guess_games, self.trivia_games,
                      self.riddle_games, self.blackjack_games, self.xo_games, self.dare_games]:
                if room in d:
                    del d[room]
                    cleared = True
            reply("🔚 تم إنهاء اللعبة الجارية." if cleared else "ℹ️ ما في لعبة جارية.")
            return

        # --- منع لعبتين بنفس الوقت ---
        if room in self.active_game and b not in ["نقاطي", "توب"]:
            game_name = self.active_game[room]
            # لعبة الصراحة والأكس أو والبلاك جاك يتعاملوا مع الأوامر بشكل خاص
            if game_name not in ["صراحة", "أكس أو", "بلاك جاك"]:
                reply(f"⚠️ في لعبة جارية ({game_name})، انتظر تنتهي أو اطلب الأدمن إنهاءها.")
                return

        # --- تخمين رقم ---
        if b == "🎯 تخمين رقم" or b == "تخمين رقم":
            number = random.randint(1, 100)
            self.guess_games[room]  = {"number": number, "attempts": 0}
            self.active_game[room]  = "تخمين رقم"
            reply("🎯 لعبة تخمين الرقم بدأت!\nاخترت رقم بين 1 و 100، شو هو؟")
            return

        # --- سؤال ثقافي ---
        if b in ["❓ سؤال ثقافي", "سؤال ثقافي", "سؤال"]:
            q = random.choice(TRIVIA_QUESTIONS)
            self.trivia_games[room] = {"answer": q["a"]}
            self.active_game[room]  = "سؤال ثقافي"
            reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
            return

        # --- سؤال رياضي ---
        if b in ["⚽ سؤال رياضي", "سؤال رياضي"]:
            q = random.choice(SPORTS_QUESTIONS)
            self.trivia_games[room] = {"answer": q["a"]}
            self.active_game[room]  = "سؤال رياضي"
            reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
            return

        # --- سؤال ديني ---
        if b in ["☪️ سؤال ديني", "سؤال ديني"]:
            q = random.choice(RELIGIOUS_QUESTIONS)
            self.trivia_games[room] = {"answer": q["a"]}
            self.active_game[room]  = "سؤال ديني"
            reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
            return

        # --- سؤال نسواني ---
        if b in ["👸 سؤال نسواني", "سؤال نسواني"]:
            q = random.choice(WOMEN_QUESTIONS)
            self.trivia_games[room] = {"answer": q["a"]}
            self.active_game[room]  = "سؤال نسواني"
            reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
            return

        # --- سؤال رجالي ---
        if b in ["💪 سؤال رجالي", "سؤال رجالي"]:
            q = random.choice(MEN_QUESTIONS)
            self.trivia_games[room] = {"answer": q["a"]}
            self.active_game[room]  = "سؤال رجالي"
            reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
            return

        # --- سؤال فني ---
        if b in ["🎬 سؤال فني", "سؤال فني"]:
            q = random.choice(ACTORS_QUESTIONS)
            self.trivia_games[room] = {"answer": q["a"]}
            self.active_game[room]  = "سؤال فني"
            reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
            return

        # --- فزورة ---
        if b in ["🧩 فزورة", "فزورة", "لغز"]:
            r = random.choice(RIDDLES)
            self.riddle_games[room] = {"answer": r["a"]}
            self.active_game[room]  = "فزورة"
            reply(f"{r['q']}\n\n⏳ الأول يجاوب صح يربح 20 نقطة! ⭐")
            return

        # --- نرد ---
        if b == "🎲 نرد" or b == "نرد":
            d = random.randint(1, 6)
            reply(f"🎲 {nick} رمى النرد... خرج {d}!")
            return

        if b.startswith("نرد ") or b.startswith("🎲 نرد "):
            opponent = b.replace("🎲 نرد", "").replace("نرد", "").strip()
            if not opponent:
                reply("❗ اكتب: نرد [اسم الشخص]")
                return
            d1 = random.randint(1, 6)
            d2 = random.randint(1, 6)
            if d1 > d2:
                result = f"🏆 {nick} فاز! ({d1} vs {d2})"
                self.add_points(room, nick, 10)
            elif d2 > d1:
                result = f"🏆 {opponent} فاز! ({d2} vs {d1})"
                self.add_points(room, opponent, 10)
            else:
                result = f"🤝 تعادل! ({d1} = {d2})"
            reply(f"🎲 {nick}: {d1}  vs  {opponent}: {d2}\n{result}")
            return

        # --- سلوت ---
        if b in ["🎰 سلوت", "سلوت"]:
            symbols = ["🍒", "🍋", "🍊", "⭐", "💎", "7️⃣", "🔔"]
            s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
            line = f"[ {s1} | {s2} | {s3} ]"
            if s1 == s2 == s3:
                pts = 100 if s1 == "💎" else 50
                self.add_points(room, nick, pts)
                reply(f"🎰 {line}\n🎉 جاكبوت! ربحت {pts} نقطة يا {nick}! 🔥")
            elif s1 == s2 or s2 == s3 or s1 == s3:
                self.add_points(room, nick, 15)
                reply(f"🎰 {line}\n✨ مش بطال! ربحت 15 نقطة يا {nick}!")
            else:
                reply(f"🎰 {line}\n😅 حظ أحسن المرة الجاية {nick}!")
            return

        # --- بلاك جاك ---
        if b in ["🃏 بلاك جاك", "بلاك جاك", "21"]:
            p_cards = [random.randint(2, 11), random.randint(2, 11)]
            d_cards = [random.randint(2, 11), random.randint(2, 11)]
            self.blackjack_games[room] = {
                "player": nick,
                "player_cards": p_cards,
                "dealer_cards": d_cards
            }
            self.active_game[room] = "بلاك جاك"
            total = sum(p_cards)
            reply(
                f"🃏 بلاك جاك! يا {nick}\n"
                f"أوراقك: {p_cards} = {total}\n"
                f"ورقة البوت الظاهرة: {d_cards[0]}\n\n"
                f"اكتب 'اسحب' لورقة إضافية أو 'وقف' للوقوف"
            )
            return

        # --- أكس أو ---
        if b.startswith("❌⭕ أكس أو") or b.startswith("أكس أو") or b.startswith("xo "):
            parts = b.replace("❌⭕ أكس أو", "").replace("أكس أو", "").replace("xo ", "").strip().split()
            opponent = parts[0] if parts else ""
            if not opponent:
                reply("❗ اكتب: أكس أو [اسم الخصم]")
                return
            board = [0] * 9
            self.xo_games[room] = {
                "players": [nick, opponent],
                "board": board,
                "turn": 0
            }
            self.active_game[room] = "أكس أو"
            board_str = render_xo_board(board)
            reply(
                f"❌⭕ أكس أو!\n{nick} (❌) vs {opponent} (⭕)\n\n"
                f"{board_str}\n\n"
                f"1️⃣2️⃣3️⃣\n4️⃣5️⃣6️⃣\n7️⃣8️⃣9️⃣\n\n"
                f"❌ دور {nick}، اختار رقم (1-9):"
            )
            return

        # --- الصراحة ---
        if b.startswith("🗣️ صراحة") or b.startswith("صراحة"):
            rest = b.replace("🗣️ صراحة", "").replace("صراحة", "").strip()
            if rest:
                players = [p.strip() for p in rest.replace("،", ",").replace("،", ",").split(",") if p.strip()]
                if nick not in players:
                    players.insert(0, nick)
                if len(players) < 2:
                    reply("❗ لازم لاعبين على الأقل.\nمثال: صراحة أحمد، سارة، محمد")
                    return
                # اختار أول سائل ومجاوب عشوائياً
                asker, answerer = random.sample(players, 2)
                self.dare_games[room] = {
                    "players": players,
                    "asker": asker,
                    "answerer": answerer,
                    "phase": "waiting_question",
                    "question": ""
                }
                self.active_game[room] = "صراحة"
                reply(
                    f"🗣️ لعبة الصراحة بدأت!\n"
                    f"اللاعبين: {' | '.join(players)}\n\n"
                    f"🎲 الاختيار العشوائي:\n"
                    f"🎤 {asker} يسأل {answerer}\n\n"
                    f"يلا {asker}، اكتب سؤالك هلق! 👇"
                )
            else:
                reply(
                    "❗ اكتب أسماء اللاعبين معك.\n"
                    "مثال: صراحة أحمد، سارة، محمد"
                )
            return

        # --- ريستارت ---
        if b in ["ريستارت", "restart"] and self.is_admin(nick):
            reply("🔄 جاري الريستارت...")
            await asyncio.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return

        # --- تغيير الاسم بالروم الحالية ---
        if b.startswith("غير لقبي ") and self.is_admin(nick):
            new_nick = b.replace("غير لقبي", "").strip()
            if not new_nick:
                reply("❗ الصيغة: غير لقبي [الاسم الجديد]")
                return
            # احفظ الاسم للروم الحالية
            self.memory.setdefault("room_nicks", {})[room] = new_nick
            self.save_memory()
            reply(f"✅ تم حفظ الاسم الجديد ({new_nick}) لروم {room.split('@')[0]}، جاري الريستارت...")
            await asyncio.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return

        # --- النقاط ---
        if b == "نقاطي":
            pts = self.get_points(room, nick)
            reply(f"⭐ {nick} عندك {pts} نقطة.")
            return

        if b == "توب":
            room_pts = self.memory.get("points", {}).get(room, {})
            if not room_pts:
                reply("📭 ما في نقاط بعد.")
                return
            top = sorted(room_pts.items(), key=lambda x: x[1], reverse=True)[:5]
            msg = "🏆 توب 5 بالنقاط:\n" + "\n".join([f"{i}️⃣ {u}: {p} نقطة" for i, (u, p) in enumerate(top, 1)])
            reply(msg)
            return

        # --- إدارة أدمن ---
        if b.startswith("اعطاء ادمن ") and self.is_owner(nick):
            target = b.replace("اعطاء ادمن", "").strip()
            if target not in self.memory["admins"]:
                self.memory["admins"].append(target)
                self.save_memory()
                reply(f"✅ {target} صار أدمن.")
            else:
                reply(f"ℹ️ {target} أصلاً أدمن.")
            return

        if b.startswith("سحب ادمن ") and self.is_owner(nick):
            target = b.replace("سحب ادمن", "").strip()
            if target in self.memory["admins"]:
                self.memory["admins"].remove(target)
                self.save_memory()
                reply(f"❌ سُحب الأدمن من {target}.")
            return

    # ============================================================
    # معالجة الخاص (فوت روم)
    # ============================================================
    async def _handle_private(self, target, nick, body, frm):
        def reply(msg):
            asyncio.create_task(self.conn.send_message(frm.split("/")[0] if "@conference." not in frm else frm, msg, mtype="chat"))

        if body.startswith("فوت ") and self.is_admin(nick):
            room_name = body.replace("فوت", "").strip()
            room_jid  = f"{room_name}@conference.syriatalk.info"
            await self.join_room(room_jid)
            reply(f"✅ دخلت روم {room_name}.")


# ============================================================
# التشغيل
# ============================================================
async def main():
    keep_alive()
    while True:
        try:
            log.info("🚀 [games_bot] بدء التشغيل...")
            conn = XMPPConnection(JID, PASSWORD, SERVER, PORT)
            if not await conn.connect():
                log.error("❌ فشل الاتصال، إعادة بعد 15 ثانية...")
                await asyncio.sleep(15)
                continue
            bot = GamesBot(conn, NICK)
            if not await bot.start():
                log.error("❌ فشل التشغيل، إعادة بعد 15 ثانية...")
                await asyncio.sleep(15)
                continue
            log.info("✅ بوت الألعاب شغال!")
            ping_fail = 0
            while conn.connected:
                await asyncio.sleep(30)
                try:
                    await conn.send_raw("<iq type='get' id='ping'><ping xmlns='urn:ietf:params:xml:ns:xmpp-ping'/></iq>")
                    ping_fail = 0
                except:
                    ping_fail += 1
                    if ping_fail >= 3:
                        conn.connected = False
                        break
        except Exception as e:
            log.error(f"❌ خطأ: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
