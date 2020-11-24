from monolith import db
import enum


MenuItems = db.Table(
    "menuitems",
    db.Column("menu_id", db.Integer, db.ForeignKey("menu.id"), primary_key=True),
    db.Column("food_id", db.Integer, db.ForeignKey("food.id"), primary_key=True),
)


class FoodCategory(enum.Enum):
    STARTERS = "Starters"
    MAIN_COURSES = "Main Courses"
    SIDE_DISHES = "Side Dishes"
    DESSERTS = "Desserts"
    DRINKS = "Drinks"
    PIZZAS = "Pizzas"
    BURGERS = "Burgers"
    SANDWICHES = "Sandwiches"

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class Menu(db.Model):
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text(100))
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))

    restaurant = db.relationship("Restaurant", back_populates="menus")
    foods = db.relationship("Food", secondary=MenuItems, back_populates="menu")


class Food(db.Model):
    __tablename__ = "food"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    category = db.Column(db.Enum(FoodCategory))
    name = db.Column(db.Text(100))
    price = db.Column(db.Float)

    menu = db.relationship("Menu", secondary=MenuItems, back_populates="foods")
