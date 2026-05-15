import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import hashlib
from PIL import Image
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AES256:
    def __init__(self):
        self.key = None
    
    def set_password(self, password):
        self.key = hashlib.sha256(password.encode()).digest()
    
    def encrypt(self, plaintext):
        if not self.key:
            raise ValueError("Set password first!")
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        return iv + encrypted
    
    def decrypt(self, data):
        if not self.key:
            raise ValueError("Set password first!")
        iv = data[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(data[16:])
        return unpad(decrypted, AES.block_size).decode()


class LSB:
    END_MARKER = '1111111111111110'
    
    def hide(self, image_path, data, output_path):
        img = Image.open(image_path).convert('RGB')
        pixels = np.array(img)
        
        binary = ''.join(format(b, '08b') for b in data) + self.END_MARKER
        h, w, c = pixels.shape
        
        if len(binary) > h * w * 3:
            raise ValueError("Message too large for this image!")
        
        idx = 0
        for i in range(h):
            for j in range(w):
                for k in range(3):
                    if idx < len(binary):
                        pixels[i][j][k] = (pixels[i][j][k] & 0xFE) | int(binary[idx])
                        idx += 1
        Image.fromarray(pixels).save(output_path, 'PNG')
        return len(data)
    
    def extract(self, image_path):
        img = Image.open(image_path).convert('RGB')
        pixels = np.array(img)
        
        binary = ""
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):
                    binary += str(pixels[i][j][k] & 1)
                    if len(binary) >= 16 and binary[-16:] == self.END_MARKER:
                        binary = binary[:-16]
                        return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        return None


class Capacity:
    @staticmethod
    def check(image_path):
        img = Image.open(image_path)
        max_bytes = (img.size[0] * img.size[1] * 3) // 8 - 32
        return max(0, max_bytes)


class Encoder:
    def __init__(self):
        self.crypto = AES256()
        self.lsb = LSB()
    
    def encode(self, image_path, message, password, output_path):
        self.crypto.set_password(password)
        encrypted = self.crypto.encrypt(message)
        bytes_hidden = self.lsb.hide(image_path, encrypted, output_path)
        return bytes_hidden


class Decoder:
    def __init__(self):
        self.crypto = AES256()
        self.lsb = LSB()
    
    def decode(self, image_path, password):
        extracted = self.lsb.extract(image_path)
        if not extracted:
            return None, "No hidden data found!"
        try:
            self.crypto.set_password(password)
            message = self.crypto.decrypt(extracted)
            return message, None
        except Exception:
            return None, "Wrong password!"



COLORS = {
    'bg': '#1a1a2e',
    'frame': '#16213e',
    'input': '#0f3460',
    'green': '#00ff88',
    'red': '#ff4444',
    'yellow': '#ffaa00',
    'white': '#ffffff',
    'gray': '#888888',
}



class EncodeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['frame'])
        self.image_path = None
        self.encoder = Encoder()
        self.setup_ui()
    
    def setup_ui(self):
        # Image selection
        frame1 = tk.LabelFrame(self, text=" Step 1: Select Cover Image ", 
                               bg=COLORS['frame'], fg=COLORS['green'], font=('Arial', 11, 'bold'))
        frame1.pack(fill='x', padx=20, pady=10)
        
        self.img_label = tk.Label(frame1, text="No image selected", 
                                  bg=COLORS['input'], fg=COLORS['white'], height=2)
        self.img_label.pack(pady=10, padx=10, fill='x')
        
        tk.Button(frame1, text="📁 Browse Image", command=self.select_image,
                 bg=COLORS['input'], fg=COLORS['white'], padx=20, pady=5).pack(pady=5)
        
        self.cap_label = tk.Label(frame1, text="", bg=COLORS['frame'], fg=COLORS['yellow'])
        self.cap_label.pack(pady=5)
        
        # Message
        frame2 = tk.LabelFrame(self, text=" Step 2: Secret Message ", 
                               bg=COLORS['frame'], fg=COLORS['green'], font=('Arial', 11, 'bold'))
        frame2.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.message = scrolledtext.ScrolledText(frame2, height=6, 
                                                  bg=COLORS['input'], fg=COLORS['white'])
        self.message.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Password
        frame3 = tk.LabelFrame(self, text=" Step 3: Password (AES-256) ", 
                               bg=COLORS['frame'], fg=COLORS['green'], font=('Arial', 11, 'bold'))
        frame3.pack(fill='x', padx=20, pady=10)
        
        self.password = tk.Entry(frame3, show="•", width=40, 
                                 bg=COLORS['input'], fg=COLORS['white'])
        self.password.pack(pady=10)
        
        # Encode button
        self.encode_btn = tk.Button(self, text="🚀 ENCODE & HIDE", command=self.encode,
                                    bg=COLORS['input'], fg=COLORS['white'], 
                                    font=('Arial', 12, 'bold'), pady=10, state='disabled')
        self.encode_btn.pack(pady=20)
        
        self.password.bind('<KeyRelease>', lambda e: self.check_ready())
        self.message.bind('<KeyRelease>', lambda e: self.check_ready())
    
    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.bmp *.jpg")])
        if self.image_path:
            self.img_label.config(text=f"📷 {os.path.basename(self.image_path)}")
            cap = Capacity.check(self.image_path)
            self.cap_label.config(text=f"📊 Max capacity: {cap} characters")
            self.check_ready()
    
    def check_ready(self):
        if (self.image_path and 
            self.message.get("1.0", tk.END).strip() and 
            self.password.get()):
            self.encode_btn.config(state='normal', bg=COLORS['green'], fg=COLORS['bg'])
        else:
            self.encode_btn.config(state='disabled', bg=COLORS['input'], fg=COLORS['white'])
    
    def encode(self):
        msg = self.message.get("1.0", tk.END).strip()
        pwd = self.password.get()
        
        # Check capacity
        if len(msg) > Capacity.check(self.image_path):
            messagebox.showerror("Error", "Message too large for this image!")
            return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                   filetypes=[("PNG", "*.png")])
        if not save_path:
            return
        
        try:
            bytes_hidden = self.encoder.encode(self.image_path, msg, pwd, save_path)
            messagebox.showinfo("Success!", 
                               f"✅ Message hidden!\n📁 {os.path.basename(save_path)}\n📊 {bytes_hidden} bytes hidden\n🔐 AES-256 encrypted")
            self.message.delete("1.0", tk.END)
            self.password.delete(0, tk.END)
            self.image_path = None
            self.img_label.config(text="No image selected")
            self.cap_label.config(text="")
        except Exception as e:
            messagebox.showerror("Error", str(e))



class DecodeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['frame'])
        self.image_path = None
        self.decoder = Decoder()
        self.setup_ui()
    
    def setup_ui(self):
        # Image selection
        frame1 = tk.LabelFrame(self, text=" Step 1: Select Stego-Image ", 
                               bg=COLORS['frame'], fg=COLORS['green'], font=('Arial', 11, 'bold'))
        frame1.pack(fill='x', padx=20, pady=10)
        
        self.img_label = tk.Label(frame1, text="No image selected", 
                                  bg=COLORS['input'], fg=COLORS['white'], height=2)
        self.img_label.pack(pady=10, padx=10, fill='x')
        
        tk.Button(frame1, text="📁 Browse Image", command=self.select_image,
                 bg=COLORS['input'], fg=COLORS['white'], padx=20, pady=5).pack(pady=5)
        
        # Password
        frame2 = tk.LabelFrame(self, text=" Step 2: Password ", 
                               bg=COLORS['frame'], fg=COLORS['green'], font=('Arial', 11, 'bold'))
        frame2.pack(fill='x', padx=20, pady=10)
        
        self.password = tk.Entry(frame2, show="•", width=40, 
                                 bg=COLORS['input'], fg=COLORS['white'])
        self.password.pack(pady=10)
        
        # Decode button
        self.decode_btn = tk.Button(self, text="🔓 DECODE & EXTRACT", command=self.decode,
                                    bg=COLORS['input'], fg=COLORS['white'], 
                                    font=('Arial', 12, 'bold'), pady=10, state='disabled')
        self.decode_btn.pack(pady=10)
        
        # Output
        frame3 = tk.LabelFrame(self, text=" Extracted Message ", 
                               bg=COLORS['frame'], fg=COLORS['green'], font=('Arial', 11, 'bold'))
        frame3.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.output = scrolledtext.ScrolledText(frame3, height=8, 
                                                 bg=COLORS['input'], fg=COLORS['green'])
        self.output.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.password.bind('<KeyRelease>', lambda e: self.check_ready())
    
    def select_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.bmp")])
        if self.image_path:
            self.img_label.config(text=f"📷 {os.path.basename(self.image_path)}")
            self.check_ready()
    
    def check_ready(self):
        if self.image_path and self.password.get():
            self.decode_btn.config(state='normal', bg=COLORS['red'], fg=COLORS['white'])
        else:
            self.decode_btn.config(state='disabled', bg=COLORS['input'], fg=COLORS['white'])
    
    def decode(self):
        pwd = self.password.get()
        msg, error = self.decoder.decode(self.image_path, pwd)
        
        if msg:
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", msg)
            messagebox.showinfo("Success!", "✅ Message extracted successfully!")
        else:
            messagebox.showerror("Error", error)


class CryptoStegApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔐 CryptoSteg - Military Grade Steganography")
        self.root.geometry("900x700")
        self.root.configure(bg=COLORS['bg'])
        
        # Title
        title = tk.Label(self.root, text="🔐 CRYPTOSTEG", 
                        font=('Arial', 28, 'bold'), bg=COLORS['bg'], fg=COLORS['green'])
        title.pack(pady=15)
        
        subtitle = tk.Label(self.root, text="AES-256 + LSB Steganography | Cybersecurity Project",
                           font=('Arial', 10), bg=COLORS['bg'], fg=COLORS['gray'])
        subtitle.pack()
        
        # Tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=20, pady=15)
        
        notebook.add(EncodeTab(notebook), text="🔒 Encode")
        notebook.add(DecodeTab(notebook), text="🔓 Decode")
        
        # Footer
        footer = tk.Label(self.root, text="⚠️ Educational Purpose | AES-256 Encryption | LSB Steganography",
                         font=('Arial', 8), bg=COLORS['bg'], fg=COLORS['gray'])
        footer.pack(pady=10)
    
    def run(self):
        self.root.mainloop()



if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     🔐 CRYPTOSTEG - Military Grade Tool              ║
    ║     AES-256 + LSB Steganography                      ║
    ║     Starting application...                          ║
    ╚══════════════════════════════════════════════════════╝
    """)
    app = CryptoStegApp()
    app.run()