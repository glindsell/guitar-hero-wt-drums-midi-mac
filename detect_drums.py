import pygame

pygame.init()
pygame.joystick.init()

count = pygame.joystick.get_count()
print(f"Controllers found: {count}")

for i in range(count):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    print(f"{i}: {joy.get_name()}")
    print(f"  buttons: {joy.get_numbuttons()}")
    print(f"  axes: {joy.get_numaxes()}")
    print(f"  hats: {joy.get_numhats()}")

if count == 0:
    raise SystemExit("No controller detected.")

joy = pygame.joystick.Joystick(0)
joy.init()

print("\nHit each pad and the kick pedal. Press Ctrl+C to stop.\n")

while True:
    for event in pygame.event.get():
        print(event)
