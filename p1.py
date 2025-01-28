import spidev
import time

def detect_lora_hat():
    try:
        # Open SPI bus
        spi = spidev.SpiDev()
        spi.open(0, 0) # Bus 0, Device 0
        spi.max_speed_hz = 1000000

        # Perform a simple read to test connection
        response = spi.xfer2([0x00]) # Simple read command

        print("✅ SX1262 LoRa HAT Detected Successfully!")
        print(f"Initial SPI Response: {response}")
        
        return spi
    except Exception as e:
        print(f"❌ Error detecting LoRa HAT: {e}")
        return None

def scan_frequencies(spi):
    if not spi:
        return
    
    try:
        # SX1268 supported frequencies (in MHz)
        frequencies = range(410, 511)  # 410-510 MHz range
        
        print("\nStarting frequency scan...")
        
        for freq in frequencies:
            # Read RSSI for the current frequency
            # Using simple read command - adjust register as needed
            rssi_response = spi.xfer2([0x00])
            
            print(f"Scanning {freq} MHz - Response: {rssi_response}")
            time.sleep(0.1)  # Brief delay between scans
            
    except Exception as e:
        print(f"Error during frequency scan: {e}")
    finally:
        spi.close()

def main():
    spi = detect_lora_hat()
    if spi:
        scan_frequencies(spi)

if __name__ == "__main__":
    main()
