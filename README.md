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

## Auth

`create user` [/api/users/create/](#)  
 `get token` [/api/users/token/](#)

## Auth

**POST** `create user` [/api/users/create/](#)  
**POST** `get token` [/api/users/token/](#)

## Product

**POST** `create product` [/api/products/](#)  
 **PUT** `update product` [/api/products/:id/](#)  
 **GET** `get all products` [/api/products/](#)  
 **GET** `retrieve product` [/api/products/:id/](#)  
 **DELETE** `delete product` [/api/products/:id/](#)  
**PUT** `set stock of product` [/api/products/:id/stock/](#) paramaters: { "stock": int}

## Order

**POST** `create order` [/api/orders/](#) paramaters:
{
"details" : [
{
"product": product_id,
"cuantity": int
}
] }  
**PUT** `update order` [/api/orders/:id/](#) paramaters:
{
"details" : [
{
"product": product_id,
"cuantity": int
}
] }  
 **GET** `get all orders` [/api/orders/](#)  
 **GET** `retrieve order` [/api/orders/:id/](#)  
 **DELETE** `delete order` [/api/orders/:id/](#)  
 **DELETE** `delete detail` [/api/orders/:id/details/:detail_id](#)
