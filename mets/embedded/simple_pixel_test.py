# SPDX-FileCopyrightText: 2024 Brian Matzelle
#
# SPDX-License-Identifier: MIT

import time
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from os import getenv

# Matrix dimensions (adjust these to match your actual matrix)
MATRIX_WIDTH = getenv("MATRIX_WIDTH")
MATRIX_HEIGHT = getenv("MATRIX_HEIGHT")

class SimplePixelTest:
    def __init__(self):
        # Initialize MatrixPortal
        self.matrixportal = MatrixPortal(
            width=MATRIX_WIDTH,
            height=MATRIX_HEIGHT,
            bit_depth=6,
            debug=False
        )
        
        # Create a bitmap to hold our pixel data
        self.bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 8)
        
        # Create a simple color palette
        self.palette = displayio.Palette(8)
        self.palette[0] = 0x000000  # Black
        self.palette[1] = 0xFF0000  # Red
        self.palette[2] = 0x00FF00  # Green
        self.palette[3] = 0x0000FF  # Blue
        self.palette[4] = 0xFFFF00  # Yellow
        self.palette[5] = 0xFF00FF  # Magenta
        self.palette[6] = 0x00FFFF  # Cyan
        self.palette[7] = 0xFFFFFF  # White
        
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
    
    def clear_display(self):
        """Clear the display to black"""
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.bitmap[x, y] = 0
    
    def set_pixel(self, x, y, color_index):
        """Set a single pixel to a specific color"""
        if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
            self.bitmap[x, y] = color_index
    
    def draw_line(self, x1, y1, x2, y2, color_index):
        """Draw a simple line between two points"""
        # Simple line drawing - just for testing
        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.set_pixel(x1, y, color_index)
        elif y1 == y2:  # Horizontal line
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.set_pixel(x, y1, color_index)
    
    def test_corners(self):
        """Test the four corners of the display"""
        print("Testing corners...")
        self.clear_display()
        
        # Top-left corner
        self.set_pixel(0, 0, 1)  # Red
        self.set_pixel(1, 0, 1)
        self.set_pixel(0, 1, 1)
        self.set_pixel(1, 1, 1)
        
        # Top-right corner
        self.set_pixel(MATRIX_WIDTH-1, 0, 2)  # Green
        self.set_pixel(MATRIX_WIDTH-2, 0, 2)
        self.set_pixel(MATRIX_WIDTH-1, 1, 2)
        self.set_pixel(MATRIX_WIDTH-2, 1, 2)
        
        # Bottom-left corner
        self.set_pixel(0, MATRIX_HEIGHT-1, 3)  # Blue
        self.set_pixel(1, MATRIX_HEIGHT-1, 3)
        self.set_pixel(0, MATRIX_HEIGHT-2, 3)
        self.set_pixel(1, MATRIX_HEIGHT-2, 3)
        
        # Bottom-right corner
        self.set_pixel(MATRIX_WIDTH-1, MATRIX_HEIGHT-1, 4)  # Yellow
        self.set_pixel(MATRIX_WIDTH-2, MATRIX_HEIGHT-1, 4)
        self.set_pixel(MATRIX_WIDTH-1, MATRIX_HEIGHT-2, 4)
        self.set_pixel(MATRIX_WIDTH-2, MATRIX_HEIGHT-2, 4)
        
        print("Corners: Red=top-left, Green=top-right, Blue=bottom-left, Yellow=bottom-right")
    
    def test_borders(self):
        """Test the borders of the display"""
        print("Testing borders...")
        self.clear_display()
        
        # Top border
        self.draw_line(0, 0, MATRIX_WIDTH-1, 0, 1)  # Red
        
        # Bottom border
        self.draw_line(0, MATRIX_HEIGHT-1, MATRIX_WIDTH-1, MATRIX_HEIGHT-1, 2)  # Green
        
        # Left border
        self.draw_line(0, 0, 0, MATRIX_HEIGHT-1, 3)  # Blue
        
        # Right border
        self.draw_line(MATRIX_WIDTH-1, 0, MATRIX_WIDTH-1, MATRIX_HEIGHT-1, 4)  # Yellow
        
        print("Borders: Red=top, Green=bottom, Blue=left, Yellow=right")
    
    def test_center_cross(self):
        """Test the center of the display with a cross"""
        print("Testing center cross...")
        self.clear_display()
        
        center_x = MATRIX_WIDTH // 2
        center_y = MATRIX_HEIGHT // 2
        
        # Vertical line through center
        self.draw_line(center_x, 0, center_x, MATRIX_HEIGHT-1, 5)  # Magenta
        
        # Horizontal line through center
        self.draw_line(0, center_y, MATRIX_WIDTH-1, center_y, 6)  # Cyan
        
        # Center pixel
        self.set_pixel(center_x, center_y, 7)  # White
        
        print(f"Center cross at ({center_x}, {center_y})")
    
    def test_checkerboard(self):
        """Test with a checkerboard pattern"""
        print("Testing checkerboard...")
        self.clear_display()
        
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                if (x + y) % 2 == 0:
                    self.set_pixel(x, y, 7)  # White
                else:
                    self.set_pixel(x, y, 0)  # Black
        
        print("Checkerboard pattern")
    
    def run_tests(self):
        """Run all pixel tests"""
        tests = [
            ("Corners Test", self.test_corners),
            ("Borders Test", self.test_borders),
            ("Center Cross Test", self.test_center_cross),
            ("Checkerboard Test", self.test_checkerboard)
        ]
        
        print(f"Starting pixel tests on {MATRIX_WIDTH}x{MATRIX_HEIGHT} matrix")
        print("Colors: 0=Black, 1=Red, 2=Green, 3=Blue, 4=Yellow, 5=Magenta, 6=Cyan, 7=White")
        
        for name, test_func in tests:
            print(f"\n--- {name} ---")
            test_func()
            time.sleep(3)  # Show each test for 3 seconds
        
        print("\nAll tests complete!")

# Run the tests
if __name__ == "__main__":
    test = SimplePixelTest()
    test.run_tests() 