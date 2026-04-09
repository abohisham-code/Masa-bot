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
from flask import Flask
from threading import Thread

# ============================================================
# Flask - Keep Alive
# ============================================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

@app.route('/home')
def home():
    return "مـرافـق مـآإسـة شغّال 🎮"

def run_flask():
    app.run(host='0.0.0.0', port=5001, debug=False)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ============================================================
# اللوغ
# ============================================================
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger("games_bot")

# ============================================================
# الإعدادات
# ============================================================
SERVER    = "syriatalk.info"
PORT      = 5222
JID       = "shoq-hanen@syriatalk.info"
PASSWORD  = "shoq-hanen"
NICK      = "مـرافـق مـآإسـة"
MY_NICK   = "ابن سـ☆☆☆ـوريـــا"
MASA_NICK = "عطـ❃⊰ـرـر آإليـ❃⊰ـآإسميـن"
ROOMS = [
    "شمس@conference.syriatalk.info",
    "راقيات@conference.syriatalk.info",
]
MEMORY_FILE = "games_memory.json"

# اسم البوت الافتراضي لكل روم
ROOM_DEFAULT_NICKS = {
    "شمس@conference.syriatalk.info":    "مـرافـق مـآإسـة",
    "راقيات@conference.syriatalk.info": "Tasaly_MØHΛMΣD",
}

# ============================================================
# الأسئلة
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
    {"q": "🧠 شو أكبر حيوان بالعالم؟", "a": "الحوت الأزرق"},
    {"q": "🧠 كم ساق للأخطبوط؟", "a": "8"},
    {"q": "🧠 شو عاصمة كندا؟", "a": "أوتاوا"},
    {"q": "🧠 كم دولة بالعالم تقريباً؟", "a": "195"},
    {"q": "🧠 شو أطول جبل بالعالم؟", "a": "إيفرست"},
    {"q": "🧠 كم دقيقة بالساعة؟", "a": "60"},
    {"q": "🧠 شو عاصمة الصين؟", "a": "بكين"},
    {"q": "🧠 كم ضلع بالمسدس؟", "a": "6"},
    {"q": "🧠 شو أكبر صحراء بالعالم؟", "a": "الصحراء الكبرى"},
    {"q": "🧠 شو عاصمة أستراليا؟", "a": "كانبيرا"},
    {"q": "🧠 كم كوكب بالمجموعة الشمسية؟", "a": "8"},
]

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
    {"q": "🏀 كم لاعب بفريق كرة السلة؟", "a": "5"},
    {"q": "⚽ شو اسم ملعب ريال مدريد؟", "a": "سانتياغو برنابيو"},
    {"q": "🎱 كم كرة بالبلياردو؟", "a": "16"},
    {"q": "⚽ مين فاز بكأس العالم 2014؟", "a": "ألمانيا"},
    {"q": "⚽ كم مرة فازت الأرجنتين بكأس العالم؟", "a": "3"},
    {"q": "⚽ مين أكثر لاعب سجل أهداف بكأس العالم؟", "a": "كلوزة"},
    {"q": "⚽ شو لون بطاقة الإنذار بكرة القدم؟", "a": "أصفر"},
    {"q": "🏐 كم لاعب بفريق الكرة الطائرة؟", "a": "6"},
    {"q": "🎾 كم ست بمباراة التنس للرجال في غراند سلام؟", "a": "5"},
]

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
    {"q": "☪️ شو المسجد الأقصى موجود بأي مدينة؟", "a": "القدس"},
    {"q": "☪️ كم سورة بالقرآن الكريم؟", "a": "114"},
    {"q": "☪️ شو اسم أول نبي بالإسلام؟", "a": "آدم"},
    {"q": "☪️ كم ملك مقرب ذُكروا بالقرآن؟", "a": "3"},
]

WOMEN_QUESTIONS = [
    {"q": "👸 شو أشهر عطر نسائي بالعالم؟", "a": "شانيل"},
    {"q": "👸 شو أول لون مسكارا اخترع؟", "a": "أسود"},
    {"q": "👸 مين مصممة الأزياء كوكو شانيل؟", "a": "غابرييل"},
    {"q": "👸 شو اسم أشهر عارضة أزياء بالتسعينيات؟", "a": "ناعومي كامبل"},
    {"q": "👸 شو أصل كلمة سبا؟", "a": "لاتيني"},
    {"q": "👸 مين رسامة الشارب المكسيكية الشهيرة؟", "a": "فريدا كالو"},
    {"q": "👸 شو أشهر عملية تجميل بالعالم؟", "a": "الأنف"},
    {"q": "👸 كم شهر فترة الحمل؟", "a": "9"},
    {"q": "👸 شو أكثر لون يحبه النساء بالملابس؟", "a": "أسود"},
    {"q": "👸 مين اخترعت الميني جيب؟", "a": "ماري كوانت"},
    {"q": "👸 شو أغلى عطر نسائي بالعالم؟", "a": "كلايف كريستيان"},
    {"q": "👸 شو اسم حقيبة هيرميس الشهيرة؟", "a": "بيركين"},
    {"q": "👸 كم طبقة بالبشرة؟", "a": "3"},
    {"q": "👸 شو اسم أول ملكة جمال كون؟", "a": "فينيسا وليامز"},
    {"q": "👸 شو أكثر حجم حذاء مبيع للنساء عالمياً؟", "a": "37"},
]

MEN_QUESTIONS = [
    {"q": "💪 شو أقوى سيارة بالعالم من حيث الحصان؟", "a": "بوغاتي"},
    {"q": "💪 شو أشهر ماركة ساعات رجالية؟", "a": "رولكس"},
    {"q": "💪 كم سيلندر بمحرك V8؟", "a": "8"},
    {"q": "💪 شو أشهر ماركة موتوسيكل؟", "a": "هارلي ديفيدسون"},
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
    {"q": "💪 شو أكثر رياضة يمارسها الرجال عالمياً؟", "a": "كرة القدم"},
]

ACTORS_QUESTIONS = [
    {"q": "🎬 مين لعب دور أبو عصام بمسلسل باب الحارة؟", "a": "بسام كوسا"},
    {"q": "🎬 مين لعب دور أبو النار بباب الحارة؟", "a": "فارس الحلو"},
    {"q": "🎬 مين بطل مسلسل عصي الدمع؟", "a": "تيم حسن"},
    {"q": "🎬 مين لعبت دور نور بمسلسل نور التركي؟", "a": "فريحة جنير"},
    {"q": "🎬 مين بطل مسلسل الهيبة؟", "a": "تيم حسن"},
    {"q": "🎬 شو اسم الممثل السوري صاحب مسلسل ضيعة ضايعة؟", "a": "ياسر العظمة"},
    {"q": "🎬 مين لعب دور وطفة بباب الحارة؟", "a": "ديمة قندلفت"},
    {"q": "🎬 مين بطل مسلسل زنديق السوري؟", "a": "ماكسيم خليل"},
    {"q": "🎬 مين لعب دور الغندور بباب الحارة؟", "a": "محمد خير جراح"},
    {"q": "🎬 شو اسم الممثلة السورية بطلة مسلسل حرائر؟", "a": "نادين تحسين"},
    {"q": "🎬 مين لعب دور أبو بدر بمسلسل الخربة؟", "a": "عباد فهد"},
    {"q": "🎬 شو اسم بطل مسلسل قيامة أرطغرل التركي؟", "a": "أنجين آلتان"},
    {"q": "🎬 شو اسم الممثل السوري صاحب مسرح الشوك؟", "a": "دريد لحام"},
    {"q": "🎬 شو اسم بطل مسلسل قيامة عثمان؟", "a": "بوراك أوزجيفيت"},
    {"q": "🎬 مين لعب دور أبو حاتم بباب الحارة؟", "a": "رفيق سبيعي"},
    {"q": "🎬 مين لعب دور الشيخ متعب بمسلسل العاصوف؟", "a": "محمد المنصور"},
    {"q": "🎬 مين لعبت دور أم كلثوم بالمسلسل الشهير؟", "a": "صباح الجزائري"},
    {"q": "🎬 مين لعب دور مختار بمسلسل مختار الثقفي؟", "a": "عباس السماكي"},
    {"q": "🎬 مين لعبت دور شهرزاد بالمسلسل الإيراني؟", "a": "ترانه عليدوستي"},
    {"q": "🎬 مين لعب دور الملك عبدالعزيز بمسلسل العاصوف؟", "a": "عبدالمحسن النمر"},
]

RIDDLES = [
    {"q": "🧩 عندي أسنان بس ما بعض، شو أنا؟", "a": "مشط"},
    {"q": "🧩 بتحملني بيدك بس أنا ما إلي وزن، شو أنا؟", "a": "ظل"},
    {"q": "🧩 كلما أخدت منه كبر، شو هو؟", "a": "حفرة"},
    {"q": "🧩 عندي وجه بس ما عندي عيون، شو أنا؟", "a": "ساعة"},
    {"q": "🧩 ما إلي صوت بس بتسمعني، شو أنا؟", "a": "صدى"},
    {"q": "🧩 بالنهار خيمة وبالليل حبة، شو أنا؟", "a": "قبة السماء"},
    {"q": "🧩 أبيض من الثلج وأخف من الريح، شو أنا؟", "a": "نفس"},
    {"q": "🧩 كلما غسلته صار أوسخ، شو هو؟", "a": "ماء"},
    {"q": "🧩 دخلت غابة وما في شجر، دخلت بيت وما في باب، شو؟", "a": "صورة"},
    {"q": "🧩 فوق البيوت وما بنام، تحت الأرض وما بقام، شو أنا؟", "a": "سطح"},
    {"q": "🧩 بتمشي بدون قدام، شو أنا؟", "a": "سيارة"},
    {"q": "🧩 ما إلي أرجل بس بتمشي كل يوم، شو أنا؟", "a": "ساعة"},
]

# ============================================================
# دوال مساعدة
# ============================================================
def escape_xml(text):
    if not text:
        return ""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))

def strip_ns(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag

def render_xo_board(board):
    symbols = {0: "⬜", 1: "❌", 2: "⭕"}
    rows = []
    for r in range(3):
        rows.append(" ".join(symbols[board[r * 3 + c]] for c in range(3)))
    return "\n".join(rows)

def check_xo_winner(board):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for combo in wins:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != 0:
            return board[combo[0]]
    if all(c != 0 for c in board):
        return -1
    return 0

# ============================================================
# XMPP Connection
# ============================================================
class XMPPConnection:
    def __init__(self, jid, password, server, port):
        self.jid      = jid
        self.password = password
        self.server   = server
        self.port     = port
        self.domain   = jid.split("@")[1]
        self.reader   = None
        self.writer   = None
        self.connected = False
        self.buffer   = ""

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
        await self.send_raw(
            f"<?xml version='1.0'?>"
            f"<stream:stream to='{self.domain}' "
            f"xmlns='jabber:client' "
            f"xmlns:stream='http://etherx.jabber.org/streams' "
            f"version='1.0'>"
        )

    async def sasl_plain_auth(self):
        await self.open_stream()
        log.info("⏳ انتظار mechanisms...")
        attempts = 0
        while True:
            data = await self.recv_raw()
            if "mechanisms" in data:
                log.info("✅ استقبلنا mechanisms")
                break
            attempts += 1
            if attempts > 20:
                log.error("❌ timeout")
                return False

        auth_str = f"\0{self.jid.split('@')[0]}\0{self.password}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        log.info("📤 إرسال SASL PLAIN auth...")
        await self.send_raw(
            f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' "
            f"mechanism='PLAIN'>{auth_b64}</auth>"
        )

        resp = await self.recv_raw()
        if "failure" in resp:
            log.error(f"❌ فشل المصادقة: {resp[:100]}")
            return False

        if "success" in resp:
            log.info("✅ نجحت المصادقة SASL!")
            await self.open_stream()
            await self.recv_raw()
            log.info("📤 إرسال bind resource...")
            await self.send_raw(
                "<iq type='set' id='bind1'>"
                "<bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'>"
                "<resource>GamesBot_1.0</resource>"
                "</bind></iq>"
            )
            await self.recv_raw()
            await self.send_raw("<presence/>")
            await self.recv_raw()
            log.info("✅ تمت المصادقة الكاملة!")
            return True
        return False

    async def send_message(self, to_jid, body, mtype="groupchat"):
        await self.send_raw(
            f"<message to='{to_jid}' type='{mtype}'>"
            f"<body>{escape_xml(body)}</body>"
            f"</message>"
        )

# ============================================================
# GamesBot
# ============================================================
class GamesBot:
    def __init__(self, conn, nick):
        self.conn   = conn
        self.nick   = nick
        self.rooms  = list(ROOMS)
        self.memory = self.load_memory()
        self.memory.setdefault("points", {})
        self.memory.setdefault("admins", [])
        self.memory.setdefault("room_nicks", {})

        # حالة الألعاب
        self.active_game     = {}
        self.guess_games     = {}
        self.trivia_games    = {}
        self.riddle_games    = {}
        self.blackjack_games = {}
        self.xo_games        = {}
        self.dare_games      = {}

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

    def get_room_nick(self, room):
        return self.memory["room_nicks"].get(room, ROOM_DEFAULT_NICKS.get(room, self.nick))

    def add_points(self, room, nick, pts):
        self.memory["points"].setdefault(room, {}).setdefault(nick, 0)
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
        await self.conn.send_raw(
            "<presence><show>chat</show>"
            "<status>🎮 مـرافـق مـآإسـة | بوت الألعاب</status>"
            "</presence>"
        )
        await asyncio.sleep(1)
        for room in ROOMS:
            room_nick = self.get_room_nick(room)
            log.info(f"📥 دخول روم: {room} باسم {room_nick}")
            await self.conn.send_raw(
                f"<presence to='{room}/{room_nick}'>"
                f"<x xmlns='http://jabber.org/protocol/muc'/>"
                f"</presence>"
            )
            await asyncio.sleep(1)
        await asyncio.sleep(4)
        banner = (
            "┏━━━━━━━ 🎮 ━━━━━━━┓\n"
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
        room_nick = self.get_room_nick(room_jid)
        await self.conn.send_raw(
            f"<presence to='{room_jid}/{room_nick}'>"
            f"<x xmlns='http://jabber.org/protocol/muc'/>"
            f"</presence>"
        )
        if room_jid not in self.rooms:
            self.rooms.append(room_jid)
        await asyncio.sleep(1)
        await self.conn.send_message(
            room_jid,
            "┏━━━━━━━ 🎮 ━━━━━━━┓\n"
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
                candidates = [
                    (i, t) for i, t in [
                        (end_msg, "</message>"),
                        (end_pre, "</presence>"),
                        (end_iq,  "</iq>")
                    ] if i != -1
                ]
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

            # تجاهل رسائل البوت نفسه
            if sender_nick in list(ROOM_DEFAULT_NICKS.values()) + [self.nick]:
                return

            if tag == "presence":
                ptype = root.attrib.get("type", "")
                if sender_nick == "ماسة" and ptype != "unavailable" and room:
                    await asyncio.sleep(1)
                    await self.conn.send_message(
                        room,
                        "💎 أنا هون يا ماسة 🌹\nمرافقك الخاص جاهز! ✨"
                    )

            elif tag == "message":
                body_elem = root.find("{jabber:client}body") or root.find("body")
                if body_elem is None or not body_elem.text:
                    return
                body  = body_elem.text.strip()
                mtype = root.attrib.get("type", "chat")

                if mtype == "groupchat" and sender_nick:
                    await self._handle_group(room, sender_nick, body)
                elif mtype == "chat" and sender_nick:
                    await self._handle_private(frm, sender_nick, body)

        except Exception as e:
            log.error(f"stanza error: {e}")

    # ============================================================
    # معالجة رسائل الجروب
    # ============================================================
    async def _handle_group(self, room, nick, body):
        def reply(msg):
            asyncio.create_task(self.conn.send_message(room, msg))

        b = body.strip()

        # ============================================================
        # تحقق من الإجابات الجارية
        # ============================================================

        # تخمين رقم
        if room in self.guess_games:
            try:
                guess = int(b)
                game  = self.guess_games[room]
                game["attempts"] += 1
                if guess == game["number"]:
                    pts = max(10, 50 - game["attempts"] * 5)
                    self.add_points(room, nick, pts)
                    del self.guess_games[room]
                    self.active_game.pop(room, None)
                    reply(f"🎯 صح يا {nick}! الرقم كان {game['number']} 🎉\nربحت {pts} نقطة! ⭐")
                elif guess < game["number"]:
                    reply(f"📈 أكبر من {guess}!")
                else:
                    reply(f"📉 أصغر من {guess}!")
                return
            except ValueError:
                pass

        # أسئلة
        if room in self.trivia_games:
            game   = self.trivia_games[room]
            answer = game["answer"].strip()
            if b.strip() == answer or answer in b.strip():
                self.add_points(room, nick, 30)
                del self.trivia_games[room]
                self.active_game.pop(room, None)
                reply(f"✅ صح يا {nick}! الجواب: {answer} 🎉\nربحت 30 نقطة! ⭐")
                return

        # فوازير
        if room in self.riddle_games:
            game   = self.riddle_games[room]
            answer = game["answer"].strip()
            if b.strip() == answer or answer in b.strip():
                self.add_points(room, nick, 20)
                del self.riddle_games[room]
                self.active_game.pop(room, None)
                reply(f"🧩 صح يا {nick}! الجواب: {answer} 🎉\nربحت 20 نقطة! ⭐")
                return

        # أكس أو
        if room in self.xo_games:
            game = self.xo_games[room]
            if nick == game["players"][game["turn"]]:
                try:
                    cell = int(b) - 1
                    if 0 <= cell <= 8 and game["board"][cell] == 0:
                        game["board"][cell] = game["turn"] + 1
                        winner = check_xo_winner(game["board"])
                        board_str = render_xo_board(game["board"])
                        if winner in [1, 2]:
                            w_nick = game["players"][winner - 1]
                            self.add_points(room, w_nick, 50)
                            del self.xo_games[room]
                            self.active_game.pop(room, None)
                            reply(f"{board_str}\n\n🏆 {w_nick} فاز! +50 نقطة ⭐")
                        elif winner == -1:
                            del self.xo_games[room]
                            self.active_game.pop(room, None)
                            reply(f"{board_str}\n\n🤝 تعادل!")
                        else:
                            game["turn"] = 1 - game["turn"]
                            next_p  = game["players"][game["turn"]]
                            symbol  = "❌" if game["turn"] == 0 else "⭕"
                            reply(f"{board_str}\n\n{symbol} دور {next_p}، اختار رقم (1-9):")
                    else:
                        reply("❗ خلية غلط أو مشغولة، جرب تاني (1-9)")
                    return
                except ValueError:
                    pass

        # بلاك جاك
        if room in self.blackjack_games:
            game = self.blackjack_games[room]
            if nick == game["player"]:
                if b in ["اسحب", "hit"]:
                    card  = random.randint(1, 11)
                    game["player_cards"].append(card)
                    total = sum(game["player_cards"])
                    if total > 21:
                        del self.blackjack_games[room]
                        self.active_game.pop(room, None)
                        reply(f"💥 طارت عليك! مجموعك {total} - خسرت 😅\nأوراقك: {game['player_cards']}")
                    else:
                        reply(f"🃏 أوراقك: {game['player_cards']} = {total}\nاكتب 'اسحب' أو 'وقف'")
                    return
                elif b in ["وقف", "stand"]:
                    p_total = sum(game["player_cards"])
                    d_cards = game["dealer_cards"]
                    while sum(d_cards) < 17:
                        d_cards.append(random.randint(1, 10))
                    d_total = sum(d_cards)
                    del self.blackjack_games[room]
                    self.active_game.pop(room, None)
                    result = (
                        f"🃏 أوراقك: {game['player_cards']} = {p_total}\n"
                        f"🤖 أوراق البوت: {d_cards} = {d_total}\n"
                    )
                    if d_total > 21 or p_total > d_total:
                        self.add_points(room, nick, 40)
                        reply(result + f"🎉 {nick} فاز! +40 نقطة ⭐")
                    elif p_total == d_total:
                        reply(result + "🤝 تعادل!")
                    else:
                        reply(result + "😅 البوت فاز هالمرة!")
                    return

        # الصراحة
        if room in self.dare_games:
            game  = self.dare_games[room]
            phase = game.get("phase")

            if phase == "waiting_question" and nick == game.get("asker"):
                game["question"] = b
                game["phase"]    = "waiting_answer"
                reply(
                    f"❓ سؤال {nick} لـ {game['answerer']}:\n"
                    f"« {b} »\n\n"
                    f"💬 {game['answerer']}، شو جوابك؟"
                )
                return

            if phase == "waiting_answer" and nick == game.get("answerer"):
                game["phase"] = "done"
                reply(
                    f"✅ جواب {nick}:\n"
                    f"« {b} »\n\n"
                    f"اكتب 'دور جديد' لجولة ثانية أو 'إنهاء الصراحة' للوقف."
                )
                return

            if b in ["دور جديد", "كمّل"] and game.get("phase") == "done":
                asker, answerer = random.sample(game["players"], 2)
                game.update({"asker": asker, "answerer": answerer, "phase": "waiting_question", "question": ""})
                reply(f"🎲 دور جديد!\n\n🎤 {asker} يسأل {answerer}\nيلا {asker}، اكتب سؤالك! 👇")
                return

            if b in ["إنهاء الصراحة", "انهاء الصراحة"]:
                del self.dare_games[room]
                self.active_game.pop(room, None)
                reply("🔚 انتهت لعبة الصراحة. شكراً للكل! 🙏")
                return

        # ============================================================
        # الأوامر
        # ============================================================

        # قائمة الأوامر
        if b in ["العاب", "الألعاب", "اوامر"]:
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
                "🎲 نرد | 🎲 نرد [اسم]\n"
                "🎰 سلوت\n"
                "🃏 بلاك جاك\n"
                "❌⭕ أكس أو [اسم]\n"
                "🗣️ صراحة أحمد، سارة، محمد\n\n"
                "⭐ نقاطي | 🏆 توب\n"
                "🔚 إنهاء اللعبة (أدمن)\n"
                "📡 فوت [روم] | اطلع [روم]"
            )
            return

        # منع لعبتين
        if room in self.active_game and b not in ["نقاطي", "توب", "ريستارت", "إنهاء اللعبة", "انهاء اللعبة"]:
            if self.active_game[room] not in ["صراحة", "أكس أو", "بلاك جاك"]:
                reply(f"⚠️ في لعبة جارية ({self.active_game[room]})، انتظر تنتهي أو اطلب من الأدمن إنهاءها.")
                return

        # تخمين رقم
        if b == "تخمين رقم":
            self.guess_games[room] = {"number": random.randint(1, 100), "attempts": 0}
            self.active_game[room] = "تخمين رقم"
            reply("🎯 لعبة تخمين الرقم بدأت!\nخمّن رقم بين 1 و 100!")
            return

        # أسئلة
        questions_map = {
            "سؤال ثقافي":  TRIVIA_QUESTIONS,
            "سؤال رياضي":  SPORTS_QUESTIONS,
            "سؤال ديني":   RELIGIOUS_QUESTIONS,
            "سؤال نسواني": WOMEN_QUESTIONS,
            "سؤال رجالي":  MEN_QUESTIONS,
            "سؤال فني":    ACTORS_QUESTIONS,
        }
        for cmd, qlist in questions_map.items():
            if b == cmd or b == cmd.split()[1]:
                q = random.choice(qlist)
                self.trivia_games[room] = {"answer": q["a"]}
                self.active_game[room]  = cmd
                reply(f"{q['q']}\n\n⏳ الأول يجاوب صح يربح 30 نقطة! ⭐")
                return

        # فزورة
        if b in ["فزورة", "لغز"]:
            r = random.choice(RIDDLES)
            self.riddle_games[room] = {"answer": r["a"]}
            self.active_game[room]  = "فزورة"
            reply(f"{r['q']}\n\n⏳ الأول يجاوب صح يربح 20 نقطة! ⭐")
            return

        # نرد
        if b == "نرد":
            reply(f"🎲 {nick} رمى النرد... خرج {random.randint(1,6)}!")
            return

        if b.startswith("نرد "):
            opponent = b[4:].strip()
            d1, d2   = random.randint(1,6), random.randint(1,6)
            if d1 > d2:
                self.add_points(room, nick, 10)
                result = f"🏆 {nick} فاز!"
            elif d2 > d1:
                self.add_points(room, opponent, 10)
                result = f"🏆 {opponent} فاز!"
            else:
                result = "🤝 تعادل!"
            reply(f"🎲 {nick}: {d1}  vs  {opponent}: {d2}\n{result}")
            return

        # سلوت
        if b == "سلوت":
            symbols = ["🍒","🍋","🍊","⭐","💎","7️⃣","🔔"]
            s1,s2,s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
            line = f"[ {s1} | {s2} | {s3} ]"
            if s1==s2==s3:
                pts = 100 if s1=="💎" else 50
                self.add_points(room, nick, pts)
                reply(f"🎰 {line}\n🎉 جاكبوت! ربحت {pts} نقطة يا {nick}! 🔥")
            elif s1==s2 or s2==s3 or s1==s3:
                self.add_points(room, nick, 15)
                reply(f"🎰 {line}\n✨ مش بطال! ربحت 15 نقطة يا {nick}!")
            else:
                reply(f"🎰 {line}\n😅 حظ أحسن المرة الجاية {nick}!")
            return

        # بلاك جاك
        if b in ["بلاك جاك", "21"]:
            p = [random.randint(2,11), random.randint(2,11)]
            d = [random.randint(2,11), random.randint(2,11)]
            self.blackjack_games[room] = {"player": nick, "player_cards": p, "dealer_cards": d}
            self.active_game[room] = "بلاك جاك"
            reply(
                f"🃏 بلاك جاك! يا {nick}\n"
                f"أوراقك: {p} = {sum(p)}\n"
                f"ورقة البوت الظاهرة: {d[0]}\n\n"
                f"اكتب 'اسحب' أو 'وقف'"
            )
            return

        # أكس أو
        if b.startswith("أكس أو "):
            opponent = b[7:].strip()
            if not opponent:
                reply("❗ اكتب: أكس أو [اسم الخصم]")
                return
            board = [0] * 9
            self.xo_games[room] = {"players": [nick, opponent], "board": board, "turn": 0}
            self.active_game[room] = "أكس أو"
            reply(
                f"❌⭕ أكس أو!\n{nick} (❌) vs {opponent} (⭕)\n\n"
                f"{render_xo_board(board)}\n\n"
                f"1️⃣2️⃣3️⃣\n4️⃣5️⃣6️⃣\n7️⃣8️⃣9️⃣\n\n"
                f"❌ دور {nick}، اختار رقم (1-9):"
            )
            return

        # الصراحة
        if b.startswith("صراحة"):
            rest    = b[7:].strip()
            players = [p.strip() for p in rest.replace("،",",").split(",") if p.strip()]
            if nick not in players:
                players.insert(0, nick)
            if len(players) < 2:
                reply("❗ لازم لاعبين على الأقل.\nمثال: صراحة أحمد، سارة، محمد")
                return
            asker, answerer = random.sample(players, 2)
            self.dare_games[room] = {
                "players": players, "asker": asker,
                "answerer": answerer, "phase": "waiting_question", "question": ""
            }
            self.active_game[room] = "صراحة"
            reply(
                f"🗣️ لعبة الصراحة بدأت!\n"
                f"اللاعبين: {' | '.join(players)}\n\n"
                f"🎲 {asker} يسأل {answerer}\n"
                f"يلا {asker}، اكتب سؤالك! 👇"
            )
            return

        # إنهاء اللعبة
        if b in ["إنهاء اللعبة", "انهاء اللعبة"] and self.is_admin(nick):
            cleared = False
            for d in [self.active_game, self.guess_games, self.trivia_games,
                      self.riddle_games, self.blackjack_games, self.xo_games, self.dare_games]:
                if room in d:
                    del d[room]
                    cleared = True
            reply("🔚 تم إنهاء اللعبة." if cleared else "ℹ️ ما في لعبة جارية.")
            return

        # النقاط
        if b == "نقاطي":
            reply(f"⭐ {nick} عندك {self.get_points(room, nick)} نقطة.")
            return

        if b == "توب":
            room_pts = self.memory.get("points", {}).get(room, {})
            if not room_pts:
                reply("📭 ما في نقاط بعد.")
                return
            top = sorted(room_pts.items(), key=lambda x: x[1], reverse=True)[:5]
            reply("🏆 توب 5:\n" + "\n".join([f"{i}️⃣ {u}: {p} نقطة" for i,(u,p) in enumerate(top,1)]))
            return

        # الرومات
        if b.startswith("فوت ") and self.is_admin(nick):
            room_name = b[4:].strip()
            room_jid  = f"{room_name}@conference.syriatalk.info"
            await self.join_room(room_jid)
            reply(f"✅ دخلت روم {room_name}.")
            return

        if b.startswith("اطلع ") and self.is_admin(nick):
            room_name = b[5:].strip()
            room_jid  = f"{room_name}@conference.syriatalk.info" if "@" not in room_name else room_name
            await self.conn.send_raw(f"<presence to='{room_jid}/{self.get_room_nick(room_jid)}' type='unavailable'/>")
            if room_jid in self.rooms:
                self.rooms.remove(room_jid)
            reply(f"👋 طلعت من روم {room_name}.")
            return

        # تغيير الاسم
        if b.startswith("غير لقبي ") and self.is_admin(nick):
            new_nick = b[9:].strip()
            if not new_nick:
                reply("❗ الصيغة: غير لقبي [الاسم الجديد]")
                return
            self.memory["room_nicks"][room] = new_nick
            self.save_memory()
            reply(f"✅ تم حفظ الاسم ({new_nick}) لروم {room.split('@')[0]}، جاري الريستارت...")
            await asyncio.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return

        # ريستارت
        if b == "ريستارت" and self.is_admin(nick):
            reply("🔄 جاري الريستارت...")
            await asyncio.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return

        # إدارة أدمن
        if b.startswith("اعطاء ادمن ") and self.is_owner(nick):
            target = b[11:].strip()
            if target not in self.memory["admins"]:
                self.memory["admins"].append(target)
                self.save_memory()
                reply(f"✅ {target} صار أدمن.")
            else:
                reply(f"ℹ️ {target} أصلاً أدمن.")
            return

        if b.startswith("سحب ادمن ") and self.is_owner(nick):
            target = b[9:].strip()
            if target in self.memory["admins"]:
                self.memory["admins"].remove(target)
                self.save_memory()
                reply(f"❌ سُحب الأدمن من {target}.")
            return

    # ============================================================
    # الخاص
    # ============================================================
    async def _handle_private(self, frm, nick, body):
        jid = frm.split("/")[0]

        def reply(msg):
            asyncio.create_task(self.conn.send_message(jid, msg, mtype="chat"))

        if body.startswith("فوت ") and self.is_admin(nick):
            room_name = body[4:].strip()
            room_jid  = f"{room_name}@conference.syriatalk.info"
            await self.join_room(room_jid)
            reply(f"✅ دخلت روم {room_name}.")

        elif body == "ريستارت" and self.is_admin(nick):
            reply("🔄 جاري الريستارت...")
            await asyncio.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)


# ============================================================
# main
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
                    await conn.send_raw(
                        "<iq type='get' id='ping'>"
                        "<ping xmlns='urn:ietf:params:xml:ns:xmpp-ping'/>"
                        "</iq>"
                    )
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
