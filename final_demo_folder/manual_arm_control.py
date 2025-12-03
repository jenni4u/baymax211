from utils.brick import Motor, reset_brick

# Initialize motors
scanner_motor = Motor("A")
drop_motor = Motor("D")

# Reset encoders to know current position
scanner_motor.reset_encoder()
drop_motor.reset_encoder()

print("=" * 50)
print("MANUAL ARM CONTROL")
print("=" * 50)
print("\nThis tool helps you manually position the arms.")
print("Enter the degrees to move each motor (positive or negative).")
print("Type 'exit' or 'quit' to stop.")
print("Type 'status' to see current positions.")
print("=" * 50)

def move_arms(scanner_degrees, drop_degrees):
    """Move both arms by the specified degrees."""
    try:
        if scanner_degrees != 0:
            current_scanner = scanner_motor.get_position()
            scanner_motor.set_dps(50)
            scanner_motor.set_position(current_scanner + scanner_degrees)
            print(f"Moving scanner arm {scanner_degrees:+d}° (to {current_scanner + scanner_degrees}°)")
        
        if drop_degrees != 0:
            current_drop = drop_motor.get_position()
            drop_motor.set_dps(50)
            drop_motor.set_position(current_drop + drop_degrees)
            print(f"Moving drop arm {drop_degrees:+d}° (to {current_drop + drop_degrees}°)")
        
        # Wait for movement to complete
        import time
        time.sleep(abs(scanner_degrees) / 50 + abs(drop_degrees) / 50 + 0.5)
        
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)
        
    except Exception as e:
        print(f"Error moving arms: {e}")
        scanner_motor.set_dps(0)
        drop_motor.set_dps(0)

def show_status():
    """Display current motor positions."""
    scanner_pos = scanner_motor.get_position()
    drop_pos = drop_motor.get_position()
    print(f"\n--- Current Positions ---")
    print(f"Scanner arm: {scanner_pos}°")
    print(f"Drop arm:    {drop_pos}°")
    print("-" * 25)

try:
    show_status()
    print("\n")
    
    while True:
        try:
            # Get scanner motor input
            scanner_input = input("scanner_arm (degrees): ").strip().lower()
            
            if scanner_input in ['exit', 'quit', 'q']:
                print("\nExiting...")
                break
            
            if scanner_input == 'status':
                show_status()
                continue
            
            # Get drop motor input
            drop_input = input("drop_arm (degrees):    ").strip().lower()
            
            if drop_input in ['exit', 'quit', 'q']:
                print("\nExiting...")
                break
            
            if drop_input == 'status':
                show_status()
                continue
            
            # Parse degrees
            try:
                scanner_degrees = int(scanner_input) if scanner_input else 0
                drop_degrees = int(drop_input) if drop_input else 0
                
                if scanner_degrees == 0 and drop_degrees == 0:
                    print("No movement requested (both inputs are 0).\n")
                    continue
                
                move_arms(scanner_degrees, drop_degrees)
                show_status()
                print()
                
            except ValueError:
                print("Error: Please enter valid integers for degrees.\n")
                continue
        
        except KeyboardInterrupt:
            print("\n\nInterrupted! Exiting...")
            break
        
except Exception as e:
    print(f"\nUnexpected error: {e}")
    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)

finally:
    print("\nStopping motors and cleaning up...")
    scanner_motor.set_dps(0)
    drop_motor.set_dps(0)
    reset_brick()
    print("Done. Arms should be in position.")
