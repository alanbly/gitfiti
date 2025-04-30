#!/usr/bin/env python3
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def render_char_to_binary(font_path, char, font_size, width=None):
    """
    Render a character to a binary grid representation using the specified font.
    The height is fixed at 7 pixels, and the width is calculated based on aspect ratio.
    """
    # Create a font object with the specified size
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Error loading font: {e}")
        sys.exit(1)
    
    # Get approximate size of the character
    try:
        # For newer Pillow versions
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
    except AttributeError:
        # For older Pillow versions
        char_width, char_height = font.getsize(char)
    
    # Fixed height for grid
    grid_height = 7
    
    # Calculate width based on aspect ratio or use specified width
    if width is None:
        # Maintain aspect ratio but ensure at least 1 pixel wide
        grid_width = max(1, round((char_width / char_height) * grid_height)) if char_height > 0 else 1
    else:
        grid_width = width
    
    # Create an image to render the character
    # Make it larger to get better quality before downscaling
    scale_factor = 4
    img = Image.new('L', (grid_width * scale_factor, grid_height * scale_factor), color=0)
    draw = ImageDraw.Draw(img)
    
    # Calculate position to center the character
    try:
        # For newer Pillow versions
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
    except AttributeError:
        # For older Pillow versions
        char_width, char_height = font.getsize(char)
    
    x = (grid_width * scale_factor - char_width) // 2
    y = (grid_height * scale_factor - char_height) // 2
    
    # Draw the character
    draw.text((x, y), char, font=font, fill=255)
    
    # Resize image to our fixed grid size
    img = img.resize((grid_width, grid_height), Image.LANCZOS)
    
    # Convert to binary grid (0s and 1s)
    threshold = 128  # Threshold for determining binary value
    binary_grid = []
    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            pixel = img.getpixel((x, y))
            binary_value = 1 if pixel >= threshold else 0
            row.append(binary_value)
        binary_grid.append(row)
    
    return binary_grid

def format_binary_grid(binary_grid):
    """Format a binary grid as a string of 0s and 1s."""
    return '\n'.join(''.join(str(cell) for cell in row) for row in binary_grid)

def render_charset(font_path, font_size, start_char=32, end_char=127, fixed_width=None):
    """Render a range of characters from the font and return their binary grids."""
    result = {}
    for char_code in range(start_char, end_char + 1):
        char = chr(char_code)
        try:
            binary_grid = render_char_to_binary(font_path, char, font_size, fixed_width)
            result[char] = binary_grid
        except Exception as e:
            print(f"Warning: Error rendering character '{char}' (code {char_code}): {e}")
    
    return result

def save_to_file(binary_data, output_file):
    """Save the binary grid data to a file."""
    with open(output_file, 'w') as f:
        for char, grid in binary_data.items():
            if char in '\'"\\':  # Handle special characters
                char_repr = repr(char)
            else:
                char_repr = f"'{char}'"
            
            f.write(f"Character: {char_repr} (ASCII: {ord(char)})\n")
            f.write(format_binary_grid(grid))
            f.write('\n\n')

def main():
    parser = argparse.ArgumentParser(description='Convert a TTF font to binary grid representations')
    parser.add_argument('font_path', help='Path to the TTF font file')
    parser.add_argument('--size', type=int, default=20, help='Font size to use for rendering (default: 20)')
    parser.add_argument('--start', type=int, default=32, help='Starting ASCII character code (default: 32)')
    parser.add_argument('--end', type=int, default=127, help='Ending ASCII character code (default: 127)')
    parser.add_argument('--width', type=int, help='Fixed width for all characters (default: calculated from aspect ratio)')
    parser.add_argument('--output', '-o', default='font_binary.txt', help='Output file (default: font_binary.txt)')
    
    args = parser.parse_args()
    
    print(f"Processing font: {args.font_path}")
    print(f"Rendering characters from ASCII {args.start} to {args.end}")
    
    # Render all characters
    binary_data = render_charset(args.font_path, args.size, args.start, args.end, args.width)
    
    # Save to file
    save_to_file(binary_data, args.output)
    
    print(f"Binary grid data saved to: {args.output}")
    print(f"Processed {len(binary_data)} characters")

if __name__ == "__main__":
    main()