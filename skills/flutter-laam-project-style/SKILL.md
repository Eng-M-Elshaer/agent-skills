---
name: flutter-laam-project-style
description: >
  Best practices and coding style for Flutter apps following the Laam For Parents project architecture.
  Use this skill whenever working on any Flutter feature, screen, Cubit, repository, model, widget, or
  configuration in a project that follows Clean Architecture + BLoC/Cubit + Freezed + Dio + GetIt.
  Trigger this skill for: creating new features, writing Cubits, setting up flavours, error handling,
  responsive UI, API integration, or reviewing/refactoring Flutter code. Even if the user doesn't
  mention "Laam" explicitly — if the task involves Flutter + Clean Architecture, use this skill.
metadata:
  version: 2.0.0
  last_modified: 2026-04-27
---

# Flutter Laam Project Style — v2.0

Production-grade Flutter development guide following Clean Architecture, BLoC/Cubit, and the
patterns established in the Laam For Parents project.

## Contents
- [Architecture Overview](#architecture-overview)
- [State Management with Cubit](#state-management-with-cubit)
- [UI and Responsive Design](#ui-and-responsive-design)
- [Error Handling](#error-handling)
- [Networking and API Integration](#networking-and-api-integration)
- [Flavours and Environment Management](#flavours-and-environment-management)
- [Code Style and Best Practices](#code-style-and-best-practices)
- [Testing](#testing)
- [Workflow for Feature Development](#workflow-for-feature-development)

---

## Architecture Overview

```
lib/
├── core/
│   ├── di/           # GetIt dependency injection setup
│   ├── networking/   # DioFactory, interceptors, api_result.dart
│   ├── routing/      # AppRouter, route constants
│   ├── theming/      # AppColors, FontSizeManager, AppStyles
│   ├── helpers/      # Extensions, utils, constants
│   └── widgets/      # Shared reusable widgets
└── features/
    └── feature_name/
        ├── data/
        │   ├── models/       # Freezed models + JSON serialization
        │   └── repos/        # Repository implementation
        ├── logic/
        │   ├── cubit.dart
        │   └── state.dart    # Freezed state
        └── ui/
            ├── screens/
            └── widgets/
```

**Rules:**
- Business logic lives **only** in Cubits — never in widgets.
- Repositories return `Either<Failure, T>` — never throw exceptions up to the UI.
- Use `GetIt` for all dependency injection; never instantiate services directly.
- Keep `core/` free of feature-specific code.

---

## State Management with Cubit

### State Definition (Freezed)

```dart
@freezed
class ExampleState with _$ExampleState {
  const factory ExampleState({
    @Default(false) bool isLoading,
    @Default(false) bool isLoadingMore,
    @Default([]) List<ExampleModel> items,
    @Default(false) bool isLastPage,
    String? errorMessage,
  }) = _ExampleState;

  factory ExampleState.initial() => const ExampleState();
}
```

### Cubit with Concurrency Guard + Pagination

```dart
class ExampleCubit extends Cubit<ExampleState> {
  final ExampleRepo _repo;
  int _currentPage = 1;

  ExampleCubit(this._repo) : super(ExampleState.initial());

  bool get canLoadMore => !state.isLastPage && !state.isLoadingMore;

  Future<void> loadData({bool refresh = false}) async {
    // ✅ Concurrency guard
    if (state.isLoading || (!refresh && state.isLoadingMore)) return;

    if (refresh) {
      _currentPage = 1;
      emit(state.copyWith(
        isLoading: true,
        items: [],
        isLastPage: false,
        errorMessage: null,
      ));
    } else {
      if (!canLoadMore) return;
      emit(state.copyWith(isLoadingMore: true));
    }

    final response = await _repo.getData(page: _currentPage);

    response.when(
      success: (newItems) {
        _currentPage++;
        emit(state.copyWith(
          isLoading: false,
          isLoadingMore: false,
          items: refresh ? newItems : [...state.items, ...newItems],
          isLastPage: newItems.isEmpty,
        ));
      },
      failure: (error) {
        emit(state.copyWith(
          isLoading: false,
          isLoadingMore: false,
          errorMessage: error.message,
        ));
      },
    );
  }
}
```

**Key rules:**
- Always guard against concurrent calls at the top of async methods.
- Never use `state.isLoading = true` — always use `copyWith`.
- Clear `errorMessage` on successful refresh.
- Separate `isLoading` (initial load) from `isLoadingMore` (pagination).

---

## UI and Responsive Design

```dart
// main.dart
ScreenUtilInit(
  designSize: const Size(375, 812), // Your design base size
  minTextAdapt: true,
  builder: (_, __) => const MyApp(),
);

// Usage
SizedBox(height: 16.h)
Text('Hello', style: TextStyle(fontSize: 14.sp))
Container(width: 200.w)
```

**Widget structure:**
```dart
class ExampleScreen extends StatelessWidget {
  const ExampleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => getIt<ExampleCubit>()..loadData(),
      child: const _ExampleView(),
    );
  }
}

class _ExampleView extends StatelessWidget {
  const _ExampleView();

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ExampleCubit, ExampleState>(
      builder: (context, state) {
        if (state.isLoading) return const LoadingWidget();
        if (state.errorMessage != null) {
          return CustomErrorWidget(
            error: state.errorMessage!,
            onRefreshTapped: () => context.read<ExampleCubit>().loadData(refresh: true),
          );
        }
        return _buildContent(state);
      },
    );
  }
}
```

---

## Error Handling

### CustomErrorWidget — Fixed Version

```dart
class CustomErrorWidget extends StatefulWidget {
  const CustomErrorWidget({
    super.key,
    required this.error,
    required this.onRefreshTapped,
  });

  final String error;
  final Future<void> Function() onRefreshTapped;

  @override
  State<CustomErrorWidget> createState() => _CustomErrorWidgetState();
}

class _CustomErrorWidgetState extends State<CustomErrorWidget> {
  bool _isRefreshing = false;

  Future<void> _handleRefresh() async {
    if (_isRefreshing) return;
    setState(() => _isRefreshing = true);
    try {
      await widget.onRefreshTapped();
    } finally {
      // ✅ Always check mounted before setState
      if (mounted) setState(() => _isRefreshing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(24.w),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // ✅ Actually show the error message
            Icon(Icons.error_outline, size: 48.r, color: AppColors.error),
            SizedBox(height: 12.h),
            Text(
              widget.error,
              textAlign: TextAlign.center,
              style: AppStyles.bodyMedium.copyWith(color: AppColors.error),
            ),
            SizedBox(height: 16.h),
            ElevatedButton(
              onPressed: _isRefreshing ? null : _handleRefresh,
              child: _isRefreshing
                  ? SizedBox(
                      width: 20.r,
                      height: 20.r,
                      child: const CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(AppLocalizations.of(context)!.retry),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Failure Model

```dart
@freezed
class Failure with _$Failure {
  const factory Failure.network({required String message}) = NetworkFailure;
  const factory Failure.server({required int statusCode, required String message}) = ServerFailure;
  const factory Failure.unknown({required String message}) = UnknownFailure;
}
```

---

## Networking and API Integration

### DioFactory

```dart
class DioFactory {
  DioFactory._();

  static Dio createDio() {
    return Dio(
      BaseOptions(
        baseUrl: FlavorConfig.instance.baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: {'Content-Type': 'application/json'},
      ),
    )
      ..interceptors.add(AuthInterceptor())
      ..interceptors.add(PrettyDioLogger(
        requestHeader: true,
        requestBody: true,
        responseBody: true,
      ));
  }
}
```

### Repository Pattern

```dart
abstract class ExampleRepo {
  Future<Either<Failure, List<ExampleModel>>> getData({required int page});
}

class ExampleRepoImpl implements ExampleRepo {
  final ExampleApiService _apiService;

  ExampleRepoImpl(this._apiService);

  @override
  Future<Either<Failure, List<ExampleModel>>> getData({required int page}) async {
    try {
      final response = await _apiService.getData(page: page);
      return Right(response.data ?? []);
    } on DioException catch (e) {
      return Left(Failure.network(message: e.message ?? 'Network error'));
    } catch (e) {
      return Left(Failure.unknown(message: e.toString()));
    }
  }
}
```

---

## Flavours and Environment Management

### ✅ Immutable FlavorConfig (Fixed)

```dart
enum Flavor { development, testing, production }

class FlavorConfig {
  final Flavor flavor;
  final String baseUrl;
  final bool showLogs;

  const FlavorConfig._({
    required this.flavor,
    required this.baseUrl,
    required this.showLogs,
  });

  static late final FlavorConfig _instance;
  static FlavorConfig get instance => _instance;

  static void init() {
    const flavorStr = String.fromEnvironment('FLAVOR', defaultValue: 'development');

    switch (flavorStr) {
      case 'production':
        _instance = const FlavorConfig._(
          flavor: Flavor.production,
          baseUrl: 'https://api.laam.sa/api/mobile/parent-app/v1.0/',
          showLogs: false,
        );
      case 'testing':
        _instance = const FlavorConfig._(
          flavor: Flavor.testing,
          baseUrl: 'https://api-prelive.laam.sa/api/mobile/parent-app/v1.0/',
          showLogs: true,
        );
      default:
        _instance = const FlavorConfig._(
          flavor: Flavor.development,
          baseUrl: 'http://192.168.1.5:3000',
          showLogs: true,
        );
    }
  }

  bool get isProduction => flavor == Flavor.production;
}
```

**Usage in `main.dart`:**
```dart
void main() {
  FlavorConfig.init(); // ✅ Called once at startup
  setupGetIt();
  runApp(const MyApp());
}
```

---

## Code Style and Best Practices

| Rule | ✅ Do | ❌ Don't |
|------|-------|---------|
| Naming | `UserProfileCubit`, `user_profile_state.dart` | `userCubit`, `State1.dart` |
| Imports | Dart → packages → local, alphabetical | Random order |
| Widget size | Extract widgets > 50 lines | Mega-build methods |
| `BuildContext` | Check `mounted` after `await` | Use context after async gap |
| Magic numbers | `const double kCardRadius = 12` | `BorderRadius.circular(12)` everywhere |
| Null safety | Use `?`, `??`, `!` only when certain | Force-unwrap blindly |

---

## Testing

### Cubit Unit Test

```dart
void main() {
  late ExampleCubit cubit;
  late MockExampleRepo mockRepo;

  setUp(() {
    mockRepo = MockExampleRepo();
    cubit = ExampleCubit(mockRepo);
  });

  tearDown(() => cubit.close());

  group('ExampleCubit.loadData', () {
    test('emits loading then success state', () async {
      when(() => mockRepo.getData(page: 1))
          .thenAnswer((_) async => Right(mockItems));

      await cubit.loadData();

      expect(cubit.state.isLoading, false);
      expect(cubit.state.items, mockItems);
      expect(cubit.state.errorMessage, isNull);
    });

    test('emits error on failure', () async {
      when(() => mockRepo.getData(page: 1))
          .thenAnswer((_) async => Left(Failure.network(message: 'No internet')));

      await cubit.loadData();

      expect(cubit.state.errorMessage, 'No internet');
      expect(cubit.state.items, isEmpty);
    });

    test('does not reload if already loading', () async {
      // Simulate concurrent call
      cubit.emit(cubit.state.copyWith(isLoading: true));
      await cubit.loadData();
      verifyNever(() => mockRepo.getData(page: any(named: 'page')));
    });
  });
}
```

**Minimum test coverage targets:**
- All Cubit methods: happy path + error path + concurrency guard
- Repositories: mock API service, verify Either mapping
- Widgets: smoke test that screen renders without errors

---

## Workflow for Feature Development

```
1. PLAN
   └── Create folder: lib/features/feature_name/{data,logic,ui}/

2. DATA LAYER
   ├── Create Freezed model + JSON serialization
   ├── Define abstract repo interface
   └── Implement repo with Either<Failure, T>

3. LOGIC LAYER
   ├── Define Freezed state with all UI-relevant fields
   └── Implement Cubit with concurrency guards

4. UI LAYER
   ├── Screen = BlocProvider + view widget
   ├── View = BlocBuilder with loading/error/success branches
   └── Use CustomErrorWidget for error states

5. DI REGISTRATION
   └── Register repo + cubit in GetIt setup file

6. ROUTING
   └── Add route in AppRouter

7. TESTING
   └── Write Cubit unit tests before merging

8. COMMIT
   └── Format: "feat(feature-name): Implement X" or "fix(cubit): Guard concurrent loadData calls"
```
