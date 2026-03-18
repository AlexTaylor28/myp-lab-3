from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from billing.models import Provider, Barrel, Invoice, InvoiceLine
from datetime import date

User = get_user_model()

class BarrelEndpointTests(APITestCase):
    
    def setUp(self):
        
        self.provider_a = Provider.objects.create(name = "Provider A", address = "123 A St", tax_id = "TAX-A")
        self.provider_b = Provider.objects.create(name = "Provider B", address = "456 B St", tax_id = "TAX-B")
        
        self.user_a = User.objects.create_user(username = "user A", password = "123", provider = self.provider_a)
        
        self.invoice_a = Invoice.objects.create(provider = self.provider_a, invoice_no = "INV-001", issued_on = date.today())
        
        self.billed_barrel = Barrel.objects.create(provider = self.provider_a, number = "B-999", oil_type = "Olive", liters = 100, billed = True)
        InvoiceLine.objects.create(invoice = self.invoice_a, barrel = self.billed_barrel, liters = 100, unit_price = "5.00", description = "Test")


# ---------------------------------------------------------------------------------
# Exercise 4 — Creating barrels: provider is taken from the logged-in user
# ---------------------------------------------------------------------------------

    def test_create_barrel_with_different_provider_in_payload_returns_201_and_forces_user_provider(self):
        
        self.client.force_authenticate(user = self.user_a)
        
        payload = {
            "number": "B-001",
            "oil_type": "Sunflower",
            "liters": 200,
            "provider": self.provider_b.id
        }
        
        url = reverse("barrel-list")
        response = self.client.post(url, payload, format = "json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        barrel = Barrel.objects.get(number = "B-001")
        self.assertEqual(barrel.provider_id, self.provider_a.id)
        self.assertEqual(response.data["provider"], self.provider_a.id)
        

# ---------------------------------------------------------------------------------
# Exercise 6 —  Tests on DELETE endpoints
# ---------------------------------------------------------------------------------

    def test_delete_barrel_linked_to_invoice_returns_400_and_prevents_deletion(self):
        
        self.client.force_authenticate(user = self.user_a)
        
        url = reverse("barrel-detail", kwargs = {"pk": self.billed_barrel.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Barrel.objects.filter(id = self.billed_barrel.id).exists())