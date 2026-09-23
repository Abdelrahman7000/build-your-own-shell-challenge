import sys


def main():
    while True:
        sys.stdout.write("$ ")
        user_input = input()
        if user_input == "exit":
            break
        elif user_input.startswith('echo'):
            print(user_input[5:])

        elif user_input.startswith('type'):
            if user_input.split()[1] in ['exit','echo','type']:
                print(f"{user_input.split()[1]} is a shell builtin")
            else:
                print(f'{user_input}: not found')


        # Invalid input
        else:
            print("invalid_command: not found")


if __name__ == "__main__":
    main()
