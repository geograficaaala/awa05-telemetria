import RPi.GPIO as GPIO
import time
import logging

TRIG = 17
ECHO = 18

ALTURA_TOTAL    = 50.0
ALTURA_MAX_AGUA = 42.5
RADIO           = 13.5
AREA_BASE       = 3.14159265 * (RADIO ** 2)
DISTANCIA_MIN   = ALTURA_TOTAL - ALTURA_MAX_AGUA
DISTANCIA_MAX   = ALTURA_TOTAL

NUM_MUESTRAS   = 5
PAUSA_MUESTRAS = 0.06
TIMEOUT_ECHO   = 0.04
log = logging.getLogger("read_distance")
if not log.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    time.sleep(0.5)

def _medir_una_vez():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    deadline = time.time() + TIMEOUT_ECHO
    while GPIO.input(ECHO) == 0:
        inicio = time.time()
        if inicio > deadline:
            log.debug("Timeout flanco ascendente")
            return None
    deadline = time.time() + TIMEOUT_ECHO
    while GPIO.input(ECHO) == 1:
        fin = time.time()
        if fin > deadline:
            log.debug("Timeout flanco descendente")
            return None
    return round((fin - inicio) * 34300 / 2, 1)

def medir_distancia_promedio(n=NUM_MUESTRAS):
    muestras = []
    for i in range(n):
        v = _medir_una_vez()
        if v is not None:
            muestras.append(v)
            log.debug(f"Muestra {i+1}/{n}: {v} cm")
        else:
            log.debug(f"Muestra {i+1}/{n}: descartada")
        if i < n - 1:
            time.sleep(PAUSA_MUESTRAS)
    if not muestras:
        return None
    muestras.sort()
    mid = len(muestras) // 2
    if len(muestras) % 2 == 0:
        return round((muestras[mid-1] + muestras[mid]) / 2, 1)
    return round(muestras[mid], 1)

def distancia_a_volumen(distancia_cm):
    altura = max(0.0, min(ALTURA_TOTAL - distancia_cm, ALTURA_MAX_AGUA))
    return round(altura, 1), round(AREA_BASE * altura / 1000.0, 2)

def leer_nivel():
    setup()
    distancia = medir_distancia_promedio()
    GPIO.cleanup()
    if distancia is None:
        log.warning("Sin respuesta JSN-SR04T — verificar TRIG(GPIO17)/ECHO(GPIO18) y 5V.")
        return None, None
    if distancia < DISTANCIA_MIN:
        log.warning(f"Distancia {distancia} cm bajo minimo ({DISTANCIA_MIN} cm) — recipiente lleno.")
    elif distancia > DISTANCIA_MAX:
        log.warning(f"Distancia {distancia} cm sobre maximo ({DISTANCIA_MAX} cm) — fuera de rango.")
    altura, volumen = distancia_a_volumen(distancia)
    log.info(f"Distancia: {distancia} cm | Agua: {altura} cm | Volumen: {volumen} L")
    return distancia, volumen

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print("=== Prueba JSN-SR04T — AWA05 ===")
    dist, vol = leer_nivel()
    if dist is not None:
        print(f"Resultado: {dist} cm | {vol} L")
    else:
        print("Sin lectura. Revisar conexion del sensor.")
