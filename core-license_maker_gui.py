import customtkinter as ctk
import json
import base64
import hashlib
import os
from datetime import datetime
from tkinter import filedialog, messagebox, font as tkFont

# ---------- CONFIG ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

lang = "en"

# Available modules
AVAILABLE_MODULES = [
    "auth",
    "admin", 
    "personal-space",
    "gps",
    "stations",
    "subscription",
    "ticket",
    "user",
    "ppk",
    "spp",
    "static",
    "lgps2",
    "capcha",
    "email",
    "database"
]

texts = {
    "en": {
        "title": "License Maker",
        "customer_id": "Customer ID",
        "start_date": "Start Date (YYYY-MM-DD)",
        "end_date": "End Date (YYYY-MM-DD)",
        "modules": "Select Modules",
        "select_all": "Select All",
        "deselect_all": "Deselect All",
        "generate": "Generate License",
        "save": "Save License",
        "help": "Help",
        "license_output": "License (Base64)",
        "help_text": (
            "Usage Instructions:\n\n"
            "1. Enter Customer ID\n"
            "2. Enter Start Date (YYYY-MM-DD)\n"
            "3. Enter End Date (YYYY-MM-DD)\n"
            "4. Select modules using checkboxes\n"
            "5. Click 'Generate License' to create the license\n"
            "6. Click 'Save License' to save it as a .lic file"
        ),
        "success": "License generated successfully!",
        "error_format": "Dates must be in YYYY-MM-DD format",
        "error_order": "Start date must be before end date",
        "warning_empty": "No license data to save",
        "saved": "License saved to {}",
        "error_customer": "Customer ID is required",
        "error_modules": "Please select at least one module"
    },
    "fa": {
        "title": "ساخت لایسنس",
        "customer_id": "شناسه مشتری",
        "start_date": "تاریخ شروع (YYYY-MM-DD)",
        "end_date": "تاریخ پایان (YYYY-MM-DD)",
        "modules": "انتخاب ماژول‌ها",
        "select_all": "انتخاب همه",
        "deselect_all": "حذف انتخاب همه",
        "generate": "ساخت لایسنس",
        "save": "ذخیره لایسنس",
        "help": "راهنما",
        "license_output": "لایسنس (Base64)",
        "help_text": (
            "راهنما:\n\n"
            "۱. شناسه مشتری را وارد کنید\n"
            "۲. تاریخ شروع را وارد کنید (YYYY-MM-DD)\n"
            "۳. تاریخ پایان را وارد کنید (YYYY-MM-DD)\n"
            "۴. ماژول‌ها را با استفاده از چک‌باکس انتخاب کنید\n"
            "۵. روی «ساخت لایسنس» کلیک کنید\n"
            "۶. برای ذخیره روی «ذخیره لایسنس» کلیک کنید (فایل با پسوند .lic ذخیره می‌شود)"
        ),
        "success": "لایسنس با موفقیت ایجاد شد!",
        "error_format": "تاریخ‌ها باید به فرمت YYYY-MM-DD باشند",
        "error_order": "تاریخ شروع باید قبل از تاریخ پایان باشد",
        "warning_empty": "هیچ لایسنس برای ذخیره وجود ندارد",
        "saved": "لایسنس ذخیره شد در {}",
        "error_customer": "شناسه مشتری الزامی است",
        "error_modules": "لطفاً حداقل یک ماژول انتخاب کنید"
    }
}

# ---------- FONT CHECK ----------
def font_exists(font_name):
    return font_name in tkFont.families()

# ---------- LOGIC ----------
def generate_random_string(length=129):
    """Generate a random string of specified length"""
    import secrets
    import string
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_signature(license_data):
    """Generate a signature for the license"""
    # Create a hash of the license data
    license_str = json.dumps(license_data, sort_keys=True)
    hash_obj = hashlib.sha256(license_str.encode('utf-8'))
    return hash_obj.hexdigest()

def get_selected_modules():
    """Get list of selected modules from checkboxes"""
    selected = []
    for module, var in module_vars.items():
        if var.get():
            selected.append(module)
    return selected

def select_all_modules():
    """Select all modules"""
    for var in module_vars.values():
        var.set(True)

def deselect_all_modules():
    """Deselect all modules"""
    for var in module_vars.values():
        var.set(False)

def generate_license():
    customer_id = customer_id_entry.get().strip()
    start_date = start_date_entry.get().strip()
    end_date = end_date_entry.get().strip()
    modules = get_selected_modules()
    
    # Validate customer ID
    if not customer_id:
        messagebox.showerror("Error", texts[lang]["error_customer"])
        return
    
    # Validate modules
    if not modules:
        messagebox.showerror("Error", texts[lang]["error_modules"])
        return
    
    # Validate dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if end <= start:
            messagebox.showerror("Error", texts[lang]["error_order"])
            return
    except ValueError:
        messagebox.showerror("Error", texts[lang]["error_format"])
        return
    
    # Create license data structure similar to TypeScript version
    license_data = {
        "customerId": customer_id,
        "startDate": start_date,
        "endDate": end_date,
        "modules": modules
    }
    
    # Generate signature (similar to TypeScript version)
    signature = generate_signature(license_data)
    random_string = generate_random_string(129)
    full_signature = random_string + signature
    
    # Add signature to license
    license_with_signature = {
        **license_data,
        "signature": full_signature
    }
    
    # Convert to base64
    license_json = json.dumps(license_with_signature, indent=2)
    encoded_license = base64.b64encode(license_json.encode('utf-8')).decode('utf-8')
    
    # Display in text area
    license_text.delete("1.0", "end")
    license_text.insert("1.0", encoded_license)
    messagebox.showinfo("Success", texts[lang]["success"])

def save_license():
    content = license_text.get("1.0", "end").strip()
    if not content:
        messagebox.showwarning("Warning", texts[lang]["warning_empty"])
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".lic", 
        filetypes=[("License Files", "*.lic"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", texts[lang]["saved"].format(file_path))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def show_help():
    messagebox.showinfo(texts[lang]["help"], texts[lang]["help_text"])

def switch_language(new_lang):
    global lang
    lang = new_lang
    update_ui_texts()

def update_ui_texts():
    persian_font_name = "Vazir" if font_exists("Vazir") else "Tahoma"
    persian_font = (persian_font_name, 12)
    english_font = ("Segoe UI", 12)

    app.title(texts[lang]["title"])
    
    if lang == "fa":
        title_label.configure(text=texts[lang]["title"], anchor="e", font=(persian_font_name, 22, "bold"))
        customer_id_label.configure(text=texts[lang]["customer_id"], anchor="e", font=persian_font)
        customer_id_entry.configure(placeholder_text=texts[lang]["customer_id"], justify="right", font=persian_font)
        start_date_entry.configure(placeholder_text=texts[lang]["start_date"], justify="right", font=persian_font)
        end_date_entry.configure(placeholder_text=texts[lang]["end_date"], justify="right", font=persian_font)
        modules_label.configure(text=texts[lang]["modules"], anchor="e", font=persian_font)
        select_all_btn.configure(text=texts[lang]["select_all"], font=persian_font)
        deselect_all_btn.configure(text=texts[lang]["deselect_all"], font=persian_font)
        generate_btn.configure(text=texts[lang]["generate"], font=persian_font)
        save_btn.configure(text=texts[lang]["save"], font=persian_font)
        help_btn.configure(text=texts[lang]["help"], font=persian_font)
        license_label.configure(text=texts[lang]["license_output"], anchor="e", font=persian_font)
        license_text.configure(justify="right", font=persian_font)
    else:
        title_label.configure(text=texts[lang]["title"], anchor="w", font=("Segoe UI", 22, "bold"))
        customer_id_label.configure(text=texts[lang]["customer_id"], anchor="w", font=english_font)
        customer_id_entry.configure(placeholder_text=texts[lang]["customer_id"], justify="left", font=english_font)
        start_date_entry.configure(placeholder_text=texts[lang]["start_date"], justify="left", font=english_font)
        end_date_entry.configure(placeholder_text=texts[lang]["end_date"], justify="left", font=english_font)
        modules_label.configure(text=texts[lang]["modules"], anchor="w", font=english_font)
        select_all_btn.configure(text=texts[lang]["select_all"], font=english_font)
        deselect_all_btn.configure(text=texts[lang]["deselect_all"], font=english_font)
        generate_btn.configure(text=texts[lang]["generate"], font=english_font)
        save_btn.configure(text=texts[lang]["save"], font=english_font)
        help_btn.configure(text=texts[lang]["help"], font=english_font)
        license_label.configure(text=texts[lang]["license_output"], anchor="w", font=english_font)
        license_text.configure(justify="left", font=english_font)

    # Reorder buttons for RTL/LTR
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
app.geometry("800x700")
app.title(texts[lang]["title"])

# Title
title_label = ctk.CTkLabel(app, text=texts[lang]["title"], font=("Segoe UI", 22, "bold"), anchor="w")
title_label.pack(pady=(10, 5), fill="x", padx=20)

# Language switcher
lang_frame = ctk.CTkFrame(app)
lang_frame.pack(pady=5)
ctk.CTkButton(lang_frame, text="English", width=80, command=lambda: switch_language("en")).grid(row=0, column=0, padx=5)
ctk.CTkButton(lang_frame, text="فارسی", width=80, command=lambda: switch_language("fa")).grid(row=0, column=1, padx=5)

# Customer ID
customer_id_label = ctk.CTkLabel(app, text=texts[lang]["customer_id"], font=("Segoe UI", 12), anchor="w")
customer_id_label.pack(pady=(10, 0), fill="x", padx=20)
customer_id_entry = ctk.CTkEntry(app, placeholder_text=texts[lang]["customer_id"], width=350)
customer_id_entry.pack(pady=5)

# Start Date
start_date_entry = ctk.CTkEntry(app, placeholder_text=texts[lang]["start_date"], width=350)
start_date_entry.pack(pady=5)

# End Date
end_date_entry = ctk.CTkEntry(app, placeholder_text=texts[lang]["end_date"], width=350)
end_date_entry.pack(pady=5)

# Modules Section
modules_label = ctk.CTkLabel(app, text=texts[lang]["modules"], font=("Segoe UI", 12), anchor="w")
modules_label.pack(pady=(10, 0), fill="x", padx=20)

# Select All/Deselect All buttons
select_buttons_frame = ctk.CTkFrame(app)
select_buttons_frame.pack(pady=5)
select_all_btn = ctk.CTkButton(select_buttons_frame, text=texts[lang]["select_all"], command=select_all_modules, width=120)
deselect_all_btn = ctk.CTkButton(select_buttons_frame, text=texts[lang]["deselect_all"], command=deselect_all_modules, width=120)
select_all_btn.pack(side="left", padx=5)
deselect_all_btn.pack(side="left", padx=5)

# Modules checkboxes frame
modules_frame = ctk.CTkScrollableFrame(app, width=600, height=150)
modules_frame.pack(pady=5, padx=20, fill="x")

# Create checkboxes for modules
module_vars = {}
default_modules = ["admin", "personal-space", "gps", "stations", "subscription", "ticket", "user", "ppk", "spp", "static"]

for i, module in enumerate(AVAILABLE_MODULES):
    var = ctk.BooleanVar(value=module in default_modules)
    module_vars[module] = var
    checkbox = ctk.CTkCheckBox(modules_frame, text=module, variable=var)
    checkbox.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=2)

# Buttons
btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=10)

generate_btn = ctk.CTkButton(btn_frame, text=texts[lang]["generate"], command=generate_license)
save_btn = ctk.CTkButton(btn_frame, text=texts[lang]["save"], command=save_license)
help_btn = ctk.CTkButton(btn_frame, text=texts[lang]["help"], command=show_help)
generate_btn.grid(row=0, column=0, padx=5)
save_btn.grid(row=0, column=1, padx=5)
help_btn.grid(row=0, column=2, padx=5)

# License Output
license_label = ctk.CTkLabel(app, text=texts[lang]["license_output"], font=("Segoe UI", 12), anchor="w")
license_label.pack(pady=(10, 0), fill="x", padx=20)

license_text = ctk.CTkTextbox(app, height=150, wrap="word")
license_text.pack(pady=5, padx=20, fill="both", expand=True)

# Set default values
customer_id_entry.insert(0, "TARENJ")
start_date_entry.insert(0, "2025-07-30")
end_date_entry.insert(0, "2025-09-15")

app.mainloop() 