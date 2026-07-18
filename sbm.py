import os
import sys
import lzma
import tkinter as tk

PRESETS = {
    'r': 'ff0000ff', 'g': '00ff00ff', 'l': '000000ff', 'w': 'ffffffff',
    'x': '00000000', 'o': 'ffa500ff', 'y': 'ffff00ff', 'p': '800080ff',
    'i': '4b0082ff', 't': '00ffffff', 'h': 'a52a2aff', 'u': '000080ff',
    'v': 'ee82eeff'
}

def clamp(value):
    return max(0, min(255, value))

def apply_math(hex_str, operator, channel, amount):
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    a = hex_str[6:8]
    
    if operator == '+':
        if channel == 'r': r = clamp(r + amount)
        elif channel == 'g': g = clamp(g + amount)
        elif channel == 'b': b = clamp(b + amount)
        else:
            r = clamp(r + amount)
            g = clamp(g + amount)
            b = clamp(b + amount)
    elif operator == '-':
        if channel == 'r': r = clamp(r - amount)
        elif channel == 'g': g = clamp(g - amount)
        elif channel == 'b': b = clamp(b - amount)
        else:
            r = clamp(r - amount)
            g = clamp(g - amount)
            b = clamp(b - amount)
        
    return f"{r:02x}{g:02x}{b:02x}{a}"

def resolve_token(token, index, custom_hex_val=None):
    base = token
    force_solid = False
    
    if base.endswith('x') and len(base) == 7:
        base = base[:-1] + "ff"
    elif base.endswith('x') and len(base) > 1 and not base.startswith('s') and '+' not in base and '-' not in base:
        base = base[:-1]
        force_solid = True
        
    operator = None
    channel = None
    amount = 0
    
    if '+' in base:
        operator = '+'
        parts = base.split('+')
        raw_base = parts[0]
        math_part = parts[1]
    elif '-' in base:
        operator = '-'
        parts = base.split('-')
        raw_base = parts[0]
        math_part = parts[1]
    else:
        raw_base = base
        math_part = None

    if math_part:
        if math_part[0] in ['r', 'g', 'b']:
            channel = math_part[0]
            amount = int(math_part[1:])
        else:
            channel = None
            amount = int(math_part)

    if raw_base in PRESETS:
        hex_val = PRESETS[raw_base]
    elif raw_base == 's':
        if custom_hex_val:
            hex_val = custom_hex_val
        else:
            hex_val = "000000ff"
    elif len(raw_base) == 6:
        hex_val = raw_base + "ff"
    elif len(raw_base) == 8:
        hex_val = raw_base
    else:
        print(f"Syntax Error at pixel {index + 1}: Invalid token '{token}'.")
        sys.exit(1)
        
    if operator:
        hex_val = apply_math(hex_val, operator, channel, amount)
        
    if force_solid:
        hex_val = hex_val[:6] + "ff"
        
    return hex_val

def parse_sbm_file(filename):
    filepath = filename if filename.endswith('.txt') else f"{filename}.txt"
    
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
        
    with open(filepath, 'r') as f:
        raw_content = f.read().strip().replace('\n', '').replace(' ', '')

    if not raw_content.startswith('sbm') or '!' not in raw_content:
        print("Syntax Error: Missing or invalid header. Expected 'sbm[width]!'.")
        sys.exit(1)
        
    header_end = raw_content.index('!')
    header = raw_content[:header_end]
    pixel_data = raw_content[header_end + 1:]
    
    try:
        width = int(header[3:])
    except ValueError:
        print("Syntax Error: Width must be a valid integer.")
        sys.exit(1)
        
    tokens = [t for t in pixel_data.split(',') if t]
    
    if len(tokens) % width != 0:
        print(f"Syntax Error: Grid mismatch. Total pixel count ({len(tokens)}) is not divisible by the defined width ({width}).")
        sys.exit(1)

    used_custom_slot = any(t.startswith('s') for t in tokens)
    custom_hex_val = None

    if used_custom_slot:
        dir_name = os.path.dirname(os.path.abspath(filepath))
        hex_file_path = os.path.join(dir_name, 'hex.txt')
        
        if not os.path.exists(hex_file_path):
            print("Syntax Error: Custom slot 's' was used, but 'hex.txt' is missing from the directory.")
            sys.exit(1)
            
        with open(hex_file_path, 'r') as hf:
            custom_hex_val = hf.read().strip()
            if len(custom_hex_val) != 8 or not all(c in '0123456789abcdefABCDEF' for c in custom_hex_val):
                print("Syntax Error: 'hex.txt' must contain a valid 8-character RGBA hex string.")
                sys.exit(1)

    final_pixels = []
    for idx, token in enumerate(tokens):
        resolved_rgba = resolve_token(token, idx, custom_hex_val)
        final_pixels.append(resolved_rgba)
                
    return width, final_pixels, filepath

def make_sbm(filename):
    width, pixels, filepath = parse_sbm_file(filename)
    
    raw_bytes = bytearray()
    raw_bytes.extend(f"sbm{width}!".encode('utf-8'))
    
    for hex_val in pixels:
        r = int(hex_val[0:2], 16)
        g = int(hex_val[2:4], 16)
        b = int(hex_val[4:6], 16)
        a = int(hex_val[6:8], 16)
        raw_bytes.extend([r, g, b, a])
        
    output_path = os.path.splitext(filepath)[0] + '.sbm'
    compressed = lzma.compress(raw_bytes)
    
    with open(output_path, 'wb') as out:
        out.write(compressed)
        
    print(f"[SUCCESS] Compiled down to compressed file: {os.path.basename(output_path)}")

def view_sbm(filename):
    width, pixels, filepath = parse_sbm_file(filename)
    height = len(pixels) // width
    
    scale = 20
    window_width = width * scale
    window_height = height * scale
    
    root = tk.Tk()
    root.title(f"SBM Viewer - {os.path.basename(filepath)}")
    root.resizable(False, False)
    
    canvas = tk.Canvas(root, width=window_width, height=window_height, bg="black", highlightthickness=0)
    canvas.pack()
    
    for idx, hex_val in enumerate(pixels):
        x = (idx % width) * scale
        y = (idx // width) * scale
        color_rgb = f"#{hex_val[0:6]}"
        canvas.create_rectangle(x, y, x + scale, y + scale, fill=color_rgb, outline="")
        
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  sbm --make   (Compiles the '.txt' file)")
        print("  sbm --view   (Views the '.txt' file)")
        print("  sbm --check  (Checks the '.txt' file)")
        sys.exit(1)
        
    command = sys.argv[1]
    target = ".txt"
    
    if command == "--make":
        make_sbm(target)
    elif command == "--view":
        view_sbm(target)
    elif command == "--check":
        parse_sbm_file(target)
        print(f"[SUCCESS] {target} passed all validation checks!")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)