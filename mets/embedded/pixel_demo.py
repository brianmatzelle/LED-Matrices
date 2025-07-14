# SPDX-FileCopyrightText: 2024 Brian Matzelle
#
# SPDX-License-Identifier: MIT

import time
import displayio
import board
import terminalio
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_bitmap_font import bitmap_font
from os import getenv

# Matrix dimensions (adjust these to match your actual matrix)
MATRIX_WIDTH = getenv("MATRIX_WIDTH")
MATRIX_HEIGHT = getenv("MATRIX_HEIGHT")

class PixelDemo:
    def __init__(self):
        # Initialize MatrixPortal
        self.matrixportal = MatrixPortal(
            width=MATRIX_WIDTH,
            height=MATRIX_HEIGHT,
            bit_depth=6,  # Higher bit depth for more colors
            debug=False
        )
        
        # Create a bitmap to hold our pixel data
        self.bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 256)
        
        # Create a color palette
        self.palette = displayio.Palette(256)
        self._create_palette()
        
        # Create the tile grid
        self.tile_grid = displayio.TileGrid(
            self.bitmap,
            pixel_shader=self.palette
        )
        
        # Create the main group
        self.main_group = displayio.Group()
        self.main_group.append(self.tile_grid)
        
        # Show the display
        self.matrixportal.display.root_group = self.main_group
    
    def _create_palette(self):
        """Create a color palette for the demo"""
        # Fill palette with various colors
        for i in range(256):
            if i < 32:
                # Red gradient
                self.palette[i] = (i * 8, 0, 0)
            elif i < 64:
                # Green gradient
                self.palette[i] = (0, (i - 32) * 8, 0)
            elif i < 96:
                # Blue gradient
                self.palette[i] = (0, 0, (i - 64) * 8)
            elif i < 128:
                # Yellow gradient
                self.palette[i] = ((i - 96) * 8, (i - 96) * 8, 0)
            elif i < 160:
                # Cyan gradient
                self.palette[i] = (0, (i - 128) * 8, (i - 128) * 8)
            elif i < 192:
                # Magenta gradient
                self.palette[i] = ((i - 160) * 8, 0, (i - 160) * 8)
            else:
                # White gradient
                self.palette[i] = ((i - 192) * 4, (i - 192) * 4, (i - 192) * 4)
    
    def coordinate_grid(self):
        """Display a coordinate grid pattern"""
        print("Displaying coordinate grid...")
        
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                # Create a pattern based on x and y coordinates
                if x == 0 or y == 0:
                    # Border in bright white
                    color_index = 255
                elif x % 8 == 0 and y % 8 == 0:
                    # Grid points in bright red
                    color_index = 31
                elif x % 4 == 0:
                    # Vertical lines in blue
                    color_index = 95
                elif y % 4 == 0:
                    # Horizontal lines in green
                    color_index = 63
                else:
                    # Fill with a pattern based on position
                    color_index = (x + y * 2) % 128
                
                self.bitmap[x, y] = color_index
        
        print("Coordinate grid displayed")
    
    def rainbow_gradient(self):
        """Display a rainbow gradient"""
        print("Displaying rainbow gradient...")
        
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                # Create rainbow based on x position
                hue = (x * 255) // MATRIX_WIDTH
                self.bitmap[x, y] = hue
        
        print("Rainbow gradient displayed")
    
    def corner_markers(self):
        """Display markers at each corner"""
        print("Displaying corner markers...")
        
        # Clear the display first
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.bitmap[x, y] = 0
        
        # Top-left corner (RED)
        for i in range(5):
            for j in range(5):
                if i < MATRIX_WIDTH and j < MATRIX_HEIGHT:
                    self.bitmap[i, j] = 31  # Bright red
        
        # Top-right corner (GREEN)
        for i in range(5):
            for j in range(5):
                x = MATRIX_WIDTH - 1 - i
                if x >= 0 and j < MATRIX_HEIGHT:
                    self.bitmap[x, j] = 63  # Bright green
        
        # Bottom-left corner (BLUE)
        for i in range(5):
            for j in range(5):
                y = MATRIX_HEIGHT - 1 - j
                if i < MATRIX_WIDTH and y >= 0:
                    self.bitmap[i, y] = 95  # Bright blue
        
        # Bottom-right corner (YELLOW)
        for i in range(5):
            for j in range(5):
                x = MATRIX_WIDTH - 1 - i
                y = MATRIX_HEIGHT - 1 - j
                if x >= 0 and y >= 0:
                    self.bitmap[x, y] = 127  # Bright yellow
        
        # Center marker (WHITE)
        center_x = MATRIX_WIDTH // 2
        center_y = MATRIX_HEIGHT // 2
        for i in range(-2, 3):
            for j in range(-2, 3):
                x = center_x + i
                y = center_y + j
                if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                    self.bitmap[x, y] = 255  # Bright white
        
        print("Corner markers displayed")
    
    def coordinate_numbers(self):
        """Display coordinate numbers (for larger matrices)"""
        print("Displaying coordinate numbers...")
        
        # Clear the display first
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.bitmap[x, y] = 0
        
        # Add number labels if matrix is large enough
        if MATRIX_WIDTH >= 32 and MATRIX_HEIGHT >= 16:
            # Create text labels for key coordinates
            group = displayio.Group()
            font = bitmap_font.load_font("fonts/Roboto-Medium-7pt.bdf")
            
            # Top-left (0,0)
            label_00 = Label(font, text="0,0", color=0xFF0000)
            label_00.x = 1
            label_00.y = 6
            group.append(label_00)
            
            # Top-right
            label_tr = Label(font, text=f"{MATRIX_WIDTH-1},0", color=0x00FF00)
            label_tr.x = MATRIX_WIDTH - 20
            label_tr.y = 6
            group.append(label_tr)
            
            # Bottom-left
            label_bl = Label(font, text=f"0,{MATRIX_HEIGHT-1}", color=0x0000FF)
            label_bl.x = 1
            label_bl.y = MATRIX_HEIGHT - 2
            group.append(label_bl)
            
            # Bottom-right
            label_br = Label(font, text=f"{MATRIX_WIDTH-1},{MATRIX_HEIGHT-1}", color=0xFFFF00)
            label_br.x = MATRIX_WIDTH - 30
            label_br.y = MATRIX_HEIGHT - 2
            group.append(label_br)
            
            # Add the text group
            self.main_group.append(group)
        
        print("Coordinate numbers displayed")
    
    def run_demo(self):
        """Run through all the demo patterns"""
        demos = [
            ("Corner Markers", self.corner_markers),
            ("Coordinate Grid", self.coordinate_grid),
            ("Rainbow Gradient", self.rainbow_gradient),
            ("Coordinate Numbers", self.coordinate_numbers)
        ]
        
        print(f"Starting pixel demo on {MATRIX_WIDTH}x{MATRIX_HEIGHT} matrix")
        
        for name, demo_func in demos:
            print(f"\n--- {name} ---")
            demo_func()
            time.sleep(5)  # Show each demo for 5 seconds
        
        print("\nDemo complete!")

# Run the demo
if __name__ == "__main__":
    demo = PixelDemo()
    demo.run_demo() 