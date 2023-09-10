def move_if_idle(check_interval, max_running_time):
    from time import sleep
    from datetime import datetime
    from pyautogui import position
    print_with_time(f"Initializing...\n")
    interval_seconds = int(check_interval*60)
    
    if max_running_time is not None:
        max_running_time_seconds = int(max_running_time*60)
        start_time = datetime.now()
    
    while True:
        init_cursor_pos = position()
        sleep(interval_seconds)
        cursor_pos = position()
        
        if max_running_time is not None:
            now = datetime.now()
            if (now - start_time).seconds >= max_running_time_seconds:
                print(f"Stopping after {max_running_time} minutes")
                return
            
        if cursor_pos == init_cursor_pos:
            random_moves_and_press(n_times=5, interval_seconds=.25)
            print_with_time(f"Moved from {cursor_pos} to {position()}")
        else:
            print_with_time(f"I won't interrupt. Pos: {cursor_pos}")
            continue


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
    

    
