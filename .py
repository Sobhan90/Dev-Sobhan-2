import tkinter as tk
from tkinter import messagebox
import string
import random
import time
import threading
import sys

# تنظیمات
PASSWORD_LENGTH = 2  # طول رمز اصلی (۵۰ خیلی سخته حدس بزنی!)
MAX_WRONG = 3
LOCK_MINUTES = 60  # ۱ ساعت → برای تست سریع 1 یا 2 بذار
MASTER_PASSWORD = "sos1234"  # رمز نجات اضطراری - حتما عوض کن!

chars = string.ascii_letters + string.digits + string.punctuation
secret = "".join(random.choices(chars, k=PASSWORD_LENGTH))

# print("رمز (تست):", secret)     # ← موقع تست باز کن - بعد کامنت کن

lock_end = 0
wrong_count = 0


def check_guess(event=None):
    global wrong_count, lock_end
    guess = entry.get().strip()
    entry.delete(0, tk.END)
    now = time.time()

    if now < lock_end:
        rem_sec = int(lock_end - now)
        mm, ss = divmod(rem_sec, 60)
        status.config(text=f"قفل تا {mm:02d}:{ss:02d} دیگه", fg="red")
        return "break"

    if guess == secret:
        messagebox.showinfo("تبریک!", "رمز درست بود!\nدسترسی آزاد شد → ۹۹")
        root.destroy()
        sys.exit(0)

    if guess == MASTER_PASSWORD:
        if lock_end - now > 1800:  # بیشتر از ۳۰ دقیقه مونده
            messagebox.showinfo("نجات!", "رمز اضطراری قبول شد!")
            root.destroy()
            sys.exit(0)
        else:
            status.config(
                text="رمز اضطراری فقط قبل ۳۰ دقیقه آخر کار می‌کنه", fg="orange"
            )
            return "break"

    wrong_count += 1

    if wrong_count >= MAX_WRONG:
        lock_end = now + (LOCK_MINUTES * 60)
        status.config(text=f"قفل {LOCK_MINUTES} دقیقه‌ای شروع شد!", fg="red")
        entry.config(state="disabled")
        btn.config(state="disabled")
        threading.Thread(target=timer_thread, daemon=True).start()
    else:
        status.config(
            text=f"اشتباه — {MAX_WRONG - wrong_count} شانس مونده", fg="#e67e22"
        )


def timer_thread():
    while time.time() < lock_end:
        rem = int(lock_end - time.time())
        m, s = divmod(rem, 60)
        try:
            status.config(text=f"قفل → {m:02d}:{s:02d} باقی مونده", fg="red")
        except:
            pass
        time.sleep(0.98)

    try:
        status.config(text="زمان قفل تموم شد — دوباره امتحان کن", fg="green")
        entry.config(state="normal")
        btn.config(state="normal")
        global wrong_count
        wrong_count = 0
    except:
        pass


# ────────────────────────────────
# اضافه شده: کپی رمز با کلیک روی نقطه مخفی
# ────────────────────────────────
def copy_secret_to_clipboard(event=None):
    root.clipboard_clear()
    root.clipboard_append(secret)
    root.update()  # اطمینان از کپی شدن
    old_text = status.cget("text")
    old_fg = status.cget("fg")
    status.config(text="رمز کپی شد (در کلیپ‌بورد)", fg="#00ff88")
    root.after(3500, lambda: status.config(text=old_text, fg=old_fg))


# پنجره اصلی
root = tk.Tk()
root.title("سیستم قفل شده")
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.configure(bg="#0d1117")

# سعی در بلاک کردن خروج
root.overrideredirect(True)  # بدون حاشیه و عنوان
root.bind("<Alt-F4>", lambda e: "break")
root.bind("<Escape>", lambda e: "break")
root.bind("<Control-Alt-Delete>", lambda e: "break")  # کار نمی‌کنه واقعاً
root.bind("<Control-q>", lambda e: "break")

frame = tk.Frame(root, bg="#161b22", bd=0)
frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

tk.Label(
    frame,
    text=f"سیستم برای امنیت قفل شده است{secret}",
    font=("Tahoma", 22, "bold"),
    bg="#161b22",
    fg="#ff5555",
).pack(pady=40)

tk.Label(
    frame,
    text=f"رمز {PASSWORD_LENGTH} کاراکتری را وارد کنید",
    font=("Tahoma", 14),
    bg="#161b22",
    fg="white",
).pack(pady=10)

entry = tk.Entry(frame, width=45, show="*", font=("Consolas", 16), justify="center")
entry.pack(pady=20)
entry.focus()

btn = tk.Button(
    frame,
    text="تأیید",
    font=("Tahoma", 14),
    bg="#21262d",
    fg="white",
    width=20,
    command=check_guess,
)
btn.pack(pady=15)

status = tk.Label(
    frame,
    text="۳ شانس دارید – اشتباه نکنید!",
    font=("Tahoma", 12),
    bg="#161b22",
    fg="#c9d1d9",
)
status.pack(pady=20)

tk.Label(
    frame,
    text=f"رمز اضطراری فقط قبل از ۳۰ دقیقه آخر قفل کار می‌کند",
    font=("Tahoma", 9),
    bg="#161b22",
    fg="#8b949e",
).pack(side="bottom", pady=15)

entry.bind("<Return>", check_guess)

# نقطه تقریباً نامرئی در گوشه پایین راست برای کپی رمز
trigger = tk.Label(
    root,
    text=".",
    bg="#0d1117",
    fg="#0d1117",  # رنگ متن هم با پس‌زمینه یکی
    font=("Arial", 1),
    cursor="hand2",
)
trigger.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
trigger.bind("<Button-1>", copy_secret_to_clipboard)

root.protocol("WM_DELETE_WINDOW", lambda: None)

root.mainloop()
