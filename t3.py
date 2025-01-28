import spidev
import time
import threading
from queue import Queue, Empty
import signal
import sys

class LoRaTransceiver:
    # SX1262 Register Addresses
    REG_PA_CONFIG = 0x95
    REG_FREQUENCY = 0x86
    REG_MODULATION = 0x8B
    REG_PACKET_CONFIG = 0x8F
    REG_PAYLOAD = 0x00
    
    def __init__(self):
        self.spi = None
        self.running = False
        self.tx_queue = Queue()
        self.rx_queue = Queue()
        self.tx_thread = None
        self.rx_thread = None
        
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

    def transmitter_thread(self):
        """Continuous transmission thread"""
        while self.running:
            try:
                # Get message from queue if available, otherwise use default
                try:
                    message = self.tx_queue.get(timeout=1.0)
                except Empty:
                    message = "LoRa Test Message"

                # Convert message to bytes if it's a string
                if isinstance(message, str):
                    message = message.encode()
                    
                # Write payload to FIFO
                self.write_register(self.REG_PAYLOAD, list(message))
                print(f"📡 Transmitting message: {message}")
                
                # Add delay between transmissions
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error in transmitter thread: {e}")
                time.sleep(1)  # Prevent rapid error loops

    def receiver_thread(self):
        """Continuous reception thread"""
        while self.running:
            try:
                # Check for received data
                data = self.read_register(self.REG_PAYLOAD, 32)  # Read up to 32 bytes
                if data and any(data):  # If we received any non-zero data
                    try:
                        message = bytes(data).decode().strip('\x00')
                        print(f"📥 Received message: {message}")
                        self.rx_queue.put(message)
                    except:
                        print(f"📥 Received raw data: {data}")
                        self.rx_queue.put(data)
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error in receiver thread: {e}")
                time.sleep(1)  # Prevent rapid error loops

    def start(self):
        """Start parallel transmission and reception"""
        if not self.spi:
            print("❌ LoRa not initialized!")
            return False

        self.running = True
        
        # Create and start transmitter thread
        self.tx_thread = threading.Thread(target=self.transmitter_thread)
        self.tx_thread.daemon = True
        self.tx_thread.start()
        
        # Create and start receiver thread
        self.rx_thread = threading.Thread(target=self.receiver_thread)
        self.rx_thread.daemon = True
        self.rx_thread.start()
        
        print("✅ Parallel transmission and reception started!")
        return True

    def stop(self):
        """Stop all operations"""
        self.running = False
        
        if self.tx_thread:
            self.tx_thread.join(timeout=1.0)
        if self.rx_thread:
            self.rx_thread.join(timeout=1.0)
            
        if self.spi:
            self.spi.close()
        
        print("🛑 LoRa operations stopped")

    def send_message(self, message):
        """Add message to transmission queue"""
        self.tx_queue.put(message)
        print(f"➡️ Message queued for transmission: {message}")

    def get_received_message(self):
        """Get message from reception queue if available"""
        try:
            return self.rx_queue.get_nowait()
        except Empty:
            return None

def signal_handler(sig, frame):
    print("\n⚠️ Stopping LoRa operations...")
    if 'lora' in globals():
        lora.stop()
    sys.exit(0)

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and initialize the transceiver
    lora = LoRaTransceiver()
    if not lora.initialize():
        return
    
    try:
        # Start parallel operations
        lora.start()
        
        # Main loop
        while True:
            # Example: Queue a message for transmission every 5 seconds
            lora.send_message(f"Hello LoRa! Time: {time.strftime('%H:%M:%S')}")
            
            # Check for received messages
            received = lora.get_received_message()
            if received:
                print(f"📬 Main loop received: {received}")
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n⚠️ Program interrupted by user")
    finally:
        lora.stop()

if __name__ == "__main__":
    main()
