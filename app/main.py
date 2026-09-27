import sys
import os
import subprocess

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
        full_path = path_dir+'/'+target_command
        #full_path = os.path.join(path_dir, target_command)
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
    tokens = []
    temp = ""
    in_quotes = False
    in_token = False  # True when actively building an argument (even if temp is empty)

    for char in user_input:
        if char == "'":
            in_quotes = not in_quotes
            in_token = True  # Handles empty quotes like ''
        elif char == " " and not in_quotes:
            if in_token:
                tokens.append(temp)
                temp = ""
                in_token = False
        else:
            temp += char
            in_token = True

    # Flush the last argument if input doesn't end with a space
    if in_token:
        tokens.append(temp)

    if not tokens:
        return "", []

    return tokens[0], tokens[1:]
    # command=user_input.partition(" ")[0]
    # args=user_input.partition(" ")[2]
    # res=[]
    # temp=''
    # is_quoted,is_first_space=False,True
    # for chr in args:
    #     if chr!="'" and chr!=' ': 
    #         temp+=chr
    #         is_first_space=True
    #     elif chr=="'" and is_quoted:
    #         is_quoted=False
    #     elif chr=="'" and not is_quoted:
    #         is_quoted=True
    #     elif chr==' ':
    #         if is_quoted: 
    #             temp+=' '
    #         elif not is_quoted and is_first_space:
    #             res.append(temp)
    #             res.append(' ')
    #             temp=''
    #             is_first_space=False
    #         else: continue
    # if temp:res.append(temp)
    # return (command,res)

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # splitting the user input into command and arguments
        # parts=user_input.split()
        # command=parts[0]
        # # getting the arguments
        # args=parts[1:]
        command,args=parse_input(user_input)
        if command == "exit":
            break
        elif command == 'pwd':
            print(os.getcwd())
        elif command == 'cd':
            # if args and os.path.isdir(args[0]):
            #     os.chdir(args[0])
            # else:
            #     print(f"cd: {args[0]}: No such file or directory")
            #target_dir = args[0] if args else os.getenv("HOME", "/")
            if not args or args[0] == "~":
                target_dir = os.getenv("HOME", "/")
            else:
                target_dir = args[0]
            try:
                os.chdir(target_dir)
            except (FileNotFoundError, NotADirectoryError, PermissionError):
                print(f"cd: {target_dir}: No such file or directory")

        elif command == 'echo':
            #print(' '.join(args))
            output=''.join(args)
            output = output.replace("'", "")

            print(output)
            
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
