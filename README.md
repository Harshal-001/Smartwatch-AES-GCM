# AES-GCM Encryption Implementations

This repository contains two implementations of AES-GCM (Galois/Counter Mode) encryption:

1. `aes_gcm.py` - Standard implementation with full features
2. `aes_gcm_iot.py` - Optimized implementation for IoT devices

## Standard Implementation (`aes_gcm.py`)

This implementation provides a straightforward interface for AES-GCM encryption and decryption:

- 256-bit AES encryption in GCM mode
- Secure random IV generation
- Authentication tag verification
- Additional authenticated data (AAD) support
- Tampering detection demonstration

## IoT-Optimized Implementation (`aes_gcm_iot.py`)

This implementation is specifically designed for resource-constrained IoT devices:

### Key Features

1. **Configurable key sizes**
   - AES-128/192/256 bit key options
   - Smaller keys for constrained devices
   - Larger keys for sensitive data

2. **Memory Optimizations**
   - Reusable cipher objects
   - Minimized memory allocations
   - Combined ciphertext format to reduce overhead

3. **Transmission Optimizations**
   - Combined format (IV + Ciphertext + Tag) for efficient transmission
   - Hex encoding for easier transport over text-based protocols
   - Minimal padding and overhead

4. **Security Enhancements for IoT**
   - Persistent IV counter to prevent nonce reuse
   - Counter-based IVs to reduce randomness requirements
   - Proper isolation of crypto parameters

5. **IoT-Specific Use Cases**
   - Optimized for sensor data encryption
   - Low overhead for small payload sizes
   - Energy-efficient operations

## Usage

### Standard Implementation

```python
# Encrypt a message
plaintext = b"This is a secret message"
key, iv, ciphertext, tag = encrypt(plaintext)

# Decrypt the message
decrypted = decrypt(iv, ciphertext, tag, key)
```

### IoT-Optimized Implementation

```python
# Create a cipher with 128-bit key for constrained device
cipher = AesGcmIoT(key_size=128, persistent_iv=True)
key = cipher.generate_key()

# Encrypt sensor data
iv, ciphertext, tag = cipher.encrypt(b"Temperature:23.5C")

# Combined format for efficient transmission
combined, iv_size, tag_size = cipher.encrypt_combined(b"Temperature:23.5C")

# Hex encoding for text protocols
hex_data = cipher.encrypt_hex(b"Temperature:23.5C")
```

## Requirements

- Python 3.6+
- cryptography library (`pip install cryptography`)

## Security Notes

- AES-GCM requires unique IVs (nonces) for each encryption with the same key
- The IoT implementation includes persistent IV handling to prevent nonce reuse
- Authenticated encryption protects against tampering with ciphertext 