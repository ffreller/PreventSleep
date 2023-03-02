def print_with_time(text):
    from datetime import datetime
    print(f"{datetime.now().strftime('%H:%M:%S')} - {text}")
    

def get_moves():
    from random import randint
    from pyautogui import size as screen_size
    max1, max2 = screen_size()
    rand1, rand2 = randint(0, max1), randint(0, max2)
    return rand1, rand2


def random_move():
    from pyautogui import moveTo
    pos1, pos2 = get_moves()
    moveTo(pos1, pos2)


def random_moves_and_press(n_times, interval_seconds):
    from pyautogui import press, click
    from time import sleep
    for _ in range(n_times):
        random_move()
        click(button="right")
        press("esc")
        sleep(interval_seconds)
    

    
def move_if_idle(max_minutes):
    from time import sleep
    from win32api import GetCursorPos
    print_with_time(f"Initializing...\n")
    max_seconds = int(max_minutes*60)
    while True:
        init_cursor_pos = GetCursorPos()
        sleep(max_seconds)
        cursor_pos = GetCursorPos()
        if cursor_pos == init_cursor_pos:
            random_moves_and_press(n_times=5, interval_seconds=.25)
            print_with_time(f"Moved from {cursor_pos} to {GetCursorPos()}")
        else:
            print_with_time(f"I won't interrupt. Pos: {cursor_pos}")
            continue
        

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="My parser")
    max_minutes_type = float
    parser.add_argument('--max_minutes', type=max_minutes_type)
    args = parser.parse_args()
    max_minutes = args.max_minutes
    if type(max_minutes) != max_minutes_type:
        print("You need to pass the number of minutes")
    else:
        move_if_idle(max_minutes)



