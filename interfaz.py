import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from interfaz_wrapper import ejecutar
from datetime import datetime

class ReporteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Descarga de Reportes 3CX - SONDA")
        self.root.geometry("420x400")
        self.root.resizable(False, False)
        self.root.configure(bg='white')

        self.color_azul = "#004b8d"
        self.fuente = ("Segoe UI", 10)

        self.instancias_vars = {
            "VIP": tk.BooleanVar(),
            "Instancia 1": tk.BooleanVar(),
            "Instancia 2": tk.BooleanVar(),
            "Instancia 3": tk.BooleanVar(),
        }

        self.usar_fechas = tk.BooleanVar()

        self.build_ui()

    def build_ui(self):
        # Contenedor principal
        main_frame = tk.Frame(self.root, bg='white', padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Título
        tk.Label(main_frame, text="Bot Descarga de Reportes 3CX", font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.color_azul).grid(row=0, column=0, columnspan=4, pady=(10, 20))

        # Selección de instancias
        tk.Label(main_frame, text="Seleccione instancias:", font=self.fuente, bg="white").grid(row=1, column=0, sticky="w", columnspan=4)
        for idx, (nombre, var) in enumerate(self.instancias_vars.items()):
            ttk.Checkbutton(main_frame, text=nombre, variable=var).grid(row=2, column=idx, padx=5, pady=5, sticky="w")

        # Checkbox fechas
        ttk.Checkbutton(main_frame, text="Filtrar por fecha", variable=self.usar_fechas,
                        command=self.toggle_fecha).grid(row=3, column=0, columnspan=4, pady=(50,10), sticky="w")

        # Fechas
        tk.Label(main_frame, text="Fecha inicio:", bg="white").grid(row=4, column=0, sticky="e", padx=5)
        self.fecha_inicio_picker = DateEntry(main_frame, date_pattern='mm/dd/yyyy')
        self.fecha_inicio_picker.grid(row=4, column=1, sticky="w", padx=5)

        tk.Label(main_frame, text="Fecha fin:", bg="white").grid(row=4, column=2, sticky="e", padx=5)
        self.fecha_fin_picker = DateEntry(main_frame, date_pattern='mm/dd/yyyy')
        self.fecha_fin_picker.grid(row=4, column=3, sticky="w", padx=5)

        # Botón ejecutar
        self.boton_ejecutar = ttk.Button(main_frame, text="Ejecutar", command=self.ejecutar_proceso)
        self.boton_ejecutar.grid(row=5, column=0, columnspan=4, pady=20)

        # Resultado
        self.resultado_label = tk.Label(main_frame, text="", bg="white", fg="green", font=self.fuente)
        self.resultado_label.grid(row=6, column=0, columnspan=4)

        self.toggle_fecha()

        # Footer
        footer = tk.Label(self.root,
                          text="© 2025 SONDA Colombia · Automatización de procesos",
                          bg="white", fg="gray", font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=10)

    def toggle_fecha(self):
        state = "normal" if self.usar_fechas.get() else "disabled"
        self.fecha_inicio_picker.configure(state=state)
        self.fecha_fin_picker.configure(state=state)

    def ejecutar_proceso(self):
        self.root.config(cursor="watch")
        self.root.update()

        try:
            instancias_seleccionadas = [nombre for nombre, var in self.instancias_vars.items() if var.get()]
            if not instancias_seleccionadas:
                messagebox.showerror("Error", "Seleccione al menos una instancia.")
                return

            fecha_inicio = self.fecha_inicio_picker.get() if self.usar_fechas.get() else None
            fecha_fin = self.fecha_fin_picker.get() if self.usar_fechas.get() else None

            if self.usar_fechas.get():
                try:
                    fi = datetime.strptime(fecha_inicio, "%m/%d/%Y")
                    ff = datetime.strptime(fecha_fin, "%m/%d/%Y")
                    if ff < fi:
                        messagebox.showerror("Error", "La fecha fin no puede ser anterior a la fecha inicio.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha inválido.")
                    return

            estado = ejecutar(instancias_seleccionadas, fecha_inicio, fecha_fin)
            self.resultado_label.config(text="Proceso ejecutado correctamente", fg="green")
        except Exception as e:
            self.resultado_label.config(text=f"Error: {e}", fg="red")
        finally:
            self.root.config(cursor="")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReporteApp(root)
    root.mainloop()
