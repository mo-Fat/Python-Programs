# Imports
import argparse
import json
from pathlib import Path
from datetime import date, timedelta

# File path
file_path = "habits.json"

# Argument Parser
parser = argparse.ArgumentParser()

# Subcommand Parser
sub = parser.add_subparsers(dest="command", required=True)

# Command Parser - 'add'
p_add = sub.add_parser("add")
# Command Argument - 'name'
p_add.add_argument("name")

# Command Parser - 'check'
p_check = sub.add_parser("check")
# Command Argument - 'number'
p_check.add_argument("number", type=int)
# Command Argument - '--date'
p_check.add_argument("--date")

# Command Parser - 'list'
p_list = sub.add_parser("list")

# Command Parser - 'remove'
p_remove = sub.add_parser("remove")
# Command Argument - 'number'
p_remove.add_argument("number", type=int)

# Command Parser - 'stats'
p_stats = sub.add_parser("stats")
# Command Argument - 'number'
p_stats.add_argument("number", type=int)

# Parse Arguments
args = parser.parse_args()

# Validate --date
if hasattr(args, "date") and args.date is not None :
    try:
        date.fromisoformat(args.date)
    except ValueError:          
        parser.error("Invalid date")

# File Existence check
file = Path(file_path)

if not file.exists():
    file.write_text(json.dumps([], indent=2))

# Habits - list
habits = json.loads(file.read_text())

# Flag to check whether file is valid or not
file_flag = False

# Validate file content
try:
    # If file is not made of a list of habits, throw an error
    if not isinstance(habits, list):
        raise ValueError("Corrupted File!")
    # Validate each habit
    for i, habit in enumerate(habits):
        try:
            # Check Type of Habit
            if not isinstance(habit, dict):
                raise TypeError
            # Check Keys of habit
            name = habit["name"]
            created = habit["created"]
            checkins = habit["checkins"]

            # Check values of keys
            if not isinstance(name, str):
                raise ValueError

            # If created is not a date, this will throw a value error
            dt = date.fromisoformat(created)

            if not isinstance(checkins, list):
                raise TypeError

            # Validate checkin dates
            for checkin in checkins:
                # If dt is not a valid date, will throw a value error
                dt = date.fromisoformat(checkin)

        except TypeError:
            print("Corrupted Habit - Type of habit is not what was expected - Deleting habit")
            habits.pop(i)
        except ValueError:
            print("Corrupted Habit")
        except KeyError:
            print("Corrupted Habit - Habbit is missing keys - Deleting habbit")
            habits.pop(i)

    # If file is not corrupted, set file_flag to True
    file_flag = True

except ValueError:
    print("File Corrupted!")
    # Ask user about deleting the file
    choice = input("Delete Old File and create new one (Y/N) ?: ")
    # Delete file and create new one
    if choice.strip().lower() == "y":
        file.write_text(json.dumps([], indent=2))

# Utility function to calculate streak from a specific index
def calculate_streak(checkins, idx):
    # Initialize streak variable
    streak = 0

    # Streak = 0 if there are no checkins
    if len(checkins) == 0:
        return streak
    
    # Streak = 1 if there are any checkins
    streak = 1

    # Algorithm to find streak
    while idx > 0 and (date.fromisoformat(checkins[idx]) - date.fromisoformat(checkins[idx - 1])).days <= 1:
        streak += 1
        idx -= 1

    return streak

# Code will only execute if file is valid
if file_flag:
    try:
        if args.command == "add":
            name = args.name
            # Check if name is empty
            if name.strip() == "":
                raise ValueError("Invalid habit name - Habit name cannot be empty")

            # Check if a habit with the same name exists
            for habit in habits:
                if habit["name"].strip().lower() == name.strip().lower():
                    raise ValueError("A Habit of the same name already exists")

            # Create the habit
            today = date.today()
            new_habit = {
                "name": name.strip(),
                "created": today.isoformat(),
                "checkins": []
            }

            # Add it to list of habits
            habits.append(new_habit)

            # Save habits
            file.write_text(json.dumps(habits, indent=2))

        elif args.command == "check":
            number = args.number

            # Check if number is valid
            if not 1 <= number <= len(habits):
                raise ValueError("Invalid Index")

            # Variable to store date for checkin
            dt = None

            try:
                if hasattr(args, "date") and args.date is not None:
                    dt = date.fromisoformat(args.date)
                    # Check if date entered is from future
                    if (date.today() - dt).days < 0:
                        raise ValueError
                else:
                    dt = date.today()
            except ValueError:
                raise ValueError("Invalid date!")

            # Check if date already exists in checkin
            habit = habits[number - 1]

            for checkin in habit["checkins"]:
                if checkin == dt.isoformat():
                    raise ValueError("Checkin already exists")

            # Add Checkin
            habit["checkins"].append(dt.isoformat())

            # Sort Checkins
            habit["checkins"].sort()

            # Save habits
            file.write_text(json.dumps(habits, indent=2))

        elif args.command == "remove":
            number = args.number
            
            # Check if number is valid
            if not 1 <= number <= len(habits):
                raise ValueError("Invalid Index")

            # Remove habit
            habits.pop(number - 1)

            # Save habits
            file.write_text(json.dumps(habits, indent=2))
            
        elif args.command == "list":
            # Print Today's date
            today = date.today()
            print(f"Today: {today.isoformat()}")

            # Iterate over habits
            for i, habit in enumerate(habits, start=1):
                # Calculate streak
                streak = 0
                checkins = habit["checkins"]

                # No checkins - Streak = 0
                if len(checkins) == 0:
                    pass
                # Checkin was on a date before yesterday - Streak = 0
                elif (today - date.fromisoformat(checkins[-1])).days > 1:
                    pass
                # There is a valid checkin that is either today or yesterday - Streak can be calculated:
                else:
                    # Streak would be 1 if code enters this block
                    streak = 1
                    # If there is only one checkin
                    if len(checkins) == 1:
                        pass
                    # There are multiple checkins
                    else:
                        ptr = len(checkins) - 1
                        while ptr > 0:
                            previous_date = date.fromisoformat(checkins[ptr - 1])
                            current_date = date.fromisoformat(checkins[ptr])

                            if (current_date - previous_date).days == 1:
                                streak += 1
                            else:
                                break

                            ptr -= 1

                print(f"{i}. [{"x" if streak > 0 else ' '}] {habit["name"]:>10} streak: {streak} days")
        else:
            # Handle the stats command
            number = args.number

            if not 1 <= number <= len(habits):
                raise ValueError("Invalid number!")

            # Habit dictionary
            habit = habits[number - 1]

            # Habit attributes
            name = habit["name"]
            created = habit["created"]
            checkins = habit["checkins"]

            # Longest streak
            longest_streak = 0

            # Current streak
            current_streak = 0

            # Today
            today = date.today()

            # Last seven days
            previous_seven_days = [False] * 7
            
            # If there are no checkins. don't proceed ahead
            if not len(checkins) == 0:
                # Last checkin
                last_checkin = date.fromisoformat(checkins[-1])

                # Calculate current streak
                if not (today - last_checkin).days > 1:
                    current_streak = calculate_streak(checkins, len(checkins) - 1)
                    # Update longest_streak
                    longest_streak = max(longest_streak, current_streak)

                # Calculate longest streak
                idx = len(checkins) - 1

                # Calculate longest streak
                while idx >= 0:
                    streak = calculate_streak(checkins, idx)
                    longest_streak = max(longest_streak, streak)
                    idx -= streak

            # Calculate stats for last seven days
            idx = len(checkins) - 1
            while idx >= 0 and (today - date.fromisoformat(checkins[idx])).days <= 6:
                diff = (today - date.fromisoformat(checkins[idx])).days
                diff = (diff + 1) * -1
                previous_seven_days[diff] = True
                idx -= 1

            # Print stats
            print(name)
            print(f"Created: {created}")
            print(f"Total check-ins: {len(checkins)}")
            print(f"Current streak: {current_streak} days")
            print(f"Longest streak: {longest_streak} days")
            print("Last 7 days:       ", end="")
            for day in previous_seven_days:
                if day:
                    print("■ ", end="")
                else:
                    print("□ ", end="")

    except ValueError as e:
        print(e)