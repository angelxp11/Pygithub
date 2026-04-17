import tkinter as tk
from tkinter import ttk
from pynput import mouse
import pyperclip
import pyautogui
import threading
import time


class AutoPasteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Pegar Texto")
        self.root.geometry("400x250")
        self.root.attributes('-topmost', True)

        self.running = False
        self.listener = None
        self.click_count = 0
        self.last_click_time = 0  # Para evitar spam

        # UI
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="Cantidad de preguntas:", font=("Arial", 10))\
            .grid(row=0, column=0, sticky="w", pady=5)

        self.questions_input = ttk.Entry(main_frame, width=12)
        self.questions_input.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(main_frame, text="Valor por pregunta:", font=("Arial", 10))\
            .grid(row=1, column=0, sticky="w", pady=5)

        self.value_label = ttk.Label(main_frame, text="-")
        self.value_label.grid(row=1, column=1, sticky="w", pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(button_frame, text="Iniciar", command=self.start_listening)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="DETENER", command=self.stop_listening)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(main_frame, text="Estado: Detenido")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)

        self.click_count_label = ttk.Label(main_frame, text="Clicks: 0")
        self.click_count_label.grid(row=4, column=0, columnspan=2, sticky="w")

    # =========================
    # CONTROL
    # =========================

    def start_listening(self):
        if self.running:
            return

        question_text = self.questions_input.get().strip()
        if not question_text.isdigit() or int(question_text) <= 0:
            self.status_label.config(text="Estado: Error - Ingresa número válido")
            return

        questions = int(question_text)
        value = 50 / questions
        paste_text = str(int(value)) if value.is_integer() else f"{value:.2f}"

        self.value_label.config(text=paste_text)
        self.running = True
        self.click_count = 0
        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: Ejecutándose")

        pyperclip.copy(paste_text)

        self.listener_thread = threading.Thread(
            target=self._listen_for_clicks,
            daemon=True
        )
        self.listener_thread.start()

    def stop_listening(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Estado: Detenido")

        if self.listener:
            self.listener.stop()

    # =========================
    # LISTENER
    # =========================

    def _listen_for_clicks(self):
        def on_click(x, y, button, pressed):
            if not self.running:
                return

            if pressed and button == mouse.Button.left:

                # Anti spam (0.5 segundos)
                if time.time() - self.last_click_time < 0.5:
                    return

                self.last_click_time = time.time()

                self.click_count += 1
                self.root.after(0, self.update_click_label)

                # Ejecutar pegado en otro hilo
                threading.Thread(
                    target=self._do_paste,
                    daemon=True
                ).start()

        with mouse.Listener(on_click=on_click) as listener:
            self.listener = listener
            listener.join()

    # =========================
    # ACCIONES
    # =========================

    def _do_paste(self):
        try:
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('enter')
        except Exception as e:
            print("Error:", e)

    def update_click_label(self):
        self.click_count_label.config(text=f"Clicks: {self.click_count}")


# =========================
# MAIN
# =========================

def main():
    root = tk.Tk()
    app = AutoPasteApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()