''' Zadanie I
__repr__
__str__
__len__
'''

#class Student:
#    def __init__(self,name, age):
#        self.name=name
#        self.age=age
#   def __str__(self):
#        return f"Студент {self.name}, возраст: {self.age}"
#student = Student("Vasya", 3)
#print(student)                      
#
#def __repr__(self):
#    return f"Student(name = '{self.name}, age = '{self.age}')"
#print(repr(student))

"Zadanie 2"

#def my_shiny_new_decorator(function_to_decorate):
#    def the_wrapper_around_the_original_function():
#        print("Я - код, который отработает до вызова функции")
#        function_to_decorate()
#        print("А я код, который отработает после")
#    return the_wrapper_around_the_original_function
#
#def stand_alone_function():
#    print("Я простая функция, и я не хочу изменений")

#stand_alone_function_decorated = my_shiny_new_decorator(stand_alone_function)
#stand_alone_function_decorated()

#@my_shiny_new_decorator
#def another_stand_alone_function():
#    print("Оставьте меня в покое")
#another_stand_alone_function()

"Zadanie 3 - Sandwich"

#def bread(func):
#    def wrapper():
#        func()
#        print("<\\_____/>")
#    return wrapper
#
#def ingridients(func):
#    def wrapper():
#        print("#pomidory")
#        func()
#        print("~salat~")
#    return wrapper
#
#@bread
#@ingridients
#def sandwich(food="--vechina--"):
#    print(food)
#sandwich()

##"Zadanie 4"

#def a_decorator_passing_arguments(function_to_decorate):
#    def a_wrapper_accepting_arguments(arg1, arg2):
#        function_to_decorate(arg1, arg2)
#    return a_wrapper_accepting_arguments
#
#@a_decorator_passing_arguments
#def print_full_name(first_name, last_name):
#    print("Меня зовут", first_name, last_name)
#print_full_name("Vasya", "Pupkin")

#"Zadanie 5"
#class Myclass(age, height):
#    def __init__(self, age, height):
#        self.age = age
#        self.height = height


#"Zadanie 6"

#class MathUtils:
#    @staticmethod
#    def add(a,b):
#        return a+b


#"Zadanie 7"

#class User:
#    def __init__(self, name, age):
#        self.name = name
#        self.age = age
#
#    @staticmethod
#    def is_valid_age(age):
#        return isinstance(age, int) and 0 < age < 150
#
#    @staticmethod
#    def is_valid_name(name):
#        return isinstance(name, str) and len(name) > 0
#if  User.is_valid_age(25) and User.is_valid_name("Иван"):
#    user=User("Иван", 25)

"Zadanie 8"
#class Shape:
#    def area(self):
#        print("Метод AREA должен быть определён")
#
#class Circle(Shape):
#    def __init__(self, radius):
#        self.radius=radius
#        "Дописать...."

#"Zadanie 9"
#from abc import ABC, abstractmethod
#class Shape(ABC):
#    @abstractmethod
#    def area(self):
#        pass
#class Circle(Shape):
#    def __init__(self,radius):
#        self.radius = radius
#    def area (self):
#        return 3.14*self.radius**2
#
#class Square(Shape):
#    def __init__(self, side):
#        self.side=side
#    def area(self):
#        return self.side ** 2
#sq = Square(10)

"Zadanie 9"

from abc import ABC, abstractmethod
class DataProcessor(ABC):
    def __init__(self, data):
        self.data= data

    @abstractmethod
    def process(self):
        pass

    @staticmethod
    def validate_data(data):
        return isinstance(data, list) and len(data) > 0

    @staticmethod
    def format_output(result):
        return f"Результат: {result}"

class NumberProcessor(DataProcessor):
    def process(self):
        if not self.validate_data(self.data
):
            print("Некорректноые данные")
        return sum(self.data
)

processor = NumberProcessor([1, 2, 3, 4, 5])
result = processor.process()
print(NumberProcessor.format_output(result))

        
