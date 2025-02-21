import network
import machine
import ntptime
import utime
import ujson

# ----- Configuration -----
LED_PIN = 5
BUTTON_PIN = 4
pill_times = [(09, 0), (14, 0), (21, 0)] # [(09, 0), (14, 0), (21, 0)]
PILL_TOLERANCE = 30
POLL_BUFFER = 300
POLL_INTERVAL = 30
TIMEZONE_OFFSET = 0

# ----- Hardware Setup -----
led = machine.Pin(LED_PIN, machine.Pin.OUT)
button = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
led.value(0)
# ----- Main Functions -----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    with open("wifi_settings.json", "r") as f:
        secrets = ujson.load(f)
    print("Connecting to Wi-Fi...")
    wlan.connect(secrets["wifi_name"], secrets["password"])
    while not wlan.isconnected():
        utime.sleep(0.5)
    print("Wi-Fi connected! IP:", wlan.ifconfig()[0])
    return wlan

def sync_time():
    print("Synchronizing time with NTP...")
    ntptime.settime()
    print("Time synchronized.")
    utime.sleep(0.5)
    print("LED flash to confirm time has sychronised")
    led.value(1)
    utime.sleep(0.1)
    led.value(0)
    return machine.RTC()

def get_current_seconds(rtc):
    dt = rtc.datetime()
    return (dt[4] * 3600 + dt[5] * 60 + dt[6] + TIMEZONE_OFFSET) % 86400, dt

def is_pill_time(current_seconds):
    return any(abs(current_seconds - (h * 3600 + m * 60)) <= PILL_TOLERANCE for h, m in pill_times)

def compute_sleep_duration(current_seconds):
    next_event = min((h * 3600 + m * 60 - current_seconds) % 86400 for h, m in pill_times)
    return next_event * 1000

def flash_led_until_acknowledged():
    print("Pill time! Flashing LED. Press the button to acknowledge.")
    flash_duration = 0
    while button.value():
        led.value(1)
        utime.sleep(0.5)
        led.value(0)
        utime.sleep(0.5)
        flash_duration += 1
        print("LED flashing for", flash_duration, "seconds")
    print("Button pressed. Stopping LED flash.")
    led.value(0)
    return flash_duration

def log_event(ip_addr, dt, flash_duration):
    """Log the pill-taking event to report.txt."""
    formatted_date = f"{dt[0]}/{dt[1]}/{dt[2]}"
    log_text = (f"IP: {ip_addr}\n"
                f"Date: {formatted_date}\n"
                f"Pill time: {dt[4]}:{dt[5]:02d}\n"
                f"LED flashed for {flash_duration} seconds.\n")
    with open("report.txt", "a") as report_file:
        report_file.write(log_text + "\n")
    print("Event logged.")

def wait_for_next_pill_event(rtc):
    while True:
        current_seconds, dt = get_current_seconds(rtc)
        next_event_s = compute_sleep_duration(current_seconds) / 1000
        if next_event_s > POLL_BUFFER:
            print("Sleeping for", next_event_s - POLL_BUFFER, "seconds.")
            utime.sleep(next_event_s - POLL_BUFFER)
        else:
            print("Within polling window. Checking every", POLL_INTERVAL, "seconds.")
            utime.sleep(POLL_INTERVAL)
        if is_pill_time(get_current_seconds(rtc)[0]):
            break

def wait_until_outside_pill_window(rtc):
    while is_pill_time(get_current_seconds(rtc)[0]):
        print("Still within pill event window; waiting 10 seconds before checking again.")
        utime.sleep(10)

# ----- Main Loop -----
wlan = connect_wifi()
rtc = sync_time()

while True:
    current_seconds, dt = get_current_seconds(rtc)
    print("Current time:", dt[4], ":", dt[5], ":", dt[6])
    if is_pill_time(current_seconds):
        flash_duration = flash_led_until_acknowledged()
        log_event(wlan.ifconfig()[0] if wlan.isconnected() else "No IP", dt, flash_duration)
        wait_until_outside_pill_window(rtc)
    else:
        wait_for_next_pill_event(rtc)

