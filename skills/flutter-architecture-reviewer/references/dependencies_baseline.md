# Flutter Dependencies Baseline (Updated)

استخدم القائمة دي كـ baseline لما تعمل مراجعة معمارية/Code Review أو تقيّم التزام مشروع Flutter بالـ stack المتفق عليه.

ملاحظة: الهدف هنا “التوافق” مع الـ stack. في التقرير، لو لقيت بدائل/نسخ قديمة/استخدام مباشر من UI، اعتبره smell واطلع توصية واضحة.

```yaml
dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  build_runner: ^2.4.7
  flutter_bloc: ^8.1.3
  freezed: ^2.4.5
  freezed_annotation: ^2.4.1
  get_it: ^7.6.4
  json_serializable: ^6.7.1
  json_annotation: ^4.8.1
  dio: ^5.3.3
  retrofit: ^4.0.3
  retrofit_generator: ^8.0.4
  pretty_dio_logger: ^1.3.1
  intl: ^0.19.0
  easy_localization: ^3.0.3
  flutter_native_splash: ^2.3.5
  flutter_svg: ^2.0.9
  flutter_screenutil: ^5.9.0
  firebase_core: ^2.27.0
  cached_network_image: ^3.3.1
  shared_preferences: ^2.2.3
  flutter_secure_storage: ^9.2.2
  shimmer: ^3.0.0
```

## Rules مرتبطة بالـ baseline

- لازم أي `Dio()`/interceptors/config يبقى في `lib/core/networking/` (مش جوه UI).
- `retrofit` يفضل يبقى في data layer (api services) مع `retrofit_generator`.
- الـ DI بـ `get_it` يبقى في `lib/core/di/`.
- `easy_localization`/`intl` تخص `core/helpers` وتهيئة app-level (مش feature-by-feature عشوائي).
- `shared_preferences` و `flutter_secure_storage` يُستخدموا من data layer (local data sources) مش من screens.

