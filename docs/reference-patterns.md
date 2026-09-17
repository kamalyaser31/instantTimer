# الدروس والأنماط المعمارية والبرمجية المقتبسة من إضافة Clock المرجعية

توثيق تحليلي شامل ومفصّل للأنماط البرمجية، والحيل الدفاعية (Defensive Coding)، وتقنيات معالجة الصوت والواجهات المقتبسة من شفرة إضافة `addons/clock`، لتكون دليلاً معيارياً لتنفيذ إضافة `tymer` في NVDA.

---

## 1. احتواء طبقة الأوامر والتعافي الذاتي من أخطاء المفاتيح (Layer Containment & Failsafe)
- **المصدر في المرجع**: `__init__.py` (الأسطر 301-331).
- **النمط**:
  - عند دخول الطبقة بـ `NVDA+Y`، يُضبط العلم `layerModeActive = True`.
  - لا يُكتفى بربط الإيماءات عبر `bindGesture`، بل تُعترض كافة الإيماءات من خلال تجاوز دالة `getScript(self, gesture)`.
  - إذا وردت إيماءة غير مسجلة في الطبقة، لا تُترك لتعطيل النظام أو إحداث احتباس للمفاتيح (Keyboard Trap)، بل تُوجّه فوراً إلى `script_error` الذي يُصدر نغمة خطأ منخفضة التردد (`tones.beep(120, 100)`)، ثم يستدعي `self.finish()`.
  - دالة `finish(self)` تقوم بثلاثة أفعال حاسمة:
    1. تصفير حالة الطبقة: `self.layerModeActive = False`.
    2. تطهير كافة الإيماءات الديناميكية: `self.clearGestureBindings()`.
    3. إعادة ربط الإيماءات العامة الأصلية: `self.bindGestures(self.__gestures)`.
- **التطبيق في Tymer**:
  - حماية تامة للوحة مفاتيح المستخدم من أي احتباس لو ضغط مفتاحاً عارضاً أثناء نشاط الطبقة.

---

## 2. الإلغاء الصامت للطبقة بمفتاح الهروب (`Escape` Dismissal)
- **المصدر في المرجع**: الأسطر 324-331.
- **النمط**:
  - تخصيص مفتاح `escape` صراحة ضمن إيماءات الطبقة ليرتبط بدالة `script_cancelLayer`؛ فتستدعي `self.finish()` دون إصدار نغمة الخطأ (Beep)، ليكون خروجاً هادئاً وواعياً بطلب المستخدم.
- **التطبيق في Tymer**:
  - عند الضغط على `Escape` داخل طبقة `NVDA+Y`، تخرج الطبقة بصمت وتعود لوحة المفاتيح لوضعها العادي.

---

## 3. حراسة النوافذ ومنع تكرار فتح الحوار (`MultiInstanceErrorWithDialog`)
- **المصدر في المرجع**: `__init__.py` (السطر 526) و `clockSettingsGUI.py`.
- **النمط**:
  - عند فتح أي نافذة حوار مشتقة من `gui.settingsDialogs.SettingsDialog`:
    ```python
    try:
        gui.mainFrame.prePopup()
        d = DurationDialog(gui.mainFrame, slotIndex)
        d.Show()
        gui.mainFrame.postPopup()
    except gui.settingsDialogs.SettingsDialog.MultiInstanceErrorWithDialog:
        pass  # أو إشعار المستخدم بأن النافذة مفتوحة سلفاً
    ```
- **التطبيق في Tymer**:
  - منع تكرار فتح نافذة ضبط المدة (`Control + N`) إذا ضغط المستخدم الاختصار عدة مرات سريعة.

---

## 4. التحقق من سلامة ملف التكوين والتعافي الذاتي (`VdtTypeError` Handling)
- **المصدر في المرجع**: `__init__.py` (الأسطر 199-220).
- **النمط**:
  - تعريف مواصفات التكوين عبر `configobj` بواسطة `confspec`:
    ```python
    confspec = {
        "verbosity": "integer(default=0)",
        "notificationStyle": "integer(default=0)",
        "entryBeep": "boolean(default=True)",
        "preExpiryCue": "boolean(default=False)",
        "restartPolicy": "string(default='resume')",
        "defaultDurations": "int_list(default=list(300, 600, 900, 1500, 3600))",
    }
    config.conf.spec["tymer"] = confspec
    ```
  - فحص القيم عند بدء التشغيل واصطياد `VdtTypeError`؛ فإن تلوثت قيمة أُعيدت لقيمتها الافتراضية وحُفظ التكوين دون أي انهيار لإقلاع NVDA.
- **التطبيق في Tymer**:
  - صيانة ملف تكوين `nvda.ini` من التلف عند التعديل اليدوي أو الترقية.

---

## 5. التحكم المباشر بمشغل الموجات الصامتة (`nvwave.fileWavePlayer`)
- **المصدر في المرجع**: `__init__.py` (الأسطر 514-516) و `clockSettingsGUI.py`.
- **النمط**:
  - يعتمد NVDA داخلياً على كائن مفرد في موديول `nvwave` لتشغيل الملفات الصوتية:
    ```python
    import nvwave
    # لتشغيل صوت:
    nvwave.playWaveFile(soundPath)
    # لإيقاف الصوت الجاري فوراً:
    if nvwave.fileWavePlayer is not None:
        nvwave.fileWavePlayer.stop()
    ```
- **التطبيق في Tymer**:
  - تنفيذ مقاطعة المنبه الأسبق بالأحدث فوراً (Alarm Preemption).
  - إسكات المنبه الرنان بضغطة `Space` داخل الطبقة بلا أي تأخير أو خيوط معالجة ثقيلة.

---

## 6. حراسة أسطح المكتب المحمية وحسابات النظام (Secure Desktop Guard)
- **المصدر في المرجع**: `__init__.py` (الأسطر 184-185).
- **النمط**:
  ```python
  import globalVars, config
  if globalVars.appArgs.secure or config.isAppX:
      return
  ```
- **التطبيق في Tymer**:
  - الامتناع عن تسجيل لوحة الإعدادات أو فتح النوافذ فوق شاشات تأمين ويندوز (Logon screen / UAC) التزاماً بالمعايير الأمنية الرسمية لـ NVDA.

---

## 7. فك تسجيل لوحة الإعدادات بنظافة عند الإنهاء (`terminate`)
- **المصدر في المرجع**: `__init__.py` (الأسطر 247-255).
- **النمط**:
  - عند إلغاء تثبيت الإضافة أو تعطيلها أو إعادة تحميل الإضافات (`NVDA+Control+F3`):
    ```python
    def terminate(self):
        super().terminate()
        try:
            gui.NVDASettingsDialog.categoryClasses.remove(TymerSettingsPanel)
        except (ValueError, KeyError, AttributeError):
            pass
        self.timerManager.terminate()
    ```
- **التطبيق في Tymer**:
  - تنزيه ذاكرة NVDA عن اللوحات الشبحية (Phantom Panels) وتفادي الاستثناءات البرمجية عند إعادة التحميل.

---

## 8. استعراض مسرد الأوامر في نمط التصفح التفاعلي (`ui.browseableMessage`)
- **المصدر في المرجع**: `__init__.py` (الأسطر 467-479).
- **النمط**:
  - صياغة مسرد الأوامر بلغة HTML واضحة وعرضه في مخزن افتراضي (Virtual Buffer):
    ```python
    browseableHtml = "<h1>" + _("Tymer Layer Commands") + "</h1><ul>" + ... + "</ul>"
    ui.browseableMessage(browseableHtml, _("Tymer Help"), isHtml=True)
    ```
- **التطبيق في Tymer**:
  - تمكين الكفيف من مراجعة كافة مفاتيح المؤقتات برايل وبأسهم القراءة عبر مفتاح `H`.

---

## 9. الاستدلال الديناميكي على المسارات النسبية (`addonHandler.getCodeAddon().path`)
- **المصدر في المرجع**: `paths.py` (السطر 15).
- **النمط**:
  ```python
  import os, addonHandler
  PLUGIN_DIR = os.path.join(addonHandler.getCodeAddon().path, "globalPlugins", "tymer")
  SOUNDS_DIR = os.path.join(PLUGIN_DIR, "waves")
  ALARM_SOUND_PATH = os.path.join(SOUNDS_DIR, "alarm.wav")
  ```
- **التطبيق في Tymer**:
  - تشغيل الإضافة بكفاءة تامة سواء في النسخ المثبتة أو المحمولة (Portable).

---

## 10. صياغة التوقيت الصديقة لقارئات الشاشة (Humanized Time Formatting)
- **المصدر في المرجع**: `__init__.py` دالة `secondsToString` (الأسطر 64-83).
- **النمط**:
  - تحويل الثواني إلى ساعات ودقائق وثوانٍ مع مراعاة صيغ الجمع وحذف القيم الصفرية:
    ```python
    def formatTime(seconds: float) -> str:
        seconds = int(round(seconds))
        if seconds <= 0:
            return _("0 seconds")
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        parts = []
        if hrs > 0:
            parts.append(_("{count} hours").format(count=hrs))
        if mins > 0:
            parts.append(_("{count} minutes").format(count=mins))
        if secs > 0:
            parts.append(_("{count} seconds").format(count=secs))
        return ", ".join(parts)
    ```
- **التطبيق في Tymer**:
  - نطق أوقات المؤقتات المتبقية والمنقضية بفصاحة وسلاسة.

---

## 11. التنسيق مع دورة أحداث الواجهة عبر `wx.PyTimer`
- **المصدر في المرجع**: `clockHandler.py` (الأسطر 66-74).
- **النمط**:
  - استخدام `wx.PyTimer` لجدولة فحص المؤقتات كل ثانية (1000ms):
    ```python
    self._timer = wx.PyTimer(self._onTick)
    self._timer.Start(1000)
    ```
  - ميزة هذا الأسلوب: يعمل مباشرة على خيط واجهة المستخدم الرئيسي (Main GUI Thread)، مما يجعل استدعاءات `ui.message()` و `tones.beep()` و `nvwave.playWaveFile()` آمنة تماماً دون حاجة إلى وساطة `wx.CallAfter()`.
- **التطبيق في Tymer**:
  - محرك الفحص الزمني للمؤقتات الخمسة في `timerHandler.py`.

---

## 12. تسجيل فئة الأوامر وتصنيف الإيماءات (`scriptCategory`)
- **المصدر في المرجع**: `__init__.py` (السطر 178).
- **النمط**:
  ```python
  class GlobalPlugin(globalPluginHandler.GlobalPlugin):
      scriptCategory = _("Tymer")
      
      @scriptHandler.script(
          category=scriptCategory,
          description=_("Activates Tymer command layer. Press H inside the layer for help."),
          gesture="kb:NVDA+y",
      )
      def script_tymerLayerCommands(self, gesture):
          ...
  ```
- **التطبيق في Tymer**:
  - ظهور الاختصار `NVDA+Y` تلقائياً في نافذة "إيماءات الإدخال" في NVDA ضمن فئة مخصصة باسم "Tymer"، ليتسنى للمستخدم إعادة تعيينه لأي اختصار يريده مستقبلاً.
