class blahError(Exception):
    pass


print("hi")
try:
    raise blahError("what's up", "blah")
except blahError as e:
    print("Gotcha")
    # print(e.[0])
    print(e.args[1])
    print(str(e))


class Stud:
    name: str = ""
    age: int = 0

    def __init__(self, given_name, given_age) -> None:
        self.name = given_name
        self.age = given_age

    def print_their_name(self):
        print(self.name)

    def print_their_age(self, age_to_compare):
        print(self.age)
        print(age_to_compare)


ram = Stud("ram", 20)
shyam = Stud("shyam", 30)

print(ram.age)
print(shyam.age)

print(ram.name)
print(shyam.name)

ram.print_their_age(45)


def a():

    raise blahError("a")


def b():
    a()
    print("g")


def c():
    b()
    print("g")


try:
    c()
    print("g")

except blahError as exc:
    pass
