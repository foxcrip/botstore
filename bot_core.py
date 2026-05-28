import os
import telebot
import mysql.connector

# ==========================================
# ⚙️ CONFIGURACIÓN Y CONEXIÓN
# ==========================================
TOKEN = os.getenv("TOKEN")

DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE"),
    'port': int(os.getenv("MYSQL_PORT", 3306))
}

bot = telebot.TeleBot(TOKEN)
CONTACTO_ADMIN = "@useragb"

def conectar_db():
    return mysql.connector.connect(**DB_CONFIG)

def obtener_precio_actual():
    """Consulta el precio configurado en la base de datos en tiempo real."""
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT valor FROM configuracion_sistema WHERE parametro = 'precio_cuenta'"
        )

        res = cursor.fetchone()

        return int(res[0]) if res else 20

    except:
        return 20

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# ==========================================
# 🛒 COMANDOS DE USUARIO
# ==========================================

@bot.message_handler(commands=['start', 'help'])
def bienvenida(message):

    uid = message.from_user.id

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT creditos FROM usuarios_autorizados WHERE user_id = %s",
            (uid,)
        )

        user = cursor.fetchone()

        if user:

            bot.reply_to(
                message,
                f"✅ <b>Sistema Activo.</b>\n\n"
                f"💰 Tu Saldo: <b>${user[0]} MXN</b>\n"
                f"👉 Toca /productos para comprar.",
                parse_mode="HTML"
            )

        else:

            bot.reply_to(
                message,
                "🔒 <b>Acceso Restringido.</b>\n"
                "Envíame tu Key de acceso para registrarte:",
                parse_mode="HTML"
            )

    except:
        pass

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@bot.message_handler(commands=['productos', 'stock'])
def mostrar_productos(message):

    uid = message.from_user.id
    precio = obtener_precio_actual()

    try:
        conn = conectar_db()
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            "SELECT creditos FROM usuarios_autorizados WHERE user_id = %s",
            (uid,)
        )

        user = cursor.fetchone()

        if not user:
            return

        cursor.execute(
            "SELECT servicio, COUNT(id) "
            "FROM combos "
            "WHERE estado = 'disponible' "
            "GROUP BY servicio"
        )

        resultados = cursor.fetchall()

        resp = (
            f"💰 <b>Saldo: ${user[0]} MXN</b> | "
            f"🏷️ <b>Costo: ${precio} c/u</b>\n\n"
        )

        resp += "🛒 <b>PRODUCTOS DISPONIBLES:</b>\n━━━━━━━━━━━━━━━━━━━━\n"

        if resultados:

            for serv, cant in resultados:
                resp += (
                    f"🔹 <b>{serv.capitalize()}</b> "
                    f"({cant}) ➡️ /{serv}\n"
                )

        else:
            resp += "⚠️ No hay stock actualmente."

        bot.reply_to(message, resp, parse_mode="HTML")

    except:
        pass

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def entregar_cuenta(message):

    uid = message.from_user.id
    servicio = message.text[1:].strip().lower()

    if servicio in ['start', 'help', 'productos', 'stock']:
        return

    precio = obtener_precio_actual()

    try:
        conn = conectar_db()
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            "SELECT creditos FROM usuarios_autorizados WHERE user_id = %s",
            (uid,)
        )

        res_user = cursor.fetchone()

        if not res_user:
            return

        if res_user[0] < precio:

            bot.reply_to(
                message,
                f"❌ <b>Saldo insuficiente.</b>\n"
                f"Costo: ${precio}\n"
                f"Tu saldo: ${res_user[0]}\n\n"
                f"Contacto: {CONTACTO_ADMIN}",
                parse_mode="HTML"
            )

            return

        cursor.execute(
            "SELECT id, cuenta "
            "FROM combos "
            "WHERE servicio = %s "
            "AND estado = 'disponible' "
            "LIMIT 1 FOR UPDATE",
            (servicio,)
        )

        res_combo = cursor.fetchone()

        if res_combo:

            id_db, cuenta_txt = res_combo

            cursor.execute(
                "UPDATE usuarios_autorizados "
                "SET creditos = creditos - %s "
                "WHERE user_id = %s",
                (precio, uid)
            )

            cursor.execute(
                "UPDATE combos "
                "SET estado = 'entregado' "
                "WHERE id = %s",
                (id_db,)
            )

            conn.commit()

            bot.reply_to(
                message,
                f"✅ <b>COMPRA EXITOSA</b>\n"
                f"Costo: ${precio}\n"
                f"Saldo: ${res_user[0] - precio}\n\n"
                f"<code>{cuenta_txt}</code>",
                parse_mode="HTML"
            )

        else:
            conn.commit()
            bot.reply_to(message, "⚠️ Sin stock de ese servicio.")

    except:

        if 'conn' in locals():
            conn.rollback()

    finally:

        if 'conn' in locals():
            cursor.close()
            conn.close()

@bot.message_handler(func=lambda message: True)
def procesar_keys(message):

    uid = message.from_user.id
    texto = message.text.strip()

    try:
        conn = conectar_db()
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            "SELECT clave FROM claves_acceso WHERE clave = %s",
            (texto,)
        )

        if cursor.fetchone():

            cursor.execute(
                "INSERT INTO usuarios_autorizados (user_id, creditos) "
                "VALUES (%s, 0)",
                (uid,)
            )

            cursor.execute(
                "DELETE FROM claves_acceso WHERE clave = %s",
                (texto,)
            )

            conn.commit()

            bot.reply_to(
                message,
                f"🔓 <b>¡Acceso Concedido!</b>\n"
                f"Saldo: $0 MXN.\n"
                f"Contacta a {CONTACTO_ADMIN} para recargar.",
                parse_mode="HTML"
            )

    except:
        pass

    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

# ==========================================
# 🚀 INICIAR BOT
# ==========================================

if __name__ == "__main__":

    print("🚀 [BOT] Corriendo con Precios Dinámicos...")

    bot.infinity_polling(
        timeout=90,
        long_polling_timeout=90
    )