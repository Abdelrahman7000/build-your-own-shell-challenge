import sys
import os
import subprocess
import shlex


BUILTINS_COMMANDS= {"exit", "echo", "type","pwd","cd"}

def find_path(target_command):
    '''
    Args:
        target_command: str: the command to find in the PATH directories
    Returns:
        str: the full path of the command if found, None otherwise
    '''
    path_var=os.getenv('PATH','')
    path_dirs=path_var.split(os.pathsep)

    for path_dir in path_dirs:
        #full_path = path_dir+'/'+target_command
        full_path = os.path.join(path_dir, target_command)
        # check if both the directory and file exist
        if os.path.isdir(path_dir) and os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
        else:
            continue
    else:
        return None

def parse_input(user_input):
    '''
    Args:
        user_input: str: the input string from the user
    Returns:
        tuple: (command, args) where command is the command to execute and args is a list of arguments
    '''
    #command, _, args_str = user_input.partition(" ")
    parts = shlex.split(user_input)
    command=parts[0] if parts else ''
    args_str = " ".join(parts[1:]) if len(parts) > 1 else ""
    res = []
    temp = ''
    active_quote = None  # Can be None, "'", or '"'
    is_first_space = True
    back_slash_active = False  # To handle escaped characters

    for char in args_str:
        # Handle Single Quotes
        if char == '\\':
            # Handle backslash logic for escaping characters in quotes and outside quotes
            if (back_slash_active and active_quote == '"') or active_quote=="'" or (back_slash_active and active_quote is None):
                temp += '\\'  # Treat as a literal backslash
                back_slash_active = False
            else:
                back_slash_active = True
        # Handle Single Quotes        
        elif char == "'" and active_quote != '"':
            if back_slash_active:
                temp += char  # Treat as a literal single quote
                back_slash_active = False

            elif active_quote == "'":
                active_quote = None  # Closing single quote
            else:
                active_quote = "'"   # Opening single quote
                
        # Handle Double Quotes
        elif char == '"' and active_quote != "'":
            if back_slash_active:
                temp += char  # Treat as a literal double quote
                back_slash_active = False

            elif active_quote == '"':
                active_quote = None  # Closing double quote
            else:
                active_quote = '"'   # Opening double quote
                
        # Handle Spaces
        elif char == ' ':
            if back_slash_active:
                temp += char  # Treat as a literal space
                back_slash_active = False
            elif active_quote is not None:
                temp += ' '
            elif is_first_space:
                res.append(temp)
                res.append(' ')
                temp = ''
                is_first_space = False
                
        # Handle Regular Characters (and nested quotes)
        else:
            if back_slash_active:
                temp += char  # Treat as a literal space
                back_slash_active = False
            else:
                temp += char
                is_first_space = True

    if temp:
        res.append(temp)

    return command, res

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        command,args=parse_input(user_input)
        if command == "exit":
            break
        elif command == 'pwd':
            print(os.getcwd())
        elif command == 'cd':
            if not args or args[0] == "~":
                target_dir = os.getenv("HOME", "/")
            else:
                target_dir = args[0]
            try:
                os.chdir(target_dir)
            except (FileNotFoundError, NotADirectoryError, PermissionError):
                print(f"cd: {target_dir}: No such file or directory")

        elif command == 'echo':
            output="".join(args)
            #output = output.replace('"', "")
            print(output)
            #print(args)
            
        elif command =="type":
            if args[0] in BUILTINS_COMMANDS:
                print(f"{args[0]} is a shell builtin")
            else:
                # if the command is not a built-in command, we will search for it in the PATH directories
                resulted_path=find_path(args[0])
                if resulted_path:
                    print(f"{args[0]} is {resulted_path}")
                else:
                    print(f'{args[0]}: not found')

            
        # executing the command if it is not a built-in command (external command/program) or invalid command
        else:
            # finding the command in the PATH directories
            command_path=find_path(command)
            
            args=[arg for arg in args if arg != ' ']
            # inserting the command at the beginning of the arguments list
            args.insert(0,command)
            if command_path:
                # executing the command using subprocess.run
                subprocess.run(
                            args,
                            executable=command_path
                )
                
            else:
                print(f"{user_input}: not found")


if __name__ == "__main__":
    main()
