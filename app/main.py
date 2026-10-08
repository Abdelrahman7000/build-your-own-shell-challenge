#import sys
import os
import subprocess
import readline
from app.shell.input_parser import parse_input, parse_redirection
from app.shell.path_checker import find_path
from app.shell.output_handler import write_stdout, write_stderr
from app.shell.autocompleter import completer, update_auto_complete_commands, AUTO_COMPLETE_COMMANDS


BUILTINS_COMMANDS= {"exit", "echo", "type","pwd","cd","complete"}


def main():
    # Update the auto-complete commands list with executables from the PATH directories
    update_auto_complete_commands()

    # Set up the readline completer
    readline.set_completer(completer)
    # Set the delimiters for word boundaries in the completer to include "-" as part of words and not to separate the word based on it. This allows for auto-completion of commands and filenames that contain hyphens.
    readline.set_completer_delims(readline.get_completer_delims().replace("-", ""))

    #print("DELIMS:", repr(readline.get_completer_delims()))
    # Make TAB triggers completion
    readline.parse_and_bind("tab: complete")
    while True:
        #sys.stdout.write("$ ")
        user_input = input("$ ")
        # parse the user input into command and arguments
        command,args=parse_input(user_input)
        
        # parse the arguments to check for output redirection
        args, output_file, redirect_symbol = parse_redirection(args)

        if command == "exit":
            break
        elif command == 'pwd':
            output=os.getcwd()
            write_stdout(output,redirect_symbol,output_file)

        elif command == 'cd':
            if not args or args[0] == "~":
                target_dir = os.getenv("HOME", "/")
            else:
                target_dir = args[0]
            try:
                os.chdir(target_dir)
            except (FileNotFoundError, NotADirectoryError, PermissionError):
                error=f"cd: {target_dir}: No such file or directory"
                write_stderr(error, redirect_symbol, output_file)

        elif command == 'echo':
            output=" ".join(args)
            write_stdout(output,redirect_symbol,output_file)
            
        elif command =="type":
            if args[0] in BUILTINS_COMMANDS:
                output=f"{args[0]} is a shell builtin"
                write_stdout(output, redirect_symbol, output_file)
            else:
                # if the command is not a built-in command, we will search for it in the PATH directories
                resulted_path=find_path(args[0])
                if resulted_path:
                    output=f"{args[0]} is {resulted_path}"
                    write_stdout(output, redirect_symbol, output_file)
                # if the command is not found in the PATH directories, we will print an error message
                else:
                    output=f'{args[0]}: not found'
                    write_stderr(output, redirect_symbol, output_file)
            
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
                write_stderr(output, redirect_symbol, output_file)



if __name__ == "__main__":
    main()
