from collections import UserDict
import datetime
import json
from abc import abstractmethod, ABC

'''Додано абстрактний базовий клас для користувальницьких представлень'''
class UserInterface(ABC):
    @abstractmethod
    def display_contacts(self, contacts):
        pass

    @abstractmethod
    def display_notes(self, notes):
        pass

    @abstractmethod
    def display_commands(self, commands):
        pass

'''Реалізації методів консольного інтерфейсу'''


class ConsoleInterface(UserInterface):
    def __init__(self, notes: list):
        self.notes = notes

    def display_contacts(self, contacts):
        contacts_info = []
        for contact in contacts:
            contacts_info.append(contact.get_info())
        return '\n'.join(contacts_info)

    def display_notes(self, notes):
        return '\n'.join(notes)

    def display_commands(self, commands):
        commands_info = []
        for command in commands:
            commands_info.append(command)
        return '\n'.join(commands_info)


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate_birthday(new_value)
        self._value = new_value

    def validate_birthday(self, birthday):
        if birthday is not None:
            try:
                datetime.datetime.strptime(birthday, "%Y-%m-%d")
            except ValueError:
                print("Invalid birthday format. Please use YYYY-MM-DD.")
                return False
            return True


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate_value(new_value)
        self._value = new_value

    @staticmethod
    def validate_value(value):
        if value is not None:
            if len(value) > 0 and len(value) < 12:
                return True
        return False


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.date.today()
            next_birthday = datetime.date(today.year, self.birthday.value.month, self.birthday.value.day)
            if next_birthday < today:
                next_birthday = datetime.date(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days = (next_birthday - today).days
            return days
        else:
            return None

    def get_info(self):
        phones_info = ''

        for phone in self.phones:
            phones_info += f'{phone.value}, '
            if self.birthday:
                return f'{self.name.value}: {phones_info} (День народження: {self.birthday.value})'
        else:
            return f'{self.name.value} : {phones_info[:-2]}'

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for record_phone in self.phones:
            if record_phone.value == phone:
                self.phones.remove(record_phone)
                return True
        return False

    def change_phones(self, phones):
        for phone in phones:
            if not self.delete_phone(phone):
                self.add_phone(phone)


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def get_all_record(self):
        return self.data

    def has_record(self, name):
        return bool(self.data.get(name))

    def get_record(self, name) -> Record:
        return self.data.get(name)

    def remove_record(self, name):
        del self.data[name]

    def search(self, value):
        if self.has_record(value):
            return self.get_record(value)

        for record in self.get_all_record().values():
            for phone in record.phones:
                if phone.value == value:
                    return record

        raise ValueError("Contact with this value does not exist.")

    def __iter__(self):
        return self.iterator()

    def iterator(self, N=1):
        all_records = self.get_all_record()
        record_keys = list(all_records.keys())
        total_records = len(record_keys)
        index = 0

        while index < total_records:
            yield [all_records[key] for key in record_keys[index:index + N]]
            index += N

    '''Додано функціонал збереження адресної книги на диск та відновлення з диска'''

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            self.data = data


def hello_func():
    return 'How I can help you?'


def exit_func():
    return 'Goodbye!'


def add_record(address_book, name, phone, birthday=None):
    record = Record(name, birthday)
    record.add_phone(phone)
    address_book.add_record(record)
    return f'Record added: {name} - {phone}'


def change_func(address_book, name, new_phone):
    record = address_book.get_record(name)
    if record:
        record.change_phones([new_phone])
        return f'Phone number changed for {name}: {new_phone}'
    else:
        return f'Record not found for name: {name}'


def show_func(address_book):
    all_records = address_book.get_all_record()
    if all_records:
        return 'All records:\n' + '\n'.join([record.get_info() for record in all_records.values()])
    else:
        return 'No records found'


'''Додано можливість пошуку за вмістом книги контактів за збігами в імені/телефоні'''


def search_func(address_book, coincidence):
    results = []

    for record in address_book.get_all_record().values():
        for phone in record.phones:
            if coincidence.lower() in phone.value.lower():
                results.append(record.get_info())
                break

    for record in address_book.get_all_record().values():
        if coincidence.lower() in record.name.value.lower():
            results.append(record.get_info())

    if results:
        return "\n".join(results)
    else:
        return "No matching records found."


def main():
    address_book = AddressBook()
    notes = []
    user_interface = ConsoleInterface(notes)


    COMMANDS = {
        'hello': hello_func,
        'exit': exit_func,
        'close': exit_func,
        'good bye': exit_func,
        'add': lambda: add_record(
            address_book,
            input('Enter name: '),
            input('Enter phone: '),
            input('Enter birthday (optional): ') or None),
        'search': lambda: search_func(address_book, input('Enter search coincidence: ')),
        'change': lambda: change_func(address_book, input('Enter name you want to change: '),
                                      input('Enter new phone: ')),
        'show all': lambda: user_interface.display_contacts(address_book.get_all_record().values()),
        'show notes': lambda: user_interface.display_notes(notes),
        'show commands': lambda: user_interface.display_commands(COMMANDS.keys())
    }

    while True:
        command = input('Enter command: ').lower()
        if command in ('exit', 'close', 'good bye'):
            print('Good bye!')
            break

        result = COMMANDS.get(command, lambda: 'Unknown command!')()
        print(result)


if __name__ == '__main__':
    main()