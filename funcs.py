def move_if_idle(check_interval: float, max_running_time: float):
    """
    Moves the cursor periodically and performs actions if the cursor remains idle.

    Parameters:
    - check_interval (float): Time in minutes between cursor position checks.
    - max_running_time (float or None): Maximum time in minutes for the script to run. If None, the script runs indefinitely.
    """
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


def print_with_time(text: str):
    """
    Prints a timestamp followed by the provided text.

    Parameters:
    - text (str): The text to be printed.
    """
    from datetime import datetime
    print(f"{datetime.now().strftime('%H:%M:%S')} - {text}")
    

def get_moves():
    """
    Generates random cursor positions within the screen size.

    Returns:
    - tuple: Two integers representing random cursor positions.
    """
    from random import randint
    from pyautogui import size as screen_size
    max1, max2 = screen_size()
    rand1, rand2 = randint(0, max1), randint(0, max2)
    return rand1, rand2


def random_move():
    """
    Moves the cursor to a random position on the screen.
    """
    from pyautogui import moveTo
    pos1, pos2 = get_moves()
    moveTo(pos1, pos2)


def random_moves_and_press(n_times: int, interval_seconds: float):
    """
    Performs a sequence of actions:
    1. Moves the cursor to a random position.
    2. Right-clicks the mouse.
    3. Presses the "esc" key.
    4. Sleeps for a specified interval.

    Parameters:
    - n_times (int): Number of times to perform the sequence.
    - interval_seconds (float): Time in seconds to sleep between sequences.
    """
    from pyautogui import press, click
    from time import sleep
    for _ in range(n_times):
        random_move()
        click(button="right")
        press("esc")
        sleep(interval_seconds)
    

    
