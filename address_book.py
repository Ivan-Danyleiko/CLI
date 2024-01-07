from collections import UserDict
from datetime import datetime

def error_handler(func):
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

def is_valid_date(date_str):
    if date_str is None:
        return True
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False

class Field:
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
    def __init__(self, value):
        self.value = value

    def validate(self, value):
        return is_valid_date(value)


class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        self.value = value

    def validate(self, value):
        return value is None or (isinstance(value, str) and value.isdigit())

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    @error_handler
    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    @error_handler
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

    @error_handler
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            
            days_left = (next_birthday - today).days
            return days_left
        else:
            return None

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def __init__(self):
        self.data = {}

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

    def show_all(self):
        if not self.data:
            return "No contacts found"

        result = ""
        for contact in self.data.values():
            phones_str = '; '.join(str(phone.value) for phone in contact.phones)
            birthday_str = f", Birthday - {contact.birthday.value}" if contact.birthday else ""
            days_until_birthday = contact.days_to_birthday() if contact.birthday else ""

            result += f"{contact.name.value}: Phone - {phones_str}{birthday_str}. Days until birthday: {days_until_birthday} days\n"

        return result
