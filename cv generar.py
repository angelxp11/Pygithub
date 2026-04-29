"""
Generador de CV Profesional Avanzado
Requiere: pip install reportlab tkcalendar
Características:
- Cargar/guardar JSON para editar después
- Date pickers para períodos
- Botón "Actual" para vigencia
- Sistema de tags para habilidades e idiomas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

W, H = letter
MX = 56
CW = W - 2 * MX

# ─── ENCABEZADOS POR IDIOMA ───────────────────────────────────────────────────

LABELS = {
    "Español": {
        "summary":    "PERFIL PROFESIONAL",
        "experience": "EXPERIENCIA LABORAL",
        "education":  "EDUCACIÓN",
        "skills":     "HABILIDADES",
        "languages":  "IDIOMAS",
    },
    "English": {
        "summary":    "PROFESSIONAL SUMMARY",
        "experience": "WORK EXPERIENCE",
        "education":  "EDUCATION",
        "skills":     "SKILLS",
        "languages":  "LANGUAGES",
    },
}

# ─── UTILIDADES PDF ───────────────────────────────────────────────────────────

def wrap_text(c, text, font, size, max_w):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_section_header(c, y, title):
    c.setLineWidth(1.1)
    c.setStrokeColorRGB(0.08, 0.08, 0.08)
    c.line(MX, y, W - MX, y)
    y -= 14
    c.setFont("Times-Bold", 9.5)
    c.setFillColorRGB(0.08, 0.08, 0.08)
    tw = c.stringWidth(title, "Times-Bold", 9.5)
    c.drawString(W / 2 - tw / 2, y, title)
    y -= 5
    c.line(MX, y, W - MX, y)
    return y - 11


# ─── GENERADOR PDF ────────────────────────────────────────────────────────────

def generate_pdf(data, lang, filepath):
    c = canvas.Canvas(filepath, pagesize=letter)
    lbl = LABELS[lang]
    y = H - 46

    # ── Línea de contacto ──────────────────────────────────────────────────────
    parts = []
    if data["address"]:   parts.append(data["address"])
    if data["city"]:      parts.append(data["city"])
    if data["postal"]:    parts.append(data["postal"])
    if data["email"]:     parts.append(data["email"])
    if data["phone"]:     parts.append(data["phone"])
    contact = "  •  ".join(parts)
    c.setFont("Times-Roman", 8)
    c.setFillColorRGB(0.25, 0.25, 0.25)
    cw = c.stringWidth(contact, "Times-Roman", 8)
    c.drawString(W / 2 - cw / 2, y, contact)
    y -= 18

    # ── Nombre ────────────────────────────────────────────────────────────────
    name = data["name"] or "Nombre Apellido"
    c.setFont("Times-Bold", 23)
    c.setFillColorRGB(0.07, 0.07, 0.07)
    nw = c.stringWidth(name, "Times-Bold", 23)
    c.drawString(W / 2 - nw / 2, y, name)
    y -= 24

    # ── Perfil Profesional ────────────────────────────────────────────────────
    if data["summary"].strip():
        y = draw_section_header(c, y, lbl["summary"])
        lines = wrap_text(c, data["summary"], "Times-Roman", 9.5, CW)
        c.setFont("Times-Roman", 9.5)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        for line in lines:
            c.drawString(MX, y, line)
            y -= 13
        y -= 5

    # ── Experiencia Laboral ───────────────────────────────────────────────────
    jobs = [j for j in data["jobs"] if j["title"].strip() or j["company"].strip()]
    if jobs:
        y = draw_section_header(c, y, lbl["experience"])
        for job in jobs:
            c.setFont("Times-Bold", 10)
            c.setFillColorRGB(0.07, 0.07, 0.07)
            c.drawString(MX, y, job["title"].upper() if job["title"] else "")
            dw = c.stringWidth(job["date"], "Times-Roman", 9)
            c.setFont("Times-Roman", 9)
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.drawString(W - MX - dw, y, job["date"])
            y -= 13
            c.setFont("Times-Italic", 9.5)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.drawString(MX, y, job["company"])
            lw = c.stringWidth(job["location"], "Times-Italic", 9.5)
            c.drawString(W - MX - lw, y, job["location"])
            y -= 12
            if job["desc"].strip():
                desc_lines = wrap_text(c, "• " + job["desc"], "Times-Roman", 9, CW - 12)
                c.setFont("Times-Roman", 9)
                c.setFillColorRGB(0.15, 0.15, 0.15)
                for dl in desc_lines:
                    c.drawString(MX + 6, y, dl)
                    y -= 12
            y -= 5
        y -= 3

    # ── Educación ─────────────────────────────────────────────────────────────
    edu_list = [e for e in data["edu"] if e["title"].strip() or e["institution"].strip()]
    if edu_list:
        y = draw_section_header(c, y, lbl["education"])
        for edu in edu_list:
            c.setFont("Times-Bold", 10)
            c.setFillColorRGB(0.07, 0.07, 0.07)
            c.drawString(MX, y, edu["title"].upper() if edu["title"] else "")
            dw = c.stringWidth(edu["date"], "Times-Roman", 9)
            c.setFont("Times-Roman", 9)
            c.setFillColorRGB(0.3, 0.3, 0.3)
            c.drawString(W - MX - dw, y, edu["date"])
            y -= 13
            c.setFont("Times-BoldItalic", 9.5)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.drawString(MX, y, edu["institution"])
            lw = c.stringWidth(edu["location"], "Times-Italic", 9.5)
            c.setFont("Times-Italic", 9.5)
            c.drawString(W - MX - lw, y, edu["location"])
            y -= 12
            if edu["desc"].strip():
                desc_lines = wrap_text(c, "• " + edu["desc"], "Times-Roman", 9, CW - 12)
                c.setFont("Times-Roman", 9)
                c.setFillColorRGB(0.15, 0.15, 0.15)
                for dl in desc_lines:
                    c.drawString(MX + 6, y, dl)
                    y -= 12
            y -= 6
        y -= 3

    # ── Habilidades (como texto separado por comas) ────────────────────────────
    skills_text = data["skills"]
    if skills_text.strip():
        y = draw_section_header(c, y, lbl["skills"])
        skill_lines = wrap_text(c, skills_text, "Times-Roman", 9.5, CW)
        c.setFont("Times-Roman", 9.5)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        for sl in skill_lines:
            c.drawString(MX, y, sl)
            y -= 13
        y -= 5

    # ── Idiomas (como texto separado por comas) ────────────────────────────────
    languages_text = data["languages"]
    if languages_text.strip():
        y = draw_section_header(c, y, lbl["languages"])
        c.setFont("Times-Italic", 9.5)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        lang_lines = wrap_text(c, languages_text, "Times-Italic", 9.5, CW)
        for ll in lang_lines:
            c.drawString(MX, y, ll)
            y -= 13

    c.save()


# ─── WIDGET PERSONALIZADO: TAG INPUT ──────────────────────────────────────────

class TagInput(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.tags = []
        self.tag_buttons = []
        
        # Frame para los tags
        self.tags_frame = tk.Frame(self, bg=self.cget("bg"))
        self.tags_frame.pack(fill="x", padx=0, pady=4)
        
        # Frame para el input
        input_frame = tk.Frame(self, bg=self.cget("bg"))
        input_frame.pack(fill="x", padx=0, pady=4)
        
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame, 
            textvariable=self.input_var,
            relief="solid", 
            bd=1, 
            font=("Arial", 10)
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.input_entry.bind("<Return>", lambda e: self.add_tag())
        
        self.add_btn = tk.Button(
            input_frame,
            text="+ Agregar",
            command=self.add_tag,
            relief="flat",
            bg="#1A1A2E",
            fg="white",
            font=("Arial", 9),
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.add_btn.pack(side="left")
        
    def add_tag(self):
        tag = self.input_var.get().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.input_var.set("")
            self.refresh_display()
    
    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.refresh_display()
    
    def refresh_display(self):
        for btn in self.tag_buttons:
            btn.destroy()
        self.tag_buttons = []
        
        for tag in self.tags:
            tag_btn = tk.Button(
                self.tags_frame,
                text=f"{tag} ✕",
                command=lambda t=tag: self.remove_tag(t),
                relief="solid",
                bd=1,
                bg="#E8E4DD",
                fg="#1A1A2E",
                font=("Arial", 9),
                padx=8,
                pady=2,
                cursor="hand2"
            )
            tag_btn.pack(side="left", padx=2, pady=2)
            self.tag_buttons.append(tag_btn)
    
    def set_tags(self, tags_list):
        self.tags = tags_list.copy() if tags_list else []
        self.refresh_display()
    
    def get_tags(self):
        return self.tags.copy()
    
    def get_text(self):
        """Retorna los tags como texto separado por comas"""
        return ", ".join(self.tags)


# ─── WIDGET PERSONALIZADO: PERIOD INPUT CON CALENDARIO ───────────────────────

class PeriodInput(tk.Frame):
    def __init__(self, parent, label_text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.start_date = None
        self.end_date = None
        self.is_current = False
        
        # Label
        if label_text:
            tk.Label(self, text=label_text, bg=self.cget("bg"), fg="#444444", 
                    font=("Arial", 9)).pack(anchor="w", padx=0, pady=(4, 2))
        
        # Frame de fechas
        dates_frame = tk.Frame(self, bg=self.cget("bg"))
        dates_frame.pack(fill="x", padx=0, pady=4)
        
        # Fecha inicio
        tk.Label(dates_frame, text="Inicio:", bg=self.cget("bg"), fg="#444444",
                font=("Arial", 8)).pack(side="left", padx=(0, 4))
        
        self.start_entry = DateEntry(dates_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, 
                                     font=("Arial", 9))
        self.start_entry.pack(side="left", padx=(0, 12))
        
        # Fecha fin
        tk.Label(dates_frame, text="Fin:", bg=self.cget("bg"), fg="#444444",
                font=("Arial", 8)).pack(side="left", padx=(0, 4))
        
        self.end_entry = DateEntry(dates_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   font=("Arial", 9))
        self.end_entry.pack(side="left", padx=(0, 12))
        
        # Botón "Actual"
        self.current_var = tk.BooleanVar(value=False)
        self.current_btn = tk.Checkbutton(
            dates_frame,
            text="Actual",
            variable=self.current_var,
            command=self.toggle_current,
            bg=self.cget("bg"),
            fg="#1A1A2E",
            font=("Arial", 9),
            cursor="hand2"
        )
        self.current_btn.pack(side="left")
        
    def toggle_current(self):
        self.is_current = self.current_var.get()
        self.end_entry.config(state="disabled" if self.is_current else "normal")
    
    def set_dates(self, start_str, end_str, is_current=False):
        """Establece fechas desde strings en formato YYYY-MM-DD"""
        try:
            if start_str:
                self.start_entry.set_date(datetime.strptime(start_str, "%Y-%m-%d").date())
            if end_str and not is_current:
                self.end_entry.set_date(datetime.strptime(end_str, "%Y-%m-%d").date())
            self.current_var.set(is_current)
            self.toggle_current()
        except:
            pass
    
    def get_period_text(self):
        """Retorna el período en formato legible"""
        start = self.start_entry.get_date().strftime("%b %Y")
        if self.is_current:
            return f"{start} — Present"
        else:
            end = self.end_entry.get_date().strftime("%b %Y")
            return f"{start} — {end}"
    
    def get_data(self):
        """Retorna los datos para guardar en JSON"""
        return {
            "start": self.start_entry.get_date().strftime("%Y-%m-%d"),
            "end": self.end_entry.get_date().strftime("%Y-%m-%d") if not self.is_current else "",
            "is_current": self.is_current
        }


# ─── INTERFAZ GRÁFICA PRINCIPAL ────────────────────────────────────────────────

class CVApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de CV Profesional")
        self.resizable(True, True)
        self.configure(bg="#F0EDE8")
        self.geometry("920x880")

        self.jobs_frames = []
        self.edu_frames = []
        self.current_file = None

        self._build_ui()
        self._load_defaults()

    # ── Colores y estilos ─────────────────────────────────────────────────────

    BG       = "#F0EDE8"
    PANEL    = "#FFFFFF"
    ACCENT   = "#1A1A2E"
    BTN_BG   = "#1A1A2E"
    BTN_FG   = "#FFFFFF"
    LABEL_FG = "#444444"
    ENTRY_BG = "#FAFAFA"
    BORDER   = "#CCCCCC"
    SEC_BG   = "#F7F5F2"

    # ── Construcción UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Título superior
        header = tk.Frame(self, bg=self.ACCENT, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.ACCENT)
        title_frame.pack(expand=True, fill="both", padx=20)
        
        tk.Label(title_frame, text="✦  Generador de CV Profesional  ✦",
                 bg=self.ACCENT, fg="#FFFFFF",
                 font=("Georgia", 15, "bold")).pack(side="left", expand=True)
        
        # Botones de carga
        tk.Button(title_frame, text="� Cargar PDF", command=self._load_pdf,
                 bg="#2196F3", fg="white", relief="flat", font=("Arial", 9),
                 padx=10, pady=4, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(title_frame, text="�📂 Cargar JSON", command=self._load_json,
                 bg="#4CAF50", fg="white", relief="flat", font=("Arial", 9),
                 padx=10, pady=4, cursor="hand2").pack(side="left", padx=5)

        # Contenedor principal con scroll
        outer = tk.Frame(self, bg=self.BG)
        outer.pack(fill="both", expand=True)

        canvas_scroll = tk.Canvas(outer, bg=self.BG, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas_scroll.yview)
        canvas_scroll.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        self.scroll_frame = tk.Frame(canvas_scroll, bg=self.BG)
        win_id = canvas_scroll.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def _on_configure(e):
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
            canvas_scroll.itemconfig(win_id, width=canvas_scroll.winfo_width())

        self.scroll_frame.bind("<Configure>", _on_configure)
        canvas_scroll.bind("<Configure>", lambda e: canvas_scroll.itemconfig(win_id, width=e.width))

        def _on_mousewheel(e):
            canvas_scroll.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel)

        # ── SECCIÓN: Información Personal ────────────────────────────────────
        self._section_title("👤  Información Personal")

        row1 = self._row()
        self.address = self._field(row1, "Dirección", width=34)
        self.city    = self._field(row1, "Ciudad", width=20)
        self.postal  = self._field(row1, "Código Postal", width=12)

        row2 = self._row()
        self.email = self._field(row2, "Correo Electrónico", width=34)
        self.phone = self._field(row2, "Teléfono", width=20)

        row3 = self._row()
        self.name  = self._field(row3, "Nombre Completo", width=54)

        # ── SECCIÓN: Perfil Profesional ───────────────────────────────────────
        self._section_title("📋  Perfil Profesional")
        self.summary = self._textarea(lines=4)

        # ── SECCIÓN: Experiencia Laboral ──────────────────────────────────────
        self._section_title("💼  Experiencia Laboral")
        self.jobs_container = tk.Frame(self.scroll_frame, bg=self.BG)
        self.jobs_container.pack(fill="x", padx=18, pady=2)
        self._add_job()
        tk.Button(self.scroll_frame, text="+ Agregar experiencia",
                  command=self._add_job,
                  bg="#E8E4DD", fg=self.ACCENT, relief="flat",
                  font=("Arial", 9), padx=10, pady=4,
                  cursor="hand2").pack(anchor="w", padx=18, pady=(0, 8))

        # ── SECCIÓN: Educación ────────────────────────────────────────────────
        self._section_title("🎓  Educación")
        self.edu_container = tk.Frame(self.scroll_frame, bg=self.BG)
        self.edu_container.pack(fill="x", padx=18, pady=2)
        self._add_edu()
        tk.Button(self.scroll_frame, text="+ Agregar educación",
                  command=self._add_edu,
                  bg="#E8E4DD", fg=self.ACCENT, relief="flat",
                  font=("Arial", 9), padx=10, pady=4,
                  cursor="hand2").pack(anchor="w", padx=18, pady=(0, 8))

        # ── SECCIÓN: Habilidades (Tags) ───────────────────────────────────────
        self._section_title("⚡  Habilidades")
        self.skills = TagInput(self.scroll_frame, bg=self.BG)
        self.skills.pack(fill="x", padx=18, pady=4)

        # ── SECCIÓN: Idiomas (Tags) ───────────────────────────────────────────
        self._section_title("🌍  Idiomas")
        self.languages = TagInput(self.scroll_frame, bg=self.BG)
        self.languages.pack(fill="x", padx=18, pady=4)

        # ── BOTÓN GENERAR PDF ─────────────────────────────────────────────────
        btn_frame = tk.Frame(self.scroll_frame, bg=self.BG)
        btn_frame.pack(fill="x", padx=18, pady=18)

        tk.Label(btn_frame, text="Idioma del CV:",
                 bg=self.BG, fg=self.LABEL_FG,
                 font=("Arial", 10, "bold")).pack(side="left", padx=(0, 8))

        self.lang_var = tk.StringVar(value="Español")
        for lang in ("Español", "English"):
            tk.Radiobutton(btn_frame, text=lang, variable=self.lang_var,
                           value=lang, bg=self.BG, fg=self.LABEL_FG,
                           activebackground=self.BG,
                           font=("Arial", 10)).pack(side="left", padx=6)

        tk.Button(btn_frame, text="  📄  Generar PDF + JSON  ",
                  command=self._on_generate,
                  bg=self.BTN_BG, fg=self.BTN_FG,
                  font=("Arial", 11, "bold"),
                  relief="flat", padx=16, pady=8,
                  cursor="hand2").pack(side="right")

        tk.Frame(self.scroll_frame, bg=self.BG, height=30).pack()

    # ── Helpers de widgets ────────────────────────────────────────────────────

    def _section_title(self, text):
        fr = tk.Frame(self.scroll_frame, bg=self.SEC_BG,
                      highlightbackground=self.BORDER,
                      highlightthickness=1)
        fr.pack(fill="x", padx=18, pady=(14, 4))
        tk.Label(fr, text=text, bg=self.SEC_BG, fg=self.ACCENT,
                 font=("Arial", 10, "bold"),
                 padx=12, pady=6).pack(anchor="w")

    def _row(self):
        fr = tk.Frame(self.scroll_frame, bg=self.BG)
        fr.pack(fill="x", padx=18, pady=2)
        return fr

    def _field(self, parent, label, width=28, entry_var=None):
        fr = tk.Frame(parent, bg=self.BG)
        fr.pack(side="left", padx=(0, 12), pady=2)
        tk.Label(fr, text=label, bg=self.BG, fg=self.LABEL_FG,
                 font=("Arial", 9)).pack(anchor="w")
        var = entry_var or tk.StringVar()
        ent = tk.Entry(fr, textvariable=var, width=width,
                       bg=self.ENTRY_BG, fg="#111111",
                       relief="solid", bd=1, font=("Arial", 10))
        ent.pack()
        return var

    def _textarea(self, lines=3):
        fr = tk.Frame(self.scroll_frame, bg=self.BG)
        fr.pack(fill="x", padx=18, pady=4)
        txt = tk.Text(fr, height=lines, wrap="word",
                      bg=self.ENTRY_BG, fg="#111111",
                      relief="solid", bd=1,
                      font=("Arial", 10), padx=6, pady=4)
        txt.pack(fill="x")
        return txt

    def _block_frame(self, container):
        fr = tk.Frame(container, bg=self.PANEL,
                      highlightbackground=self.BORDER,
                      highlightthickness=1)
        fr.pack(fill="x", pady=4)
        return fr

    def _get_text(self, widget):
        return widget.get("1.0", "end").strip()

    # ── Bloques dinámicos: Empleo ─────────────────────────────────────────────

    def _add_job(self):
        fr = self._block_frame(self.jobs_container)
        inner = tk.Frame(fr, bg=self.PANEL, padx=10, pady=8)
        inner.pack(fill="x")

        row1 = tk.Frame(inner, bg=self.PANEL); row1.pack(fill="x", pady=2)
        row2 = tk.Frame(inner, bg=self.PANEL); row2.pack(fill="x", pady=2)
        row3 = tk.Frame(inner, bg=self.PANEL); row3.pack(fill="x", pady=2)

        title    = self._field(row1, "Cargo", width=28)
        company  = self._field(row1, "Empresa", width=22)
        location = self._field(row1, "Ciudad", width=16)
        
        # Período con calendario
        period = PeriodInput(row2, "Período", bg=self.PANEL)
        period.pack(fill="x")

        tk.Label(row3, text="Descripción", bg=self.PANEL,
                 fg=self.LABEL_FG, font=("Arial", 9)).pack(anchor="w")
        desc_txt = tk.Text(row3, height=2, wrap="word",
                           bg=self.ENTRY_BG, fg="#111111",
                           relief="solid", bd=1,
                           font=("Arial", 10), padx=6, pady=4)
        desc_txt.pack(fill="x")

        def remove():
            fr.destroy()
            self.jobs_frames = [j for j in self.jobs_frames if j["frame"].winfo_exists()]

        tk.Button(inner, text="✕ Eliminar", command=remove,
                  bg=self.PANEL, fg="#AA3333", relief="flat",
                  font=("Arial", 8), cursor="hand2").pack(anchor="e")

        self.jobs_frames.append({
            "frame": fr, "title": title, "company": company,
            "location": location, "period": period, "desc": desc_txt
        })

    # ── Bloques dinámicos: Educación ──────────────────────────────────────────

    def _add_edu(self):
        fr = self._block_frame(self.edu_container)
        inner = tk.Frame(fr, bg=self.PANEL, padx=10, pady=8)
        inner.pack(fill="x")

        row1 = tk.Frame(inner, bg=self.PANEL); row1.pack(fill="x", pady=2)
        row2 = tk.Frame(inner, bg=self.PANEL); row2.pack(fill="x", pady=2)
        row3 = tk.Frame(inner, bg=self.PANEL); row3.pack(fill="x", pady=2)

        title       = self._field(row1, "Título / Programa", width=28)
        institution = self._field(row1, "Institución", width=28)
        location    = self._field(row2, "Ciudad", width=16)
        
        # Período con calendario
        period = PeriodInput(row2, "Período", bg=self.PANEL)
        period.pack(fill="x")

        tk.Label(row3, text="Descripción (opcional)", bg=self.PANEL,
                 fg=self.LABEL_FG, font=("Arial", 9)).pack(anchor="w")
        desc_txt = tk.Text(row3, height=2, wrap="word",
                           bg=self.ENTRY_BG, fg="#111111",
                           relief="solid", bd=1,
                           font=("Arial", 10), padx=6, pady=4)
        desc_txt.pack(fill="x")

        def remove():
            fr.destroy()
            self.edu_frames = [e for e in self.edu_frames if e["frame"].winfo_exists()]

        tk.Button(inner, text="✕ Eliminar", command=remove,
                  bg=self.PANEL, fg="#AA3333", relief="flat",
                  font=("Arial", 8), cursor="hand2").pack(anchor="e")

        self.edu_frames.append({
            "frame": fr, "title": title, "institution": institution,
            "location": location, "period": period, "desc": desc_txt
        })

    # ── Cargar desde PDF ──────────────────────────────────────────────────────

    def _load_pdf(self):
        """Carga un CV desde un PDF. Busca automáticamente el JSON asociado."""
        filepath = filedialog.askopenfilename(
            filetypes=[("PDF", "*.pdf")],
            title="Seleccionar CV en PDF"
        )
        if not filepath:
            return
        
        # Buscar el JSON asociado
        json_filepath = filepath.replace(".pdf", ".json")
        
        if not os.path.exists(json_filepath):
            # Si no existe JSON, preguntar si crear uno
            resultado = messagebox.askyesno(
                "Archivo JSON no encontrado",
                f"No se encontró el archivo de datos:\n{os.path.basename(json_filepath)}\n\n"
                f"¿Deseas crear un nuevo JSON asociado?\n"
                f"(Se rellenará con los datos por defecto)\n\n"
                f"Podrás editar toda la información."
            )
            if not resultado:
                return
            
            # Crear un JSON con datos por defecto
            data = {
                "address": "",
                "city": "",
                "postal": "",
                "email": "",
                "phone": "",
                "name": "Nombre del Profesional",
                "summary": "",
                "skills": [],
                "languages": [],
                "jobs": [],
                "edu": []
            }
        else:
            try:
                with open(json_filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudo leer el JSON:\n{ex}")
                return
        
        try:
            # Limpiar trabajos y educación existentes
            for j in self.jobs_frames[:]:
                if j["frame"].winfo_exists():
                    j["frame"].destroy()
            self.jobs_frames = []
            
            for e in self.edu_frames[:]:
                if e["frame"].winfo_exists():
                    e["frame"].destroy()
            self.edu_frames = []
            
            # Cargar datos personales
            self.address.set(data.get("address", ""))
            self.city.set(data.get("city", ""))
            self.postal.set(data.get("postal", ""))
            self.email.set(data.get("email", ""))
            self.phone.set(data.get("phone", ""))
            self.name.set(data.get("name", ""))
            
            self.summary.delete("1.0", "end")
            self.summary.insert("1.0", data.get("summary", ""))
            
            # Cargar trabajos
            jobs_data = data.get("jobs", [])
            if jobs_data:
                for job_data in jobs_data:
                    self._add_job()
                    j = self.jobs_frames[-1]
                    j["title"].set(job_data.get("title", ""))
                    j["company"].set(job_data.get("company", ""))
                    j["location"].set(job_data.get("location", ""))
                    j["period"].set_dates(
                        job_data.get("period", {}).get("start", ""),
                        job_data.get("period", {}).get("end", ""),
                        job_data.get("period", {}).get("is_current", False)
                    )
                    j["desc"].delete("1.0", "end")
                    j["desc"].insert("1.0", job_data.get("desc", ""))
            
            # Cargar educación
            edu_data = data.get("edu", [])
            if edu_data:
                for edu_item in edu_data:
                    self._add_edu()
                    e = self.edu_frames[-1]
                    e["title"].set(edu_item.get("title", ""))
                    e["institution"].set(edu_item.get("institution", ""))
                    e["location"].set(edu_item.get("location", ""))
                    e["period"].set_dates(
                        edu_item.get("period", {}).get("start", ""),
                        edu_item.get("period", {}).get("end", ""),
                        edu_item.get("period", {}).get("is_current", False)
                    )
                    e["desc"].delete("1.0", "end")
                    e["desc"].insert("1.0", edu_item.get("desc", ""))
            
            # Cargar habilidades
            skills_list = data.get("skills", [])
            self.skills.set_tags(skills_list)
            
            # Cargar idiomas
            languages_list = data.get("languages", [])
            self.languages.set_tags(languages_list)
            
            self.current_file = filepath
            
            # Si se creó un nuevo JSON, guardarlo
            if not os.path.exists(json_filepath):
                try:
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except:
                    pass
            
            messagebox.showinfo("¡Listo!", 
                f"CV cargado exitosamente desde:\n{os.path.basename(filepath)}\n\n"
                f"Ahora puedes editar la información.")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{ex}")

    # ── Cargar JSON ───────────────────────────────────────────────────────────

    def _load_json(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")],
            title="Cargar datos del CV"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Limpiar trabajos y educación existentes
            for j in self.jobs_frames[:]:
                if j["frame"].winfo_exists():
                    j["frame"].destroy()
            self.jobs_frames = []
            
            for e in self.edu_frames[:]:
                if e["frame"].winfo_exists():
                    e["frame"].destroy()
            self.edu_frames = []
            
            # Cargar datos personales
            self.address.set(data.get("address", ""))
            self.city.set(data.get("city", ""))
            self.postal.set(data.get("postal", ""))
            self.email.set(data.get("email", ""))
            self.phone.set(data.get("phone", ""))
            self.name.set(data.get("name", ""))
            
            self.summary.delete("1.0", "end")
            self.summary.insert("1.0", data.get("summary", ""))
            
            # Cargar trabajos
            for job_data in data.get("jobs", []):
                self._add_job()
                j = self.jobs_frames[-1]
                j["title"].set(job_data.get("title", ""))
                j["company"].set(job_data.get("company", ""))
                j["location"].set(job_data.get("location", ""))
                j["period"].set_dates(
                    job_data.get("period", {}).get("start", ""),
                    job_data.get("period", {}).get("end", ""),
                    job_data.get("period", {}).get("is_current", False)
                )
                j["desc"].delete("1.0", "end")
                j["desc"].insert("1.0", job_data.get("desc", ""))
            
            # Cargar educación
            for edu_data in data.get("edu", []):
                self._add_edu()
                e = self.edu_frames[-1]
                e["title"].set(edu_data.get("title", ""))
                e["institution"].set(edu_data.get("institution", ""))
                e["location"].set(edu_data.get("location", ""))
                e["period"].set_dates(
                    edu_data.get("period", {}).get("start", ""),
                    edu_data.get("period", {}).get("end", ""),
                    edu_data.get("period", {}).get("is_current", False)
                )
                e["desc"].delete("1.0", "end")
                e["desc"].insert("1.0", edu_data.get("desc", ""))
            
            # Cargar habilidades
            skills_list = data.get("skills", [])
            self.skills.set_tags(skills_list)
            
            # Cargar idiomas
            languages_list = data.get("languages", [])
            self.languages.set_tags(languages_list)
            
            self.current_file = filepath
            messagebox.showinfo("¡Listo!", "Datos cargados correctamente.")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{ex}")

    # ── Datos por defecto ─────────────────────────────────────────────────────

    def _load_defaults(self):
        self.address.set("CALLE 61A #2W-25")
        self.city.set("BUCARAMANGA")
        self.postal.set("680005")
        self.email.set("SANCHEZDEANYELA@GMAIL.COM")
        self.phone.set("+57 3160901958")
        self.name.set("Deanyela Michelle Sanchez Choperena")

        self.summary.insert("1.0",
            "Estudiante de Administración de Empresas con experiencia en atención al cliente "
            "y manejo de caja en entornos comerciales como restaurante y heladería. He gestionado "
            "transacciones en sistemas POS, realizado cierres de caja y arqueos con precisión, "
            "además de brindar servicio directo al cliente con enfoque en eficiencia, orden y buena "
            "comunicación. Me caracterizo por ser responsable, organizada y con disposición para "
            "aprender y adaptarme a diferentes entornos laborales.")

        if self.jobs_frames:
            j = self.jobs_frames[0]
            j["title"].set("OPERADORA DE CAJA")
            j["company"].set("Churritos")
            j["location"].set("Bucaramanga")
            j["period"].set_dates("2025-10-01", "", is_current=True)
            j["desc"].insert("1.0",
                "Gestioné el manejo de caja y transacciones en sistema POS, "
                "realizando arqueos y garantizando precisión y eficiencia.")

        if self.edu_frames:
            e = self.edu_frames[0]
            e["title"].set("ADMINISTRACIÓN DE EMPRESAS")
            e["institution"].set("UNIVERSIDAD DE INVESTIGACION Y DESARROLLO - UDI")
            e["location"].set("Bucaramanga")
            e["period"].set_dates("2025-02-01", "", is_current=True)
            e["desc"].insert("1.0",
                "Estudiante actual con formación en gestión organizacional, "
                "finanzas y procesos administrativos.")

        self.skills.set_tags([
            "Atención al cliente",
            "Manejo de caja",
            "Multitarea",
            "Memoria activa",
            "Rapidez",
            "Empatía",
            "Comunicación verbal"
        ])
        
        self.languages.set_tags([
            "Español (Nativo)",
            "Inglés (A1 – Elemental)"
        ])

    # ── Recolectar datos y generar ────────────────────────────────────────────

    def _on_generate(self):
        if not self.name.get().strip():
            messagebox.showwarning("Campo vacío", "Por favor ingresa el nombre completo.")
            return

        # Recolectar datos
        data = {
            "address":   self.address.get().strip(),
            "city":      self.city.get().strip(),
            "postal":    self.postal.get().strip(),
            "email":     self.email.get().strip(),
            "phone":     self.phone.get().strip(),
            "name":      self.name.get().strip(),
            "summary":   self._get_text(self.summary),
            "skills":    self.skills.get_tags(),
            "languages": self.languages.get_tags(),
            "jobs": [
                {
                    "title":    j["title"].get().strip(),
                    "company":  j["company"].get().strip(),
                    "location": j["location"].get().strip(),
                    "date":     j["period"].get_period_text(),
                    "desc":     self._get_text(j["desc"]),
                    "period":   j["period"].get_data(),
                }
                for j in self.jobs_frames
                if j["frame"].winfo_exists()
            ],
            "edu": [
                {
                    "title":       e["title"].get().strip(),
                    "institution": e["institution"].get().strip(),
                    "location":    e["location"].get().strip(),
                    "date":        e["period"].get_period_text(),
                    "desc":        self._get_text(e["desc"]),
                    "period":      e["period"].get_data(),
                }
                for e in self.edu_frames
                if e["frame"].winfo_exists()
            ],
        }

        lang = self.lang_var.get()
        safe_name = data["name"].replace(" ", "_") or "CV"
        default_file = f"CV_{safe_name}.pdf"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_file,
            filetypes=[("PDF", "*.pdf")],
            title="Guardar CV como..."
        )
        if not filepath:
            return

        try:
            # Generar PDF
            pdf_data = data.copy()
            pdf_data["skills"] = ", ".join(data["skills"])
            pdf_data["languages"] = ", ".join(data["languages"])
            generate_pdf(pdf_data, lang, filepath)
            
            # Guardar JSON con el mismo nombre
            json_filepath = filepath.replace(".pdf", ".json")
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("¡Listo!", 
                f"CV generado exitosamente:\n{filepath}\n\nDatos guardados:\n{json_filepath}")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo generar el CV:\n{ex}")


# ─── PUNTO DE ENTRADA ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CVApp()
    app.mainloop()
