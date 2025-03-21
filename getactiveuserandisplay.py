#!/usr/bin/python3 -u

import subprocess
import re
import pwd

def get_active_user_and_display():
    try:
        users_output = subprocess.check_output(['who'], universal_newlines=True)
        users = set(re.findall(r'^(\S+)', users_output, re.MULTILINE))

        if len(users) == 1:
            user = users.pop()
            user_home = pwd.getpwnam(user).pw_dir
            env_output = subprocess.check_output(['sudo', '-u', user, 'env'], universal_newlines=True)
            display_match = re.search(r'^DISPLAY=(:\d+)', env_output, re.MULTILINE)

            if display_match:
                display = display_match.group(1)
            else:
                display = None

            return user, user_home, display
        else:
            return None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def get_session_type_for_user(username):
    try:
        output = subprocess.check_output(['loginctl', 'list-sessions', '--no-legend'], universal_newlines=True)
        for line in output.strip().split('\n'):
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 2 and parts[2] == username:
                session_id = parts[0]
                session_info = subprocess.check_output(['loginctl', 'show-session', session_id, '-p', 'Type'], universal_newlines=True)
                return session_info.strip().split('=')[1]

    except Exception as e:
        print(f"Error: {e}")
        return None

user, user_home, display = get_active_user_and_display()

if(not display):
    display = ":0"

if user:
    session_type = get_session_type_for_user(user)
    if session_type:
        print(f"Active user: {user}, Home directory: {user_home}, DISPLAY: {display}, Session Type: {session_type}")
    else:
        print(f"Active user: {user}, Home directory: {user_home}, DISPLAY: {display}, but unable to determine session type")
else:
    print("No single active user found or unable to determine")
