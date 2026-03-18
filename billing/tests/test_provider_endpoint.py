from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel

User = get_user_model()

class ProviderEndpointTests(APITestCase):
    
    def setUp(self):
        
        self.provider_a = Provider.objects.create(name = "Provider A", address = "123 A St", tax_id = "TAX-A")
        self.provider_b = Provider.objects.create(name = "Provider B", address = "456 B St", tax_id = "TAX-B")

        self.admin_user = User.objects.create_superuser(username = "admin", password = "123")
        self.user_a = User.objects.create_user(username = "user A", password = "123", provider = self.provider_a)

        Barrel.objects.create(provider = self.provider_a, number = "B-001", oil_type = "Olive", liters = 100, billed = True)
        Barrel.objects.create(provider = self.provider_a, number = "B-002", oil_type = "Olive", liters = 50, billed = False)
        

    def test_provider_list_returns_name_and_tax_id(self):
        
        provider = Provider.objects.create(
            name="Acme Oils",
            address="Main St 1",
            tax_id="TAX-12345",
        )
        
        user = User.objects.create_user(
            username="provider_user",
            password="strongpass123",
            provider=provider,
        )
        
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("name", response.data[0])
        self.assertIn("tax_id", response.data[0])
        self.assertEqual(response.data[0]["name"], provider.name)
        self.assertEqual(response.data[0]["tax_id"], provider.tax_id)


# ---------------------------------------------------------------------------------
# Exercise 5 — Creating barrels: provider is taken from the logged-in user
# ---------------------------------------------------------------------------------

    def test_get_provider_list_as_superuser_returns_200_and_all_providers(self):
        
        self.client.force_authenticate(user = self.admin_user)
        
        url = reverse("provider-list")
        response = self.client.get(url)

        exptected_count = Provider.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), exptected_count)


    def test_get_provider_list_as_regular_user_returns_200_and_only_own_provider(self):
        
        self.client.force_authenticate(user = self.user_a)        
        
        url = reverse("provider-list")
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.provider_a.id)
        

    def test_get_provider_detail_as_superuser_returns_200_and_correct_liters(self):
        
        self.client.force_authenticate(user = self.admin_user)
        
        url = reverse("provider-detail", kwargs = {"pk": self.provider_a.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.provider_a.id)
        self.assertEqual(response.data["billed_liters"], 100)
        self.assertEqual(response.data["liters_to_bill"], 50)


    def test_get_provider_detail_as_regular_user_returns_error(self):
        
        self.client.force_authenticate(user = self.user_a)
        
        url = reverse("provider-detail", kwargs = {"pk": self.provider_b.id})
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
