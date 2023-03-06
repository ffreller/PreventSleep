from funcs import move_if_idle

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="My parser")
    parser.add_argument('--check_interval', type=float)
    parser.add_argument('--max_running_time', type=float, default=None)
    args = parser.parse_args()
    check_interval = args.check_interval
    max_running_time = args.max_running_time
    if type(check_interval) != float:
        print("You need to pass the number of minutes")
    else:
        move_if_idle(check_interval, max_running_time)



