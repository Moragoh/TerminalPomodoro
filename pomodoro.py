#!/usr/bin/python3
import json
import json
import os
import platform
import subprocess
import time
import subprocess
import time
from datetime import datetime

"""Most of this was written by ChatGPT"""

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "pomodoro_settings.json")

main_menu_ascii_art = r"""                                                                                                  
,------.                            ,--.                      
|  .--. ' ,---. ,--,--,--. ,---.  ,-|  | ,---. ,--.--. ,---.  
|  '--' || .-. ||        || .-. |' .-. || .-. ||  .--'| .-. | 
|  | --' ' '-' '|  |  |  |' '-' '\ `-' |' '-' '|  |   ' '-' ' 
`--'      `---' `--`--`--' `---'  `---'  `---' `--'    `---'   
"""

work_ascii_art = r"""
                                                                                   
           .---.                         ,-.  
          /. ./|                     ,--/ /|  
      .--'.  ' ;   ,---.    __  ,-.,--. :/ |  
     /__./ \ : |  '   ,'\ ,' ,'/ /|:  : ' /   
 .--'.  '   \' . /   /   |'  | |' ||  '  /    
/___/ \ |    ' '.   ; ,. :|  |   ,''  |  :    
;   \  \;      :'   | |: :'  :  /  |  |   \   
 \   ;  `      |'   | .; :|  | '   '  : |. \  
  .   \    .\  ;|   :    |;  : |   |  | ' \ \ 
   \   \   ' \ | \   \  / |  , ;   '  : |--'  
    :   '  |--"   `----'   ---'    ;  |,'     
     \   \ ;                       '--'       
      '---"                                                            
                                                     
"""
break_ascii_art = r"""
                                                                                                                                           
,-.----.                           ___     
\    /  \                        ,--.'|_   
;   :    \                       |  | :,'  
|   | .\ :             .--.--.   :  : ' :  
.   : |: |    ,---.   /  /    '.;__,'  /   
|   |  \ :   /     \ |  :  /`./|  |   |    
|   : .  /  /    /  ||  :  ;_  :__,'| :    
;   | |  \ .    ' / | \  \    `. '  : |__  
|   | ;\  \'   ;   /|  `----.   \|  | '.'| 
:   ' | \.''   |  / | /  /`--'  /;  :    ; 
:   : :-'  |   :    |'--'.     / |  ,   /  
|   |.'     \   \  /   `--'---'   ---`-'   
`---'        `----'                        
                                                                                                       
"""

def clear_terminal():
    """Clear the terminal screen."""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def load_config():
    """Load configuration from a file or create a default one if it doesn't exist."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        default_config = {}  # Define your default configuration here
        with open(CONFIG_FILE, 'w') as file:
            json.dump(default_config, file)
        return default_config
    except json.JSONDecodeError:
        return {}


def save_config(config):
    """Save configuration to a file."""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def format_time(seconds):
    """Convert seconds to hours and minutes."""
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return hours, minutes

def get_float_input(prompt):
    """Get a valid float input from the user."""
    while True:
        user_input = input(prompt)
        try:
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_int_input(prompt):
    """Get a valid integer input from the user."""
    while True:
        user_input = input(prompt)
        try:
            return int(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def settings_menu():
    """Display the settings menu and handle user input."""
    while True:
        clear_terminal()
        print("Settings Menu:")
        print("1) Set Work Duration")
        set_duration('work_duration')
        
        print("\n2) Set Short Break Duration")
        set_duration('short_break_duration')
        
        print("\n3) Set Long Break Duration")
        set_duration('long_break_duration')
        
        print("\n4) Set Number of Cycles")
        set_cycles()
        
        print("\n5) Go back to Main Menu")

        user_input = input("Press m to go back to the main menu \n")
        if user_input == 'm':
            # Break the loop and go back to the main menu upon any user input
            break

def set_duration(duration_key):
    """Set the duration (work, short break, or long break)."""
    while True:
        user_input = get_float_input(f"Enter {duration_key.replace('_', ' ').title()} in minutes: ")
        if user_input > 0:
            config = load_config()
            config[duration_key] = user_input
            save_config(config)
            print(f"{duration_key.replace('_', ' ').title()} set to {user_input} minutes.")
            break
        else:
            print("Duration must be greater than 0.")

def set_cycles():
    """Set the number of cycles."""
    while True:
        user_input = get_int_input("Enter the number of cycles: ")
        if user_input > 0:
            config = load_config()
            config['cycles'] = user_input
            save_config(config)
            print(f"Number of cycles set to {user_input}.")
            break
        else:
            print("Number of cycles must be greater than 0.")

def send_notification(title, message, duration=3):
    """Send macOS persistent notification using AppleScript."""
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script])

    # Wait for the specified duration (in seconds)
    subprocess.run(['sleep', str(duration)])

def get_total_work_time_today():
    """Get the total work time for the current day."""
    today = datetime.now().strftime("%Y-%m-%d")
    total_work_time_key = f"total_work_time_{today}"

    config = load_config()
    total_work_seconds = config.get(total_work_time_key, 0)
    total_hours, total_minutes = format_time(total_work_seconds)
    return f"{total_hours} hours {total_minutes} minutes"

def get_longest_time_worked():
    """Get the longest time worked."""
    config = load_config()

    # Retrieve the longest time worked and the day it was achieved
    longest_time_worked = config.get('longest_time_worked', 0)
    longest_time_worked_date = config.get('longest_time_worked_date', "N/A")
    
    # Convert the time to hours and minutes
    longest_hours, longest_minutes = format_time(longest_time_worked)

    # Format the time into a readable string
    longest_time_formatted = f"{longest_hours} hours {longest_minutes} minutes"

    return longest_time_formatted, longest_time_worked_date


def pomodoro_timer(work_duration, short_break_duration, long_break_duration, cycles):
    """Run the Pomodoro timer."""
    # Get the current day in the format YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    # Create a key for the total work time for the current day
    total_work_time_key = f"total_work_time_{today}"

    # Load the configuration to get the last completed cycle and total work time for the day
    config = load_config()
    last_completed_cycle = config.get('last_completed_cycle', 0)
    total_work_time = config.get(total_work_time_key, 0)
    longest_time_worked = config.get('longest_time_worked', 0)

    # Loop through cycles
    for cycle in range(last_completed_cycle + 1, cycles + 1):
        total_work_time = config.get(total_work_time_key, 0)
        longest_time_worked = config.get('longest_time_worked', 0)

        # Work session
        print(f"Cycle {cycle}/{cycles}")
        art_to_display = work_ascii_art  # Update ASCII art for work session
        # Update total work time and display countdown
        total_work_time += countdown(int(work_duration * 60), total_work_time, cycle, cycles, art_to_display)
        
        # Save work time on end
        config[total_work_time_key] = total_work_time
        save_config(config)
        
        send_notification("Pomodoro", "Work session completed!")  # Notification for work session
        if total_work_time >= longest_time_worked:
            today = datetime.now().strftime("%Y-%m-%d")
            longest_time_worked = total_work_time
            longest_time_worked_date = today
            config['longest_time_worked'] = longest_time_worked
            config['longest_time_worked_date'] = longest_time_worked_date
            save_config(config)


        # Display total work time in hours and minutes
        total_hours, total_minutes = format_time(total_work_time)
        print(f"Total work time for {today}: {total_hours} hours {total_minutes} minutes")

        # Ask the user if they want to continue the session or go to the main menu
        user_input = input("Do you want to continue the session? (yes/no): ").lower()
        if user_input == 'no':
            # Reset cycle and go to the main menu
            last_completed_cycle = 0
            save_config({'last_completed_cycle': last_completed_cycle})
            break
        # elif user_input != 'yes':
        #     # If the user does not want to continue, save total work time for the day
        #     config[total_work_time_key] = total_work_time
        #     save_config(config)
        #     # Reset cycle and go to the main menu
        #     last_completed_cycle = 0
        #     save_config({'last_completed_cycle': last_completed_cycle})
        #     break

        # Check if it's the last cycle to determine the type of break
        if cycle < cycles:
            print("Take a short break!")
            art_to_display = break_ascii_art
            countdown(int(short_break_duration * 60), total_work_time, cycle, cycles, art_to_display)
        else:
            print("Take a long break!")
            art_to_display = break_ascii_art
            countdown(int(long_break_duration * 60), total_work_time, cycle, cycles, art_to_display)

        send_notification("Pomodoro", "Break session completed!")  # Notification for break end

        # Ask the user if they want to continue after the break
        user_input = input("Do you want to continue? (yes/no): ").lower()
        if user_input == 'no':
            # If the user does not want to continue, reset cycle and go to the main menu
            last_completed_cycle = 0
            save_config({'last_completed_cycle': last_completed_cycle})
            break

    # Save total work time and longest time worked for the day in the configuration
    config[total_work_time_key] = total_work_time
    config['longest_time_worked'] = longest_time_worked
    save_config(config)

    input("Pomodoro session complete. Press any key to go back to the main menu.")

def countdown(seconds, total_work_time, current_cycle, total_cycles, art_to_display):
    """Display a countdown timer and return the total seconds."""
    for remaining_time in range(seconds-1, -1, -1):
        clear_terminal()
        print(art_to_display)
        print(f"Time remaining: {remaining_time // 60} minutes {remaining_time % 60} seconds")
        if current_cycle <= total_cycles:
            print(f"Cycle {current_cycle}/{total_cycles}")
        hours, minutes = format_time(total_work_time)
        print(f"Total time worked today: {hours} hours {minutes} minutes")
        print("\n^s to pause ^r to resume")
        print("CTRL + C to quit (progress will not be saved)")
        time.sleep(1)
    return seconds

def custom_timer_menu():
    """Menu for custom timer."""
    clear_terminal()
    print("Custom Timer:")
    duration = int(get_float_input("Enter timer duration in minutes: ")) * 60

    """Display a countdown timer and wait for user input."""
    for remaining_time in range(duration-1, -1, -1):
        clear_terminal()
        print(f"Custom Timer\n")
        print(f"Time remaining: {remaining_time // 60} minutes {remaining_time % 60} seconds")
        time.sleep(1)
    send_notification("Hey", "The custom timer is over!")
    input("Timer completed. Press any key to go back to the main menu.")

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        clear_terminal()
        print(main_menu_ascii_art)
        print("Main Menu:")
        print("1) Start Another Session")
        print("2) Start Custom Timer")
        print("3) Go to Settings")
        print("4) Reset Last Completed Cycle")
        print("5) Exit")

        print(f"\nTotal work time today: {get_total_work_time_today()}")

        # Display longest time 
        longest_time, longest_time_date = get_longest_time_worked()
        print(f"Personal best: {longest_time} ({longest_time_date})")

        user_choice = input("Enter your choice (1/2/3/4/5): ")
        if user_choice == '1':
            # Start another session with saved settings
            config = load_config()
            work_duration = config.get('work_duration', 25)
            short_break_duration = config.get('short_break_duration', 5)
            long_break_duration = config.get('long_break_duration', 15)
            cycles = config.get('cycles', 4)
            pomodoro_timer(work_duration, short_break_duration, long_break_duration, cycles)
        elif user_choice == '2':
            # Start custom timer
            custom_timer_menu()
        elif user_choice == '3':
            # Go to settings
            settings_menu()
        elif user_choice == '4':
            # Reset last completed cycle to 0
            print("Cycles reset!")
            config = load_config()
            config['last_completed_cycle'] = 0
            save_config(config)
            print("Last completed cycle reset to 0.")
        elif user_choice == '5':
            # Exit the program
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main_menu()
