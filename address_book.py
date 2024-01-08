from collections import UserDict
from datetime import datetime


def is_valid_date(date_str, date_format='%d-%m-%Y'):
    """
    Перевіряє, чи є рядок вірним представленням дати.

    :param date_str: Рядок, який представляє дату.
    :param date_format: Формат дати (за замовчуванням '%d-%m-%Y').
    :return: True, якщо дата вірна, False - в іншому випадку.
    """
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return False




class Field:
    """
    Базовий клас для полів контакту.

    :param value: Початкове значення поля.
    """
    def __init__(self, value):
        self.__value = value

    def validate(self, value):
        """
        Перевіряє, чи є значення вірним для даного типу поля.

        :param value: Значення для перевірки.
        :return: True, якщо значення вірне, False - в іншому випадку.
        """
        return True

    @property
    def value(self):
        """Повертає поточне значення поля."""
        return self.__value

    @value.setter
    def value(self, new_value):
        """
        Встановлює нове значення для поля після перевірки валідності.

        :param new_value: Нове значення для встановлення.
        :raise ValueError: Якщо нове значення невірного формату.
        """
        if not self.validate(new_value):
            raise ValueError("Invalid value format")
        self.__value = new_value

    def __str__(self):
        """Повертає рядкове представлення поточного значення поля."""
        return str(self.value)

class Birthday(Field):
    """
    Клас для представлення поля "дата народження".

    :param value: Значення поля (об'єкт datetime).
    """
    def __init__(self, value):
        self.value = value

    def validate(self, value):
        """Перевіряє, чи є значення об'єктом datetime."""
        return isinstance(value, datetime)


class Name(Field):
    def validate(self, value):
        return value is None or (isinstance(value, str) and value.replace(" ", "").isalpha())

class Phone(Field):
    """
    Клас для представлення поля "телефон".

    :param value: Значення поля (рядок).
    """
    def __init__(self, value):
        self.value = value

    def validate(self, value):
        """Перевіряє, чи є значення рядком, що складається лише з цифр."""
        return value is None or (isinstance(value, str) and value.isdigit())

class Record(Field):
    """
    Клас для представлення контакту.

    :param name: Ім'я контакту (рядок).
    :param birthday: Дата народження контакту (рядок у форматі '%d-%m-%Y').
    """
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = [{'value': ''}]
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        """Добавити номер телефону"""
        self.phones.append({'value': phone})

    def remove_phone(self, phone):
        """Видалити номер телефону"""
        while any(p.value == phone for p in self.phones if p.value):
            for p in self.phones:
                if p.value == phone:
                    self.phones.remove(p)
                    break

    def edit_phone(self, old_phone, new_phone):
        """
        Редагує номер телефону у списку телефонів контакту.

        :param old_phone: Старий номер телефону для заміни.
        :param new_phone: Новий номер телефону.
        :raise ValueError: Якщо старий номер телефону не знайдений.
        """
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit is not None:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError(f"Phone {old_phone} not found for {self.name.value}")

    def find_phone(self, phone):
        """
        Пошук телефону в списку телефонів контакту.

        :param phone: Номер телефону для пошуку.
        :return: Знайдений телефон або None, якщо не знайдено.
        """
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def days_to_birthday(self, today):
        """
        Обчислює кількість днів до дня народження.

        :param today: Поточна дата.
        :return: Кількість днів до дня народження або None, якщо день народження не вказано.
        :raise ValueError: Якщо формат дня народження невірний.
        """
        if self.birthday:
            today = datetime.now()

            if isinstance(self.birthday.value, datetime):
                next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)

                if today > next_birthday:
                    next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)

                days_left = (next_birthday - today).days
                return days_left
            elif is_valid_date(self.birthday.value, '%d-%m-%Y'):
                day, month, _ = map(int, self.birthday.value.split('-'))
                next_birthday = datetime(today.year, month, day)

                if today > next_birthday:
                    next_birthday = datetime(today.year + 1, month, day)

                days_left = (next_birthday - today).days
                return days_left
            else:
                raise ValueError("Invalid birthday format")
        else:
            return None
        
    def get_info(self):
        """Повертає рядкове представлення контакту для виведення."""
        phones_str = '; '.join(str(p['value']) for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

    def __str__(self):
        """Повертає рядкове представлення контакту для виведення."""
        phones_str = '; '.join(str(p['value']) for p in self.phones)
        birthday_str = f", Birthday - {self.birthday.value}" if self.birthday else ""
        days_until_birthday = self.days_to_birthday(None)

        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}. Days until birthday: {days_until_birthday} days"

class AddressBook(UserDict):
    def __init__(self):
        self.data = {}

    def add_record(self, user):
        """
        Додає новий контакт до адресної книги.

        :param user: Екземпляр класу Record для додавання.
        :return: Рядок з підтвердженням додавання контакту.
        :raise ValueError: Якщо переданий об'єкт не є екземпляром класу Record.
        """
        if not isinstance(user, Record):
            raise ValueError("Invalid contact type. Expected Record.")
        
        self.data[user.name.value] = user
        return f"Contact {user.name.value} added."

    def find(self, name):
        """
        Пошук контакту за ім'ям.

        :param name: Ім'я для пошуку контакту.
        :return: Знайдений контакт або None, якщо не знайдено.
        """
        return self.data.get(name)

    def delete(self, name):
        """
        Видаляє контакт з адресної книги за ім'ям.

        :param name: Ім'я контакту для видалення.
        """
        if name in self.data:
            del self.data[name]

    def __iter__(self):
        """
        Повертає ітератор для перегляду всіх контактів у адресній книзі.

        :return: Ітератор з контактами.
        """
        return iter(self.data.values())

    def iterator(self, n):
        """
        Розділяє контакти на групи по n елементів і повертає ітератор.

        :param n: Кількість контактів у кожній групі.
        :return: Ітератор з групами контактів.
        """
        records = list(self.data.values())
        for i in range(0, len(records), n):
            yield records[i:i + n]

    def format_contacts(self, contacts, today=None):
        """
        Форматує контакти у рядок для виведення.

        :param contacts: Список контактів для форматування.
        :param today: Поточна дата.
        :return: Рядок з відформатованими контактами.
        """
        if not contacts:
            return "No matching contacts found"

        result = ""
        for contact in contacts:
            phones_str = '; '.join(str(phone['value']) for phone in contact.phones)
            birthday_str = f", Birthday - {contact.birthday.value}" if contact.birthday else ""
            days_until_birthday = contact.days_to_birthday(today) if contact.birthday else ""

            result += f"{contact.name.value}: Phone - {phones_str}{birthday_str}. Days until birthday: {days_until_birthday} days\n"

        return result

    def show_all_contacts(self, today=None):
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
            birthday_str = f", Birthday - {contact.birthday}" if contact.birthday else ""
            days_until_birthday = contact.days_to_birthday(today) if contact.birthday else ""

            result += f"{contact.name.value}: Phone - {phones_str}{birthday_str}. Days until birthday: {days_until_birthday} days\n"

        return result


    
    def show_all(self, *args):
        """
        Виводить усі контакти з адресної книги у вигляді рядка.

        :param args: Додаткові аргументи.
        :return: Рядок з відформатованими контактами.
        """
        return self.show_all_contacts(*args)
