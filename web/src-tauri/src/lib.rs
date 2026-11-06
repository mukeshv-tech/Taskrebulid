// Standard Tauri v2 entry point with system tray & window management
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Emitter, Manager, WebviewUrl, WebviewWindowBuilder,
};

#[tauri::command]
async fn open_oauth_window(app_handle: tauri::AppHandle, auth_url: String) -> Result<(), String> {
    // If an existing auth window is already open, close it first
    if let Some(existing) = app_handle.get_webview_window("oauth_window") {
        let _ = existing.close();
    }

    let parsed_url = auth_url
        .parse::<url::Url>()
        .map_err(|e| format!("Invalid URL: {}", e))?;

    let handle_clone = app_handle.clone();
    let win = WebviewWindowBuilder::new(
        &app_handle,
        "oauth_window",
        WebviewUrl::External(parsed_url),
    )
    .title("Sign in to TaskRebuild")
    .inner_size(520.0, 680.0)
    .resizable(false)
    .center()
    .always_on_top(true)
    .on_navigation(move |url| {
        let url_str = url.as_str();
        // Check if redirect contains Supabase authentication tokens
        if url_str.contains("access_token=") && url_str.contains("refresh_token=") {
            let _ = handle_clone.emit("oauth-callback", url_str.to_string());
            if let Some(w) = handle_clone.get_webview_window("oauth_window") {
                let _ = w.close();
            }
            return false;
        }
        true
    })
    .build()
    .map_err(|e| format!("Failed to create OAuth window: {}", e))?;

    let _ = win.set_focus();
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            // Create Tray Menu items
            let toggle_item = MenuItem::with_id(app, "toggle", "Show / Hide TaskRebuild", true, None::<&str>)?;
            let quit_item = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&toggle_item, &quit_item])?;

            // Build Tray Icon
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "toggle" => {
                        if let Some(window) = app.get_webview_window("main") {
                            if window.is_visible().unwrap_or(false) {
                                let _ = window.hide();
                            } else {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            if window.is_visible().unwrap_or(false) {
                                let _ = window.hide();
                            } else {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                    }
                })
                .build(app)?;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![open_oauth_window])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
