# iOS Scene Lifecycle Regression Test Matrix

Select only tests relevant to features found in the project.

| Area | Test | Expected result |
|---|---|---|
| Launch | Fresh install / cold launch | Correct initial screen, no UIScene assertion/crash |
| Launch | Warm launch | No duplicate window/root controller |
| Auth root | Logged-out launch | Existing login/onboarding/splash flow unchanged |
| Auth root | Logged-in launch | Existing authenticated root unchanged |
| Lifecycle | Background → foreground | UI/state behavior unchanged |
| Lifecycle | Active → inactive → active | No duplicated work or lost UI state |
| Scene | Window becomes active | Correct window receives UI updates |
| Appearance | Theme at launch | Same light/dark/custom theme as before |
| Storyboard | Initial view controller | No double initialization or flash of wrong screen |
| Programmatic root | Root setup | Root created once and retained |
| Push | Foreground notification | Same presentation behavior |
| Push | Notification tap from background | Correct destination screen |
| Push | Notification tap from terminated app | Correct startup + destination |
| Deep link | Custom URL while app open | Existing callback still works |
| Deep link | Custom URL cold launch | Existing callback still works |
| Universal links | Foreground/cold | Existing destination unchanged |
| Payments | Redirect callback | Success/failure callback still delivered |
| Social auth | Facebook/Google/TikTok callback | Login callback still delivered |
| Stripe | URL callback | Stripe redirect still handled |
| VoIP | Incoming call | Existing CallKit/VoIP path unchanged |
| Background | Background task | Registration/execution unchanged |
| Update flow | Forced-update alert | Presents on the active window |
| Navigation | Push-triggered navigation | Uses active scene/window |
| Older OS | Lowest supported iOS | App still launches and behaves as before |
| iPad | Multitasking/resizing if supported | No wrong-window UI operations |
