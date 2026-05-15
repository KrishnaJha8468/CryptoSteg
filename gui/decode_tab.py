import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.decoder import Decoder
from features.logger import ActivityLogger
from .styles import COLORS, FONTS


class DecodeTab(tk.Frame):
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_medium'])
        self.parent = parent
        
        self.image_path = None
        self.decoder = Decoder()
        self.logger = ActivityLogger()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Step 1: Image Selection
        step1_frame = tk.LabelFrame(self, text=" Step 1: Select Stego-Image ",
                                    bg=COLORS['bg_medium'], fg=COLORS['accent_green'],
                                    font=FONTS['heading'])
        step1_frame.pack(fill='x', padx=20, pady=10)
        
        self.img_label = tk.Label(step1_frame, text="No image selected",
                                  bg=COLORS['bg_light'], fg=COLORS['text_white'],
                                  width=60, height=2, relief='sunken')
        self.img_label.pack(pady=10, padx=10)
        
        tk.Button(step1_frame, text="📁 Browse Stego-Image", command=self.select_image,
                 bg=COLORS['bg_light'], fg=COLORS['text_white'],
                 padx=20, pady=5, cursor='hand2').pack(pady=5)
        
        # Step 2: Password
        step2_frame = tk.LabelFrame(self, text=" Step 2: Enter Password (AES-256) ",
                                    bg=COLORS['bg_medium'], fg=COLORS['accent_green'],
                                    font=FONTS['heading'])
        step2_frame.pack(fill='x', padx=20, pady=10)
        
        self.password_entry = tk.Entry(step2_frame, show="•", width=40,
                                       bg=COLORS['bg_light'], fg=COLORS['text_white'],
                                       font=('Arial', 11))
        self.password_entry.pack(pady=10)
        self.password_entry.bind('<KeyRelease>', self.check_ready)
        
        # Decode Button
        self.decode_btn = tk.Button(self, text="🔓 DECODE & EXTRACT MESSAGE",
                                   command=self.decode_message,
                                   bg=COLORS['bg_light'], fg=COLORS['text_white'],
                                   font=FONTS['button'], padx=30, pady=10,
                                   state='disabled', cursor='hand2')
        self.decode_btn.pack(pady=10)
        
        # Output Area
        output_frame = tk.LabelFrame(self, text=" Extracted Message ",
                                     bg=COLORS['bg_medium'], fg=COLORS['accent_green'],
                                     font=FONTS['heading'])
        output_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8,
                                                      bg=COLORS['bg_light'],
                                                      fg=COLORS['accent_green'],
                                                      insertbackground='white',
                                                      font=('Consolas', 11))
        self.output_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def select_image(self):
        """Select stego image"""
        self.image_path = filedialog.askopenfilename(
            title="Select Stego-Image",
            filetypes=[("PNG files", "*.png"), ("BMP files", "*.bmp"), ("All images", "*.png *.bmp")]
        )
        
        if self.image_path:
            filename = os.path.basename(self.image_path)
            self.img_label.config(text=f"📷 {filename}")
            self.check_ready()
    
    def check_ready(self, event=None):
        """Check if ready to decode"""
        if self.image_path and self.password_entry.get():
            self.decode_btn.config(state='normal', bg=COLORS['accent_red'],
                                  fg=COLORS['text_white'])
        else:
            self.decode_btn.config(state='disabled', bg=COLORS['bg_light'],
                                  fg=COLORS['text_white'])
    
    def decode_message(self):
        """Extract and decrypt the message"""
        password = self.password_entry.get()
        
        try:
            result = self.decoder.decode(self.image_path, password)
            
            if result['success']:
                # Display message
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert("1.0", result['message'])
                
                # Log success
                self.logger.log_decode(
                    image_name=os.path.basename(self.image_path),
                    status="SUCCESS",
                    message_length=len(result['message'])
                )
                
                messagebox.showinfo("Success!", "✅ Message extracted and decrypted successfully!")
            else:
                # Log failure
                self.logger.log_decode(
                    image_name=os.path.basename(self.image_path),
                    status=f"FAILED: {result['error']}"
                )
                messagebox.showerror("Error", result['error'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode: {str(e)}")