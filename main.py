import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont
import os
import json
import re

class CodeEditor:
    def __init__(self, master):
        self.master = master
        self.filename = None
        self.settings = self.load_settings()
        self.load_language()
        self.setup_ui()
        self.master.iconbitmap('logo.ico')

    def about(self):
        messagebox.showinfo(self.lang_strings['about'], self.lang_strings['about_text'])

    def setup_ui(self):
        self.master.title("Lumine IDE")
        self.master.geometry("1000x700")

        # Stil ayarları
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TFrame", background="#f0f0f0")

        # Ana çerçeve
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Araç çubuğu
        self.create_toolbar(main_frame)

        # Metin alanı ve satır numaraları için çerçeve
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Metin alanı
        self.text_font = tkfont.Font(family="Consolas", size=12)
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, undo=True, font=self.text_font)
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Satır numaraları
        self.line_numbers = tk.Text(text_frame, width=4, padx=4, takefocus=0, border=0, font=self.text_font)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Durum çubuğu
        self.status_bar = ttk.Label(main_frame, text=f"{self.lang_strings['line']}: 1, {self.lang_strings['column']}: 0", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Metin alanı değişiklik olayları
        self.text_area.bind('<<Modified>>', self.on_modify)
        self.text_area.bind('<KeyRelease>', self.on_key_release)

        self.update_line_numbers()

        # Menü çubuğu
        self.create_menu()

        # Tema uygula
        self.apply_theme(self.settings['theme'])

    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.new_button = ttk.Button(toolbar, text=self.lang_strings['new'], command=self.new_file)
        self.new_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.open_button = ttk.Button(toolbar, text=self.lang_strings['open'], command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.save_button = ttk.Button(toolbar, text=self.lang_strings['save'], command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=2, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.lang_strings['new'], command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label=self.lang_strings['open'], command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label=self.lang_strings['save'], command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label=self.lang_strings['save_as'], command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label=self.lang_strings['exit'], command=self.master.quit)
        menubar.add_cascade(label=self.lang_strings['file'], menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label=self.lang_strings['undo'], command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label=self.lang_strings['redo'], command=self.text_area.edit_redo, accelerator="Ctrl+Y")
        menubar.add_cascade(label=self.lang_strings['edit'], menu=edit_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        theme_menu.add_command(label=self.lang_strings['light_theme'], command=lambda: self.change_theme("light"))
        theme_menu.add_command(label=self.lang_strings['dark_theme'], command=lambda: self.change_theme("dark"))
        settings_menu.add_cascade(label=self.lang_strings['theme'], menu=theme_menu)
        
        language_menu = tk.Menu(settings_menu, tearoff=0)
        language_menu.add_command(label="English", command=lambda: self.change_language("en"))
        language_menu.add_command(label="Türkçe", command=lambda: self.change_language("tr"))
        settings_menu.add_cascade(label=self.lang_strings['language'], menu=language_menu)
        
        menubar.add_cascade(label=self.lang_strings['settings'], menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=self.lang_strings['about'], command=self.about)
        menubar.add_cascade(label=self.lang_strings['help'], menu=help_menu)

        self.master.config(menu=menubar)

        # Klavye kısayolları
        self.master.bind('<Control-n>', lambda event: self.new_file())
        self.master.bind('<Control-o>', lambda event: self.open_file())
        self.master.bind('<Control-s>', lambda event: self.save_file())

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.master.title("Lumine IDE - New File")

    def open_file(self):
        self.filename = filedialog.askopenfilename(defaultextension=".txt",
                                                   filetypes=[("All Files", "*.*"),
                                                              ("Text Files", "*.txt"),
                                                              ("Python Files", "*.py")])
        if self.filename:
            self.text_area.delete(1.0, tk.END)
            with open(self.filename, "r") as f:
                self.text_area.insert(tk.END, f.read())
            self.master.title(f"Lumine IDE - {os.path.basename(self.filename)}")
            self.highlight_syntax()

    def save_file(self):
        if not self.filename:
            self.save_file_as()
        else:
            self.save_current_file()

    def save_file_as(self):
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("All Files", "*.*"),
                                                                ("Text Files", "*.txt"),
                                                                ("Python Files", "*.py")])
        if self.filename:
            self.save_current_file()

    def save_current_file(self):
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(self.text_area.get(1.0, tk.END))
            self.master.title(f"Lumine IDE - {os.path.basename(self.filename)}")
            messagebox.showinfo("Info", self.lang_strings['file_saved'])

    def on_modify(self, event):
        self.update_line_numbers()
        self.text_area.edit_modified(False)

    def update_line_numbers(self):
        line_numbers = self.get_line_numbers()
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers)
        self.line_numbers.config(state='disabled')

    def get_line_numbers(self):
        output = ''
        row, col = self.text_area.index(tk.END).split('.')
        for i in range(1, int(row)):
            output += f"{i}\n"
        return output

    def update_status_bar(self):
        row, col = self.text_area.index(tk.INSERT).split('.')
        line_count = self.text_area.get('1.0', tk.END).count('\n')
        self.status_bar.config(text=f"{self.lang_strings['line']}: {row}, {self.lang_strings['column']}: {col} | {self.lang_strings['total_lines']}: {line_count}")

    def highlight_syntax(self):
        # Tüm mevcut etiketleri kaldır
        for tag in self.text_area.tag_names():
            self.text_area.tag_remove(tag, "1.0", "end")

        content = self.text_area.get("1.0", "end-1c")
        
        # Python anahtar kelimeleri
        keywords = r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
        self.highlight_pattern(keywords, 'keyword')

        # Fonksiyonlar
        functions = r'\b([a-zA-Z_][a-zA-Z0-9_]*(?=\s*\())'
        self.highlight_pattern(functions, 'function')

        # Stringler
        strings = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
        self.highlight_pattern(strings, 'string')

        # Yorumlar
        comments = r'(#.*)'
        self.highlight_pattern(comments, 'comment')

        # Sayılar
        numbers = r'\b(\d+)\b'
        self.highlight_pattern(numbers, 'number')

        # Dekoratörler
        decorators = r'(@[a-zA-Z_][a-zA-Z0-9_]*)'
        self.highlight_pattern(decorators, 'decorator')

    def highlight_pattern(self, pattern, tag):
        content = self.text_area.get("1.0", "end-1c")
        for match in re.finditer(pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_area.tag_add(tag, start, end)

    def apply_syntax_highlighting_colors(self):
        theme = self.settings['theme']
        if theme == 'light':
            self.text_area.tag_config('keyword', foreground='#0000FF')
            self.text_area.tag_config('function', foreground='#CC00FF')
            self.text_area.tag_config('string', foreground='#008000')
            self.text_area.tag_config('comment', foreground='#808080')
            self.text_area.tag_config('number', foreground='#FF8000')
            self.text_area.tag_config('decorator', foreground='#AA5500')
        else:  # dark theme
            self.text_area.tag_config('keyword', foreground='#569CD6')
            self.text_area.tag_config('function', foreground='#DCDCAA')
            self.text_area.tag_config('string', foreground='#CE9178')
            self.text_area.tag_config('comment', foreground='#6A9955')
            self.text_area.tag_config('number', foreground='#B5CEA8')
            self.text_area.tag_config('decorator', foreground='#C586C0')

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'theme': 'dark', 'language': 'en'}  # Varsayılan ayarlar

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def change_theme(self, theme):
        self.settings['theme'] = theme
        self.save_settings()
        self.apply_theme(theme)

    def apply_theme(self, theme):
        if theme == 'light':
            self.text_area.config(
                bg="white", 
                fg="black", 
                insertbackground="black", 
                insertwidth=2,
                selectbackground="#a6c2ff",
                selectforeground="black"
            )
            self.line_numbers.config(bg="lightgray", fg="black")
        else:  # dark theme
            self.text_area.config(
                bg="#1E1E1E", 
                fg="#D4D4D4", 
                insertbackground="white", 
                insertwidth=2,
                selectbackground="#264f78",
                selectforeground="white"
            )
            self.line_numbers.config(bg="#252526", fg="#D4D4D4")
        
        self.apply_syntax_highlighting_colors()

    def on_key_release(self, event):
        self.update_status_bar()
        self.highlight_syntax()

    def change_language(self, lang):
        self.settings['language'] = lang
        self.save_settings()
        self.load_language()
        self.update_ui_text()

    def load_language(self):
        lang = self.settings.get('language', 'en')
        if lang == 'en':
            self.lang_strings = {
                'file': 'File',
                'new': 'New',
                'open': 'Open',
                'save': 'Save',
                'save_as': 'Save As',
                'exit': 'Exit',
                'edit': 'Edit',
                'undo': 'Undo',
                'redo': 'Redo',
                'settings': 'Settings',
                'theme': 'Theme',
                'light_theme': 'Light Theme',
                'dark_theme': 'Dark Theme',
                'language': 'Language',
                'help': 'Help',
                'about': 'About',
                'line': 'Line',
                'column': 'Column',
                'total_lines': 'Total Lines',
                'file_saved': 'File saved.',
                'about_text': 'Lumine IDE\n\nVersion 1.0\n\nA modern code editor for bright ideas.'
            }
        else:  # 'tr'
            self.lang_strings = {
                'file': 'Dosya',
                'new': 'Yeni',
                'open': 'Aç',
                'save': 'Kaydet',
                'save_as': 'Farklı Kaydet',
                'exit': 'Çıkış',
                'edit': 'Düzenle',
                'undo': 'Geri Al',
                'redo': 'İleri Al',
                'settings': 'Ayarlar',
                'theme': 'Tema',
                'light_theme': 'Açık Tema',
                'dark_theme': 'Koyu Tema',
                'language': 'Dil',
                'help': 'Yardım',
                'about': 'Hakkında',
                'line': 'Satır',
                'column': 'Sütun',
                'total_lines': 'Toplam Satır',
                'file_saved': 'Dosya kaydedildi.',
                'about_text': 'Lumine IDE\n\nSürüm 1.0\n\nAydınlık fikirler için modern bir kod editörü.'
            }

    def update_ui_text(self):
        # Menü metinlerini güncelle
        menubar = self.master.nametowidget(self.master.cget("menu"))
        menubar.entryconfig(1, label=self.lang_strings['file'])
        menubar.entryconfig(2, label=self.lang_strings['edit'])
        menubar.entryconfig(3, label=self.lang_strings['settings'])
        menubar.entryconfig(4, label=self.lang_strings['help'])

        # Alt menüleri güncelle
        file_menu = menubar.nametowidget(menubar.entrycget(1, "menu"))
        file_menu.entryconfig(0, label=self.lang_strings['new'])
        file_menu.entryconfig(1, label=self.lang_strings['open'])
        file_menu.entryconfig(2, label=self.lang_strings['save'])
        file_menu.entryconfig(3, label=self.lang_strings['save_as'])
        file_menu.entryconfig(5, label=self.lang_strings['exit'])

        edit_menu = menubar.nametowidget(menubar.entrycget(2, "menu"))
        edit_menu.entryconfig(0, label=self.lang_strings['undo'])
        edit_menu.entryconfig(1, label=self.lang_strings['redo'])

        settings_menu = menubar.nametowidget(menubar.entrycget(3, "menu"))
        settings_menu.entryconfig(0, label=self.lang_strings['theme'])
        settings_menu.entryconfig(1, label=self.lang_strings['language'])

        # Tema alt menüsünü güncelle
        theme_menu = menubar.nametowidget(settings_menu.entrycget(0, "menu"))
        theme_menu.entryconfig(0, label=self.lang_strings['light_theme'])
        theme_menu.entryconfig(1, label=self.lang_strings['dark_theme'])

        help_menu = menubar.nametowidget(menubar.entrycget(4, "menu"))
        help_menu.entryconfig(0, label=self.lang_strings['about'])

        # Araç çubuğu butonlarını güncelle
        self.new_button.config(text=self.lang_strings['new'])
        self.open_button.config(text=self.lang_strings['open'])
        self.save_button.config(text=self.lang_strings['save'])

        # Durum çubuğunu güncelle
        self.update_status_bar()

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
