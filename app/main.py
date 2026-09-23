import sys

BUILTINS_COMMANDS= {"exit", "echo", "type"}
def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        # parts=user_input.split()
        # command=parts[0] if parts else ""

        if user_input == "exit":
            break
        elif user_input.startswith('echo'):
            print(user_input[5:])

        elif user_input.startswith('type'):
            if user_input.split()[1] in BUILTINS_COMMANDS:
                print(f"{user_input.split()[1]} is a shell builtin")
            else:
                print(f'{user_input.split()[1]}: not found')


        # Invalid input
        else:
            print(f"{user_input}: not found")


if __name__ == "__main__":
    main()
