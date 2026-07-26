#!/usr/bin/env python3
"""
Asta - A simple autoclicker tool
Click automatically at specified intervals
"""

import mouse
import time
import keyboard
from typing import Optional

class Asta:
    def __init__(self, interval: float = 0.1, button: str = "left"):
        """
        Initialize the autoclicker.
        
        Args:
            interval: Time between clicks in seconds (default: 0.1)
            button: Mouse button to click - "left", "right", or "middle" (default: "left")
        """
        self.interval = interval
        self.button = button
        self.is_running = False
        self.start_key = "s"  # Press 's' to start
        self.stop_key = "e"   # Press 'e' to stop
        
    def start(self):
        """Start the autoclicker"""
        self.is_running = True
        print(f"✓ Autoclicker started! Clicking every {self.interval}s")
        print(f"Press '{self.stop_key}' to stop, or Ctrl+C to exit")
        
        try:
            while self.is_running:
                if keyboard.is_pressed(self.stop_key):
                    self.stop()
                    break
                
                mouse.click(self.button)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the autoclicker"""
        self.is_running = False
        print("✗ Autoclicker stopped")
    
    def run_interactive(self):
        """Run the autoclicker with interactive controls"""
        print("=" * 50)
        print("Asta - Autoclicker")
        print("=" * 50)
        print(f"Click interval: {self.interval}s")
        print(f"Button: {self.button}")
        print(f"\nPress '{self.start_key}' to start clicking")
        print(f"Press '{self.stop_key}' to stop clicking")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                if keyboard.is_pressed(self.start_key):
                    self.start()
                    time.sleep(0.3)  # Debounce
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("\n✓ Asta closed")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Asta - Simple Autoclicker")
    parser.add_argument("--interval", type=float, default=0.1, 
                        help="Time between clicks in seconds (default: 0.1)")
    parser.add_argument("--button", type=str, default="left", 
                        choices=["left", "right", "middle"],
                        help="Mouse button to click (default: left)")
    parser.add_argument("--start-key", type=str, default="s",
                        help="Key to start clicking (default: s)")
    parser.add_argument("--stop-key", type=str, default="e",
                        help="Key to stop clicking (default: e)")
    
    args = parser.parse_args()
    
    clicker = Asta(interval=args.interval, button=args.button)
    clicker.start_key = args.start_key
    clicker.stop_key = args.stop_key
    
    clicker.run_interactive()


if __name__ == "__main__":
    main()
