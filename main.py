from datetime import datetime
from address_book import Birthday, Name, Phone, Record, AddressBook, is_valid_date
import pickle

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
    if len(args) < 2 or len(args) > 3:
        raise ValueError("Invalid number of arguments for 'add' command. Usage: add [name] [phone] [birthday]")

    name, *rest = args
    phone, birthday = (rest + [None, None])[:2]

    if name in contacts:
        existing_contact = contacts[name]
        if phone:
            existing_contact['phone'].value += f", {birthday}" if birthday else ""
        if birthday and not existing_contact['birthday'].value:
            existing_contact['birthday'].value = birthday
        return f"Birthday added to contact {name}. New phone: {existing_contact['phone'].value}"
    else:
        contacts[name] = {'phone': Phone(phone), 'birthday': Birthday(birthday)}
        return f"Contact {name} added with phone {phone}" + (f" and birthday {birthday}" if birthday else "")


@input_error
def get_contact(self, *args):
    if len(args) != 1:
        raise ValueError("Invalid number of arguments for 'get' command. Usage: get [name]")

    name, = args
    if name in self.data:
        contact = self.data[name]
        days_until_birthday = contact['birthday'].days_until_birthday()
        return f"Contact {name}: Phone - {contact['phone']}, Birthday - {contact['birthday']}. Days until birthday: {days_until_birthday} days"
    else:
        raise KeyError(f"Contact {name} not found")


@input_error
def change_contact(contacts, *args):
    if len(args) < 2 or len(args) > 3:
        raise ValueError("Invalid number of arguments for 'change' command. Usage: change [name] [phone] [birthday]")

    name, phone, *birthday = args
    birthday = birthday[0] if birthday else None

    if name in contacts:
        existing_contact = contacts[name]
        if phone:
            existing_contact['phone'].value = phone
        if birthday is not None:
            if not is_valid_date(birthday, '%d-%m-%Y'):
                raise ValueError("Invalid value format for 'birthday'. Use the format: DD-MM-YYYY")
            existing_contact['birthday'] = Birthday(birthday)
        return f"Contact {name} changed. New phone: {existing_contact['phone'].value}, New birthday: {existing_contact['birthday'].value}" if phone or birthday else "No changes made"
    else:
        raise KeyError(f"Contact {name} not found")


@input_error
def show_all_contacts(contacts, *args):
    if not contacts:
        return "No contacts found"

    result = ""
    for contact in contacts.values():
        phones_str = '; '.join(str(phone.value) for phone in contact.phones)
        birthday_str = f", Birthday - {contact.birthday.value}" if contact.birthday else ""
        days_until_birthday = contact.days_to_birthday() if contact.birthday else ""

        result += f"{contact.name.value}: Phone - {phones_str}{birthday_str}. Days until birthday: {days_until_birthday} days\n"

    return result





@input_error
def search_contacts(contacts, search_term):
    matching_contacts = []

    for name, contact in contacts.items():
        phone_value = str(contact['phone'].value) if contact['phone'] else ""
        birthday_value = str(contact['birthday'].value) if contact['birthday'] else ""

        if (
            search_term.lower() in name.lower() or
            any(search_term.lower() in field_value.lower() for field_value in [phone_value, birthday_value])
        ):
            matching_contacts.append({name: {'phone': contact['phone'], 'birthday': contact['birthday']}})

    if matching_contacts:
        return matching_contacts
    else:
        return "No matching contacts found"


@input_error
def hello(*args):
    return "How can I help you?"


class AddressBookWithFileOps(AddressBook):
    def __init__(self):
        super().__init__()
        self.table = {
            "add": add_contact,
            "change": change_contact,
            "get" : get_contact,
            "show all": show_all_contacts,
            "search": search_contacts,
            "hello": hello
        }

    def run_interactive_console(self):
        while True:
            user_input = input(">>> ").strip().lower()

            if user_input in {"good bye", "close", "exit"}:
                self.save_to_file("address_book_data.pkl")
                print("Good bye!")
                break
            elif user_input == "hello":
                print(self.table["hello"]())
            elif user_input.startswith("search"):
                search_term = user_input[len("search"):].strip()
                matching_contacts = self.search_contacts(search_term)
                print(matching_contacts)
            else:
                command, *args = user_input.split()

                if command == "show" and args and args[0] == "all":
                    print(self.table["show all"](self.data))
                elif command in {"add", "change", "phone", "show all", "search", "hello"}:
                    print(self.table[command](self.data, *args))
                else:
                    print("No such command")

    def search_contacts(self, search_term):
        matching_contacts = []
        for name, contact in self.data.items():
            phone_value = str(contact['phone'].value) if contact['phone'] else ""
            birthday_value = str(contact['birthday'].value) if contact['birthday'] else ""

            if (
                search_term.lower() in name.lower() or
                any(search_term.lower() in field_value.lower() for field_value in [phone_value, birthday_value])
            ):
                matching_contacts.append(f"{name}: Phone - {phone_value}, Birthday - {birthday_value}. Days until birthday: {contact['birthday'].days_until_birthday()} days")

        if matching_contacts:
            return "\n".join(matching_contacts)
        else:
            return "No matching contacts found"

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found. A new AddressBook object is created.")


if __name__ == "__main__":
    book = AddressBookWithFileOps()
    book.load_from_file("address_book_data.pkl")
    book.run_interactive_console()
