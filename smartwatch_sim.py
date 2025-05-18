import os
import time
import gc
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Import optimized IoT implementation
from aes_gcm_iot import AesGcmEnhanced


class SmartWatchSimulation:
    """
    Simulates AES-GCM encryption/decryption on a low-resource environment like a smartwatch.
    """

    def __init__(self):
        # Typical smartwatch constraints
        self.available_ram = 512 * 1024  # 512 KB RAM
        self.available_storage = 4 * 1024 * 1024  # 4 MB storage
        self.battery_capacity = 100  # Arbitrary units
        self.battery_level = 100

        # Performance metrics
        self.execution_times = {}

        # Test data sizes (typical for smartwatch)
        self.sensor_data = b"heartrate:72,steps:8541,calories:325,sleep:7.2h"
        self.fitness_data = b"activity:running,distance:5.2km,pace:5:42,elevation:125m"
        self.notification = b"Message from Alice: Are you available for a meeting at 3 PM today?"

    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        # Force garbage collection to ensure fair comparison
        gc.collect()

        # Measure execution time
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        return result, execution_time

    def run_standard_aes_gcm_test(self, data, key_size=256):
        """Run test with standard implementation."""
        print(f"\n----- Standard AES-GCM ({key_size}-bit) -----")

        # Generate key of specified size
        key = os.urandom(key_size // 8)

        # Encryption
        def encrypt_standard():
            iv = os.urandom(12)
            encryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            ).encryptor()

            ciphertext = encryptor.update(data) + encryptor.finalize()
            tag = encryptor.tag

            return iv, ciphertext, tag

        # Measure encryption time
        (iv, ciphertext, tag), encryption_time = self.measure_execution_time(encrypt_standard)
        self.execution_times[f'standard_aes{key_size}_encrypt'] = encryption_time

        # Decryption
        def decrypt_standard():
            decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            ).decryptor()

            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext

        # Measure decryption time
        _, decryption_time = self.measure_execution_time(decrypt_standard)
        self.execution_times[f'standard_aes{key_size}_decrypt'] = decryption_time

        # Report
        print(f"Data size: {len(data)} bytes")
        print(f"Encrypted size: {len(iv) + len(ciphertext) + len(tag)} bytes")
        print(f"Encryption time: {encryption_time:.3f} ms")
        print(f"Decryption time: {decryption_time:.3f} ms")
        print(f"Total crypto time: {encryption_time + decryption_time:.3f} ms")

    def run_optimized_aes_gcm_test(self, data, key_size=128, persistent_iv=True):
        """Run test with IoT-optimized implementation."""
        print(f"\n----- IoT-Optimized AES-GCM ({key_size}-bit) -----")

        # Create IoT-optimized cipher
        cipher = AesGcmEnhanced(key_size=key_size, persistent_iv=persistent_iv)

        # Generate key
        def gen_key():
            return cipher.generate_key()

        _, key_gen_time = self.measure_execution_time(gen_key)
        self.execution_times[f'iot_aes{key_size}_key_gen'] = key_gen_time

        # Encryption - basic
        def encrypt_basic():
            return cipher.encrypt(data)

        (iv, ciphertext, tag), encryption_time = self.measure_execution_time(encrypt_basic)
        self.execution_times[f'iot_aes{key_size}_encrypt'] = encryption_time

        # Encryption - combined (more efficient for transmission)
        def encrypt_combined():
            return cipher.encrypt_combined(data)

        _, encryption_combined_time = self.measure_execution_time(encrypt_combined)
        self.execution_times[f'iot_aes{key_size}_encrypt_combined'] = encryption_combined_time

        # Decryption
        def decrypt_basic():
            return cipher.decrypt(iv, ciphertext, tag)

        _, decryption_time = self.measure_execution_time(decrypt_basic)
        self.execution_times[f'iot_aes{key_size}_decrypt'] = decryption_time

        # Report
        print(f"Data size: {len(data)} bytes")
        print(f"Encrypted size: {len(iv) + len(ciphertext) + len(tag)} bytes")
        print(f"Key generation time: {key_gen_time:.3f} ms")
        print(f"Encryption time: {encryption_time:.3f} ms")
        print(f"Combined encryption time: {encryption_combined_time:.3f} ms")
        print(f"Decryption time: {decryption_time:.3f} ms")
        print(f"Total crypto time: {encryption_time + decryption_time:.3f} ms")

        # Simulate battery impact
        self.battery_level -= (encryption_time + decryption_time) / 1000

        return cipher

    def compare_key_sizes(self, data):
        """Compare different key sizes for IoT implementation."""
        print("\n===== COMPARING KEY SIZES =====")
        print(f"Data: {data.decode()}")
        print(f"Size: {len(data)} bytes")

        for key_size in [128, 192, 256]:
            self.run_optimized_aes_gcm_test(data, key_size=key_size)

    def simulate_repeated_operations(self, count=100):
        """Simulate repeated encryptions as would happen on a smartwatch."""
        print(f"\n===== SIMULATING {count} REPEATED OPERATIONS =====")

        # Create optimized cipher with persistent IV
        cipher = AesGcmEnhanced(key_size=128, persistent_iv=True)
        cipher.generate_key()

        # Mock sensor data
        heart_rate = b"heartrate:72"

        # Warm up
        for _ in range(5):
            cipher.encrypt(heart_rate)

        # Measure batch operations
        start_time = time.perf_counter()

        for i in range(count):
            # Simulate changing heart rate
            heart_rate = f"heartrate:{70 + i % 20}".encode()
            iv, ciphertext, tag = cipher.encrypt(heart_rate)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        # Report
        print(f"Total time for {count} encryptions: {total_time:.2f} ms")
        print(f"Average time per encryption: {total_time / count:.3f} ms")
        print(f"Operations per second: {count / (total_time / 1000):.1f}")

    def simulate_smartwatch_day(self):
        """Simulate a day of smartwatch operation."""
        print("\n===== SMARTWATCH DAILY SIMULATION =====")

        # Initialize cipher once and reuse (as a smartwatch would)
        cipher = AesGcmEnhanced(key_size=128, persistent_iv=True)
        key = cipher.generate_key()

        # Simulate periodic sensor readings (every 5 min = 288 times per day)
        sensor_readings = 288

        # Simulate notifications (received throughout the day)
        notifications = 40

        # Simulate fitness activity data (uploaded a few times)
        fitness_uploads = 5

        # Start with full battery
        self.battery_level = 100

        # Measure performance
        start_time = time.perf_counter()

        # Simulate sensor readings
        for _ in range(sensor_readings):
            # Generate random heart rate between 60-100
            heart_rate = f"heartrate:{60 + os.urandom(1)[0] % 40}".encode()
            cipher.encrypt_combined(heart_rate)

        # Simulate notifications
        for _ in range(notifications):
            cipher.encrypt_combined(self.notification)

        # Simulate fitness uploads
        for _ in range(fitness_uploads):
            cipher.encrypt_combined(self.fitness_data)

        end_time = time.perf_counter()
        total_crypto_time = (end_time - start_time) * 1000

        # Report
        total_operations = sensor_readings + notifications + fitness_uploads
        print(f"Total operations: {total_operations}")
        print(f"Total crypto processing time: {total_crypto_time:.2f} ms")
        print(f"Average time per operation: {total_crypto_time / total_operations:.3f} ms")
        print(f"Estimated battery impact: {total_crypto_time / 1000:.3f} units")
        print(f"Battery remaining: {self.battery_level:.2f}%")

    def run_simulation(self):
        """Run the complete smartwatch simulation."""
        print("======= SMARTWATCH AES-GCM SIMULATION =======")
        print("Simulating encryption operations on a low-resource device")
        print(f"Available RAM: {self.available_ram / 1024:.0f} KB")
        print(f"Available storage: {self.available_storage / 1024 / 1024:.0f} MB")
        print(f"Initial battery: {self.battery_level}%")

        # Test 1: Standard vs Optimized implementation
        print("\n----- TEST 1: STANDARD VS OPTIMIZED -----")
        self.run_standard_aes_gcm_test(self.sensor_data, key_size=256)
        self.run_optimized_aes_gcm_test(self.sensor_data, key_size=128)

        # Test 2: Key size comparison
        print("\n----- TEST 2: KEY SIZE IMPACT -----")
        self.compare_key_sizes(self.fitness_data)

        # Test 3: Repeated operations (common in IoT)
        print("\n----- TEST 3: REPEATED OPERATIONS -----")
        self.simulate_repeated_operations(count=100)

        # Test 4: Daily usage simulation
        print("\n----- TEST 4: DAILY USAGE SIMULATION -----")
        self.simulate_smartwatch_day()

        # Summary
        print("\n======= PERFORMANCE SUMMARY =======")
        print("Execution Times (milliseconds):")
        for operation, time_ms in self.execution_times.items():
            print(f"  {operation}: {time_ms:.3f} ms")

        print("\nKey Insights:")
        std_256_time = self.execution_times.get('standard_aes256_encrypt', 0) + self.execution_times.get(
            'standard_aes256_decrypt', 0)
        iot_128_time = self.execution_times.get('iot_aes128_encrypt', 0) + self.execution_times.get(
            'iot_aes128_decrypt', 0)

        if std_256_time > 0 and iot_128_time > 0:
            improvement = (std_256_time - iot_128_time) / std_256_time * 100
            print(f"- IoT-optimized implementation is {improvement:.1f}% faster than standard implementation")


if __name__ == "__main__":
    # Run the simulation
    simulation = SmartWatchSimulation()
    simulation.run_simulation()