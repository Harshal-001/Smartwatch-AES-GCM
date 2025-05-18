import os
import time
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class AesGcmEnhanced:
    """
    Enhanced AES-GCM implementation optimized for IoT/smartwatch environments.
    Includes additional optimizations beyond the base IoT implementation:

    - Optimized IV generation with pre-allocated buffers
    - Counter-based nonce with minimal randomness
    - Memory-efficient operations
    - Efficient buffer management
    """

    def __init__(self, key_size=128, persistent_iv=True):
        """Initialize the enhanced AES-GCM cipher."""
        self.key_size = key_size
        self.key_bytes = key_size // 8
        self.key = None
        self.persistent_iv = persistent_iv

        # Counter for persistent IV
        self._iv_counter = 0
        self._max_iv_counter = 2 ** 32 - 1  # 32-bit counter (4 bytes)

        # Pre-allocated buffer for IV generation
        self._iv_buffer = bytearray(12)  # GCM recommended IV size

        # Flag for first run initialization
        self._initialized = False

    def generate_key(self):
        """Generate a new random key."""
        self.key = os.urandom(self.key_bytes)
        return self.key

    def set_key(self, key):
        """Set an existing key."""
        if len(key) != self.key_bytes:
            raise ValueError(f"Key must be exactly {self.key_bytes} bytes for AES-{self.key_size}")
        self.key = key

    def _init_iv_buffer(self):
        """Initialize the IV buffer with random prefix (done once)."""
        # For persistent IV, we use format: 8-byte random prefix + 4-byte counter
        # This gets called only once to maximize performance
        if self.persistent_iv:
            # Generate the random prefix (bytes 0-7)
            random_prefix = os.urandom(8)
            self._iv_buffer[0:8] = random_prefix
            self._iv_counter = 0

        self._initialized = True

    def generate_iv(self):
        """
        Generate a nonce/IV efficiently.
        Returns the IV buffer directly without copying for performance.
        """
        # First-time initialization
        if not self._initialized:
            self._init_iv_buffer()

        if not self.persistent_iv:
            # Standard random IV
            random_iv = os.urandom(12)
            self._iv_buffer[:] = random_iv
            return bytes(self._iv_buffer)

        # Counter-based IV generation (minimal randomness)
        if self._iv_counter >= self._max_iv_counter:
            # Reset when counter exhausted - in practice, would rarely happen
            self._init_iv_buffer()

        # Increment counter and update buffer in-place
        self._iv_counter += 1

        # Pack counter value directly into the buffer (bytes 8-11)
        # This is faster than conversion methods
        struct.pack_into('>I', self._iv_buffer, 8, self._iv_counter)

        return bytes(self._iv_buffer)

    def encrypt(self, plaintext, associated_data=None):
        """Encrypt data with optimized AES-GCM."""
        if self.key is None:
            self.generate_key()

        # Generate IV efficiently
        iv = self.generate_iv()

        # Create encryptor
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        # Add associated data if provided
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        # Encrypt the plaintext
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Get the tag
        tag = encryptor.tag

        return iv, ciphertext, tag

    def decrypt(self, iv, ciphertext, tag, associated_data=None):
        """Decrypt data with optimized AES-GCM."""
        if self.key is None:
            raise ValueError("No key set. Call set_key() or generate_key() first.")

        # Create decryptor
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        # Add associated data if provided
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        # Decrypt the ciphertext
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    def encrypt_combined(self, plaintext, associated_data=None):
        """Encrypt and return combined output for efficient transmission."""
        iv, ciphertext, tag = self.encrypt(plaintext, associated_data)

        # Combine for efficient transmission (IV + Ciphertext + Tag)
        # Use pre-allocated buffer if size is predictable
        total_size = len(iv) + len(ciphertext) + len(tag)
        result = bytearray(total_size)

        # Copy data into result buffer
        result[0:len(iv)] = iv
        result[len(iv):len(iv) + len(ciphertext)] = ciphertext
        result[len(iv) + len(ciphertext):] = tag

        return bytes(result), len(iv), len(tag)

    def decrypt_combined(self, combined_data, iv_size=12, tag_size=16, associated_data=None):
        """Decrypt data from combined format: IV + Ciphertext + Tag."""
        # Extract components directly from buffer
        iv = combined_data[:iv_size]
        tag = combined_data[-tag_size:]
        ciphertext = combined_data[iv_size:-tag_size]

        # Decrypt
        return self.decrypt(iv, ciphertext, tag, associated_data)


def benchmark_comparison(iterations=10000, warmup=1000):
    """Compare standard vs enhanced implementations."""
    print("\n=== ENHANCED VS STANDARD IMPLEMENTATION BENCHMARK ===")
    print(f"Running {iterations} iterations with {warmup} warmup iterations")

    data = b"heartrate:75,steps:8541,calories:325"
    print(f"Data size: {len(data)} bytes")

    # Warmup both implementations to ensure fair comparison
    print("\nWarming up implementations...")
    key = os.urandom(16)  # 128-bit key

    # Warmup standard
    for _ in range(warmup):
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    # Create and warmup enhanced implementation
    cipher = AesGcmEnhanced(key_size=128, persistent_iv=True)
    cipher.generate_key()

    for _ in range(warmup):
        iv, ciphertext, tag = cipher.encrypt(data)

    # Force GC to clear any warmup artifacts
    import gc
    gc.collect()

    # Standard implementation
    print("\nStandard Implementation:")
    start = time.perf_counter()

    for _ in range(iterations):
        iv = os.urandom(12)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

    end = time.perf_counter()
    std_time = (end - start) * 1000
    print(f"Total time: {std_time:.2f} ms")
    print(f"Avg time per operation: {std_time / iterations:.6f} ms")
    print(f"Operations per second: {iterations / (std_time / 1000):.1f}")

    # Enhanced implementation
    print("\nEnhanced Implementation:")
    start = time.perf_counter()

    for _ in range(iterations):
        iv, ciphertext, tag = cipher.encrypt(data)

    end = time.perf_counter()
    enh_time = (end - start) * 1000
    print(f"Total time: {enh_time:.2f} ms")
    print(f"Avg time per operation: {enh_time / iterations:.6f} ms")
    print(f"Operations per second: {iterations / (enh_time / 1000):.1f}")

    # Comparison
    improvement = ((std_time - enh_time) / std_time) * 100
    print(f"\nImprovement: {improvement:.1f}%")
    print(f"The enhanced implementation is {std_time / enh_time:.1f}x faster")

    # Test with different data sizes to demonstrate scaling
    print("\n--- Testing with different data sizes ---")
    sizes = [32, 64, 128, 256, 512]

    for size in sizes:
        # Generate test data of specified size
        test_data = os.urandom(size)

        # Standard implementation
        start = time.perf_counter()
        for _ in range(1000):  # Fewer iterations for larger sizes
            iv = os.urandom(12)
            encryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            ).encryptor()
            ciphertext = encryptor.update(test_data) + encryptor.finalize()
            tag = encryptor.tag
        end = time.perf_counter()
        std_size_time = (end - start) * 1000

        # Enhanced implementation
        start = time.perf_counter()
        for _ in range(1000):
            iv, ciphertext, tag = cipher.encrypt(test_data)
        end = time.perf_counter()
        enh_size_time = (end - start) * 1000

        size_improvement = ((std_size_time - enh_size_time) / std_size_time) * 100
        print(f"Size {size} bytes: Enhanced is {size_improvement:.1f}% faster")

    return std_time, enh_time


if __name__ == "__main__":
    print("Running enhanced AES-GCM benchmark comparison...")
    benchmark_comparison(iterations=100000, warmup=1000)