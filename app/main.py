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
    #     command, _, args_str = user_input.partition(" ")

    res = []
    temp = ''
    active_quote = None  # Can be None, "'", or '"'
    is_first_space = True
    back_slash_active = False  # To handle escaped characters

    for char in user_input:
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
                #res.append(' ')
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
    command = res[0] if res else ''
    args = res[1:]
    return command, args

def parse_redirection(args):
    """
    Args:
        args: list of command arguments
    Returns:
        cleaned_args: arguments without redirection
        output_file: filename or None
    """

    if ">" in args:
        index = args.index(">")
        return args[:index], args[index + 1], args[index] # return the arguments before ">", the filename after ">", and the ">" symbol itself

    if "1>" in args:
        index = args.index("1>")
        return args[:index], args[index + 1], args[index] # return the arguments before "1>", the filename after "1>", and the "1>" symbol itself
    if "2>" in args:
            index = args.index("2>")
            return args[:index], args[index + 1], args[index] # return the arguments before "2>", the filename after "2>", and the "2>" symbol itself
    if "1>>" in args or ">>" in args:
            index = args.index("1>>") if "1>>" in args else args.index(">>")
            return args[:index], args[index + 1], args[index]
    if "2>>" in args:
                index = args.index("2>>") 
                return args[:index], args[index + 1], args[index]
    
    return args, None, None # No redirection found

def write_stdout(output, redirect_symbol=None, output_file=None):
    """
    Args:
        output: str: the output to write
        output_file: str or None: the file to write to, or None to print to stdout
        redirect_symbol: str or None: the redirection symbol (">", "1>", "2>") or None
    """
    if output_file:
        # create the file if it doesn't exist, overwrite it, or append it
        if redirect_symbol in (">", "1>"): 
            with open(output_file, "w") as f:
                f.write(output + "\n")
        else:  # "1>>" or ">>"
            with open(output_file, "a") as f:
                f.write(output + "\n")
    else:
        print(output)


def write_stderr(output, redirect_symbol=None, error_file=None):
    """
    Args:
        output: str: the output to write
        error_file: str or None: the file to write to, or None to print to stderr
    """
    if error_file:
        if redirect_symbol == "2>":
            with open(error_file, "w") as f:
                f.write(output + "\n")
        else: # "2>>"
            with open(error_file, "a") as f:
                f.write(output + "\n")
    else:
        print(output, file=sys.stderr)

def handle_builtin_output(output, redirect_symbol, output_file):
    """
    Args:
        output: str: the output to write
        redirect_symbol: str or None: the redirection symbol (">", "1>", "2>") or None
        output_file: str or None: the file to write to, or None to print to stdout
    """

    if redirect_symbol == "2>":
        # 2> does not affect stdout. But we will still create an empty file if specified
        open(output_file, "w").close()

        print(output)
    else:
        write_stdout(output, redirect_symbol,output_file)

def handle_builtin_error(error,redirect_symbol, output_file):
    """
    Args:
        error: str: the error message to write
        redirect_symbol: str or None: the redirection symbol (">", "1>", "2>") or None
        output_file: str or None: the file to write to, or None to print to stdout
    """
    if redirect_symbol == "2>":
        # write the error message to the specified file
        write_stderr(error, redirect_symbol, output_file)
    else:
        # write the error message to stderr
        write_stderr(error, redirect_symbol, output_file)

def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # parse the user input into command and arguments
        command,args=parse_input(user_input)
        
        # parse the arguments to check for output redirection
        args, output_file, redirect_symbol = parse_redirection(args)

        if command == "exit":
            break
        elif command == 'pwd':
            output=os.getcwd()
            handle_builtin_output(output, redirect_symbol, output_file)

        elif command == 'cd':
            if not args or args[0] == "~":
                target_dir = os.getenv("HOME", "/")
            else:
                target_dir = args[0]
            try:
                os.chdir(target_dir)
            except (FileNotFoundError, NotADirectoryError, PermissionError):
                #print(f"cd: {target_dir}: No such file or directory")
                error=f"cd: {target_dir}: No such file or directory"
                handle_builtin_error(error, redirect_symbol, output_file)

        elif command == 'echo':
            output=" ".join(args)
            handle_builtin_output(output, redirect_symbol, output_file)
            
            
        elif command =="type":
            if args[0] in BUILTINS_COMMANDS:
                output=f"{args[0]} is a shell builtin"
                handle_builtin_output(output, redirect_symbol, output_file)
            else:
                # if the command is not a built-in command, we will search for it in the PATH directories
                resulted_path=find_path(args[0])
                if resulted_path:
                    output=f"{args[0]} is {resulted_path}"
                    handle_builtin_output(output, redirect_symbol, output_file)
                # if the command is not found in the PATH directories, we will print an error message
                else:
                    output=f'{args[0]}: not found'
                    handle_builtin_error(output, redirect_symbol, output_file)

            
        # executing the command if it is not a built-in command (external command/program) or invalid command
        else:
            # finding the command in the PATH directories
            command_path = find_path(command)

            if command_path: # if the command is found in the PATH directories
                # inserting the command at the beginning of the arguments list
                args.insert(0, command)
                # executing the command using subprocess.run and redirecting the output to a file if specified
                if output_file and redirect_symbol == "2>":
                    with open(output_file, "w") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stderr=f
                        )
                elif output_file and redirect_symbol == "2>>":
                    with open(output_file, "a") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stderr=f
                        )
                elif output_file and redirect_symbol in {">", "1>"}:
                    with open(output_file, "w") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stdout=f
                        )
                elif output_file and redirect_symbol in {"1>>", ">>"}:
                    with open(output_file, "a") as f:
                        subprocess.run(
                            args,
                            executable=command_path,
                            stdout=f
                        )
                # executing the command without output redirection
                else:
                    subprocess.run(
                            args,
                            executable=command_path
                    )

            # command not found (unidentified command)
            else:
                output=f"{user_input}: not found"
                handle_builtin_error(output, redirect_symbol, output_file)




if __name__ == "__main__":
    main()
