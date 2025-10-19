## iClinic - تشغيل البوت على Termux خطوة بخطوة

هذه الخطوات من الصفر حتى يعمل البوت. انسخ الأوامر كما هي بالترتيب.

### 1) تثبيت Termux وإعداد الأساسيات
- افتح تطبيق Termux ثم نفّذ:
```bash
pkg update -y && pkg upgrade -y
pkg install -y git python python-pip nano
```

### 2) جلب المشروع أو إنشاء مجلد العمل
- إذا عندك هذا المجلد على Github، استعمل:
```bash
git clone <YOUR_REPO_URL>.git iclinic
cd iclinic
```
- أو لو لا يوجد مستودع، أنشئ مجلدًا جديدًا وانسخ الملفات إليه:
```bash
mkdir -p iclinic && cd iclinic
```

### 3) إنشاء الملفات المطلوبة (إن لم تستخدم git clone)
- أنشئ البنية التالية:
```bash
mkdir -p iclinic/data/admin iclinic/data/user iclinic/iclinic
touch iclinic/__init__.py
```
- أنشئ ملفات البيانات (انسخ المحتوى من هذا المستند لاحقًا):
```bash
nano iclinic/data/emojis.json
nano iclinic/data/admin/main_menu.json
nano iclinic/data/admin/add_subject.json
nano iclinic/data/admin/add_case_or_question.json
nano iclinic/data/user/first_time.json
nano iclinic/data/user/home.json
```
- أنشئ ملفات البايثون:
```bash
nano iclinic/iclinic/texts.py
nano iclinic/bot.py
```

### 4) وضع الأكواد داخل الملفات
- افتح كل ملف بالأمر `nano <المسار>` ثم الصق النص المناسب. الأكواد كاملة موجودة أسفل هذا الدليل في قسم "المحتوى الكامل للملفات".
- للحفظ في nano: اضغط Ctrl+O ثم Enter ثم Ctrl+X للخروج.

### 5) إعداد البيئة والمتطلبات
```bash
cat > requirements.txt <<'EOF'
python-telegram-bot==21.4
python-dotenv==1.0.1
EOF

cat > .env <<'EOF'
BOT_TOKEN=123456789:YOUR_TELEGRAM_BOT_TOKEN_HERE
EOF

pip install --upgrade pip
pip install -r requirements.txt
```

### 6) تشغيل البوت
- شغّل البوت:
```bash
python -m iclinic.bot
```
- في تيليغرام، افتح محادثة البوت (الاسم iClinic) وأرسل `/start`.

### 7) تشغيل دائم في الخلفية (اختياري)
```bash
pip install tmux
# تشغيل جلسة جديدة
termux-wake-lock || true
# إن لم يكن tmux متاحًا على Termux استخدم nohup:
nohup python -m iclinic.bot >/dev/null 2>&1 &
```

---

## المحتوى الكامل للملفات

ضع كل ملف في المسار المذكور:

### iclinic/iclinic/texts.py
```python
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

@dataclass
class TextStore:
    root: Path
    @classmethod
    def default(cls) -> "TextStore":
        return cls(root=Path(__file__).resolve().parents[1] / "iclinic" / "data")
    def _load(self, *parts: str) -> Dict[str, Any] | List[Any]:
        path = self.root.joinpath(*parts)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    def emojis(self) -> Dict[str, str]:
        return self._load("emojis.json")
    def admin_main_menu(self) -> Dict[str, Any]:
        return self._load("admin", "main_menu.json")
    def admin_add_subject(self) -> Dict[str, Any]:
        return self._load("admin", "add_subject.json")
    def admin_add_case_or_question(self) -> Dict[str, Any]:
        return self._load("admin", "add_case_or_question.json")
    def user_first_time(self) -> Dict[str, Any]:
        return self._load("user", "first_time.json")
    def user_home(self) -> Dict[str, Any]:
        return self._load("user", "home.json")
```

### iclinic/bot.py
```python
from __future__ import annotations
import asyncio, os
from dataclasses import dataclass
from typing import List
from iclinic.iclinic.texts import TextStore
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

@dataclass
class IClinicBot:
    token: str
    texts: TextStore
    def keyboard(self, labels: List[str]) -> ReplyKeyboardMarkup:
        rows = [[label] for label in labels]
        return ReplyKeyboardMarkup(rows, resize_keyboard=True)
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_home = self.texts.user_home()
        labels = [item["label"] for item in user_home["menu"]]
        await update.message.reply_text(user_home["title"], reply_markup=self.keyboard(labels))
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = (update.message.text or "").strip()
        admin_menu = self.texts.admin_main_menu()
        admin_labels = [item["label"] for item in admin_menu["menu"]]
        if text in admin_labels:
            await update.message.reply_text(f"[Admin] اخترت: {text}")
        else:
            await update.message.reply_text("اختر خيارًا من القائمة ⬆️")
async def main() -> None:
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise SystemExit("Set BOT_TOKEN environment variable first")
    texts = TextStore.default()
    bot = IClinicBot(token=token, texts=texts)
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", bot.cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text))
    print("iClinic bot is running. Press Ctrl+C to stop.")
    await app.run_polling()
if __name__ == "__main__":
    asyncio.run(main())
```

### بيانات JSON
- أنشئ الملفات أدناه داخل `iclinic/data/`:

`iclinic/data/emojis.json`
```json
{"dna":"🧬","pill":"💊","thermometer":"🌡️","bandage":"🩹","lungs":"🫁","brain":"🧠","microbe":"🦠","telescope":"🔭","stethoscope":"🩺","microscope":"🔬","clamp":"🗜️"}
```

`iclinic/data/admin/main_menu.json`
```json
{"title":"iClinic Admin","header":"لوحة إدارة iClinic","menu":[{"id":"subjects","label":"إضافة مادة 🧬"},{"id":"case_or_question","label":"إضافة حالة مرضية أو سؤال 🩺❓"},{"id":"join","label":"طلبات الانضمام 🔭"},{"id":"delete","label":"الحذف 🗜️"}]}
```

`iclinic/data/admin/add_subject.json`
```json
{"prompt":"أدخل اسم المادة 🧬","confirm":["موافق ✅","لا ❌"],"saved":"تم حفظ المادة 📁"}
```

`iclinic/data/admin/add_case_or_question.json`
```json
{"menu":[{"id":"case","label":"حالة مرضية 🩺"},{"id":"question","label":"سؤال ❓"}],"shared":{"choose_subject":"اختر المادة 🧬"},"question":{"ask":"أدخل نص السؤال 🧠❓","choices_hint":"A) ...\nB) ...\nC) ...\nD) ...\nE) ...","answer_prompt":"اختر الإجابة الصحيحة ✅","saved":"تم حفظ السؤال 📁"},"case":{"ask":"أدخل تفاصيل الحالة 🩺","help":"الأعراض 🌡️🩹، سوابق 🧬، فحوصات 🔬، تشخيص 🧠، علاج 💊","saved":"تم حفظ الحالة 📁"}}
```

`iclinic/data/user/first_time.json`
```json
{"title":"مرحبا بك في iClinic 🤖","steps":["أرسل طلب استخدام البوت","انتظر قبول الأدمن ⏳"]}
```

`iclinic/data/user/home.json`
```json
{"title":"iClinic","menu":[{"id":"cases","label":"حالات مرضية 🩺"},{"id":"questions","label":"أسئلة مباشرة ❓"}],"notes":"هذه أداة تعليمية ولا تغني عن الاستشارة الطبية 🩺"}
```

---

انتهى. إذا واجهت خطأ، انسخ رسالة الخطأ هنا وسأصلحها لك فورًا.
