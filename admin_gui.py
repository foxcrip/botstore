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

        # Configuración de red y BD
        self.TOKEN = '8703223104:AAFD4E7vQjjxU1ppmz1YhQQrJI--dhluN_E'
        self.bot = telebot.TeleBot(self.TOKEN)
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'bot_user',
            'password': 'aldo1324',
            'database': 'bot_telegram'
        }

        self.construir_interfaz()
        self.actualizar_todo()

    def conectar_db(self):
        return mysql.connector.connect(**self.DB_CONFIG)

    def construir_interfaz(self):
        ctk.CTkLabel(self, text="🛡️ PANEL DE CONTROL CENTRAL", font=("Roboto", 24, "bold")).pack(pady=(15, 5))

        self.tabs = ctk.CTkTabview(self, width=700, height=480)
        self.tabs.pack(padx=20, pady=10, fill="both", expand=True)

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

        ctk.CTkButton(self, text="🔄 SINCRONIZAR BASE DE DATOS", command=self.actualizar_todo, fg_color="#333333", hover_color="#1a1a1a", height=45, font=("Arial", 14, "bold")).pack(pady=15, fill="x", padx=20)

    # ==========================================
    # 🏗️ CONSTRUCCIÓN DE CADA PESTAÑA
    # ==========================================
    def construir_tab_combos(self):
        tab = self.tabs.tab("📦 Inventario y Stock")
        ctk.CTkLabel(tab, text="Monitor de Cuentas en Tiempo Real", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.lista_servicios = ctk.CTkTextbox(tab, state="disabled", fg_color="#0a0a0a", text_color="#00FF00", font=("Consolas", 14))
        self.lista_servicios.pack(pady=10, padx=20, fill="both", expand=True)

        caja_carga = ctk.CTkFrame(tab, fg_color="transparent")
        caja_carga.pack(pady=10, fill="x", padx=20)
        
        self.input_nom_servicio = ctk.CTkEntry(caja_carga, placeholder_text="Nombre del servicio (ej: wlmart)", width=250)
        self.input_nom_servicio.pack(side="left", padx=(0, 10), expand=True, fill="x")

        ctk.CTkButton(caja_carga, text="📂 Subir Archivo .txt", fg_color="#CD7F32", hover_color="#A0522D", command=self.cargar_archivo_combos).pack(side="right")

    def construir_tab_keys(self):
        tab = self.tabs.tab("🔑 Llaves de Acceso")
        ctk.CTkLabel(tab, text="Generador de Tokens de Acceso", font=("Arial", 16, "bold")).pack(pady=5)

        caja_input = ctk.CTkFrame(tab, fg_color="transparent")
        caja_input.pack(pady=5, fill="x", padx=20)

        self.input_nueva_key = ctk.CTkEntry(caja_input, placeholder_text="Escribe una nueva Key de acceso...", width=250)
        self.input_nueva_key.pack(side="left", padx=(0, 10), expand=True, fill="x")

        ctk.CTkButton(caja_input, text="➕ Agregar Key", command=self.agregar_key, fg_color="#228B22", hover_color="#006400", width=120).pack(side="right")

        ctk.CTkLabel(tab, text="👇 Haz clic sobre cualquier llave para copiarla automáticamente", font=("Arial", 12, "italic"), text_color="#aaaaaa").pack(pady=(10,0))

        self.panel_llaves_interactivo = ctk.CTkScrollableFrame(tab, fg_color="#0a0a0a")
        self.panel_llaves_interactivo.pack(pady=5, padx=20, fill="both", expand=True)

        self.lbl_notificacion = ctk.CTkLabel(tab, text="", font=("Arial", 14, "bold"), text_color="#00FF00")
        self.lbl_notificacion.pack(pady=(0, 5))

    def construir_tab_usuarios(self):
        tab = self.tabs.tab("👥 Clientes")
        ctk.CTkLabel(tab, text="Control de Usuarios Registrados", font=("Arial", 16, "bold")).pack(pady=10)

        self.lista_usuarios = ctk.CTkTextbox(tab, state="disabled", fg_color="#0a0a0a", text_color="#00FF00", font=("Consolas", 14))
        self.lista_usuarios.pack(pady=10, padx=20, fill="both", expand=True)

        caja_ban = ctk.CTkFrame(tab, fg_color="transparent")
        caja_ban.pack(pady=10, fill="x", padx=20)

        self.input_ban_id = ctk.CTkEntry(caja_ban, placeholder_text="ID de Telegram a expulsar...", width=250)
        self.input_ban_id.pack(side="left", padx=(0, 10), expand=True, fill="x")

        ctk.CTkButton(caja_ban, text="🚫 Banear / Eliminar", command=self.banear_usuario, fg_color="#8B0000", hover_color="#FF0000", width=120).pack(side="right")

    # ==========================================
    # 💰 PESTAÑA: CRÉDITOS Y PRECIO
    # ==========================================
    def construir_tab_creditos(self):
        tab = self.tabs.tab("💰 Créditos y Precio")
        
        # --- NUEVA SECCIÓN: PRECIO GLOBAL ---
        frame_precio = ctk.CTkFrame(tab)
        frame_precio.pack(pady=(5, 10), padx=20, fill="x")
        
        ctk.CTkLabel(frame_precio, text="⚙️ CONFIGURACIÓN DE PRECIO", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.lbl_precio_actual = ctk.CTkLabel(frame_precio, text="Precio actual: Cargando...", text_color="#00FF00", font=("Arial", 12, "bold"))
        self.lbl_precio_actual.pack()

        caja_precio = ctk.CTkFrame(frame_precio, fg_color="transparent")
        caja_precio.pack(pady=5)
        
        self.input_nuevo_precio = ctk.CTkEntry(caja_precio, placeholder_text="Nuevo precio $", width=120)
        self.input_nuevo_precio.pack(side="left", padx=5)
        
        ctk.CTkButton(caja_precio, text="💾 Guardar Precio", command=self.guardar_precio, fg_color="#1f538d", hover_color="#14375e", width=120).pack(side="left", padx=5)

        # --- SECCIÓN: RECARGA DE SALDOS ---
        ctk.CTkLabel(tab, text="Gestión de Saldos y Recargas", font=("Arial", 16, "bold")).pack(pady=(10, 0))
        ctk.CTkLabel(tab, text="👇 Haz clic sobre cualquier usuario para copiar y autocompletar su ID", font=("Arial", 12, "italic"), text_color="#aaaaaa").pack(pady=(0,5))

        self.lbl_noti_creditos = ctk.CTkLabel(tab, text="", font=("Arial", 14, "bold"), text_color="#00FF00")
        self.lbl_noti_creditos.pack(pady=(0, 5))

        # Panel desplazable interactivo para los saldos
        self.panel_saldos_interactivo = ctk.CTkScrollableFrame(tab, fg_color="#0a0a0a", height=150)
        self.panel_saldos_interactivo.pack(pady=5, padx=20, fill="both", expand=True)

        # Formulario de carga
        frame_carga = ctk.CTkFrame(tab, fg_color="transparent")
        frame_carga.pack(pady=10, fill="x", padx=20)

        self.input_user_id = ctk.CTkEntry(frame_carga, placeholder_text="ID del Usuario", width=250)
        self.input_user_id.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.input_monto = ctk.CTkEntry(frame_carga, placeholder_text="Monto $", width=100)
        self.input_monto.pack(side="left", padx=5)

        ctk.CTkButton(frame_carga, text="➕ Cargar Saldo", fg_color="#228B22", hover_color="#006400", command=self.cargar_creditos, width=120).pack(side="right")

    def construir_tab_broadcast(self):
        tab = self.tabs.tab("📢 Difusión Masiva")
        ctk.CTkLabel(tab, text="Envío de Anuncios y Promociones", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.caja_texto_msg = ctk.CTkTextbox(tab, height=150, font=("Arial", 14))
        self.caja_texto_msg.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkButton(
            tab, 
            text="🚀 TRANSMITIR A TODOS LOS CLIENTES", 
            command=self.iniciar_broadcast_hilo, 
            fg_color="#1f538d", 
            hover_color="#14375e",
            font=("Arial", 14, "bold"),
            height=45
        ).pack(pady=20, padx=20, fill="x")

    # ==========================================
    # ⚙️ LÓGICA DE NEGOCIO
    # ==========================================

    def actualizar_todo(self):
        self.actualizar_lista_servicios()
        self.actualizar_lista_keys()
        self.actualizar_lista_usuarios()
        self.actualizar_lista_creditos() 

    def actualizar_lista_servicios(self):
        self.lista_servicios.configure(state="normal")
        self.lista_servicios.delete("0.0", "end")
        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT servicio, COUNT(CASE WHEN estado = 'disponible' THEN 1 END) FROM combos GROUP BY servicio")
            resultados = cursor.fetchall()
            
            if resultados:
                for (serv, stock) in resultados:
                    self.lista_servicios.insert("end", f"> Comando: /{serv.ljust(15)} | Stock: {stock} cuentas\n")
            else:
                self.lista_servicios.insert("end", "> SISTEMA: No hay servicios registrados en la BD.\n")
        except: pass
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()
        self.lista_servicios.configure(state="disabled")

    def cargar_archivo_combos(self):
        servicio = self.input_nom_servicio.get().strip().lower()
        if not servicio:
            messagebox.showwarning("Error", "Escribe el nombre del servicio primero (ej: walmart).")
            return
            
        ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if not ruta_archivo: return

        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                lineas = [linea.strip() for linea in f if linea.strip()]
            
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            sql = "INSERT INTO combos (servicio, cuenta) VALUES (%s, %s)"
            datos = [(servicio, l) for l in lineas]
            
            cursor.executemany(sql, datos)
            conexion.commit()
            
            messagebox.showinfo("Éxito", f"Se cargaron {len(lineas)} cuentas para el comando /{servicio}")
            self.input_nom_servicio.delete(0, 'end')
            self.actualizar_lista_servicios()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()

    def agregar_key(self):
        nueva_key = self.input_nueva_key.get().strip()
        if not nueva_key: return

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO claves_acceso (clave) VALUES (%s)", (nueva_key,))
            conexion.commit()
            self.input_nueva_key.delete(0, 'end')
            self.actualizar_lista_keys()
            
            self.copiar_al_portapapeles(nueva_key)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()

    def actualizar_lista_keys(self):
        for widget in self.panel_llaves_interactivo.winfo_children():
            widget.destroy()

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT clave FROM claves_acceso ORDER BY id DESC")
            
            for (c,) in cursor.fetchall():
                btn_llave = ctk.CTkButton(
                    self.panel_llaves_interactivo,
                    text=f"🗝️ {c}",
                    font=("Consolas", 14),
                    fg_color="#1a1a1a",
                    hover_color="#333333",
                    anchor="w",
                    command=lambda llave=c: self.copiar_al_portapapeles(llave)
                )
                btn_llave.pack(fill="x", pady=2, padx=5)
                
        except: pass
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()

    def copiar_al_portapapeles(self, llave_pura):
        self.clipboard_clear()
        self.clipboard_append(llave_pura)
        self.lbl_notificacion.configure(text=f"✅ ¡Copiada: {llave_pura}!")
        self.after(3000, lambda: self.lbl_notificacion.configure(text=""))

    def banear_usuario(self):
        user_id = self.input_ban_id.get().strip()
        if not user_id: return
        if not messagebox.askyesno("Confirmar Baneo", f"¿Eliminar acceso al ID {user_id}?"): return

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios_autorizados WHERE user_id = %s", (user_id,))
            conexion.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Éxito", f"Usuario {user_id} baneado.")
                self.input_ban_id.delete(0, 'end')
                self.actualizar_lista_usuarios()
                self.actualizar_lista_creditos()
            else:
                messagebox.showwarning("No encontrado", "Ese ID no está registrado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()

    def actualizar_lista_usuarios(self):
        self.lista_usuarios.configure(state="normal")
        self.lista_usuarios.delete("0.0", "end")
        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT user_id, fecha_registro FROM usuarios_autorizados ORDER BY fecha_registro DESC")
            for (uid, fecha) in cursor.fetchall():
                self.lista_usuarios.insert("end", f"> 👤 {uid} | Ingreso: {fecha}\n")
        except: pass
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()
        self.lista_usuarios.configure(state="disabled")

    # ==========================================
    # 💰 NUEVA LÓGICA DE CRÉDITOS Y PRECIO
    # ==========================================
    def guardar_precio(self):
        nuevo_p = self.input_nuevo_precio.get().strip()
        if not nuevo_p: return
        try:
            nuevo_p = int(nuevo_p)
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("UPDATE configuracion_sistema SET valor = %s WHERE parametro = 'precio_cuenta'", (nuevo_p,))
            conexion.commit()
            messagebox.showinfo("Éxito", f"✅ Precio global actualizado a ${nuevo_p} MXN.\nEl bot ya está cobrando este nuevo monto.")
            self.input_nuevo_precio.delete(0, 'end')
            self.actualizar_lista_creditos()
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número entero válido.")
        except Exception as e:
            messagebox.showerror("Error BD", f"Asegúrate de haber creado la tabla de configuración. Error: {e}")
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()

    def actualizar_lista_creditos(self):
        # 1. Limpiar panel anterior
        for widget in self.panel_saldos_interactivo.winfo_children():
            widget.destroy()

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            
            # Obtener y mostrar el precio actual
            cursor.execute("SELECT valor FROM configuracion_sistema WHERE parametro = 'precio_cuenta'")
            res = cursor.fetchone()
            if res:
                self.lbl_precio_actual.configure(text=f"Precio actual por cuenta: ${res[0]} MXN")
            
            # Crear botones interactivos para cada usuario
            cursor.execute("SELECT user_id, creditos FROM usuarios_autorizados ORDER BY creditos DESC")
            for (uid, cred) in cursor.fetchall():
                btn_user = ctk.CTkButton(
                    self.panel_saldos_interactivo,
                    text=f"👤 ID: {uid}   |   💰 Saldo: ${cred} MXN",
                    font=("Consolas", 14),
                    fg_color="#1a1a1a",
                    hover_color="#333333",
                    anchor="w",
                    command=lambda u=uid: self.copiar_id_y_pegar(str(u))
                )
                btn_user.pack(fill="x", pady=2, padx=5)
        except: pass
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()

    def copiar_id_y_pegar(self, user_id):
        # Copiar al portapapeles
        self.clipboard_clear()
        self.clipboard_append(user_id)
        
        # AUTOCOMPLETAR LA CAJA DE TEXTO PARA RECARGAR
        self.input_user_id.delete(0, 'end')
        self.input_user_id.insert(0, user_id)
        
        # Animación visual
        self.lbl_noti_creditos.configure(text=f"✅ ¡ID {user_id} listo para recargar!")
        self.after(3000, lambda: self.lbl_noti_creditos.configure(text=""))

    def cargar_creditos(self):
        uid = self.input_user_id.get().strip()
        monto = self.input_monto.get().strip()
        
        if not uid or not monto: 
            messagebox.showwarning("Error", "Debes ingresar un ID y un monto.")
            return

        try:
            monto = int(monto)
            
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT creditos FROM usuarios_autorizados WHERE user_id = %s", (uid,))
            if not cursor.fetchone():
                messagebox.showwarning("No encontrado", "Ese ID de usuario no está registrado en el sistema.")
                return

            cursor.execute("UPDATE usuarios_autorizados SET creditos = creditos + %s WHERE user_id = %s", (monto, uid))
            conexion.commit()
            
            messagebox.showinfo("Recarga Exitosa", f"✅ Se han recargado ${monto} MXN al usuario {uid}.")
            
            self.input_user_id.delete(0, 'end')
            self.input_monto.delete(0, 'end')
            
            self.actualizar_lista_creditos()
            
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número entero válido (ej: 100).")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en la BD: {str(e)}")
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()
    # ==========================================

    def iniciar_broadcast_hilo(self):
        mensaje = self.caja_texto_msg.get("0.0", "end").strip()
        if len(mensaje) < 2: return
        
        if messagebox.askyesno("Confirmar Transmisión", "¿Enviar este mensaje masivo a todos los clientes?"):
            threading.Thread(target=self.proceso_broadcast, args=(mensaje,)).start()

    def proceso_broadcast(self, mensaje):
        exitos, fallos = 0, 0
        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT user_id FROM usuarios_autorizados")
            usuarios = cursor.fetchall()
            
            for (uid,) in usuarios:
                try:
                    self.bot.send_message(uid, f"📢 **COMUNICADO OFICIAL:**\n\n{mensaje}", parse_mode="Markdown")
                    exitos += 1
                except: fallos += 1
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'conexion' in locals() and conexion.is_connected(): cursor.close(); conexion.close()
        
        self.caja_texto_msg.delete("0.0", "end")
        messagebox.showinfo("Reporte de Transmisión", f"✅ Enviados con éxito: {exitos}\n❌ Fallidos (bloqueos): {fallos}")

if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()