######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for
from service.models import Product, Category
from service.common import status
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Health check endpoint"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Home page"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Check content type is correct"""
    if request.headers.get("Content-Type") != content_type:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
             f"Content-Type must be {content_type}")


######################################################################
# C R E A T E   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """Creates a Product"""
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# R E A D   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """Reads a Product"""
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, 
             f"Product with id '{product_id}' was not found.")
    return product.serialize(), status.HTTP_200_OK


######################################################################
# U P D A T E   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """Updates a Product"""
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, 
             f"Product with id '{product_id}' was not found.")
    product.deserialize(request.get_json())
    product.update()
    return product.serialize(), status.HTTP_200_OK


######################################################################
# D E L E T E   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """Deletes a Product"""
    product = Product.find(product_id)
    if product:
        product.delete()
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# L I S T   P R O D U C T S
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Lists Products with optional filtering"""
    products = []
    params = request.args
    
    if "name" in params:
        products = Product.find_by_name(params["name"])
    elif "category" in params:
        category = getattr(Category, params["category"].upper())
        products = Product.find_by_category(category)
    elif "available" in params:
        available = params["available"].lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available)
    else:
        products = Product.all()

    results = [product.serialize() for product in products]
    return jsonify(results), status.HTTP_200_OK