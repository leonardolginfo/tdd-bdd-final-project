######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
import os
import logging
from decimal import Decimal
from urllib.parse import quote_plus
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product, Category
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


class TestProductRoutes(TestCase):
    """Test Cases for Product Routes"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """Runs after each test"""
        db.session.remove()

    def _create_products(self, count=1):
        """Factory to create products"""
        products = []
        for _ in range(count):
            product = ProductFactory()
            resp = self.client.post(BASE_URL, json=product.serialize())
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            products.append(resp.get_json())
        return products

    ######################################################################
    # TEST CASES
    ######################################################################

    def test_index(self):
        """Test index page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health(self):
        """Test health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], "OK")

    def test_create_product(self):
        """Test creating a product"""
        product = ProductFactory()
        resp = self.client.post(
            BASE_URL,
            json=product.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.headers.get("Location"))

    def test_get_product(self):
        """Test getting a product"""
        product = self._create_products(1)[0]
        resp = self.client.get(f"{BASE_URL}/{product['id']}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["id"], product["id"])

    def test_update_product(self):
        """Test updating a product"""
        product = self._create_products(1)[0]
        product["description"] = "updated"
        resp = self.client.put(
            f"{BASE_URL}/{product['id']}",
            json=product,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["description"], "updated")

    def test_delete_product(self):
        """Test deleting a product"""
        product = self._create_products(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{product['id']}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.client.get(f"{BASE_URL}/{product['id']}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_products(self):
        """Test listing all products"""
        self._create_products(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), 5)

    def test_query_by_name(self):
        """Test querying by name"""
        products = self._create_products(3)
        name = products[0]["name"]
        count = len([p for p in products if p["name"] == name])
        resp = self.client.get(BASE_URL, query_string={"name": name})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), count)

    def test_query_by_category(self):
        """Test querying by category"""
        products = self._create_products(5)
        category = products[0]["category"]
        count = len([p for p in products if p["category"] == category])
        resp = self.client.get(BASE_URL, query_string={"category": category})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.get_json()), count)

    def test_query_by_availability(self):
        """Test querying by availability"""
        self._create_products(10)
        resp = self.client.get(BASE_URL, query_string={"available": "true"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertTrue(all(p["available"] is True for p in data))