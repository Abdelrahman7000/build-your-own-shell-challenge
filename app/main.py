import sys
import os
import subprocess

BUILTINS_COMMANDS= {"exit", "echo", "type","pwd"}

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
        full_path = path_dir+'/'+target_command
        # check if both the directory and file exist
        if os.path.isdir(path_dir) and os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
        else:
            continue
    else:
        return None



def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # splitting the user input into command and arguments
        parts=user_input.split()
        command=parts[0]
        # getting the arguments
        args=parts[1:]

        if command == "exit":
            break
        elif command == 'pwd':
            current_dir = os.getcwd()
            print(current_dir)
        elif command == 'echo':
            print(' '.join(args))

        elif user_input.startswith("type"):
            if args[0] in BUILTINS_COMMANDS:
                print(f"{args[0]} is a shell builtin")
            else:
                # if the command is not a built-in command, we will search for it in the PATH directories
                resulted_path=find_path(args[0])
                if resulted_path:
                    print(f"{args[0]} is {resulted_path}")
                else:
                    print(f'{args[0]}: not found')

            
        # executing the command if it is not a built-in command or invalid command
        else:
            # finding the command in the PATH directories
            command_path=find_path(command)
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
