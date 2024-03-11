import keyboard
import pyautogui

class LockScreen:
    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.is_locked = False

    def lock_window(self):
        if not self.is_locked:
            self.master.iconify()
            self.is_locked = True
            print("Window is locked.")
            self.disable_alt_tab()
            keyboard.hook(self.on_key_event)  # Start listening to keyboard events

    def unlock_window(self):
        if self.is_locked:
            self.master.deiconify()
            self.is_locked = False
            print("Window is unlocked.")
            self.enable_alt_tab()
            keyboard.unhook_all()  # Stop listening to keyboard events

    def on_close(self):
        if self.is_locked:
            self.lock_window()
        else:
            self.master.destroy()

    def on_key_event(self, e):
        if e.event_type == keyboard.KEY_DOWN and e.name in ["alt", "tab"]:
            print("Alt + Tab is pressed. Locking...")
            self.lock_window()

    def disable_alt_tab(self):
        pyautogui.hotkey("alt", "tab", interval=0.0)

    def enable_alt_tab(self):
        # You may need to add a delay here to ensure the keys are released before enabling Alt + Tab again
        pyautogui.hotkey("alt", "tab", interval=0.1)

