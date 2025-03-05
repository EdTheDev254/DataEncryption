from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from hashlib import sha256

def gcd(a, b):
    """Calculate the greatest common divisor."""
    while b:
        a, b = b, a % b
    return a

def find_square_size(img, num_rows=5):
    """Detect the square size in the image."""
    width, height = img.size
    change_diffs = []
    
    for y in range(min(num_rows, height)):
        prev_color = None
        prev_x = None
        for x in range(width):
            color = img.getpixel((x, y))
            if prev_color is None:
                prev_color = color
                prev_x = x
            elif color != prev_color:
                diff = x - prev_x
                if diff > 0:
                    change_diffs.append(diff)
                prev_color = color
                prev_x = x
    
    if not change_diffs:
        raise ValueError("No color changes found to detect square_size")
    
    square_size = change_diffs[0]
    for diff in change_diffs[1:]:
        square_size = gcd(square_size, diff)
        if square_size == 1:
            break
    
    return square_size

def decrypt_data(encrypted_data, key_str):
    """
    Decrypt the data using AES-256-CBC.
    
    Args:
        encrypted_data (bytes): The IV + ciphertext.
        key_str (str): The encryption key.
    
    Returns:
        str: The original sentence.
    """
    key = sha256(key_str.encode('utf-8')).digest()
    iv = encrypted_data[:16]  # First 16 bytes are the IV
    ciphertext = encrypted_data[16:]  # Rest is the ciphertext
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data.decode('utf-8')

def decode_image(image_path, key_str):
    """
    Decode the image back to the original sentence using the encryption key.
    
    Args:
        image_path (str): Path to the image file.
        key_str (str): The encryption key.
    
    Returns:
        str: The decoded sentence.
    """
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    
    # Detect square_size
    square_size = find_square_size(img)
    
    # Calculate grid size
    S = width // square_size
    
    # Extract bits
    bits = []
    for i in range(S):
        for j in range(S):
            x = j * square_size + square_size // 2
            y = i * square_size + square_size // 2
            r, g, b = img.getpixel((x, y))
            if r == g == b == 0:  # Black
                bits.append(1)
            elif r == g == b == 128:  # Grey
                bits.append(0)
            else:  # White (unused space)
                break  # Stop at unused bits
    
    # Convert bits to bytes
    encrypted_data = bytes(int(''.join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits), 8))
    
    # Decrypt the data
    original_string = decrypt_data(encrypted_data, key_str)
    return original_string

# Example usage
if __name__ == "__main__":
    image_path = "test.png"
    key = input("Enter the encryption key: ")
    try:
        decoded_string = decode_image(image_path, key)
        print("Decoded string:", decoded_string)
    except Exception as e:
        print("Error decoding image:", e)