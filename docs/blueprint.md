# المخطط التنفيذي الشامل لشفرة إضافة Tymer (Implementation Blueprint)

دليل هندسي كامل ومباشر للمبرمج أو الوكيل اللاحق، يحتوي على المواصفات الدقيقة لكافة ملفات المشروع وفئاته ودواله.

---

## 1. مواصفات البيانات وهيكل التكوين (`confspec`)

```python
confspec = {
    # 0: صوت فقط (افتراضي)، 1: نطق فقط، 2: صوت ونطق معاً
    "notificationStyle": "integer(default=0)",
    # 0: مبتدئ (إرشادات كاملة)، 1: متقدم (أرقام وحالة مقتضبة)
    "verbosity": "integer(default=0)",
    # تفعيل نغمة خافتة عند ولوج الطبقة
    "entryBeep": "boolean(default=True)",
    # تفعيل نغمة تحذيرية خافتة قبل انتهاء الوقت بـ 10 ثوانٍ
    "preExpiryCue": "boolean(default=False)",
    # سياسة إعادة التشغيل: "resume" (استئناف)، "reset" (تصفير)، "pause" (تعليق)
    "restartPolicy": "string(default='resume')",
    # المدد الافتراضية للفتحات الخمس بالثواني (5، 10، 15، 25، 60 دقيقة)
    "defaultDurations": "int_list(default=list(300, 600, 900, 1500, 3600))",
    # عناوين مخصصة اختيارية للفتحات الخمس
    "slotLabels": "string_list(default=list('', '', '', '', ''))",
}
```

---

## 2. موديول إدارة المؤقتات (`addon/globalPlugins/tymer/timerHandler.py`)

### فئة الفتحة `TimerSlot`:
- **السمات (Attributes)**:
  - `index: int`: رقم الفتحة (من 1 إلى 5).
  - `label: str`: العنوان المخصص (إن وجد).
  - `duration: float`: المدة الكلية بالثواني.
  - `targetTime: Optional[float]`: الطابع الزمني المستهدف عند الانتهاء (`time.time() + remaining`).
  - `remainingOnPause: Optional[float]`: الوقت المتبقي المحفوظ عند التعليق.
  - `state: str`: حالة المؤقت:
    - `"stopped"`: متوقف / خامل.
    - `"running"`: قيد العد التنازلي.
    - `"paused"`: معلق مؤقتاً.
  - `cueEmitted: bool`: علم يُضبط على True عند انطلاق نغمة التحذير المسبق لئلا تتكرر.
- **الدوال (Methods)**:
  - `start()`: ينقل الحالة إلى `"running"` ويضبط `targetTime = time.time() + duration`.
  - `pause()`: ينقل الحالة إلى `"paused"` ويحفظ `remainingOnPause = remaining()`.
  - `resume()`: يستأنف العد ويضبط `targetTime = time.time() + remainingOnPause`.
  - `reset()`: يُلغي المؤقت ويعيده إلى `"stopped"` مع استعادة المدة الأصلية.
  - `setDuration(seconds: float, label: str = "")`: يضبط المدة والعنوان ويعيد المؤقت إلى `"stopped"`.
  - `remaining() -> float`: يُرجع الثواني المتبقية حتى الصفر بدقة.

### فئة محرك العد `CountdownEngine`:
- يُدير قائمة الفتحات الخمس: `self.slots: List[TimerSlot]`، إضافة لفتحة المؤقت السريع المستقلة في الذاكرة الحية `self.quickSlot: TimerSlot` (المفتاح Q).
- يمتلك مؤقت `self._ticker = wx.PyTimer(self._onTick)` يعمل كل ثانية (1000ms) بنظام النبض المشروط بالحاجة (ينبض إذا كانت أي من الفتحات الخمس أو المؤقت السريع في حالة `running`).
- يمتلك مؤقت إيقاف الصوت التلقائي `self._alarmAutoStopTimer = wx.PyTimer(self.silenceAlarm)`.
- يمتلك ساعة إيقاف خفيفة في الذاكرة: `self.stopwatch = Stopwatch()`.
- **دالة `_onTick()`**:
  - تفحص المؤقتات النشطة الخمسة إضافة لـ `quickSlot` (`state == "running"`).
  - إذا تبقّى 10 ثوانٍ وكان `preExpiryCue` مفعلاً و `not slot.cueEmitted`:
    - تُطلق نغمة التحذير المسبق وتضبط `slot.cueEmitted = True`.
  - إذا بلغ المؤقت الصفر (`remaining <= 0`):
    - تطلق التنبيه عبر `self.triggerAlarm(slot)`.
    - تُصفّر المؤقت تلقائياً عبر `slot.reset()` ليعود لحالة التوقف `stopped` فورياً.
- **دالة `triggerAlarm(slot: TimerSlot)`**:
  - تُنفذ مبدأ **مقاطعة الأسبق بالأحدث (Alarm Preemption)**:
    - توقف أي صوت شغال عبر `if nvwave.fileWavePlayer: nvwave.fileWavePlayer.stop()`.
  - تشغل الملف الصوتي `nvwave.playWaveFile(alarmWavPath)`.
  - تبدأ مؤقت الإيقاف التلقائي لمدة ثانية واحدة (`self._alarmAutoStopTimer.StartOnce(1000)`).
  - إذا كان نمط الإشعار يسمح بالنطق: تصوغ رسالة الانتهاء وتُرسلها عبر `ui.message(msg)`.
- **دالة `silenceAlarm()`**:
  - تُسكت مشغل الصوت فوراً عبر `if nvwave.fileWavePlayer: nvwave.fileWavePlayer.stop()`.
  - توقف مؤقت الإيقاف التلقائي إن كان يعمل.

---

## 3. حوار ضبط المدة (`addon/globalPlugins/tymer/durationDialog.py`)

- فئة مشتقة من `gui.settingsDialogs.SettingsDialog`.
- العنوان: `_("Set Timer {number} Duration").format(number=slotIndex)`.
- **عناصر الواجهة**:
  1. حقل نصي اختياري: `_("Timer &label (optional):")` -> `wx.TextCtrl`.
  2. حقل رقمي للساعات: `_("&Hours:")` -> `wx.SpinCtrl(min=0, max=99)`.
  3. حقل رقمي للدقائق: `_("&Minutes:")` -> `wx.SpinCtrl(min=0, max=59)`.
  4. حقل رقمي للثواني: `_("&Seconds:")` -> `wx.SpinCtrl(min=0, max=59)`.
  5. أزرار القياس: `wx.OK`, `wx.CANCEL`.
- **التركيز التلقائي (`postInit`)**:
  - نقل التركيز فوراً إلى حقل الدقائق: `self.minutesCtrl.SetFocus()`.
- **الحفظ (`onOk`)**:
  - احتساب إجمالي الثواني: `total = hours * 3600 + minutes * 60 + seconds`.
  - إذا كان `total <= 0`: إظهار رسالة تحذير ميسرة تمنع حفظ مدة صفرية.
  - تطبيق المدة على الفتحة وحفظ الإعدادات.

### فئة حوار المؤقت السريع `QuickDurationDialog`:
- فئة مخصصة مشتقة من `SettingsDialog` للضبط والبدء الفوري لمؤقت مخصص لمرة واحدة (`quickSlot`).
- العنوان: `_("Set Quick Timer Duration")`.
- لا تحتوي على حقل تسمية؛ مقتصرة على: ساعات، دقائق، ثوانٍ مع تركيز تلقائي على الدقائق.
- تذكر آخر مدة استخدمت خلال الجلسة.
- تعليق المؤقت الجاري تلقائياً عند الفتح، واستئنافه عند الإلغاء، واستبداله والبدء الفوري عند الموافقة.

---

## 4. لوحة الإعدادات (`addon/globalPlugins/tymer/settingsGUI.py`)

- فئة مشتقة من `gui.settingsDialogs.SettingsPanel`.
- العنوان: `title = _("Tymer")`.
- **الضوابط في `makeSettings`**:
  1. نمط الإشعار (`wx.Choice`): (صوت فقط، نطق فقط، صوت ونطق معاً).
  2. مستوى الإسهاب (`wx.Choice`): (مبتدئ، متقدم).
  3. خانة اختيار نغمة ولوج الطبقة (`wx.CheckBox`): تمكين/تعطيل.
  4. خانة اختيار التحذير المسبق (`wx.CheckBox`): تمكين/تعطيل التنبيه عند اقتراب الصفر.
  5. سياسة إعادة التشغيل (`wx.Choice`): (استئناف، تصفير، تعليق).
  6. زر "إعادة تعيين كافة المؤقتات للوضع الافتراضي".

---

## 5. صلب الإضافة والطبقة (`addon/globalPlugins/tymer/__init__.py`)

- الفئة `GlobalPlugin(globalPluginHandler.GlobalPlugin)`.
- `scriptCategory = _("Tymer")`.
- **تكوين الإيماءات للطبقة**:
  - `1` إلى `5` مجردة: استعلام أو بدء المؤقتات 1-5.
  - `shift+1` إلى `shift+5`: تعليق أو استئناف المؤقتات 1-5.
  - `control+1` إلى `control+5`: فتح حوار ضبط مدة المؤقتات 1-5.
  - `alt+1` إلى `alt+5`: تصفير المؤقتات 1-5 وإسكات الرنين.
  - `q`: استعلام عن المؤقت السريع أو فتح حوار ضبطه والبدء إن كان متوقفاً.
  - `shift+q`: تعليق المؤقت السريع أو استئنافه.
  - `control+q`: فتح حوار ضبط مدة المؤقت السريع في أي وقت.
  - `alt+q`: تصفير المؤقت السريع وإسكات الرنين.
  - `s`، `shift+s`، `control+s`، `alt+s`: ساعة الإيقاف.
  - `h`: `script_help`
  - `space`: `script_silenceAlarm`
  - `a`: `script_reportAll` (يشمل المؤقت السريع إذا كان نشطاً).
  - `escape`: `script_cancelLayer`
- **آلية الدخول**:
  - `tones.beep(100, 10)` إن كان `entryBeep` مفعلاً.
  - ربط المفاتيح بـ `bindGesture`.
  - `self.layerModeActive = True`.
- **آلية الخروج**:
  - تنفيذ الأمر ثم `self.finish()` لإعادة المفاتيح.
  - اعتراض أي خطأ وتوجيهه لـ `script_error`.

---

## 6. منظومة البناء والتحزيم المعتمدة (`scons` & `buildVars.py`)

تعتمد الإضافة قالب البناء المعياري لإضافات NVDA:
- **ملف المتغيرات الأساسية (`buildVars.py`)**: يُحدد الاسم `tymer`، الإصدار `2026.1`، المطور `Kamal Yaser`، وحدود التوافقية (`minimumNVDAVersion = 2024.1.0` و `lastTestedNVDAVersion = 2026.2.0`).
- **قالب البيان (`manifest.ini.tpl` و `manifest-translated.ini.tpl`)**: يُولَّد منهما تلقائياً ملف `addon/manifest.ini` عند تنفيذ أمر البناء.
- **استخلاص التعريب**: تشغيل أمر `scons pot` لتوليد ملف `tymer.pot` وترجمته في `addon/locale/ar/LC_MESSAGES/nvda.po`.
- **البناء النهائي**: تشغيل أمر `scons` لتجميع ملفات `.mo`، وتحويل التوثيق من Markdown إلى HTML، وحزم الإضافة في ملف `tymer-2026.1.nvda-addon`.
- **النشر على GitHub**: استخدام GitHub CLI لإنشاء المستودع وإطلاق الإصدار (`gh repo create`, `gh release create`).


---

## 7. ميثاق الجودة والحراسة البرمجية (Clean Code & Karpathy Guardrails)

يلتزم المنفّذ في الجلسة التالية بالقواعد الصارمة الآتية:
1. **دلالة الأسماء على المقصد (Names Reveal Intent)**: اجتناب الأسماء العامة والمبهمة (`data`, `temp`, `helper`, `manager` دون تخصيص)، واستعمال الأسماء الصريحة (`CountdownEngine`, `TimerSlot`, `DurationDialog`).
2. **صغر الدوال وفصل المسؤوليات (Functions ≤ 20 lines, SRP)**: كل دالة تؤدي عملاً واحداً وتفصل بين الأوامر (Commands) والاستعلامات (Queries).
3. **أقصى حد للوسائط (Arguments ≤ 4)**: لا تتجاوز أي دالة 4 معاملات، وتجنب الوسائط المنطقية الثنائية الغامضة (Boolean flags).
4. **التعليقات للتعليل لا للوصف (Comments Explain Why, Not What)**: تجنب التعليقات السطحية الشارحة لما يفعله الكود بديهة، والتركيز على تعليل القرارات غير المباشرة.
5. **الامتناع عن كتم الأخطاء العام (No Broad Exception Swallowing)**: اصطياد الاستثناءات المحددة بدقة (`VdtTypeError`, `MultiInstanceErrorWithDialog`)، وعدم استخدام `except:` أو `except Exception:` الصامتة مطلقاً.
6. **حراسة التخوم والاطمئنان للعقد (Guard Boundaries, Trust Contract)**: التحقق الصارم من صحة المدخلات الخارجية في نوافذ الحوار والتكوين، مع الامتناع عن الفحوصات الدفاعية الزائدة داخل الدوال المحمية بالعقد.
7. **معايير نجاح حقيقية ومتحقق منها (Verifiable Success Criteria)**: اختبارات `run_tests.py` لا تعتمد على نتائج وهمية أو كتم فشل، بل تختبر منطق العد والتحول الزمني فعلياً.
8. **البساطة الجراحية المباشرة (Surgical Simplicity & YAGNI)**: كتابة أقل شفرة ممكنة تؤدي المطلوب، دون أي استباق تجريدي أو مرونة غير مطلوبة.

