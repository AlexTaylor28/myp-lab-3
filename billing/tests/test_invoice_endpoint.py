from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from billing.models import Provider, Invoice, Barrel, InvoiceLine
from datetime import date

User = get_user_model()

class InvoiceEndpointTests(APITestCase):
    
    def setUp(self):
        self.provider_a = Provider.objects.create(name = "Provider A", address = "123 A St", tax_id = "TAX-A")
        self.provider_b = Provider.objects.create(name = "Provider B", address = "456 B St", tax_id = "TAX-B")
        
        self.user_a = User.objects.create_user(username = "user A", password = "123", provider = self.provider_a)
        self.client.force_authenticate(user = self.user_a)
        
        self.invoice_a = Invoice.objects.create(provider = self.provider_a, invoice_no = "INV-A001", issued_on = date.today())
        self.invoice_b = Invoice.objects.create(provider = self.provider_b, invoice_no = "INV-B002", issued_on = date.today())
        
        self.barrel_b = Barrel.objects.create(provider = self.provider_b, number = "B-001", oil_type = "Olive", liters = 100)

# ---------------------------------------------------------------------------------
# Exercise 2 — Adding a barrel to an invoice must enforce same provide
# ---------------------------------------------------------------------------------

    def test_add_line_with_barrel_from_different_provider_returns_400(self):

        payload = {
            "unit_price": "5.00",
            "barrel": self.barrel_b.id,
            "liters": 100,
            "description": "Premium Olive Oil"
        }
        
        url = reverse("invoice-add-line", kwargs = {"pk": self.invoice_a.id})
        response = self.client.post(url, payload, format = "json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "barrel provider must match invoice provider")
        self.assertEqual(InvoiceLine.objects.count(), 0)
        self.assertFalse(Barrel.objects.get(id = self.barrel_b.id).billed)
        
 
# ---------------------------------------------------------------------------------
# Exercise 3 —  Provider scoping: users must not access other providers’ invoices
# ---------------------------------------------------------------------------------

    def test_get_invoice_list_as_scoped_user_returns_200_and_own_invoices(self):
        
        url = reverse("invoice-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 
        self.assertEqual(response.data[0]["invoice_no"], self.invoice_a.invoice_no)
        
    def test_get_invoice_detail_for_different_provider_returns_404(self):
        
        url = reverse("invoice-detail", kwargs = {"pk": self.invoice_b.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)