from peewee import *
from collections import OrderedDict
import datetime
import csv
import os
import sys


db = SqliteDatabase('inventory.db')

print("Welcome to the inventory managememt system !!")
class Product(Model):
    product_id = AutoField() 
    product_name = CharField(max_length=255, unique = True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField(default=datetime.datetime.now)   
    
    class Meta:
        database = db


def menu_loop():
    """Shows the menu"""
    choice = None
    while choice != 'q':
        clear()
        print("\n**** Main menu ****\n")
        print("Enter 'q' to quit")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()

        if choice in menu:
            clear()
            menu[choice]()
        elif choice == 'q':
            clear()
        elif choice not in menu:
            print("That's not a valid option, please try again")
            input("Please enter any key to continue..")
            

def read_csv(anyfile):
    with open(anyfile, newline='') as csvfile:
        productreader = csv.DictReader(csvfile, delimiter=',')
        goods = list(productreader)
        return goods
        

def clean_data(raw_products):
    for product in raw_products:
        product['product_price']=product['product_price'].strip('$')
        product['product_price']=float(product['product_price'])
        product['product_price']=product['product_price']*100
        product['product_price']=int(product['product_price'])
        product['product_quantity']=int(product['product_quantity'])
        product['date_updated']=datetime.datetime.strptime(product['date_updated'],'%m/%d/%Y')
        
                                                                    
def load_products(goods):   
    for product in goods:
        try:
            Product.create(product_name=product['product_name'],
                       product_quantity=product['product_quantity'], product_price=product['product_price'],
                       date_updated=product['date_updated'])
        except IntegrityError:
            product_record = Product.get(product_name=product['product_name'])
            if product_record.date_updated <= product['date_updated']:
                product_record.product_name = product['product_name']
                product_record.product_quantity = product['product_quantity']
                product_record.product_price = product['product_price']
                product_record.date_updated = product['date_updated']
                product_record.save()
        

    
def add_entry():
    """Add an entry to the database"""
    prod_name_input = input("\nPlease enter the name of the product: ")
    entries = Product.select()
    #the below line will only return one result if True because there are no duplicates in the database
    entries = entries.where(Product.product_name == prod_name_input)
    if entries:  
        print("\nThat product already exists, we will update it with the new information")
        update = Product.get(product_name = prod_name_input)
        while True:
            try:
                update.product_quantity = int(input("Please enter the quantity of products: "))
            except ValueError:
                print("That's not a valid input, quantity must be an integer, please try again")
            else:
                break
        while True:
            try:
                update.product_price = int(input("Please enter price of the product (in cents): "))
            except ValueError:
                print("That's not a valid input, price must be in cents (integer), please try again")
            else:
                break    
        update.date_updated = datetime.datetime.now()
        update.save()
        print("This existing product has been updated with the new information!")        
    else:
        while True:
            try:
                prod_quant_input = int(input("Please enter the quantity of products: "))
            except ValueError:
                print("That's not a valid input, quantity must be an integer, please try again")
            else:
                break

        while True:
            try:
                prod_price_input = int(input("Please enter the price of the product (in cents): "))
            except ValueError:
                print("That's not a valid input, price must be in cents (integer), please try again")
            else:
                break          

        Product.create(product_name = prod_name_input, product_quantity = prod_quant_input,
                       product_price = prod_price_input)
        print("Thank you, the product has been added successfully!")
    
     
def view_entries():
    """View an entry in the database"""
    while True:
        try:
            user_query = int(input("Please enter the product ID you are looking for : "))
        except ValueError:
            print("Wrong entry, product IDs must be integers, please try again")
        else:
            break
    entries = Product.select()
    entries = entries.where(Product.product_id == user_query)
    while not entries:
        print("There is no such product ID, please try again")
        while True:
            try:
                user_query = int(input("Please enter the product ID you are looking for : "))
                entries = Product.select()
                entries = entries.where(Product.product_id == user_query)
            except ValueError:
                print("Wrong entry, product IDs must be integers, please try again")
            else:
                break
    else:    
        for entry in entries:
            print('='*60)
            print("The product you are looking for is : {}".format(entry.product_name))
            print("There are {} units of the product".format(entry.product_quantity))
            print("The price of the product is {} cents".format(entry.product_price))
            print('='*60)
            input("\nPlease press any key to continue..")
    
def backup_database():
    """Back-up the database into a new csv file"""
    with open('products.csv', 'a') as csvfile:
        fieldnames = ['product_id', 'product_name', 'product_quantity',
                  'product_price', 'date_updated']
        backup_database = csv.DictWriter(csvfile, fieldnames=fieldnames)
        backup_database.writeheader()
        entries = Product.select()
        for entry in entries:
            backup_database.writerow({'product_id': entry.product_id,
                                      'product_name': entry.product_name,
                                      'product_quantity': entry.product_quantity,
                                      'product_price': entry.product_price,
                                      'date_updated': entry.date_updated})

        print("\nYour database has been backed-up successfully!\n")    
        


def initialize():
    """Create the database"""
    db.connect()
    db.create_tables([Product], safe=True)
    

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_empty():
    entries = Product.select()
    for entry in entries:
        if entry is not None:
            return "not empty"
    return "empty"

    
def clear_database():
    """Deletes all entries in the database"""


    
menu = OrderedDict([
        ('a', add_entry),
        ('v', view_entries),
        ('b', backup_database),
        ])


if __name__ == '__main__':
    initialize()
    new_products = read_csv('inventory.csv')
    clean_data(new_products)
    if check_empty() == "empty":
        load_products(new_products)
    menu_loop()

