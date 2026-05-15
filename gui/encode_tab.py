import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.encoder import Encoder
from features.capacity import CapacityChecker
from features.logger import ActivityLogger
from .styles import COLORS, FONTS


class EncodeTab(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_medium'])
        self.parent = parent
        
        self.image_path = None
        self.encoder = Encoder()
        self.logger = ActivityLogger()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Step 1: Image Selection
        step1_frame = tk.LabelFrame(self, text=" Step 1: Select Cover Image ", 
                                    bg=COLORS['bg_medium'], fg=COLORS['accent_green'],
                                    font=FONTS['heading'])
        step1_frame.pack(fill='x', padx=20, pady=10)
        
        self.img_label = tk.Label(step1_frame, text="No image selected", 
                                  bg=COLORS['bg_light'], fg=COLORS['text_white'],
                                  width=60, height=2, relief='sunken')
        self.img_label.pack(pady=10, padx=10)
        
        btn_frame = tk.Frame(step1_frame, bg=COLORS['bg_medium'])
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="📁 Browse Image", command=self.select_image,
                 bg=COLORS['bg_light'], fg=COLORS['text_white'],
                 padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        self.capacity_label = tk.Label(step1_frame, text="", 
                                       bg=COLORS['bg_medium'], fg=COLORS['accent_yellow'])
        self.capacity_label.pack(pady=5)
        
        # Step 2: Message Input
        step2_frame = tk.LabelFrame(self, text=" Step 2: Enter Secret Message ",
                                    bg=COLORS['bg_medium'], fg=COLORS['accent_green'],
                                    font=FONTS['heading'])
        step2_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.message_text = scrolledtext.ScrolledText(step2_frame, height=6,
                                                       bg=COLORS['bg_light'],
                                                       fg=COLORS['text_white'],
                                                       insertbackground='white',
                                                       font=('Consolas', 10))
        self.message_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Character count
        self.char_count = tk.Label(step2_frame, text="Characters: 0",
                                   bg=COLORS['bg_medium'], fg=COLORS['text_gray'])
        self.char_count.pack(pady=5)
        
        # Bind char count update
        self.message_text.bind('<KeyRelease>', self.update_char_count)
        
        # Step 3: Password
        step3_frame = tk.LabelFrame(self, text=" Step 3: Set Password (AES-256) ",
                                    bg=COLORS['bg_medium'], fg=COLORS['accent_green'],
                                    font=FONTS['heading'])
        step3_frame.pack(fill='x', padx=20, pady=10)
        
        self.password_entry = tk.Entry(step3_frame, show="•", width=40,
                                       bg=COLORS['bg_light'], fg=COLORS['text_white'],
                                       font=('Arial', 11))
        self.password_entry.pack(pady=10)
        self.password_entry.bind('<KeyRelease>', lambda e: self.check_ready())
        
        # Encode Button
        self.encode_btn = tk.Button(self, text="🚀 ENCODE & HIDE MESSAGE",
                                   command=self.encode_message,
                                   bg=COLORS['bg_light'], fg=COLORS['text_white'],
                                   font=FONTS['button'], padx=30, pady=10,
                                   state='disabled', cursor='hand2')
        self.encode_btn.pack(pady=20)
    
    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Image files", "*.png *.bmp *.jpg *.jpeg")]
        )
        
        if self.image_path:
            filename = os.path.basename(self.image_path)
            self.img_label.config(text=f"📷 {filename}")
            self.check_capacity()
            self.check_ready()
    
    def check_capacity(self):
       
        if self.image_path:
            try:
                capacity = CapacityChecker.calculate(self.image_path)
                self.capacity_label.config(
                    text=f"📊 Max capacity: ~{capacity['max_characters']} characters"
                )
            except Exception as e:
                self.capacity_label.config(text=f"📊 Error reading image: {str(e)}")
    
    def update_char_count(self, event=None):
       
        text = self.message_text.get("1.0", tk.END).strip()
        count = len(text)
        self.char_count.config(text=f"Characters: {count}")
        
        # Check if message fits
        if self.image_path and text:
            try:
                can_hide = CapacityChecker.can_hide(self.image_path, text)
                if not can_hide['can_hide']:
                    self.char_count.config(fg=COLORS['accent_red'])
                    self.encode_btn.config(state='disabled')
                else:
                    self.char_count.config(fg=COLORS['text_gray'])
                    self.check_ready()
            except:
                pass
        else:
            self.check_ready()
    
    def check_ready(self):
        
        if (self.image_path and 
            self.message_text.get("1.0", tk.END).strip() and 
            self.password_entry.get()):
            self.encode_btn.config(state='normal', bg=COLORS['accent_green'], 
                                  fg=COLORS['bg_dark'])
        else:
            self.encode_btn.config(state='disabled', bg=COLORS['bg_light'],
                                  fg=COLORS['text_white'])
    
    def encode_message(self):
        
        message = self.message_text.get("1.0", tk.END).strip()
        password = self.password_entry.get()
        
        # Ask for save location
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="stego_image.png"
        )
        
        if not save_path:
            return
        
        try:
            # Encode
            result = self.encoder.encode(
                image_path=self.image_path,
                message=message,
                password=password,
                output_path=save_path
            )
            
            # Log activity
            self.logger.log_encode(
                image_name=os.path.basename(self.image_path),
                output_name=os.path.basename(save_path),
                message_length=len(message),
                status="SUCCESS"
            )
            
            # Show success
            messagebox.showinfo("Success!", 
                               f"✅ Message hidden successfully!\n\n"
                               f"📁 Saved as: {os.path.basename(save_path)}\n"
                               f"📊 Hidden {result['bytes_hidden']} bytes\n"
                               f"🔐 Protected with AES-256 encryption")
            
            # Clear fields
            self.message_text.delete("1.0", tk.END)
            self.password_entry.delete(0, tk.END)
            self.image_path = None
            self.img_label.config(text="No image selected")
            self.capacity_label.config(text="")
            self.char_count.config(text="Characters: 0")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encode: {str(e)}")
            self.logger.log_encode(
                image_name=os.path.basename(self.image_path) if self.image_path else "unknown",
                output_name="",
                message_length=len(message),
                status=f"FAILED: {str(e)}"
            )