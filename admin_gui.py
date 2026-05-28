
import customtkinter as ctk
import mysql.connector
import telebot
from tkinter import messagebox, filedialog
import threading

# ==========================================
# 🎨 CONFIGURACIÓN VISUAL Y TEMA
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdminDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Terminal Admin | Plataforma de Ventas")
        self.geometry("750x700")
        self.resizable(True, True)

        # ==========================================
        # ⚙️ CONFIGURACIÓN
        # ==========================================
        self.TOKEN = 'TU_TOKEN_AQUI'

        self.bot = telebot.TeleBot(self.TOKEN)

        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'bot_user',
            'password': 'aldo1324',
            'database': 'bot_telegram'
        }

        self.construir_interfaz()
        self.actualizar_todo()

    # ==========================================
    # 🔌 CONEXIÓN MYSQL
    # ==========================================
    def conectar_db(self):
        return mysql.connector.connect(**self.DB_CONFIG)

    # ==========================================
    # 🏗️ INTERFAZ
    # ==========================================
    def construir_interfaz(self):

        ctk.CTkLabel(
            self,
            text="🛡️ PANEL DE CONTROL CENTRAL",
            font=("Roboto", 24, "bold")
        ).pack(pady=(15, 5))

        self.tabs = ctk.CTkTabview(
            self,
            width=700,
            height=480
        )

        self.tabs.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

        self.tabs.add("📦 Inventario y Stock")
        self.tabs.add("🔑 Llaves de Acceso")
        self.tabs.add("👥 Clientes")
        self.tabs.add("💰 Créditos y Precio")
        self.tabs.add("📢 Difusión Masiva")

        self.construir_tab_combos()
        self.construir_tab_keys()
        self.construir_tab_usuarios()
        self.construir_tab_creditos()
        self.construir_tab_broadcast()

        ctk.CTkButton(
            self,
            text="🔄 SINCRONIZAR BASE DE DATOS",
            command=self.actualizar_todo,
            fg_color="#333333",
            hover_color="#1a1a1a",
            height=45,
            font=("Arial", 14, "bold")
        ).pack(pady=15, fill="x", padx=20)

    # ==========================================
    # 📦 TAB INVENTARIO
    # ==========================================
    def construir_tab_combos(self):

        tab = self.tabs.tab("📦 Inventario y Stock")

        ctk.CTkLabel(
            tab,
            text="Monitor de Cuentas en Tiempo Real",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.lista_servicios = ctk.CTkTextbox(
            tab,
            state="disabled",
            fg_color="#0a0a0a",
            text_color="#00FF00",
            font=("Consolas", 14)
        )

        self.lista_servicios.pack(
            pady=10,
            padx=20,
            fill="both",
            expand=True
        )

        caja_carga = ctk.CTkFrame(tab, fg_color="transparent")
        caja_carga.pack(pady=10, fill="x", padx=20)

        self.input_nom_servicio = ctk.CTkEntry(
            caja_carga,
            placeholder_text="Nombre del servicio",
            width=250
        )

        self.input_nom_servicio.pack(
            side="left",
            padx=(0, 10),
            expand=True,
            fill="x"
        )

        ctk.CTkButton(
            caja_carga,
            text="📂 Subir Archivo .txt",
            fg_color="#CD7F32",
            hover_color="#A0522D",
            command=self.cargar_archivo_combos
        ).pack(side="right")

    # ==========================================
    # 🔑 TAB KEYS
    # ==========================================
    def construir_tab_keys(self):

        tab = self.tabs.tab("🔑 Llaves de Acceso")

        ctk.CTkLabel(
            tab,
            text="Generador de Tokens",
            font=("Arial", 16, "bold")
        ).pack(pady=5)

        caja_input = ctk.CTkFrame(tab, fg_color="transparent")
        caja_input.pack(pady=5, fill="x", padx=20)

        self.input_nueva_key = ctk.CTkEntry(
            caja_input,
            placeholder_text="Nueva key...",
            width=250
        )

        self.input_nueva_key.pack(
            side="left",
            padx=(0, 10),
            expand=True,
            fill="x"
        )

        ctk.CTkButton(
            caja_input,
            text="➕ Agregar Key",
            command=self.agregar_key,
            fg_color="#228B22",
            hover_color="#006400",
            width=120
        ).pack(side="right")

        self.panel_llaves = ctk.CTkScrollableFrame(
            tab,
            fg_color="#0a0a0a"
        )

        self.panel_llaves.pack(
            pady=10,
            padx=20,
            fill="both",
            expand=True
        )

    # ==========================================
    # 👥 TAB USUARIOS
    # ==========================================
    def construir_tab_usuarios(self):

        tab = self.tabs.tab("👥 Clientes")

        ctk.CTkLabel(
            tab,
            text="Usuarios Registrados",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.lista_usuarios = ctk.CTkTextbox(
            tab,
            state="disabled",
            fg_color="#0a0a0a",
            text_color="#00FF00",
            font=("Consolas", 14)
        )

        self.lista_usuarios.pack(
            pady=10,
            padx=20,
            fill="both",
            expand=True
        )

    # ==========================================
    # 💰 TAB CRÉDITOS
    # ==========================================
    def construir_tab_creditos(self):

        tab = self.tabs.tab("💰 Créditos y Precio")

        frame_precio = ctk.CTkFrame(tab)
        frame_precio.pack(pady=10, padx=20, fill="x")

        self.lbl_precio_actual = ctk.CTkLabel(
            frame_precio,
            text="Precio actual: Cargando..."
        )

        self.lbl_precio_actual.pack(pady=5)

        caja_precio = ctk.CTkFrame(
            frame_precio,
            fg_color="transparent"
        )

        caja_precio.pack(pady=5)

        self.input_nuevo_precio = ctk.CTkEntry(
            caja_precio,
            placeholder_text="Nuevo precio",
            width=120
        )

        self.input_nuevo_precio.pack(side="left", padx=5)

        ctk.CTkButton(
            caja_precio,
            text="💾 Guardar Precio",
            command=self.guardar_precio
        ).pack(side="left", padx=5)

        frame_carga = ctk.CTkFrame(tab, fg_color="transparent")
        frame_carga.pack(pady=15, fill="x", padx=20)

        self.input_user_id = ctk.CTkEntry(
            frame_carga,
            placeholder_text="ID Usuario",
            width=250
        )

        self.input_user_id.pack(
            side="left",
            padx=(0, 5),
            expand=True,
            fill="x"
        )

        self.input_monto = ctk.CTkEntry(
            frame_carga,
            placeholder_text="Monto",
            width=100
        )

        self.input_monto.pack(side="left", padx=5)

        ctk.CTkButton(
            frame_carga,
            text="➕ Cargar Saldo",
            command=self.cargar_creditos,
            fg_color="#228B22",
            hover_color="#006400",
            width=120
        ).pack(side="right")

    # ==========================================
    # 📢 TAB BROADCAST
    # ==========================================
    def construir_tab_broadcast(self):

        tab = self.tabs.tab("📢 Difusión Masiva")

        self.caja_texto_msg = ctk.CTkTextbox(
            tab,
            height=150,
            font=("Arial", 14)
        )

        self.caja_texto_msg.pack(
            pady=10,
            padx=20,
            fill="both",
            expand=True
        )

        ctk.CTkButton(
            tab,
            text="🚀 TRANSMITIR",
            command=self.iniciar_broadcast_hilo,
            fg_color="#1f538d",
            hover_color="#14375e",
            height=45
        ).pack(pady=20, padx=20, fill="x")

    # ==========================================
    # 🔄 ACTUALIZAR
    # ==========================================
    def actualizar_todo(self):
        self.actualizar_lista_servicios()
        self.actualizar_lista_keys()
        self.actualizar_lista_usuarios()

    # ==========================================
    # 📦 SERVICIOS
    # ==========================================
    def actualizar_lista_servicios(self):

        self.lista_servicios.configure(state="normal")
        self.lista_servicios.delete("0.0", "end")

        try:

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT servicio,
                COUNT(CASE WHEN estado='disponible' THEN 1 END)
                FROM combos
                GROUP BY servicio
            """)

            resultados = cursor.fetchall()

            if resultados:

                for serv, stock in resultados:

                    self.lista_servicios.insert(
                        "end",
                        f"/{serv} | Stock: {stock}\n"
                    )

            else:

                self.lista_servicios.insert(
                    "end",
                    "No hay servicios registrados.\n"
                )

        except Exception as e:
            print(e)

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

        self.lista_servicios.configure(state="disabled")

    # ==========================================
    # 📂 CARGAR COMBOS
    # ==========================================
    def cargar_archivo_combos(self):

        servicio = self.input_nom_servicio.get().strip().lower()

        if not servicio:
            messagebox.showwarning(
                "Error",
                "Escribe el nombre del servicio."
            )
            return

        ruta_archivo = filedialog.askopenfilename(
            filetypes=[("Archivos TXT", "*.txt")]
        )

        if not ruta_archivo:
            return

        try:

            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                lineas = [x.strip() for x in f if x.strip()]

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            sql = """
                INSERT INTO combos (servicio, cuenta)
                VALUES (%s, %s)
            """

            datos = [(servicio, l) for l in lineas]

            cursor.executemany(sql, datos)

            conexion.commit()

            messagebox.showinfo(
                "Éxito",
                f"{len(lineas)} cuentas cargadas."
            )

            self.actualizar_lista_servicios()

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    # ==========================================
    # 🔑 AGREGAR KEYS
    # ==========================================
    def agregar_key(self):

        nueva_key = self.input_nueva_key.get().strip()

        if not nueva_key:
            return

        try:

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute(
                "INSERT INTO claves_acceso (clave) VALUES (%s)",
                (nueva_key,)
            )

            conexion.commit()

            self.input_nueva_key.delete(0, 'end')

            self.actualizar_lista_keys()

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    # ==========================================
    # 🔑 MOSTRAR KEYS
    # ==========================================
    def actualizar_lista_keys(self):

        for widget in self.panel_llaves.winfo_children():
            widget.destroy()

        try:

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT clave FROM claves_acceso ORDER BY id DESC"
            )

            for (clave,) in cursor.fetchall():

                btn = ctk.CTkButton(
                    self.panel_llaves,
                    text=clave,
                    command=lambda c=clave: self.copiar(c)
                )

                btn.pack(fill="x", pady=2)

        except:
            pass

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    # ==========================================
    # 📋 COPIAR
    # ==========================================
    def copiar(self, texto):

        self.clipboard_clear()
        self.clipboard_append(texto)

    # ==========================================
    # 👥 USUARIOS
    # ==========================================
    def actualizar_lista_usuarios(self):

        self.lista_usuarios.configure(state="normal")
        self.lista_usuarios.delete("0.0", "end")

        try:

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT user_id, creditos
                FROM usuarios_autorizados
                ORDER BY creditos DESC
            """)

            for uid, cred in cursor.fetchall():

                self.lista_usuarios.insert(
                    "end",
                    f"ID: {uid} | Saldo: ${cred}\n"
                )

        except:
            pass

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

        self.lista_usuarios.configure(state="disabled")

    # ==========================================
    # 💰 GUARDAR PRECIO
    # ==========================================
    def guardar_precio(self):

        nuevo = self.input_nuevo_precio.get().strip()

        if not nuevo:
            return

        try:

            nuevo = int(nuevo)

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE configuracion_sistema
                SET valor = %s
                WHERE parametro = 'precio_cuenta'
            """, (nuevo,))

            conexion.commit()

            messagebox.showinfo(
                "Éxito",
                f"Precio actualizado a ${nuevo}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    # ==========================================
    # 💳 CARGAR CRÉDITOS
    # ==========================================
    def cargar_creditos(self):

        uid = self.input_user_id.get().strip()
        monto = self.input_monto.get().strip()

        if not uid or not monto:
            return

        try:

            monto = int(monto)

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE usuarios_autorizados
                SET creditos = creditos + %s
                WHERE user_id = %s
            """, (monto, uid))

            conexion.commit()

            messagebox.showinfo(
                "Éxito",
                f"Saldo agregado correctamente."
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    # ==========================================
    # 📢 BROADCAST
    # ==========================================
    def iniciar_broadcast_hilo(self):

        mensaje = self.caja_texto_msg.get(
            "0.0",
            "end"
        ).strip()

        if len(mensaje) < 2:
            return

        threading.Thread(
            target=self.proceso_broadcast,
            args=(mensaje,)
        ).start()

    def proceso_broadcast(self, mensaje):

        try:

            conexion = self.conectar_db()
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT user_id FROM usuarios_autorizados"
            )

            usuarios = cursor.fetchall()

            for (uid,) in usuarios:

                try:

                    self.bot.send_message(
                        uid,
                        f"📢 {mensaje}"
                    )

                except:
                    pass

            messagebox.showinfo(
                "Éxito",
                "Broadcast enviado."
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:

            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

# ==========================================
# 🚀 INICIAR APP
# ==========================================
if __name__ == "__main__":

    app = AdminDashboard()
    app.mainloop()

