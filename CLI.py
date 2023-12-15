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
    name, phone = args
    if not name in contacts:
        contacts[name] = phone
        return f"Contact {name} added with phone {phone}"
    elif name in contacts:
        return f"The contact {name} already exists"
    if ValueError:
        return "Invalid input. Use 'add name phone' format."

@input_error
def change_contact(contacts, *args):
    name, phone = args
    if name in contacts:
        contacts[name] = phone
        return f"Phone number for {name} changed to {phone}"
    elif not name in contacts:
        raise KeyError(f"Contact {name} not found")
    if ValueError:
        return "Invalid input. Use 'change name phone' format."

@input_error
def get_phone(contacts, *args):
    name, = args
    if name in contacts:
        return f"Phone number for {name}: {contacts[name]}"
    elif not name in contacts:
        raise KeyError(f"Contact {name} not found")
    if ValueError:
        return "Invalid input. Use 'phone name' format."
    

@input_error
def show_all_contacts(contacts, *args):
    if not contacts:
        return "No contacts found"
    
    result = "\n".join([f"{name}: {phone}" for name, phone in contacts.items()])
    return result
    
    

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
        user_input = input(">>> ").strip().lower()

        if user_input in {"good bye", "close", "exit"}:
            print("Good bye!")
            break
        else:
            command, *args = user_input.split()

            if command == "show" and args and args[0] == "all":
                print(table["show all"](contacts))
            elif command in table:
                print(table[command](contacts, *args))
            else:
                print("No such command")




if __name__ == "__main__":
    main()
