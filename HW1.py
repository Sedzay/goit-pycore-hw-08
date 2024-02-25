from collections import UserDict
import datetime as dt
from datetime import datetime as dtdt
import pickle

# Оголошуємо декоратор input_error
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found"
        except IndexError:
            return "Not found"
        except Exception as e:
            return e

    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    # реалізація класу
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    # реалізація класу
	def __init__(self, value):
         super().__init__(value)
         if not value.isdigit() or len(value)!=10:
             raise Exception('Тел номер має бути з 10 чисел')
         
class Birthday(Field):
    def __init__(self, value):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            date_object = dtdt.strptime(value, "%d.%m.%Y")
            super().__init__(date_object)
        except ValueError:
            raise ValueError("Формат дати має бути: DD.MM.YYYY")
        

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу
    
    def add_phone(self,phone):
        self.phones.append(Phone(phone))
        
    def find_phone(self,phone):
        for ph in self.phones:
            if str(ph) == phone:
                return ph.value
    
    def edit_phone(self,old_phone,new_phone):
        for ph in self.phones:
            if str(ph) == old_phone:
                ph.value = new_phone
             
    def remove_phone(self,phone):
        self.phones = [ph for ph in self.phones if str(ph) != phone]

    def add_birthday(self,birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        if self.birthday:
            return f"Контакт: {self.name.value}, Телефон: {'; '.join(p.value for p in self.phones)}, ДР: {self.birthday.value.strftime('%d.%m.%Y')}"
        else:
            return f"Контакт: {self.name.value}, Телефон: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    
    
    # додавання запису
    def add_record(self,record):
        self.data[record.name.value] = record
            
    #пошук записів
    def find(self,name):
        return self.data.get(name)
    
    #виделення запису
    def delete(self,name):
        rec = self.find(name)
        if rec:
           del self.data[name] 
           
    @input_error
    def add_birthday(self, args):
        name, birthday = args
        record = self.find(name)
        if record:
            record.add_birthday(birthday)
            return f"ДР {birthday} додан до {name}"
        else:
            return "Контакт не знайден"

    @input_error
    def show_birthday(self,args):
        name = args[0]
        record = self.find(name)
        if record and record.birthday:
            print(f"День народження {name}: {record.birthday.value.strftime('%d.%m.%Y')}")
        else:
            print(f"День народження для {name} не знайдено.")

    @input_error
    def birthdays(self):
        today_date = dtdt.today()
        today_year = today_date.year
        birthdays_found = False
    
        for record in self.data.values():
            if record.birthday:
                user_birthday = record.birthday.value.replace(year=today_year)  # Замінюю рік на поточний
                if user_birthday < today_date:
                    user_birthday = user_birthday.replace(year=today_year + 1)  # Якщо ДР вже відбувся
                
                if 0 <= (user_birthday - today_date).days < 7:
                    weekday_num = user_birthday.weekday()
                    if weekday_num == 5:  # Saturday
                        user_birthday += dt.timedelta(days=2)
                    elif weekday_num == 6:  # Sunday
                        user_birthday += dt.timedelta(days=1)
                    
                    print(f"{record.name.value}: {user_birthday.strftime('%d.%m.%Y')}")
                    birthdays_found = True
            if not birthdays_found:
                print(f"День народження не знайдено.")
                
    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            pass  # Повернення нового об'єкта адресної книги, якщо файл не знайдено

    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)
            
           
def main():
    @input_error
    def parse_input(user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, *args
    
    book = AddressBook()
    book.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_data()
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) < 2:
                print("Invalid command. Usage: add <name> <phone>")
                continue
            name, phone = args
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            print(f"Added contact: {name}, {phone}")

        elif command == "change":
            if len(args) < 3:
                print("Invalid command. Usage: change <name> <old_phone> <new_phone>")
                continue
            name, old_phone, new_phone = args
            record = book.find(name)
            if record:
                record.edit_phone(old_phone, new_phone)
                print(f"Phone number updated for {name} from {old_phone} to {new_phone}")
            else:
                print("Contact not found.")

        elif command == "phone":
            if len(args) < 1:
                print("Invalid command. Usage: phone <name>")
                continue
            name = args[0]
            record = book.find(name)
            if record:
                print(record)
            else:
                print("Contact not found.")

        elif command == "all":
            for name, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            if len(args) < 2:
                print("Invalid command. Usage: add-birthday <name> <birthday>")
                continue 
            print(book.add_birthday(args))

        elif command == "show-birthday":
            if len(args) < 1:
                print("Invalid command. Usage: show-birthday <name>")
                continue
            book.show_birthday(args)

        elif command == "birthdays":
            book.birthdays()

        else:
            print("Invalid command.")
            
if __name__ == "__main__":
    main()
    
