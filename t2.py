import spidev
import time

class LoRaTransceiver:
    # SX1262 Register Addresses
    REG_PA_CONFIG = 0x95
    REG_FREQUENCY = 0x86
    REG_MODULATION = 0x8B
    REG_PACKET_CONFIG = 0x8F
    REG_PAYLOAD = 0x00
    
    def __init__(self):
        self.spi = None
        
    def initialize(self):
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 1000000
            
            # Configure basic parameters
            self.set_frequency(433)  # 433 MHz
            self.set_power(14)       # 14 dBm
            self.configure_modulation()
            
            print("✅ LoRa transceiver initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing LoRa transceiver: {e}")
            return False
    
    def set_frequency(self, freq_mhz):
        freq_reg = int(freq_mhz * 1000000 / 61.035)
        self.write_register(self.REG_FREQUENCY, [(freq_reg >> 16) & 0xFF, 
                                               (freq_reg >> 8) & 0xFF, 
                                               freq_reg & 0xFF])
    
    def set_power(self, power_dbm):
        self.write_register(self.REG_PA_CONFIG, [power_dbm & 0xFF])
    
    def configure_modulation(self):
        # Configure for LoRa mode, BW=125kHz, SF=7, CR=4/5
        self.write_register(self.REG_MODULATION, [0x72])
        # Set packet mode
        self.write_register(self.REG_PACKET_CONFIG, [0x80])
    
    def write_register(self, address, data):
        if not self.spi:
            return
        self.spi.xfer2([address | 0x80] + data)
    
    def read_register(self, address, length=1):
        if not self.spi:
            return None
        return self.spi.xfer2([address & 0x7F] + [0] * length)[1:]
    
    def transmit(self, message):
        try:
            # Convert message to bytes if it's a string
            if isinstance(message, str):
                message = message.encode()
                
            # Write payload to FIFO
            self.write_register(self.REG_PAYLOAD, list(message))
            print(f"📡 Transmitting message: {message}")
            
            # Wait for transmission to complete
            time.sleep(0.1)
            return True
            
        except Exception as e:
            print(f"❌ Error during transmission: {e}")
            return False
    
    def receive(self, timeout=5):
        try:
            print("👂 Listening for incoming messages...")
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                # Check for received data
                data = self.read_register(self.REG_PAYLOAD, 32)  # Read up to 32 bytes
                if data and any(data):  # If we received any non-zero data
                    try:
                        message = bytes(data).decode().strip('\x00')
                        print(f"📥 Received message: {message}")
                        return message
                    except:
                        print(f"📥 Received raw data: {data}")
                        return data
                time.sleep(0.1)
            
            print("⏰ Receive timeout reached")
            return None
            
        except Exception as e:
            print(f"❌ Error during reception: {e}")
            return None
    
    def close(self):
        if self.spi:
            self.spi.close()

def main():
    # Create and initialize the transceiver
    lora = LoRaTransceiver()
    if not lora.initialize():
        return
    
    try:
        # Example: Transmit a message
        lora.transmit("Hello LoRa!")
        
        # Wait and then try to receive
        time.sleep(1)
        received = lora.receive(timeout=10)
        
        if received:
            print(f"Round-trip test successful!")
        
    finally:
        lora.close()

if __name__ == "__main__":
    main()
