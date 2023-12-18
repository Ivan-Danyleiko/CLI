from collections import UserDict

def input_error(func):
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

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    @input_error
    def add_phone(self, phone):
        self.phones.append(Phone(phone))


    @input_error
    def remove_phone(self, phone):
        while any(p.value == phone for p in self.phones):
            for p in self.phones:
                if p.value == phone:
                    self.phones.remove(p)
                    break

    
    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit is not None:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError(f"Phone {old_phone} not found for {self.name.value}")

    @input_error
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"

class AddressBook(UserDict):
    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record

    @input_error
    def find(self, name):
        return self.data.get(name)

    @input_error
    def delete(self, name):
        if name in self.data:
            del self.data[name]

# Приклад використання
if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    if john:
        john.edit_phone("1234567890", "1112223333")
        print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

        # Пошук конкретного телефону у записі John
        found_phone = john.find_phone("5555555555")
        print(f"{john.name.value}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
