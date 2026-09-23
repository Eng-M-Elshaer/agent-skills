# Authoritative references

Use these sources when validating or updating this skill.

## Apple

- Transitioning to the UIKit scene-based life cycle  
  https://developer.apple.com/documentation/uikit/transitioning-to-the-uikit-scene-based-life-cycle

- Specifying the scenes your app supports  
  https://developer.apple.com/documentation/uikit/specifying-the-scenes-your-app-supports

- UIApplicationDelegate.application(_:configurationForConnecting:options:)  
  https://developer.apple.com/documentation/uikit/uiapplicationdelegate/application(_:configurationforconnecting:options:)

- Managing your app's life cycle  
  https://developer.apple.com/documentation/uikit/managing-your-app-s-life-cycle

- UIWindowSceneDelegate  
  https://developer.apple.com/documentation/uikit/uiwindowscenedelegate

## Important interpretation

- iOS 27 SDK: UIKit apps must adopt scene-based lifecycle.
- Static scene configuration in `Info.plist` is valid.
- `configurationForConnecting` is required when static scene configuration is absent, or when the app wants to alter/select configuration dynamically.
- A storyboard scene configuration lets UIKit create the window and initial root automatically.
- A programmatic scene should create `UIWindow(windowScene:)` in `scene(_:willConnectTo:options:)`.
- Once scene lifecycle is adopted, UI lifecycle behavior belongs in scene callbacks rather than the corresponding legacy AppDelegate callbacks.

Re-check Apple documentation when a future SDK changes these rules.
