import pygame
import math
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from hashlib import sha256
import os

# Initialize Pygame
pygame.init()

def encrypt_data(data, key_str):
    """
    Encrypt the data using AES-256-CBC with a key derived from key_str.
    
    Args:
        data (str): The sentence to encrypt.
        key_str (str): The encryption key provided by the user.
    
    Returns:
        bytes: The IV + ciphertext.
    """
    key = sha256(key_str.encode('utf-8')).digest()  # Hash key to 32 bytes
    iv = os.urandom(16)  # Random 16-byte IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()  # Pad to multiple of 16 bytes
    padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data  # Prepend IV to ciphertext

def bytes_to_bits(byte_list):
    """Convert bytes to a list of bits."""
    return [int(bit) for byte in byte_list for bit in f'{byte:08b}']

def generate_image(message, key_str, output_file, max_size=400 ):
    """
    Generate an image from encrypted data.
    
    Args:
        sentence (str): The sentence to encode.
        key_str (str): The encryption key.
        max_size (int): Maximum image size in pixels.
        output_file (str): File path to save the image.
    """
    # Encrypt the sentence
    encrypted_data = encrypt_data(message, key_str)
    
    # Convert to bits
    bits = bytes_to_bits(encrypted_data)
    N = len(bits)
    
    # Calculate grid size
    S = math.ceil(math.sqrt(N))
    square_size = max_size // S
    if square_size < 1:
        raise ValueError("Data too large for the given max_size")
    
    # Image size
    image_size = S * square_size
    
    # Create surface
    surface = pygame.Surface((image_size, image_size))
    
    # Define colors
    BLACK = (0, 0, 0)    # Represents 1
    GREY = (128, 128, 128)  # Represents 0
    WHITE = (255, 255, 255)  # Unused space
    
    # Draw the grid
    for i in range(S):
        for j in range(S):
            index = i * S + j
            if index < N:
                color = BLACK if bits[index] == 1 else GREY
            else:
                color = WHITE  # Fill remaining space with white
            rect = pygame.Rect(j * square_size, i * square_size, square_size, square_size)
            pygame.draw.rect(surface, color, rect)
    
    # Save the image
    output_file = output_file + ".png"
    pygame.image.save(surface, output_file)
    print(f"Image saved as {output_file}")

# Example usage
if __name__ == "__main__":
    #sentence = input("Enter message: ")
    message = """Hello World."
    """
    output_file = input("Enter image name with no extension: ")
    key = input("Enter the encryption key: ")
    generate_image(message, key, output_file)