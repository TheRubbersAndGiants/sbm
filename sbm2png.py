import os
import sys
import lzma
import tkinter as tk

def convert_sbm_to_png(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
        
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in ['.sbm', '.sbma']:
        print("Error: Input file must be a compressed .sbm or .sbma file.")
        sys.exit(1)

    with open(filepath, 'rb') as f:
        compressed_data = f.read()
        
    try:
        raw_bytes = lzma.decompress(compressed_data)
    except Exception:
        print("Error: Failed to decompress file. File might be corrupted.")
        sys.exit(1)

    try:
        header_end = raw_bytes.index(b'!')
    except ValueError:
        print("Syntax Error: Invalid file structure. Missing header terminator '!'")
        sys.exit(1)
        
    header = raw_bytes[:header_end].decode('utf-8')
    pixel_bytes = raw_bytes[header_end + 1:]
    
    if header.startswith('sbma'):
        try:
            width = int(header[4:])
        except ValueError:
            print("Syntax Error: Invalid width value in sbma header.")
            sys.exit(1)
    elif header.startswith('sbm'):
        try:
            width = int(header[3:])
        except ValueError:
            print("Syntax Error: Invalid width value in sbm header.")
            sys.exit(1)
    else:
        print("Syntax Error: Unknown file header identifier.")
        sys.exit(1)

    bytes_per_pixel = 4
    if len(pixel_bytes) % bytes_per_pixel != 0:
        print("Error: Pixel byte stream length is mismatched for RGBA format.")
        sys.exit(1)
        
    total_pixels = len(pixel_bytes) // bytes_per_pixel
    if total_pixels % width != 0:
        print("Error: Decompressed pixel grid size does not match the header width.")
        sys.exit(1)
        
    height = total_pixels // width

    root = tk.Tk()
    root.withdraw()
    photo = tk.PhotoImage(width=width, height=height)
    
    for idx in range(total_pixels):
        x = idx % width
        y = idx // width
        
        offset = idx * bytes_per_pixel
        r = pixel_bytes[offset]
        g = pixel_bytes[offset + 1]
        b = pixel_bytes[offset + 2]
        
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        photo.put(color_hex, (x, y))
        
    output_png_path = os.path.splitext(filepath)[0] + '.png'
    photo.write(output_png_path, format='png')
    root.destroy()
    
    print(f"[SUCCESS] Successfully converted {os.path.basename(filepath)} to {os.path.basename(output_png_path)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python sbm2png.py <filename.sbm>")
        print("  python sbm2png.py <filename.sbma>")
        sys.exit(1)
        
    convert_sbm_to_png(sys.argv[1])