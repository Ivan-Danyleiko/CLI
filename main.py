from datetime import datetime
from address_book import Birthday, Name, Phone, Record, AddressBook, is_valid_date
import pickle

def input_error(func):
    """
    Декоратор для обробки помилок під час виклику методів класу AddressBookWithFileOps.

    :param func: Декорована функція.
    :return: Обгортка для обробки помилок.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except KeyError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Handler error: {e}"
        except IndexError as e:
            return f"Index error: {e}"

    return wrapper

class AddressBookWithFileOps(AddressBook):
    def __init__(self):
        """
        Ініціалізує об'єкт класу AddressBookWithFileOps.
        """
        super().__init__()
        self.table = {
            "add": self.add_contact,
            "change": self.change_contact,
            "get": self.get_contact,
            "show all": self.show_all,
            "search": self.search_contacts,
            "hello": self.hello
        }

    def get_info(self, name):
        """
        Повертає інформацію про контакт у вигляді рядка.

        :param name: Ім'я контакту.
        :return: Інформація про контакт або повідомлення про відсутність контакту.
        """
        contact = self.find(name)
        if contact:
            return str(contact)
        else:
            return f"Contact {name} not found"

    def __getstate__(self):
        """
        Серіалізує об'єкт для збереження у файлі.

        :return: Стан об'єкту.
        """
        state = self.__dict__.copy()
        state.pop('wrapper', None)
        return state

    def __setstate__(self, state):
        """
        Десеріалізує об'єкт після зчитування з файлу.

        :param state: Стан об'єкту.
        """
        self.__dict__.update(state)
        self.table = {
            "add": self.add_contact,
            "change": self.change_contact,
            "get": self.get_contact,
            "show all": self.show_all,
            "search": self.search_contacts,
            "hello": self.hello
        }

    @input_error
    def add_contact(self, *args):
        """
        Додає новий контакт або редагує існуючий у адресній книзі.

        :param args: Аргументи команди 'add'.
        :return: Повідомлення про успішне виконання операції або повідомлення про помилку.
        """
        if len(args) < 2 or len(args) > 3:
            raise ValueError("Invalid number of arguments for 'add' command. Usage: add [name] [phone] [birthday]")

        name, phone, birthday = args[0], args[1], args[2] if len(args) == 3 else None

        existing_contact = self.find(name)

        if existing_contact:
            if isinstance(existing_contact, Record):
                if birthday and not is_valid_date(birthday, '%d-%m-%Y'):
                    raise ValueError("Invalid value format for 'birthday'. Use the format: DD-MM-YYYY")

                existing_contact.birthday.value = birthday
                existing_contact.add_phone(phone)
                return f"Birthday added to contact {name}. New phone: {existing_contact.phones[-1].value}"
            else:
                raise ValueError("Invalid contact type")
        else:
            new_contact = Record(name, Birthday(birthday))
            new_contact.add_phone(phone)
            self.add_record(new_contact)
            return f"Contact {name} added with phone {phone}" + (f" and birthday {birthday}" if birthday else "")

    @input_error
    def change_contact(self, *args):
        """
        Змінює існуючий контакт у адресній книзі.

        :param args: Аргументи команди 'change'.
        :return: Повідомлення про успішне виконання операції або повідомлення про помилку.
        """
        if len(args) < 2 or len(args) > 3:
            raise ValueError("Invalid number of arguments for 'change' command. Usage: change [name] [phone] [birthday]")

        name, phone, *birthday = args
        birthday = birthday[0] if birthday else None

        if name in self.data:
            existing_contact = self.data[name]
            if phone:
                existing_contact.phones = [Phone(phone)]
            if birthday is not None:
                if not is_valid_date(birthday, '%d-%m-%Y'):
                    raise ValueError("Invalid value format for 'birthday'. Use the format: DD-MM-YYYY")
                existing_contact.birthday = Birthday(birthday)
            return f"Contact {existing_contact.name.value} changed. New phone: {existing_contact.phones[-1].value}, New birthday: {existing_contact.birthday.value}" if phone or birthday else "No changes made"
        else:
            raise KeyError(f"Contact {name} not found")

    @input_error
    def get_contact(self, *args):
        """
        Отримує телефонний номер для вказаного контакту.

        :param args: Аргументи команди 'get'.
        :return: Телефонний номер або повідомлення про відсутність контакту.
        """
        if len(args) != 1:
            raise ValueError("Invalid number of arguments for 'get' command. Usage: get [name]")

        name, = args
        if name in self.data:
            contact = self.data[name]
            if isinstance(contact, Record):
                phones_str = '; '.join(str(phone.value) for phone in contact.phones)
                return f"Phone number for {contact.name.value}: {phones_str}"
            else:
                raise ValueError("Invalid contact type")
        else:
            raise KeyError(f"Contact {name} not found")

    @input_error
    def show_all(self, today=None):
        """
        Виводить усі контакти з адресної книги у вигляді рядка.

        :param today: Поточна дата.
        :return: Рядок з відформатованими контактами.
        """
        if not self.data:
            return "No contacts found"

        result = ""
        for contact in self.data.values():
            phones_str = '; '.join(str(phone['value']) for phone in contact.phones)
            birthday_str = f", Birthday - {contact.birthday.value}" if contact.birthday else ""
            days_until_birthday = contact.days_to_birthday(today) if contact.birthday else ""

            result += f"{contact.name.value}: Phone - {phones_str}{birthday_str}. Days until birthday: {days_until_birthday} days\n"

        return result


    @input_error
    def search_contacts(self, search_term):
        """
        Шукає контакти за вказаним терміном.

        :param search_term: Термін для пошуку.
        :return: Рядок з відформатованими контактами або повідомлення про їх відсутність.
        """
        matching_contacts = []
        for name, contact in self.data.items():
            phone_value = str(contact.phones[0]['value']) if contact.phones else ""
            birthday_value = str(contact.birthday) if contact.birthday else ""

            if (
                search_term.lower() in name.lower() or
                any(search_term.lower() in field_value.lower() for field_value in [phone_value, birthday_value])
            ):
                matching_contacts.append(contact)

        if matching_contacts:
            return self.format_contacts(matching_contacts)
        else:
            return "No matching contacts found"

    @input_error
    def hello(self, *args):
        """
        Виводить вітання.

        :param args: Додаткові аргументи (ігноруються).
        :return: Рядок з вітанням.
        """
        return "How can I help you?"

    @input_error
    def run_interactive_console(self):
        """
        Запускає інтерактивну консоль для взаємодії з користувачем.
        """
        while True:
            user_input = input(">>> ").strip().lower()

            if not user_input:
                print("No command entered")
                continue

            if user_input in {"good bye", "close", "exit"}:
                self.save_to_file("address_book_data.pkl")
                print("Good bye!")
                break
            elif user_input == "hello":
                print(self.hello())
            elif user_input.startswith("search"):
                search_term = user_input[len("search"):].strip()
                matching_contacts = self.search_contacts(search_term)
                print(matching_contacts)
            else:
                command, *args = user_input.split()

                if command == "show" and args and args[0] == "all":
                    print(self.show_all())
                elif command in {"add", "change", "get", "show all", "search", "hello"}:
                    print(self.table.get(command, lambda *args: "Invalid command")(*args))
                else:
                    print("No such command")

    def load_from_file(self, filename):
        """
        Завантажує дані з файлу у форматі pickle та оновлює об'єкт AddressBookWithFileOps.

        :param filename: Ім'я файлу для завантаження даних.
        """
        try:
            with open(filename, 'rb') as file:
                loaded_data = pickle.load(file)
                self.data = loaded_data
                print(f"Data loaded successfully. Number of records: {len(self.data)}")
        except FileNotFoundError:
            print(f"File {filename} not found. A new AddressBook object is created.")
        except pickle.UnpicklingError as e:
            print(f"Error loading data from file: {e}")

    def save_to_file(self, filename):
        """
        Зберігає дані у файл у форматі pickle.

        :param filename: Ім'я файлу для збереження даних.
        """
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)
            print(f"Data saved successfully. Number of records: {len(self.data)}")


if __name__ == "__main__":
    book = AddressBookWithFileOps()
    book.load_from_file("address_book_data.pkl")
    today = datetime.now().date()
    book.run_interactive_console()
    book.save_to_file("address_book_data.pkl")
    search_result = book.search_contacts("r")
    for contact in search_result:
        print(book.get_info(contact.name.value))
