import time
import SX126x  # Make sure you have the correct library installed

def configure_lora():
    """Configures the LoRa module with basic settings."""
    lora = SX126x()
    try:
        lora.begin()
        lora.set_spreading_factor(7)
        lora.set_bandwidth(125)
        lora.set_coding_rate(5)
        lora.set_preamble_length(8)
        lora.set_sync_word(0x12)
        lora.set_power(22)
        print("✅ LoRa Module Initialized Successfully!")
        return lora
    except Exception as e:
        print(f"❌ Error configuring LoRa module: {e}")
        return None

def scan_frequencies(lora, freq_start, freq_end, step=0.1):
    """Scans the given frequency range for incoming packets."""
    print(f"📡 Scanning frequencies from {freq_start} MHz to {freq_end} MHz in steps of {step} MHz...")
    try:
        for freq in range(int(freq_start * 10), int(freq_end * 10), int(step * 10)):
            frequency = freq / 10.0
            lora.set_frequency(frequency)
            print(f"🌐 Tuning to {frequency:.1f} MHz...")
            lora.receive_mode()

            # Wait for potential packet reception
            start_time = time.time()
            while time.time() - start_time < 2:  # Listen for 2 seconds per frequency
                packet = lora.receive_packet()
                if packet:
                    print(f"📦 Packet Received on {frequency:.1f} MHz: {packet}")
                    break  # Stop scanning on first detected packet

            time.sleep(0.5)  # Pause briefly before moving to the next frequency
    except KeyboardInterrupt:
        print("\n🚪 Scanning interrupted by user.")
    finally:
        print("📡 Frequency scanning complete.")
        lora.end()

if __name__ == "__main__":
    # Define frequency range and step
    region = input("Enter region (EU/US/ASIA): ").strip().upper()
    if region == "EU":
        freq_start, freq_end = 863, 870
    elif region == "US":
        freq_start, freq_end = 902, 928
    elif region == "ASIA":
        freq_start, freq_end = 433, 510
    else:
        print("❌ Invalid region. Using EU defaults (863–870 MHz).")
        freq_start, freq_end = 863, 870

    # Initialize and configure LoRa
    lora = configure_lora()
    if lora:
        scan_frequencies(lora, freq_start, freq_end)
