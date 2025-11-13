class Vahicle:
    def __init__(self, make, model):
        self.make = make
        self.model = model
    def display_info(self):
        return f"Made BY: {self.make}, Model: {self.model}"
class Car(Vahicle):
    def __init__(self,make, model, num_doors):
        super().__init__(make, model)
        self.num_doors = num_doors
    def car_info(self):
        return f"{self.display_info()}, Number of Doors: {self.num_doors}"

my_car = Car("Toyota", "Corolla",4)
print(my_car.car_info())