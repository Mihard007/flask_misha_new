from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout
from decouple import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config("DATABASE_URI", default="")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  title = db.Column(db.String(100), nullable=False)
  price = db.Column(db.Integer, nullable=False)
  isActive = db.Column(db.Boolean, default=True)

  def __repr__(self):
    return f'Basket: {self.title}'

@app.route('/')
def index():
  items = Item.query.order_by(Item.price).all()
  return render_template('index.html', data=items)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/create', methods=['POST', 'GET'])
def create():
  if request.method == "POST":
    title = request.form['title']
    price = request.form['price']
    item = Item(title=title, price=price)

    try:
      db.session.add(item)
      db.session.commit()
      return redirect('/')
    except:
      return "Error"
  else:
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
  if request.method == "POST":
    title = request.form['title']
    price = request.form['price']

    try:
      new_item = Item.query.filter_by(id=f'{id}').first()
      new_item.title = title
      new_item.price = price
      db.session.commit()
      return redirect('/')
    except:
      return "Error"
  else:
    return render_template('edit.html')

@app.route('/delete/<int:id>')
def delete_item(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/')

@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)
    api = Api(merchant_id=1396424, secret_key='test')
    checkout = Checkout(api=api)
    data = {
    "currency": "USD",
    "amount": item.price * 100
    }

    url = checkout.url(data).get('checkout_url')
    return redirect(url)

if __name__ == "__main__":
  app.run(debug=True, port=8080)