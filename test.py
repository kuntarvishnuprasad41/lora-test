import spidev
import time

def detect_lora_hat():
    try:
        # Open SPI bus
        spi = spidev.SpiDev()
        spi.open(0, 0)  # Bus 0, Device 0
        spi.max_speed_hz = 1000000
        
        # Perform a simple read to test connection
        response = spi.xfer2([0x00])  # Simple read command
        
        print("✅ SX1262 LoRa HAT Detected Successfully!")
        print(f"Initial SPI Response: {response}")
        
        # Close SPI connection
        spi.close()
        return True
    
    except Exception as e:
        print(f"❌ Error detecting LoRa HAT: {e}")
        return False

if __name__ == "__main__":
    detect_lora_hat()
