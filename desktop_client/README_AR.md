# TRELLIS.2 Desktop for Windows

واجهة سطح مكتب أولية لويندوز لرفع صورة إلى خدمة TRELLIS.2 المستضافة وتنزيل النموذج الناتج بصيغة GLB. المعالجة تتم على خادم بعيد، لذلك لا تحتاج بطاقة NVIDIA محلية.

## التشغيل
1. ثبّت Python 3.11 أو أحدث من الموقع الرسمي.
2. افتح مجلد `desktop_client` وشغّل `install_dependencies.bat`.
3. شغّل `run_app.bat`، واختر صورة، ثم اضغط Generate.
4. بعد اكتمال المعالجة اضغط Export GLB.

## إنشاء EXE
شغّل `build_exe.bat` على Windows. أو افتح تبويب Actions وشغّل `Build Windows Desktop EXE`، ثم نزّل artifact المسمى `TRELLIS2-Desktop-Windows` عند نجاح البناء.

مهم: هذه واجهة أولية تعتمد على مساحة Hugging Face العامة، وقد تتوقف أو تتغير واجهتها أو تفرض حدودًا. تُرفع الصور إلى خادم بعيد؛ لا ترفع صورًا خاصة أو حساسة. لم يتم اختبار البناء والتوليد على جهاز Windows فعلي بعد.

الخدمة: https://huggingface.co/spaces/microsoft/TRELLIS.2
