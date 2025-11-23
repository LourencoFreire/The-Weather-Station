import machine, onewire, ds18x20, dht, neopixel, time

DS_Pin = 1
DHT_Pin = 2
LED_pin = 3
Num_LEDS = 16

dht_sensor = dht.DHT22(machine.Pin(DHT_Pin))
ds_pin = machine.Pin(DS_Pin)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

if not roms:
    print("Warning, bcuz i just want to /j")

np = neopixel.NeoPixel(machine.Pin(LED_pin), Num_LEDS)
cold = (0, 0, 255)
mid  = (0, 255, 0)
hot  = (255, 0, 0)
Hum_LED = (255, 255, 0)

def blend(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def apply_brightness(color, factor=0.5):
    return (int(color[0]*factor), int(color[1]*factor), int(color[2]*factor))

def update_leds_by_temp(temp):
    if temp is None:
        col = (0, 0, 0)
    elif temp <= 15:
        col = cold
    elif temp < 25:
        t = (temp - 15) / 10.0
        col = blend(cold, mid, t)
    elif temp < 35:
        t = (temp - 25) / 10.0
        col = blend(mid, hot, t)
    else:
        col = hot
    col = apply_brightness(col, 0.5)
    for i in range(Num_LEDS):
        np[i] = col

def update_leds_by_humidity(hum):
    if hum is None:
        return
    leds_to_light = 0
    if hum >= 30:
        leds_to_light = 1
    if hum >= 60:
        leds_to_light = 2
    if hum >= 90:
        leds_to_light = 3

    for i in range(leds_to_light):
        np[i] = Hum_LED
    np.write()

while True:
    temp = None
    hum = None

    if roms:
        try:
            ds_sensor.convert_temp()
            time.sleep(0.67) 
            t_read = ds_sensor.read_temp(roms[0])
            if isinstance(t_read, (int, float)):
                temp = t_read
            else:
                print("oops, temp sensor not connected")
        except:
            print("just give up", )

    try:
        dht_sensor.measure()
        hum = dht_sensor.humidity()
    except:
        print("Another Error")
        
    print("Temp: {} °C  Hum: {}".format(
        "{:.1f}".format(temp) if temp is not None else "N/A",
        "{:.1f}%".format(hum) if hum is not None else "N/A"
    ))

    update_leds_by_temp(temp)
    update_leds_by_humidity(hum)

    time.sleep(0.67)  
