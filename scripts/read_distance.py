import RPi.GPIO as GPIO
import time

TRIG = 17
ECHO = 18

ALTURA_TOTAL    = 50.0
ALTURA_MAX_AGUA = 42.5
RADIO           = 13.5
AREA_BASE       = 3.14159265 * (RADIO ** 2)
DISTANCIA_MIN   = ALTURA_TOTAL - ALTURA_MAX_AGUA

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    time.sleep(0.5)

def medir_distancia():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    timeout = time.time() + 0.04
    while GPIO.input(ECHO) == 0:
        inicio = time.time()
        if inicio > timeout:
            return None
    timeout = time.time() + 0.04
    while GPIO.input(ECHO) == 1:
        fin = time.time()
        if fin > timeout:
            return None
    duracion = fin - inicio
    distancia = (duracion * 34300) / 2
    return round(distancia, 1)

def distancia_a_volumen(distancia_cm):
    altura_agua = ALTURA_TOTAL - distancia_cm
    altura_agua = max(0.0, min(altura_agua, ALTURA_MAX_AGUA))
    volumen_litros = (AREA_BASE * altura_agua) / 1000.0
    return round(altura_agua, 1), round(volumen_litros, 2)

def leer_nivel():
    setup()
    distancia = medir_distancia()
    GPIO.cleanup()
    if distancia is None:
        print("[ERROR] Sin respuesta del sensor JSN-SR04T")
        return None, None
    if distancia < DISTANCIA_MIN:
        print(f"[WARN] Distancia {distancia} cm fuera de rango")
    altura, volumen = distancia_a_volumen(distancia)
    print(f"[SENSOR] Distancia: {distancia} cm | Agua: {altura} cm | Volumen: {volumen} L")
    return distancia, volumen

if __name__ == "__main__":
    leer_nivel()
