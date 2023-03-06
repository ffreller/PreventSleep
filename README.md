This scripts moves your mouse and presses mouse and kerboard buttons with the periodicity you choose. It only acts if your mouse position does not change in a given period of time.

I use it to prevent my PC to go on idle.

**Requirements:**

Python >= 3.8
(only tested in Windows 10)


**Arguments:**

*check_interval* (REQUIRED) - the time in minutes the script will sleep between its periodics checks for inactivity. (NOTE: if you want to prevent a computer action that will check for inactivity in X minutes, you should set this argument to X / 2)

*max_running_time* (OPTIONAL) - number of minutes after which this script should stop. (NOTE: the actual time the script stops also depends on *check_interval*, because this script will check if elapsed_time > *max_running_time* every *check_interval* minutes)


**Install requirements**

pip install -r requirements.txt


**Example run**

python main.py --check_interval=5 --max_running_time=100