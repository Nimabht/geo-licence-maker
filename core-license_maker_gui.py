import customtkinter as ctk
import json
import base64
import hashlib
import os
from datetime import datetime
from tkinter import filedialog, messagebox, font as tkFont
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

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
    "calendar",
    "ion",
    "ppp"
]

texts = {
    "en": {
        "title": "License Maker",
        "customer_id": "Customer ID",
        "private_key": "Private Key (PEM)",
        "browse": "Browse...",
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
            "2. Choose Private Key (PEM)\n"
            "3. Enter Start Date (YYYY-MM-DD)\n"
            "4. Enter End Date (YYYY-MM-DD)\n"
            "5. Select modules using checkboxes\n"
            "6. Click 'Generate License' to create the license\n"
            "7. Click 'Save License' to save it as a .lic file\n\n"
            "Note: The private key is used to sign the license (RSA-SHA256)."
        ),
        "success": "License generated successfully!",
        "error_format": "Dates must be in YYYY-MM-DD format",
        "error_order": "Start date must be before end date",
        "warning_empty": "No license data to save",
        "saved": "License saved to {}",
        "error_customer": "Customer ID is required",
        "error_modules": "Please select at least one module",
        "error_private_key": "Private key file not found or invalid!",
        "error_private_key_missing": "Please choose a private key file (.pem)"
    },
    "fa": {
        "title": "ساخت لایسنس",
        "customer_id": "شناسه مشتری",
        "private_key": "کلید خصوصی (PEM)",
        "browse": "انتخاب فایل...",
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
            "۲. کلید خصوصی (PEM) را انتخاب کنید\n"
            "۳. تاریخ شروع را وارد کنید (YYYY-MM-DD)\n"
            "۴. تاریخ پایان را وارد کنید (YYYY-MM-DD)\n"
            "۵. ماژول‌ها را با استفاده از چک‌باکس انتخاب کنید\n"
            "۶. روی «ساخت لایسنس» کلیک کنید\n"
            "۷. برای ذخیره روی «ذخیره لایسنس» کلیک کنید (فایل با پسوند .lic ذخیره می‌شود)\n\n"
            "توجه: از این کلید برای امضای لایسنس (RSA-SHA256) استفاده می‌شود."
        ),
        "success": "لایسنس با موفقیت ایجاد شد!",
        "error_format": "تاریخ‌ها باید به فرمت YYYY-MM-DD باشند",
        "error_order": "تاریخ شروع باید قبل از تاریخ پایان باشد",
        "warning_empty": "هیچ لایسنس برای ذخیره وجود ندارد",
        "saved": "لایسنس ذخیره شد در {}",
        "error_customer": "شناسه مشتری الزامی است",
        "error_modules": "لطفاً حداقل یک ماژول انتخاب کنید",
        "error_private_key": "فایل کلید خصوصی نامعتبر یا یافت نشد!",
        "error_private_key_missing": "لطفاً فایل کلید خصوصی (.pem) را انتخاب کنید"
    }
}

# ---------- FONT CHECK ----------
def font_exists(font_name):
    return font_name in tkFont.families()

# ---------- LOGIC ----------
def generate_random_hex_prefix(length=129):
    """Generate a hex-only random string with the exact requested length (matches TS behavior)."""
    import secrets
    # secrets.token_hex(n) returns 2n hex chars; make slightly longer then trim to exact length
    hex_str = secrets.token_hex((length // 2) + 1)
    return hex_str[:length]

def generate_signature_with_private_key(license_data, key_path: str):
    """Generate a signature using the provided private key (PEM)."""
    try:
        if not os.path.exists(key_path):
            raise FileNotFoundError("Key not found")
        # Read private key file
        with open(key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        
        # Create license data string (exactly like TypeScript JSON.stringify: no spaces, same key order)
        license_str = json.dumps(license_data, separators=(",", ":"), ensure_ascii=False)
        
        # Sign the data
        signature = private_key.sign(
            license_str.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return signature.hex()
    except Exception as e:
        raise Exception(f"SIGN_ERROR: {str(e)}")

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

def browse_private_key():
    file_path = filedialog.askopenfilename(
        title="Select Private Key",
        filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
    )
    if file_path:
        private_key_entry.delete(0, "end")
        private_key_entry.insert(0, file_path)

def generate_license():
    customer_id = customer_id_entry.get().strip()
    key_path = private_key_entry.get().strip()
    start_date = start_date_entry.get().strip()
    end_date = end_date_entry.get().strip()
    modules = get_selected_modules()
    
    # Validate customer ID
    if not customer_id:
        messagebox.showerror("Error", texts[lang]["error_customer"])
        return
    
    # Validate private key path
    if not key_path:
        messagebox.showerror("Error", texts[lang]["error_private_key_missing"])
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
    
    try:
        # Generate signature using selected private key
        signature = generate_signature_with_private_key(license_data, key_path)
        random_prefix = generate_random_hex_prefix(129)
        full_signature = random_prefix + signature
        
        # Add signature to license
        license_with_signature = {
            **license_data,
            "signature": full_signature
        }
        
        # Convert to base64
        license_json = json.dumps(license_with_signature, separators=(",", ":"), ensure_ascii=False)
        encoded_license = base64.b64encode(license_json.encode('utf-8')).decode('utf-8')
        
        # Display in text area
        license_text.delete("1.0", "end")
        license_text.insert("1.0", encoded_license)
        messagebox.showinfo("Success", texts[lang]["success"])
        
    except Exception as e:
        messagebox.showerror("Error", texts[lang]["error_private_key"])

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
        private_key_label.configure(text=texts[lang]["private_key"], anchor="e", font=persian_font)
        browse_btn.configure(text=texts[lang]["browse"], font=persian_font)
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
        private_key_label.configure(text=texts[lang]["private_key"], anchor="w", font=english_font)
        browse_btn.configure(text=texts[lang]["browse"], font=english_font)
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
app.geometry("900x750")
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

# Private Key picker
private_key_label = ctk.CTkLabel(app, text=texts[lang]["private_key"], font=("Segoe UI", 12), anchor="w")
private_key_label.pack(pady=(10, 0), fill="x", padx=20)
private_key_frame = ctk.CTkFrame(app)
private_key_frame.pack(pady=5, padx=20, fill="x")
private_key_entry = ctk.CTkEntry(private_key_frame, placeholder_text="private_key.pem")
private_key_entry.pack(side="left", expand=True, fill="x")
browse_btn = ctk.CTkButton(private_key_frame, text=texts[lang]["browse"], width=110, command=browse_private_key)
browse_btn.pack(side="left", padx=8)

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
modules_frame = ctk.CTkScrollableFrame(app, width=700, height=180)
modules_frame.pack(pady=5, padx=20, fill="x")

# Create checkboxes for modules
module_vars = {}
default_modules = ["auth","admin", "personal-space", "gps", "stations", "subscription", "ticket", "user", "ppk", "spp", "static","calendar","ion","ppp"]

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

license_text = ctk.CTkTextbox(app, height=160, wrap="word")
license_text.pack(pady=5, padx=20, fill="both", expand=True)

# Set default values
customer_id_entry.insert(0, "TARENJ")
# Pre-fill with default file name if present
if os.path.exists("private_key.pem"):
    private_key_entry.insert(0, os.path.abspath("private_key.pem"))
start_date_entry.insert(0, "2025-07-30")
end_date_entry.insert(0, "2025-09-15")

app.mainloop() 