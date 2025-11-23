import machine, onewire, ds18x20, dht, neopixel, time

DS_Pin = 1
DHT_Pin = 2
LED_pin = 3
Num_LEDS = 16 

dht_sensor = dht.DHT22(machine.Pin(DHT_Pin))
np = neopixel.NeoPixel(machine.Pin(LED_pin), Num_LEDS)

ds_pin = machine.Pin(DS_Pin)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

COLD = (0, 0, 255)
MID  = (0, 255, 0)
HOT  = (255, 0, 0)

def blend(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def apply_brightness(color, factor=0.2):
    return (int(color[0]*factor), int(color[1]*factor), int(color[2]*factor))

def update_leds_by_temp(temp):
    if temp is None:
        col = (0,0,0)
    else:
        if temp <= 15:
            col = COLD
        elif temp < 25:
            t = (temp - 15) / 10.0
            col = blend(COLD, MID, t)
        elif temp < 35:
            t = (temp - 25) / 10.0
            col = blend(MID, HOT, t)
        else:
            col = HOT
    col = apply_brightness(col, 0.2)
    for i in range(Num_LEDS):
        np[i] = col
    np.write()

while True:
    temp = None
    hum = None
    
    if roms:
        try:
            ds_sensor.convert_temp()
            time.sleep_ms(750)
            t_read = ds_sensor.read_temp(roms[0])
            if isinstance(t_read, (int, float)):
                temp = t_read
            else:
                print("Aviso: ERRO NA LEITURA DO DS18B20:", t_read)
        except Exception as e:
            print("ERRO NA LEITURA DO DS18B20:", e)
    else:
        print("Nenhum sensor DS18B20 detectado")

    try:
        dht_sensor.measure()
        hum = dht_sensor.humidity()
    except Exception as e:
        print("ERRO A LER O DHT:", e)

    if temp is None:
        print("Temp: N/A", "Hum:", ("{:.1f}%".format(hum) if hum is not None else "N/A"))
    else:
        print("Temp: {:.1f} °C  Hum: {}".format(temp, ("{:.1f}%".format(hum) if hum is not None else "N/A")))

    update_leds_by_temp(temp)
