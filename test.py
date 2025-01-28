import spidev
import time
import RPi.GPIO as GPIO

class SX1268:
    # SX1268 Register Addresses
    REG_VERSION = 0x42
    REG_PACKET_CONFIG = 0x0D
    REG_FREQUENCY = 0x08
    
    def __init__(self, bus=0, device=0, reset_pin=22):
        self.reset_pin = reset_pin
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000
        self.setup_gpio()
        self.reset()
        
    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.reset_pin, GPIO.OUT)
        
    def reset(self):
        GPIO.output(self.reset_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, GPIO.HIGH)
        time.sleep(0.1)
    
    def read_register(self, address):
        response = self.spi.xfer2([address & 0x7F, 0x00])
        return response[1]
    
    def write_register(self, address, value):
        self.spi.xfer2([address | 0x80, value])
    
    def detect_device(self):
        try:
            version = self.read_register(self.REG_VERSION)
            if version:
                print(f"✅ SX1268 LoRa Device Detected! Version: 0x{version:02X}")
                return True
            else:
                print("❌ Could not detect SX1268 device")
                return False
        except Exception as e:
            print(f"❌ Error detecting device: {e}")
            return False
    
    def scan_frequencies(self):
        # SX1268 frequency ranges
        frequency_ranges = [
            (410, 510),  # Low frequency range
            (780, 960)   # High frequency range
        ]
        
        print("Starting frequency scan...")
        
        for start_freq, end_freq in frequency_ranges:
            current_freq = start_freq
            while current_freq <= end_freq:
                try:
                    # Set frequency (simplified - would need actual register calculations)
                    freq_reg_value = int((current_freq * 1000000) / 32000)
                    self.write_register(self.REG_FREQUENCY, freq_reg_value & 0xFF)
                    
                    # Listen for packets
                    print(f"Scanning {current_freq} MHz...")
                    time.sleep(0.5)  # Listen on each frequency for 500ms
                    
                    # Check for received data (simplified)
                    rssi = self.read_register(0x0E)  # Example RSSI register
                    if rssi > 0:
                        print(f"Signal detected at {current_freq} MHz! RSSI: -{rssi} dBm")
                    
                    current_freq += 1
                except Exception as e:
                    print(f"Error scanning frequency {current_freq} MHz: {e}")
                    current_freq += 1
                    continue
    
    def cleanup(self):
        self.spi.close()
        GPIO.cleanup()

def main():
    try:
        lora = SX1268()
        if lora.detect_device():
            print("Beginning frequency scan...")
            lora.scan_frequencies()
        else:
            print("Cannot proceed with scan - device not detected")
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
    finally:
        if 'lora' in locals():
            lora.cleanup()

if __name__ == "__main__":
    main()
