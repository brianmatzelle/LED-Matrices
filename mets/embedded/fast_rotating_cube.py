# SPDX-FileCopyrightText: 2024 Brian Matzelle
#
# SPDX-License-Identifier: MIT

import time
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from os import getenv

# Matrix dimensions
MATRIX_WIDTH = int(getenv("MATRIX_WIDTH", "64"))
MATRIX_HEIGHT = int(getenv("MATRIX_HEIGHT", "64"))

# Pre-computed sine/cosine lookup table (scaled by 1000 for integer math)
SINE_TABLE = []
COSINE_TABLE = []
for i in range(360):
    import math
    angle = i * math.pi / 180
    SINE_TABLE.append(int(math.sin(angle) * 1000))
    COSINE_TABLE.append(int(math.cos(angle) * 1000))

class FastRotatingCube:
    def __init__(self):
        # Initialize MatrixPortal
        self.matrixportal = MatrixPortal(
            width=MATRIX_WIDTH,
            height=MATRIX_HEIGHT,
            bit_depth=4,  # Reduced bit depth for faster updates
            debug=False
        )
        
        # Dim the display (0.0 = off, 1.0 = full brightness)
        self.matrixportal.display.brightness = 0.3
        
        # Create a bitmap to hold our pixel data
        self.bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 8)
        
        # Create a simple color palette (dimmed colors as alternative)
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
        
        # Define cube vertices (scaled by 1000 for integer math)
        self.vertices = [
            [-1000, -1000, -1000],  # 0: Back bottom left
            [1000, -1000, -1000],   # 1: Back bottom right
            [1000, 1000, -1000],    # 2: Back top right
            [-1000, 1000, -1000],   # 3: Back top left
            [-1000, -1000, 1000],   # 4: Front bottom left
            [1000, -1000, 1000],    # 5: Front bottom right
            [1000, 1000, 1000],     # 6: Front top right
            [-1000, 1000, 1000]     # 7: Front top left
        ]
        
        # Define cube edges (which vertices are connected)
        self.edges = [
            # Back face
            [0, 1], [1, 2], [2, 3], [3, 0],
            # Front face
            [4, 5], [5, 6], [6, 7], [7, 4],
            # Connecting edges
            [0, 4], [1, 5], [2, 6], [3, 7]
        ]
        
        # Rotation angles (in degrees for lookup table)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
        # Animation speed (degrees per frame)
        self.rotation_speed = 3
        
        # Scale factor (integer, will be divided by 1000)
        self.scale = min(MATRIX_WIDTH, MATRIX_HEIGHT) * 300  # 0.3 * 1000
        
        # Center of the display (scaled by 1000)
        self.center_x = (MATRIX_WIDTH * 1000) // 2
        self.center_y = (MATRIX_HEIGHT * 1000) // 2
        
        # Previous frame pixels to track changes
        self.previous_pixels = set()
        
        # Pre-allocate arrays for transformed vertices
        self.transformed_vertices = [[0, 0] for _ in range(8)]
    
    def set_brightness(self, brightness):
        """Set display brightness (0.0 = off, 1.0 = full brightness)"""
        self.matrixportal.display.brightness = max(0.0, min(1.0, brightness))
        print(f"Brightness set to {brightness}")
    
    def create_dimmed_palette(self, dim_factor=0.3):
        """Create a dimmed color palette (alternative to display brightness)"""
        # Dim factor: 0.0 = black, 1.0 = full brightness
        self.palette[0] = 0x000000  # Black (unchanged)
        self.palette[1] = int(0xFF * dim_factor) << 16  # Dimmed Red
        self.palette[2] = int(0xFF * dim_factor) << 8   # Dimmed Green
        self.palette[3] = int(0xFF * dim_factor)        # Dimmed Blue
        self.palette[4] = (int(0xFF * dim_factor) << 16) | (int(0xFF * dim_factor) << 8)  # Dimmed Yellow
        self.palette[5] = (int(0xFF * dim_factor) << 16) | int(0xFF * dim_factor)         # Dimmed Magenta
        self.palette[6] = (int(0xFF * dim_factor) << 8) | int(0xFF * dim_factor)          # Dimmed Cyan
        self.palette[7] = (int(0xFF * dim_factor) << 16) | (int(0xFF * dim_factor) << 8) | int(0xFF * dim_factor)  # Dimmed White
        print(f"Palette dimmed to {dim_factor * 100:.0f}% brightness")
    
    def fast_clear(self, pixels_to_clear):
        """Clear only specific pixels instead of entire display"""
        for x, y in pixels_to_clear:
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                self.bitmap[x, y] = 0
    
    def set_pixel(self, x, y, color_index):
        """Set a single pixel to a specific color"""
        if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
            self.bitmap[x, y] = color_index
    
    def fast_rotate_point(self, point):
        """Fast integer-based rotation using lookup tables"""
        x, y, z = point
        
        # Get sine and cosine values from lookup tables
        sin_x = SINE_TABLE[self.angle_x % 360]
        cos_x = COSINE_TABLE[self.angle_x % 360]
        sin_y = SINE_TABLE[self.angle_y % 360]
        cos_y = COSINE_TABLE[self.angle_y % 360]
        sin_z = SINE_TABLE[self.angle_z % 360]
        cos_z = COSINE_TABLE[self.angle_z % 360]
        
        # Rotate around X-axis
        new_y = (y * cos_x - z * sin_x) // 1000
        new_z = (y * sin_x + z * cos_x) // 1000
        y, z = new_y, new_z
        
        # Rotate around Y-axis
        new_x = (x * cos_y + z * sin_y) // 1000
        new_z = (-x * sin_y + z * cos_y) // 1000
        x, z = new_x, new_z
        
        # Rotate around Z-axis
        new_x = (x * cos_z - y * sin_z) // 1000
        new_y = (x * sin_z + y * cos_z) // 1000
        x, y = new_x, new_y
        
        return [x, y, z]
    
    def fast_project_to_2d(self, point):
        """Fast integer-based 2D projection"""
        x, y, z = point
        
        # Simple orthographic projection with integer math
        screen_x = (x * self.scale // 1000 + self.center_x) // 1000
        screen_y = (y * self.scale // 1000 + self.center_y) // 1000
        
        return screen_x, screen_y
    
    def fast_draw_line(self, x1, y1, x2, y2, color_index, current_pixels):
        """Fast line drawing with pixel tracking"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x_step = 1 if x1 < x2 else -1
        y_step = 1 if y1 < y2 else -1
        
        error = dx - dy
        x, y = x1, y1
        
        while True:
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                self.bitmap[x, y] = color_index
                current_pixels.add((x, y))
            
            if x == x2 and y == y2:
                break
                
            error2 = 2 * error
            
            if error2 > -dy:
                error -= dy
                x += x_step
            
            if error2 < dx:
                error += dx
                y += y_step
    
    def fast_draw_cube(self):
        """Fast cube drawing with optimized pixel updates"""
        # Track current frame pixels
        current_pixels = set()
        
        # Transform all vertices with pre-allocated array
        for i, vertex in enumerate(self.vertices):
            rotated = self.fast_rotate_point(vertex)
            self.transformed_vertices[i] = self.fast_project_to_2d(rotated)
        
        # Draw all edges
        for edge in self.edges:
            start_vertex = self.transformed_vertices[edge[0]]
            end_vertex = self.transformed_vertices[edge[1]]
            
            # Use different colors for different types of edges
            if edge in [[0, 1], [1, 2], [2, 3], [3, 0]]:  # Back face
                color = 1  # Red
            elif edge in [[4, 5], [5, 6], [6, 7], [7, 4]]:  # Front face
                color = 2  # Green
            else:  # Connecting edges
                color = 3  # Blue
            
            self.fast_draw_line(
                start_vertex[0], start_vertex[1],
                end_vertex[0], end_vertex[1],
                color, current_pixels
            )
        
        # Clear only pixels from previous frame that aren't used in current frame
        pixels_to_clear = self.previous_pixels - current_pixels
        self.fast_clear(pixels_to_clear)
        
        # Update previous pixels for next frame
        self.previous_pixels = current_pixels
    
    def update_rotation(self):
        """Update rotation angles for animation"""
        self.angle_x = (self.angle_x + self.rotation_speed) % 360
        self.angle_y = (self.angle_y + int(self.rotation_speed * 0.7)) % 360
        self.angle_z = (self.angle_z + int(self.rotation_speed * 0.5)) % 360
    
    def run_animation(self, duration=None):
        """Run the fast rotating cube animation"""
        print("Starting FAST rotating cube animation...")
        print(f"Matrix size: {MATRIX_WIDTH}x{MATRIX_HEIGHT}")
        print("Optimizations: Integer math, lookup tables, differential updates")
        print("Colors: Red=back face, Green=front face, Blue=connecting edges")
        print(f"Display brightness: {self.matrixportal.display.brightness}")
        print("Press Ctrl+C to stop")
        
        # Initial clear
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.bitmap[x, y] = 0
        
        start_time = time.time()
        frame_count = 0
        last_fps_time = start_time
        
        try:
            while True:
                frame_start = time.monotonic()
                
                # Check if we should stop (if duration is specified)
                if duration and time.time() - start_time >= duration:
                    break
                
                # Draw the current frame
                self.fast_draw_cube()
                
                # Update rotation for next frame
                self.update_rotation()
                
                frame_count += 1
                
                # Print FPS every 2 seconds
                current_time = time.time()
                if current_time - last_fps_time >= 2.0:
                    elapsed = current_time - last_fps_time
                    fps = (frame_count - (frame_count - int(elapsed * 60))) / elapsed
                    print(f"FPS: {fps:.1f}")
                    last_fps_time = current_time
                
                # Very minimal delay for maximum speed
                frame_time = time.monotonic() - frame_start
                if frame_time < 0.016:  # Try to maintain ~60 FPS
                    time.sleep(0.016 - frame_time)
        
        except KeyboardInterrupt:
            print("\nAnimation stopped by user")
        
        finally:
            # Clear display when done
            for y in range(MATRIX_HEIGHT):
                for x in range(MATRIX_WIDTH):
                    self.bitmap[x, y] = 0
            print("Animation complete!")

# Run the animation
if __name__ == "__main__":
    cube = FastRotatingCube()
    
    # Example: Adjust brightness if needed
    # cube.set_brightness(0.1)  # Very dim
    # cube.set_brightness(0.5)  # Medium brightness
    # cube.set_brightness(1.0)  # Full brightness
    
    # Alternative: Use dimmed colors instead of display brightness
    # cube.create_dimmed_palette(0.2)  # 20% brightness colors
    
    cube.run_animation() 