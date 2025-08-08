import customtkinter as ctk
import json
from datetime import datetime
from tkinter import filedialog, messagebox, font as tkFont
import base64

# ---------- CONFIG ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

lang = "en"

texts = {
    "en": {
        "title": "License Maker",
        "start_date": "Start Date (YYYY-MM-DD)",
        "end_date": "End Date (YYYY-MM-DD)",
        "generate": "Generate License",
        "save": "Save License",
        "help": "Help",
        "license_json": "License",
        "help_text": (
            "Usage Instructions:\n\n"
            "1. Enter Start Date (YYYY-MM-DD)\n"
            "2. Enter End Date (YYYY-MM-DD)\n"
            "3. Click 'Generate License' to create the license\n"
            "4. Click 'Save License' to save it as a license file (.lic)"
        ),
        "success": "License generated successfully!",
        "error_format": "Dates must be in YYYY-MM-DD format",
        "error_order": "Start date must be before end date",
        "warning_empty": "No license data to save",
        "saved": "License saved to {}"
    },
    "fa": {
        "title": "ساخت لایسنس",
        "start_date": "تاریخ شروع (YYYY-MM-DD)",
        "end_date": "تاریخ پایان (YYYY-MM-DD)",
        "generate": "ساخت لایسنس",
        "save": "ذخیره لایسنس",
        "help": "راهنما",
        "license_json": "لایسنس",
        "help_text": (
            "راهنما:\n\n"
            "۱. تاریخ شروع را وارد کنید (YYYY-MM-DD)\n"
            "۲. تاریخ پایان را وارد کنید (YYYY-MM-DD)\n"
            "۳. روی «ساخت لایسنس» کلیک کنید\n"
            "۴. برای ذخیره روی «ذخیره لایسنس» کلیک کنید (فایل با پسوند .lic ذخیره می‌شود)"
        ),
        "success": "لایسنس با موفقیت ایجاد شد!",
        "error_format": "تاریخ‌ها باید به فرمت YYYY-MM-DD باشند",
        "error_order": "تاریخ شروع باید قبل از تاریخ پایان باشد",
        "warning_empty": "هیچ لایسنس برای ذخیره وجود ندارد",
        "saved": "لایسنس ذخیره شد در {}"
    }
}

# ---------- FONT CHECK ----------
def font_exists(font_name):
    return font_name in tkFont.families()

# ---------- LOGIC ----------
def generate_license():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if end <= start:
            messagebox.showerror("Error", texts[lang]["error_order"])
            return
    except ValueError:
        messagebox.showerror("Error", texts[lang]["error_format"])
        return

    license_data = {
        "startDate": start_date,
        "endDate": end_date,
        "issuedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "signature": __import__("hashlib").sha256(f"{start_date}{end_date}".encode()).hexdigest()
    }
    json_str = json.dumps(license_data, indent=4, ensure_ascii=False)
    encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    license_text.delete("1.0", "end")
    license_text.insert("1.0", encoded)
    messagebox.showinfo("Success", texts[lang]["success"])

def save_license():
    content = license_text.get("1.0", "end").strip()
    if not content:
        messagebox.showwarning("Warning", texts[lang]["warning_empty"])
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".lic", 
                                             filetypes=[("License Files", "*.lic")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Saved", texts[lang]["saved"].format(file_path))

def show_help():
    messagebox.showinfo(texts[lang]["help"], texts[lang]["help_text"])

def switch_language(new_lang):
    global lang
    lang = new_lang
    update_ui_texts()

def update_ui_texts():
    persian_font_name = "Vazir" if font_exists("Vazir") else "Tahoma"
    persian_font = (persian_font_name, 14)
    english_font = ("Segoe UI", 14)

    app.title(texts[lang]["title"])
    if lang == "fa":
        title_label.configure(text=texts[lang]["title"], anchor="e", font=(persian_font_name, 22, "bold"))
        start_date_entry.configure(placeholder_text=texts[lang]["start_date"],
                                   justify="right", font=persian_font)
        end_date_entry.configure(placeholder_text=texts[lang]["end_date"],
                                 justify="right", font=persian_font)
        generate_btn.configure(text=texts[lang]["generate"], font=persian_font)
        save_btn.configure(text=texts[lang]["save"], font=persian_font)
        help_btn.configure(text=texts[lang]["help"], font=persian_font)
        license_label.configure(text=texts[lang]["license_json"], anchor="e", font=persian_font)
        license_text.configure(justify="right", font=persian_font)
    else:
        title_label.configure(text=texts[lang]["title"], anchor="w", font=("Segoe UI", 22, "bold"))
        start_date_entry.configure(placeholder_text=texts[lang]["start_date"],
                                   justify="left", font=english_font)
        end_date_entry.configure(placeholder_text=texts[lang]["end_date"],
                                 justify="left", font=english_font)
        generate_btn.configure(text=texts[lang]["generate"], font=english_font)
        save_btn.configure(text=texts[lang]["save"], font=english_font)
        help_btn.configure(text=texts[lang]["help"], font=english_font)
        license_label.configure(text=texts[lang]["license_json"], anchor="w", font=english_font)
        license_text.configure(justify="left", font=english_font)

    if lang == "fa":
        generate_btn.grid(row=0, column=2, padx=5)
        save_btn.grid(row=0, column=1, padx=5)
        help_btn.grid(row=0, column=0, padx=5)
    else:
        generate_btn.grid(row=0, column=0, padx=5)
        save_btn.grid(row=0, column=1, padx=5)
        help_btn.grid(row=0, column=2, padx=5)

# ---------- UI ----------
app = ctk.CTk()
app.geometry("600x450")
app.title(texts[lang]["title"])

title_label = ctk.CTkLabel(app, text=texts[lang]["title"], font=("Segoe UI", 22, "bold"), anchor="w")
title_label.pack(pady=(10, 5), fill="x", padx=20)

lang_frame = ctk.CTkFrame(app)
lang_frame.pack(pady=5)
ctk.CTkButton(lang_frame, text="English", width=80, command=lambda: switch_language("en")).grid(row=0, column=0, padx=5)
ctk.CTkButton(lang_frame, text="فارسی", width=80, command=lambda: switch_language("fa")).grid(row=0, column=1, padx=5)

start_date_entry = ctk.CTkEntry(app, placeholder_text=texts[lang]["start_date"], width=350)
start_date_entry.pack(pady=5)

end_date_entry = ctk.CTkEntry(app, placeholder_text=texts[lang]["end_date"], width=350)
end_date_entry.pack(pady=5)

btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=10)

generate_btn = ctk.CTkButton(btn_frame, text=texts[lang]["generate"], command=generate_license)
save_btn = ctk.CTkButton(btn_frame, text=texts[lang]["save"], command=save_license)
help_btn = ctk.CTkButton(btn_frame, text=texts[lang]["help"], command=show_help)
generate_btn.grid(row=0, column=0, padx=5)
save_btn.grid(row=0, column=1, padx=5)
help_btn.grid(row=0, column=2, padx=5)

license_label = ctk.CTkLabel(app, text=texts[lang]["license_json"], font=("Segoe UI", 14), anchor="w")
license_label.pack(pady=(10, 0), fill="x", padx=20)

license_text = ctk.CTkTextbox(app, height=150, wrap="word")
license_text.pack(pady=5, padx=20, fill="both", expand=True)

app.mainloop()
