import spidev
import time
from sx126x import SX126x

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

def configure_lora():
    # LoRa configuration
    lora = SX126x()
    try:
        lora.begin()
        lora.set_frequency(868.0)  # Adjust for your region (868 MHz for EU, 915 MHz for US, etc.)
        lora.set_spreading_factor(7)
        lora.set_bandwidth(125)
        lora.set_coding_rate(5)
        lora.set_preamble_length(8)
        lora.set_sync_word(0x12)
        lora.set_power(22)
        lora.receive_mode()

        print("✅ LoRa Module Configured Successfully!")
        return lora
    except Exception as e:
        print(f"❌ Error configuring LoRa module: {e}")
        return None

def receive_lora_packets(lora):
    print("📡 Listening for incoming LoRa packets...")
    try:
        while True:
            packet = lora.receive_packet()
            if packet:
                print(f"📦 Packet Received: {packet}")
            time.sleep(1)  # Adjust based on desired polling rate
    except KeyboardInterrupt:
        print("\n🚪 Exiting...")
    finally:
        lora.end()

if __name__ == "__main__":
    if detect_lora_hat():
        lora = configure_lora()
        if lora:
            receive_lora_packets(lora)
