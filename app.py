from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from password import my_password
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://root:{my_password}@localhost/e_commerce"
db = SQLAlchemy(app)
ma = Marshmallow(app)


class CustomerSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)


    class Meta:
        fields = ("id", "name", "email", "phone")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    id = fields.Integer(required=True)
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("username", "password", "id", "customer_id")

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

class ProductSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    price = fields.Integer(required=True)
    inventory = fields.Integer(required=True)
    
    class Meta:
        fields = ("id", "name", "price", "inventory")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class OrderSchema(ma.Schema):
    id = fields.Integer(required=True)
    date = fields.Date(required=True)
    customer_id = fields.Integer(required=True)
    
    class Meta:
        fields = ("id", "date", "customer_id")
        
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(320), nullable=False)
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

class Customer_Account(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref=('customer_account'), uselist=False)
    
order_product = db.Table('Order_Product',
                         db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
                         db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    inventory = db.Column(db.Integer, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    
@app.route('/')
def home():
    return 'Hooray! You made it!'

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer():
    customer = Customer.query.all()
    return customer_schema.jsonify(customer)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_customer = Customer(id=customer_data['id'], name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New Customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer.id = customer_data['id']
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "Customer details updated successfully"}), 200

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer removed successfully"}), 200

@app.route('/customer_accounts', methods=['GET'])
def get_customer_accounts():
    customer_accounts = Customer_Account.query.all()
    return customer_accounts_schema.jsonify(customer_accounts)

@app.route('/customer_accounts/<int:id>', methods=['GET'])
def get_customer_account():
    customer_account = Customer_Account.query.all()
    return customer_schema.jsonify(customer_account)

@app.route('/customer_accounts', methods=['POST'])
def add_customer_account():
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_customer_account = Customer(id=customer_account_data['id'], username=customer_account_data['username'], password=customer_account_data['password'], customer_id=customer_account_data['customer_id'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message": "New Customer Account added successfully"}), 201

@app.route('/customer_accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    customer_account = Customer_Account.query.get_or_404(id)
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    customer_account.id = customer_account_data['id']
    customer_account.username = customer_account_data['username']
    customer_account.password = customer_account_data['password']
    customer_account.customer_id = customer_account_data['customer_id']
    db.session.commit()
    return jsonify({"message": "Customer Account details updated successfully"}), 200

@app.route('/customer_accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    customer_account = Customer_Account.query.get_or_404(id)
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message": "Customer Account removed successfully"}), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return orders_schema.jsonify(orders)

@app.route('/orders/<int:id>', methods=['GET'])
def get_order():
    order = Order.query.all()
    return order_schema.jsonify(order)

@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_order = Order(id=order_data['id'], date=order_data['date'], customer_id=order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "New Order added successfully"}), 201

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get_or_404(id)
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    order.id = order_data['id']
    order.date = order_data['date']
    order.customer_id = order_data['customer_id']
    db.session.commit()
    return jsonify({"message": "Order details updated successfully"}), 200

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order removed successfully"}), 200

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product():
    product = Product.query.all()
    return product_schema.jsonify(product)

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_product = Product(id=product_data['id'], name=product_data['name'], price=product_data['price'], inventory=product_data['inventory'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New Product added successfully"}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.id = product_data['id']
    product.name = product_data['name']
    product.price = product_data['price']
    product.inventory = product_data['inventory']
    db.session.commit()
    return jsonify({"message": "Product details updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product removed successfully"}), 200

with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True)
    
