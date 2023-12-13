def args_parser_typed(*type_args):
    def args_parser(func):
        def wrapper(args):
            function_args = args.split(" ")

            if len(type_args) != len(function_args):
                print("Incorrect arguments amount")
                return

            for i in range(len(type_args)):
                function_args[i] = type_args[i](function_args[i])

            try:
                res = func(*function_args)
            except TypeError as err:
                print(f"Error: {err}")
                res = None
            except ValueError as err:
                print(f"Handler error: {err}")
                res = None

            print(f"Command result: {res}")

        return wrapper
    return args_parser


@args_parser_typed(str)
def add_handler(number):
    if len(number) == 0:
        raise ValueError("Nothing I need something")

    print(f"{number} was added")
    return number


@args_parser_typed(int, int)
def sum_handler(a, b):
    return a + b


def main():
    table = {
        "add": add_handler,
        "sum": sum_handler
    }

    while True:
        user_input = input(">>> ")
        first_space = user_input.find(" ")

        handler_name = user_input[:first_space]
        args = user_input[first_space:].strip()

        if table.get(handler_name) is not None:
            table[handler_name](args)
        else:
            print("No such command")


if __name__ == "__main__":
    main()