import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import re

class RegresionLinealApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Regresión Lineal RGB Gamer Style - Ultra Flexible")
        self.root.geometry("900x700")
        self.root.configure(bg='#0f0f0f')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Arial", 12), foreground="lime", background="#1f1f1f", padding=10)
        style.configure("Treeview", background="#1a1a1a", foreground="cyan", fieldbackground="#1a1a1a", rowheight=25, font=("Courier", 10))
        style.map("TButton", background=[('active', '#00ffcc')])

        self.create_widgets()

    def evaluar_expresion(self, expresion, x_val=None):
        try:
            # Reemplazamos ^ por ** para potencias
            expresion = expresion.replace('^', '**')
            contexto_seguro = {
                'e': math.e,
                'pi': math.pi,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'ln': math.log,
                'sqrt': math.sqrt,
                'abs': abs,
                'exp': math.exp,
                '__builtins__': {}
            }
            if x_val is not None:
                contexto_seguro['x'] = x_val
                contexto_seguro['X'] = x_val
            resultado = eval(expresion, contexto_seguro)
            return float(resultado)
        except Exception as e:
            raise ValueError(f"Error al evaluar '{expresion}': {str(e)}")

    def parsear_punto(self, punto_str):
        punto_str = punto_str.strip()
        # Si está en forma (x, y)
        if punto_str.startswith('(') and punto_str.endswith(')'):
            punto_str = punto_str[1:-1]
        # Separar por la primera coma
        if ',' in punto_str:
            partes = punto_str.split(',', 1)
            x_expr = partes[0].strip()
            y_expr = partes[1].strip()
        else:
            # Solo una expresión, la tomamos como y, x será None para asignar luego
            x_expr = None
            y_expr = punto_str.strip()

        if x_expr is None:
            # No hay x dado, asumimos x_val se asigna fuera o 0
            x = None
        else:
            try:
                x = float(x_expr)
            except ValueError:
                x = self.evaluar_expresion(x_expr)

        try:
            # Si x no es None lo pasamos para evaluar y
            y = self.evaluar_expresion(y_expr, x)
        except Exception:
            # Si falla, intentamos sin x
            y = self.evaluar_expresion(y_expr)

        return (x, y)

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Ingresa los puntos (x, y) o expresiones matemáticas:",
                              fg="white", bg="#0f0f0f", font=("Arial", 14))
        self.label.pack(pady=10)

        self.help_label = tk.Label(self.root, 
                                   text="Ejemplos: (2,4), (e^2, 5), (0, e^2-4), sin(pi/2), (1, -1), (0, 0)",
                                   fg="yellow", bg="#0f0f0f", font=("Arial", 10))
        self.help_label.pack(pady=5)

        self.text_entry = tk.Text(self.root, height=5, width=60,
                                  bg="#1a1a1a", fg="white", insertbackground='white')
        self.text_entry.insert(tk.END, "(2,4), e^2, (0, e^2-4), sin(pi/2), (1, -1), (0, 0)")
        self.text_entry.pack(pady=10)

        self.calc_button = ttk.Button(self.root, text="Calcular Recta de Regresión", command=self.calcular_regresion)
        self.calc_button.pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("x", "y", "xy", "x^2"), show="headings")
        for col in ("x", "y", "xy", "x^2"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=20)

        self.resultado_label = tk.Label(self.root, text="", fg="white", bg="#0f0f0f", font=("Arial", 14))
        self.resultado_label.pack()

        self.puntos_label = tk.Label(self.root, text="", fg="cyan", bg="#0f0f0f", font=("Arial", 10), 
                                     wraplength=800)
        self.puntos_label.pack(pady=5)

    def extraer_puntos_del_texto(self, texto):
        puntos = []
        # Extraemos primero los puntos completos (x,y)
        patron_puntos = r'\(([^()]+,[^()]+)\)'
        puntos_con_parentesis = re.findall(patron_puntos, texto)

        # Eliminamos esos puntos del texto original para evitar duplicados
        for p in puntos_con_parentesis:
            puntos.append(f"({p.strip()})")
            texto = texto.replace(f"({p})", '')

        # Ahora extraemos expresiones sueltas (separadas por comas o espacios)
        expresiones_sueltas = [exp.strip() for exp in re.split(r'[,\s]+', texto) if exp.strip()]
        puntos.extend(expresiones_sueltas)

        return puntos

    def calcular_regresion(self):
        try:
            texto = self.text_entry.get("1.0", tk.END).strip()
            if not texto:
                messagebox.showerror("Error", "Por favor ingresa al menos dos puntos o expresiones")
                return

            puntos_str = self.extraer_puntos_del_texto(texto)
            if not puntos_str:
                raise ValueError("No se encontraron puntos o expresiones válidas")

            puntos = []
            puntos_evaluados_str = []
            contador_x = 0

            for punto_str in puntos_str:
                try:
                    # Si el punto no tiene x explícito, le asignamos x incremental
                    x_val = None
                    if punto_str.startswith('(') and ',' in punto_str:
                        x, y = self.parsear_punto(punto_str)
                        if x is None:
                            x = contador_x
                            contador_x += 1
                    else:
                        # Solo y dado
                        y = self.evaluar_expresion(punto_str)
                        x = contador_x
                        contador_x += 1
                    puntos.append((x, y))
                    puntos_evaluados_str.append(f"({x:.3f}, {y:.3f})")
                except Exception as e:
                    messagebox.showerror("Error", f"Error en '{punto_str}': {str(e)}")
                    return

            if len(puntos) < 2:
                messagebox.showerror("Error", "Se necesitan al menos 2 puntos para calcular la regresión")
                return

            self.puntos_label.config(text=f"Puntos evaluados: {', '.join(puntos_evaluados_str)}")

            x_vals = np.array([p[0] for p in puntos])
            y_vals = np.array([p[1] for p in puntos])

            for item in self.tree.get_children():
                self.tree.delete(item)

            xy_vals = x_vals * y_vals
            x2_vals = x_vals ** 2

            for i in range(len(x_vals)):
                self.tree.insert("", "end", values=(
                    f"{x_vals[i]:.4f}", 
                    f"{y_vals[i]:.4f}", 
                    f"{xy_vals[i]:.4f}", 
                    f"{x2_vals[i]:.4f}"
                ))

            n = len(x_vals)
            sum_x = np.sum(x_vals)
            sum_y = np.sum(y_vals)
            sum_xy = np.sum(xy_vals)
            sum_x2 = np.sum(x2_vals)

            denominador = n * sum_x2 - sum_x ** 2
            if abs(denominador) < 1e-10:
                messagebox.showerror("Error", "No se puede calcular la regresión (denominador muy pequeño)")
                return

            m = (n * sum_xy - sum_x * sum_y) / denominador
            b = (sum_y - m * sum_x) / n

            self.resultado_label.config(text=f"Ecuación: Y = {m:.4f}X + {b:.4f}")
            self.mostrar_grafica(x_vals, y_vals, m, b)

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def mostrar_grafica(self, x_vals, y_vals, m, b):
        # Destruye cualquier gráfico previo
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Widget) and hasattr(widget, 'get_tk_widget'):
                widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))

        ax.scatter(x_vals, y_vals, color='cyan', s=50, zorder=5)

        x_min, x_max = min(x_vals), max(x_vals)
        x_range = x_max - x_min
        x_line = np.linspace(x_min - 0.1 * x_range, x_max + 0.1 * x_range, 100)
        y_line = m * x_line + b
        ax.plot(x_line, y_line, color='lime', linestyle='--', linewidth=2)

        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            ax.annotate(f'P{i+1}', (x, y), xytext=(5, 5), textcoords='offset points', color='white', fontsize=8)

        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#0f0f0f')
        ax.set_title('Regresión Lineal Ultra Flexible', color='white', fontsize=12)
        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        ax.grid(True, alpha=0.3, color='gray')

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)


if __name__ == '__main__':
    root = tk.Tk()
    app = RegresionLinealApp(root)
    root.mainloop()
