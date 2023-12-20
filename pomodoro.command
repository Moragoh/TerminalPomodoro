#!/usr/bin/python3
import time
import os
import platform
import json
from datetime import datetime

# Configuration file path
CONFIG_FILE = "pomodoro_config.json"

work_ascii_art = """
                                                                                   
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
break_ascii_art = """
                                                                                                                                           
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
    """Load configuration from a file."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
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

    # Loop through cycles
    for cycle in range(last_completed_cycle + 1, cycles + 1):
        # Work session
        print(f"Cycle {cycle}/{cycles}")
        art_to_display = work_ascii_art  # Update ASCII art for work session
        # Update total work time and display countdown
        total_work_time += countdown(int(work_duration * 60), total_work_time, cycle, cycles, art_to_display)

        # Display total work time in hours and minutes
        total_hours, total_minutes = format_time(total_work_time)
        print(f"Total work time for {today}: {total_hours} hours {total_minutes} minutes")

        # Ask the user if they want to continue the session or go to the main menu
        user_input = input("Do you want to continue the session? (yes/no): ").lower()
        if user_input == 'main':
            # Exit the loop and go to the main menu
            break
        elif user_input != 'yes':
            # If the user does not want to continue, save total work time for the day
            config[total_work_time_key] = total_work_time
            save_config(config)
            # Reset cycle and go to main menu
            last_completed_cycle = 0
            save_config({'last_completed_cycle': last_completed_cycle})
            break

        # Ask the user if they want to start working again
        user_input = input("Do you want to start working again? (yes/no): ").lower()
        if user_input != 'yes':
            # If the user does not want to start working, save total work time for the day
            config[total_work_time_key] = total_work_time
            save_config(config)
            # Go to the main menu
            break

        # Wait for user input to start the break
        input("Press Enter to start the break...")

        # Check if it's the last cycle to determine the type of break
        if cycle < cycles:
            print("Take a short break!")
            art_to_display = break_ascii_art
            countdown(int(short_break_duration * 60), total_work_time, cycle, cycles, art_to_display)
        else:
            print("Take a long break!")
            art_to_display = break_ascii_art
            countdown(int(long_break_duration * 60), total_work_time, cycle, cycles, art_to_display)

    print("Pomodoro sessions completed!")
    print(f"Total work time for {today}: {total_hours} hours {total_minutes} minutes")

    # Save total work time for the day in the configuration
    config[total_work_time_key] = total_work_time
    save_config(config)

def countdown(seconds, total_work_time, current_cycle, total_cycles, art_to_display):
    """Display a countdown timer and return the total seconds."""
    for remaining_time in range(seconds, 0, -1):
        clear_terminal()
        print(art_to_display)
        print(f"Time remaining: {remaining_time // 60} minutes {remaining_time % 60} seconds")
        if current_cycle <= total_cycles:
            print(f"Cycle {current_cycle}/{total_cycles}: Work session")
        hours, minutes = format_time(total_work_time)
        print(f"Total time worked today: {hours} hours {minutes} minutes")
        time.sleep(1)
    return seconds


def main_menu():
    """Display the main menu and handle user input."""
    while True:
        clear_terminal()
        print("Main Menu:")
        print("1) Start Another Session")
        print("2) Go to Settings")
        print("3) Reset Last Completed Cycle")
        print("4) Exit")

        user_choice = input("Enter your choice (1/2/3/4): ")
        if user_choice == '1':
            # Start another session with saved settings
            config = load_config()
            work_duration = config.get('work_duration', 25)
            short_break_duration = config.get('short_break_duration', 5)
            long_break_duration = config.get('long_break_duration', 15)
            cycles = config.get('cycles', 4)
            pomodoro_timer(work_duration, short_break_duration, long_break_duration, cycles)
        elif user_choice == '2':
            # Go to settings
            settings_menu()
        elif user_choice == '3':
            # Reset last completed cycle to 0
            print("Cycles reset!")
            config = load_config()
            config['last_completed_cycle'] = 0
            save_config(config)
            print("Last completed cycle reset to 0.")
        elif user_choice == '4':
            # Exit the program
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()
