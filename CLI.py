def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Handler error: {e}"
        except IndexError as e:
            return f"Index error: {e}"
    return wrapper

@input_error
def add_contact(contacts, *args):
    try:
        name, phone = args
        contacts[name] = phone
        return f"Contact {name} added with phone {phone}"
    except ValueError:
        return "Invalid input. Use 'add name phone' format."

@input_error
def change_contact(contacts, *args):
    try:
        name, phone = args
        if name in contacts:
            contacts[name] = phone
            return f"Phone number for {name} changed to {phone}"
        else:
            raise KeyError(f"Contact {name} not found")
    except ValueError:
        return "Invalid input. Use 'change name phone' format."

@input_error
def get_phone(contacts, *args):
    try:
        name, = args
        if name in contacts:
            return f"Phone number for {name}: {contacts[name]}"
        else:
            raise KeyError(f"Contact {name} not found")
    except ValueError:
        return "Invalid input. Use 'phone name' format."

@input_error
def show_all_contacts(contacts, *args):
    try:
        if not contacts:
            return "No contacts found"
        result = "\n".join([f"{name}: {phone}" for name, phone in contacts.items()])
        return result
    except ValueError:
        return "Invalid input. Use 'show all' format."

@input_error
def hello(*args):
    return "How can I help you?"

def main():
    contacts = {}

    table = {
        "add": add_contact,
        "change": change_contact,
        "phone": get_phone,
        "show all": show_all_contacts,
        "hello": hello
    }

    while True:
        user_input = input(">>> ").strip()

        if user_input.lower() in {"good bye", "close", "exit"}:
            print("Good bye!")
            break
        else:
            command, *args = user_input.split()
            matching_commands = [cmd for cmd in table.keys() if cmd.startswith(command)]
            
            if matching_commands:
                print(table[matching_commands[0]](contacts, *args))
            else:
                print("No such command")


if __name__ == "__main__":
    main()
