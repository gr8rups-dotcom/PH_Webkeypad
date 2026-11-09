# Phone Keyboard: use your iPhone (or any phone) as a laptop keyboard

Laptop keyboard broken? Run one small Python script on the laptop, open the link it prints in your phone's browser, and type on the phone. Your keystrokes appear on the laptop.

It works over **Wi-Fi** (or your phone's Personal Hotspot), **not Bluetooth**. This is deliberate: iPhones don't allow apps to act as a Bluetooth keyboard.

## Quick start

1. Install Python 3 on the laptop.
2. Install the one dependency:
   ```
   pip install pynput
   ```
3. Run the script:
   ```
   python iphone_keyboard.py
   ```
4. On your phone (same Wi-Fi as the laptop, or the laptop connected to the phone's hotspot), open the link the script prints, for example `http://192.168.1.25:8765/?t=483920`.
5. Click into any text field on the laptop and type on the phone.

Keep the terminal window open while you use it. Press Ctrl+C to stop.

## Features

- Live typing, including backspace
- One-shot Ctrl / Alt / Shift / Win toggles
- Esc, Tab, Del, Enter, arrows, Home/End, F1-F12
- Shortcuts: Copy, Paste, Cut, Undo, Select All, Alt+Tab, Win, Win+D, Ctrl+Alt+Del
- Works with any phone browser (iPhone, Android)

## Security: please read

This program lets anyone who opens the link type on your computer.

- A random 6-digit PIN is generated on every run and is required in the link.
- Traffic is plain HTTP and is not encrypted. **Use it only on a Wi-Fi network or hotspot you trust. Do not use it on public Wi-Fi.**
- Stop the script (Ctrl+C) when you are done.
- Do not change the PIN to something easy to guess.

## Limitations

- The script must be running on the laptop, so it does not work at a login screen or before Windows has started.
- US keyboard layout assumed for typed characters.
- When the phone's text box is empty, use the on-screen Bksp button.
- macOS: allow Python under System Settings > Privacy & Security > Accessibility.
- Windows: allow the firewall prompt for private networks.
- Linux: works on X11; Wayland may block simulated keys.

## License

MIT. Use it, change it, share it.

Built by Anamitra Halder.
