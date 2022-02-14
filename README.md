# Ecommerce api

## Requirements

    python > 3.7

## Preparing the environment

Create your python environment

```bash
python3 -m venv env
source env/bin/activate
```

## install dependencies

`pip install -r requirements.txt`

## Run migrations

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

## Run server

```bash
python manage.py runserver
```


# API endpoints

## URL
[https://ntoo.pythonanywhere.com/api/](https://ntoo.pythonanywhere.com/api/)  

## Auth

`create user` [/api/user/create/](https://ntoo.pythonanywhere.com/api/user/create/)  
 `get token` [/api/user/token/](https://ntoo.pythonanywhere.com/api/user/token/)


## Product

**POST** `create product` [/api/products/](https://ntoo.pythonanywhere.com/api/products/)  
 **PUT** `update product` [/api/products/:id/](https://ntoo.pythonanywhere.com/api/products/)  
 **GET** `get all products` [/api/products/](https://ntoo.pythonanywhere.com/api/products/)  
 **GET** `retrieve product` [/api/products/:id/](https://ntoo.pythonanywhere.com/api/products/)  
 **DELETE** `delete product` [/api/products/:id/](https://ntoo.pythonanywhere.com/api/products/)  
**PUT** `set stock of product` [/api/products/:id/stock/](https://ntoo.pythonanywhere.com/api/products/) paramaters: { "stock": int}

## Order

**POST** `create order` [/api/orders/](https://ntoo.pythonanywhere.com/api/orders/) paramaters:
{
"details" : [
{
"product": product_id,
"cuantity": int
}
] }  
**PUT** `update order` [/api/orders/:id/](https://ntoo.pythonanywhere.com/api/orders/) paramaters:
{
"details" : [
{
"product": product_id,
"cuantity": int
}
] }  
 **GET** `get all orders` [/api/orders/](https://ntoo.pythonanywhere.com/api/orders/)  
 **GET** `retrieve order` [/api/orders/:id/](https://ntoo.pythonanywhere.com/api/orders/)  
 **DELETE** `delete order` [/api/orders/:id/](https://ntoo.pythonanywhere.com/api/orders/)  
 **DELETE** `delete detail` [/api/orders/:id/details/:detail_id](https://ntoo.pythonanywhere.com/api/orders/)
