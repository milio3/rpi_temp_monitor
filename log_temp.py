import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Intentar importar configuración desde config.py, si no existe usar valores por defecto
try:
    from config import (
        BASE_DIR, LOG_FILE, TEMPLATE_FILE, INDEX_FILE, ALERT_LOG_FILE,
        TEMP_SENSOR_PATH, TEMP_MIN_VALID, TEMP_MAX_VALID,
        TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD,
        DAILY_HOURS, HISTORY_DAYS
    )
except ImportError:
    # Configuración por defecto si config.py no existe
    BASE_DIR = Path("/home/dev/proyectos/monitor_temp")
    LOG_FILE = BASE_DIR / "temp.log"
    TEMPLATE_FILE = BASE_DIR / "template.html"
    INDEX_FILE = BASE_DIR / "index.html"
    ALERT_LOG_FILE = BASE_DIR / "alerts.log"
    
    TEMP_SENSOR_PATH = "/sys/class/thermal/thermal_zone0/temp"
    TEMP_MIN_VALID = 0.0
    TEMP_MAX_VALID = 100.0
    TEMP_WARNING_THRESHOLD = 70.0
    TEMP_CRITICAL_THRESHOLD = 80.0
    DAILY_HOURS = 24
    HISTORY_DAYS = 30

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BASE_DIR / "monitor.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_cpu_temp():
    """Lee la temperatura de la CPU desde el sistema."""
    try:
        if not os.path.exists(TEMP_SENSOR_PATH):
            logging.error(f"Ruta de sensor de temperatura no encontrada: {TEMP_SENSOR_PATH}")
            return None
        
        with open(TEMP_SENSOR_PATH, "r") as f:
            raw_temp = f.read().strip()
            temp = float(raw_temp) / 1000.0
            
            # Validar rango razonable
            if temp < TEMP_MIN_VALID or temp > TEMP_MAX_VALID:
                logging.warning(f"Temperatura fuera de rango válido: {temp}°C")
                return None
            
            return temp
    except FileNotFoundError:
        logging.error(f"Archivo de sensor no encontrado: {TEMP_SENSOR_PATH}")
        return None
    except (ValueError, OSError) as e:
        logging.error(f"Error al leer temperatura: {e}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado al leer temperatura: {e}")
        return None

def validate_temp(temp):
    """Valida que la temperatura esté en un rango válido."""
    if temp is None:
        return False
    return TEMP_MIN_VALID <= temp <= TEMP_MAX_VALID

def log_alert(temp, level):
    """Registra una alerta cuando la temperatura supera umbrales."""
    try:
        alert_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {temp:.2f}°C | {level}\n"
        if ALERT_LOG_FILE.exists():
            with open(ALERT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(alert_msg)
        else:
            with open(ALERT_LOG_FILE, "w", encoding="utf-8") as f:
                f.write("# Fecha y Hora | Temperatura | Nivel (WARNING/CRITICAL)\n")
                f.write(alert_msg)
        logging.warning(f"ALERTA {level}: Temperatura {temp:.2f}°C")
    except Exception as e:
        logging.error(f"Error al escribir alerta: {e}")

def check_alerts(temp):
    """Verifica si la temperatura requiere generar alertas."""
    if temp is None:
        return
    
    if temp >= TEMP_CRITICAL_THRESHOLD:
        log_alert(temp, "CRITICAL")
    elif temp >= TEMP_WARNING_THRESHOLD:
        log_alert(temp, "WARNING")

def update_log(temp):
    """Actualiza el archivo de log con la temperatura actual."""
    if not validate_temp(temp):
        logging.warning(f"Temperatura inválida no registrada: {temp}")
        return
    
    try:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"{ahora} | {temp:.2f} | DATA\n"
        
        # Asegurar que el directorio existe
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linea)
        
        # Verificar alertas
        check_alerts(temp)
    except OSError as e:
        logging.error(f"Error al escribir en log: {e}")
    except Exception as e:
        logging.error(f"Error inesperado al actualizar log: {e}")

def consolidate_yesterday():
    """Consolida los datos del día anterior en un registro SUMMARY."""
    if not LOG_FILE.exists():
        return
    
    try:
        ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        # Verificar si ya existe un SUMMARY para ayer
        if any(ayer in l and "SUMMARY" in l for l in lineas):
            return

        datos_ayer = []
        otras_lineas = []
        
        for l in lineas:
            if ayer in l and "DATA" in l:
                try:
                    parts = l.split("|")
                    if len(parts) < 3:
                        continue
                    ts_str = parts[0].strip()
                    temp = float(parts[1].strip())
                    hora = ts_str.split(" ")[1][:5]
                    datos_ayer.append({"t": temp, "h": hora})
                except (ValueError, IndexError) as e:
                    logging.warning(f"Error al procesar línea para consolidación: {l.strip()}, error: {e}")
                    continue
            else:
                otras_lineas.append(l)

        if datos_ayer:
            min_e = min(datos_ayer, key=lambda x: x['t'])
            max_e = max(datos_ayer, key=lambda x: x['t'])
            val_str = f"{min_e['t']:.2f} ({min_e['h']})/{max_e['t']:.2f} ({max_e['h']})"
            resumen = f"{ayer} 00:00:00 | {val_str} | SUMMARY\n"
            otras_lineas.append(resumen)
            
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(otras_lineas)
            
            logging.info(f"Consolidado {len(datos_ayer)} registros del {ayer}")
    except OSError as e:
        logging.error(f"Error al consolidar datos de ayer: {e}")
    except Exception as e:
        logging.error(f"Error inesperado en consolidación: {e}")

def parse_log_line(line):
    """Parsea una línea del log y retorna un diccionario con los datos o None si es inválida."""
    if "|" not in line or line.startswith("#"):
        return None
    
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 3:
        return None
    
    try:
        dt = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        record_type = parts[2]
        
        if record_type == "DATA":
            temp = float(parts[1])
            return {"type": "DATA", "datetime": dt, "temp": temp}
        elif record_type == "SUMMARY":
            vals = parts[1].split("/")
            if len(vals) < 2:
                return None
            
            # Extraer valor y hora: "12.34 (15:00)"
            def extract_val_time(s):
                s = s.strip()
                if "(" in s:
                    val_str, time_str = s.split("(")
                    return float(val_str.strip()), time_str.replace(")", "").strip()
                return float(s), ""

            v_min, t_min = extract_val_time(vals[0])
            v_max, t_max = extract_val_time(vals[1])
            
            return {
                "type": "SUMMARY", 
                "datetime": dt, 
                "min": v_min, 
                "min_time": t_min,
                "max": v_max,
                "max_time": t_max
            }
    except (ValueError, IndexError) as e:
        logging.debug(f"Error al parsear línea: {line.strip()}, error: {e}")
        return None
    
    return None

def render_html(current_temp):
    """Genera el archivo HTML con los datos actualizados."""
    if not TEMPLATE_FILE.exists():
        logging.error(f"Archivo template no encontrado: {TEMPLATE_FILE}")
        return
    
    daily_data = []
    history_data = []
    limite_24h = datetime.now() - timedelta(hours=DAILY_HOURS)

    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parsed = parse_log_line(line)
                    if parsed is None:
                        continue
                    
                    if parsed["type"] == "DATA" and parsed["datetime"] > limite_24h:
                        # Guardar datetime completo para ordenar después
                        daily_data.append({
                            "x": parsed["datetime"].isoformat(),
                            "y": parsed["temp"],
                            "dt": parsed["datetime"]  # Para ordenar
                        })
                    elif parsed["type"] == "SUMMARY":
                        history_data.append({
                            "d": parsed["datetime"].strftime("%Y-%m-%d"),
                            "min": parsed["min"],
                            "max": parsed["max"],
                            "min_time": parsed.get("min_time", ""),
                            "max_time": parsed.get("max_time", ""),
                            "dt": parsed["datetime"]  # Para ordenar
                        })
        except OSError as e:
            logging.error(f"Error al leer archivo de log: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al procesar log: {e}")
    
    # Ordenar datos diarios por timestamp
    daily_data.sort(key=lambda x: x["dt"])
    # Eliminar campo temporal dt antes de JSON
    daily_data_clean = [{"x": d["x"], "y": d["y"]} for d in daily_data]
    
    # Ordenar historial por fecha (reciente a antiguo para procesar meses)
    history_data.sort(key=lambda x: x["dt"], reverse=True)
    
    # Generar datos mensuales
    monthly_data = {}
    for h in history_data:
        month_key = h["dt"].strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {"min": h["min"], "max": h["max"], "days": 0}
        else:
            monthly_data[month_key]["min"] = min(monthly_data[month_key]["min"], h["min"])
            monthly_data[month_key]["max"] = max(monthly_data[month_key]["max"], h["max"])
        monthly_data[month_key]["days"] += 1
        
    monthly_data_clean = [
        {"d": k, "min": v["min"], "max": v["max"]} 
        for k, v in monthly_data.items()
    ]
    # Ordenar meses cronológicamente
    monthly_data_clean.sort(key=lambda x: x["d"]) 
    
    # Datos de historial (últimos HISTORY_DAYS)
    # history_data ya está ordenado reciente -> antiguo
    history_subset = history_data[:HISTORY_DAYS]
    history_subset.reverse()  # Ordenar antiguo -> reciente para gráfico
    
    history_data_clean = [{
        "d": h["d"], 
        "min": h["min"], 
        "max": h["max"],
        "min_t": h["min_time"],
        "max_t": h["max_time"]
    } for h in history_subset]

    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            html = f.read()

        # Escapar JSON para prevenir inyección
        temp_display = current_temp if current_temp is not None else 0.0
        html = html.replace("{{CURRENT_TEMP}}", f"{temp_display:.2f}")
        html = html.replace("{{LAST_UPDATE}}", datetime.now().strftime("%H:%M:%S"))
        html = html.replace("{{DAILY_JSON}}", json.dumps(daily_data_clean))
        html = html.replace("{{HISTORY_JSON}}", json.dumps(history_data_clean))
        html = html.replace("{{MONTHLY_JSON}}", json.dumps(monthly_data_clean))

        # Asegurar que el directorio existe
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        
        logging.info(f"HTML generado exitosamente con {len(daily_data_clean)} registros diarios y {len(history_data_clean)} días de historial")
    except OSError as e:
        logging.error(f"Error al escribir archivo HTML: {e}")
    except Exception as e:
        logging.error(f"Error inesperado al generar HTML: {e}")

if __name__ == "__main__":
    try:
        consolidate_yesterday()
        t = get_cpu_temp()
        if t is not None:
            update_log(t)
        render_html(t)
    except Exception as e:
        logging.critical(f"Error crítico en ejecución principal: {e}", exc_info=True)
