from collections import UserDict
from datetime import datetime
import pickle

def error_handler(func):
    """
    Декоратор для обробки помилок під час виклику функцій.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Value error: {e}"
        except IndexError as e:
            return f"Index error: {e}"
    return wrapper

def is_valid_date(date_str, format_str):
    """
    Перевірка, чи вказана дата має правильний формат.
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

class Field:
    """
    Клас-база для представлення полів контакту.
    """
    def __init__(self, value):
        self.__value = value

    def validate(self, value):
        return True

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value):
        if not self.validate(new_value):
            raise ValueError("Invalid value format")
        self.__value = new_value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    """
    Клас для представлення дати народження контакту.
    """
    def __init__(self, value=None):
        self.value = value

    def validate(self, value):
        return value is None or is_valid_date(value, '%d-%m-%Y')

class Name(Field):
    """
    Клас для представлення імені контакту.
    """
    pass

class Phone(Field):
    """
    Клас для представлення номеру телефону контакту.
    """
    def __init__(self, value):
        self.value = value

    def validate(self, value):
        return isinstance(value, str) and value.isdigit()
    
@error_handler
def add_contact(contacts, *args):
    """
    Додавання нового контакту або зміна існуючого.
    """
    if len(args) < 2 or len(args) > 3:
        raise ValueError("Invalid number of arguments for 'add' command. Usage: add [name] [phone] [birthday]")

    name, phone, *birthday = args
    birthday = birthday[0] if birthday else None

    if name in contacts:
        existing_contact = contacts[name]
        # Always add the birthday to the existing phone number
        existing_contact['phone'].value += f", {birthday}" if birthday else ""
        existing_contact['birthday'].value = birthday
        return f"Birthday added to contact {name}. New phone: {existing_contact['phone'].value}"
    else:
        contacts[name] = {'phone': Phone(phone), 'birthday': Birthday(birthday)}
        return f"Contact {name} added with phone {phone}" + (f" and birthday {birthday}" if birthday else "")


@error_handler
def change_contact(contacts, *args):
    """
    Зміна інформації про існуючий контакт.
    """
    if len(args) < 2 or len(args) > 3:
        raise ValueError("Invalid number of arguments for 'change' command. Usage: change [name] [phone] [birthday]")

    name, phone, *birthday = args
    birthday = birthday[0] if birthday else None

    if name in contacts:
        existing_contact = contacts[name]
        if phone:
            existing_contact['phone'].value = phone
        if birthday:
            # Check if the date has the correct format
            if birthday is not None and not is_valid_date(birthday, '%d-%m-%Y'):
                raise ValueError("Invalid value format for 'birthday'. Use the format: DD-MM-YYYY")
            # Check if the 'birthday' object already exists
            if existing_contact['birthday']:
                existing_contact['birthday'].value = birthday
            else:
                existing_contact['birthday'] = Birthday(birthday)
        return f"Contact {name} changed. New phone: {existing_contact['phone'].value}, New birthday: {existing_contact['birthday'].value}" if phone or birthday else "No changes made"
    else:
        raise KeyError(f"Contact {name} not found")


@error_handler
def get_phone(contacts, *args):
    """
    Отримання номеру телефону для вказаного контакту.
    """
    if len(args) != 1:
        raise ValueError("Invalid number of arguments for 'phone' command. Usage: phone [name]")

    name, = args
    if name in contacts:
        return f"Phone number for {name}: {contacts[name]['phone']}"
    else:
        raise KeyError(f"Contact {name} not found")

@error_handler
def show_all_contacts(contacts, *args):
    """
    Показ усіх контактів.
    """
    if not contacts:
        return "No contacts found"

    result = "\n".join([f"{name}: Phone - {contact['phone']}, Birthday - {contact['birthday']}" for name, contact in contacts.items()])
    return result

@error_handler
def search_contacts(contacts, search_term):
    """
    Пошук контактів за заданим рядком.
    """
    search_results = []

    for name, contact in contacts.items():
        if search_term.lower() in name.lower() or search_term in contact['phone'].value:
            search_results.append(f"{name}: Phone - {contact['phone']}, Birthday - {contact['birthday']}")

    if search_results:
        return "\n".join(search_results)
    else:
        return "No matching contacts found"

@error_handler
def hello(*args):
    """
    Виведення привітання.
    """
    return "Hello! How can I assist you?"

class AddressBook(UserDict):
    """
    Клас для представлення адресної книги.
    """
    def __init__(self):
        super().__init__()

        self.table = {
            "add": add_contact,
            "change": change_contact,
            "phone": get_phone,
            "show all": show_all_contacts,
            "search": search_contacts, 
            "hello": hello
        }

    @error_handler
    def hello(*args):
        return "Hello! How can I assist you?"

    @error_handler
    def add_record(self, user):
        self.data[user.name.value] = user

    @error_handler
    def find(self, name):
        return self.data.get(name)

    @error_handler
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def __iter__(self):
        return iter(self.data.values())

    def iterator(self, n):
        records = list(self.data.values())
        for i in range(0, len(records), n):
            yield records[i:i + n]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run_interactive_console(self):
        """
        Запуск інтерактивної консолі для взаємодії з користувачем.
        """
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
        """
        Пошук контактів за заданим рядком.
        """
        matching_contacts = []
        for name, contact in self.data.items():
            if (
                search_term.lower() in name.lower() or
                any(search_term.lower() in contact[field].value.lower() for field in ["phone", "birthday"])
            ):
                matching_contacts.append({name: contact})
        return matching_contacts

    def save_to_file(self, filename):
        """
        Збереження даних у файл.
        """
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        """
        Завантаження даних з файлу.
        """
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print(f"File {filename} not found. A new AddressBook object is created.")

if __name__ == "__main__":
    with AddressBook() as book:
        book.run_interactive_console()
