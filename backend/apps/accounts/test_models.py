"""Tests for accounts models."""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from .models import CustomUser, UserProfile, Address


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }

    def test_create_user(self) -> None:
        """Test creating a regular user."""
        user = CustomUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_email_verified)

    def test_create_superuser(self) -> None:
        """Test creating a superuser."""
        user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_email_unique_constraint(self) -> None:
        """Test that email must be unique."""
        CustomUser.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                email='test@example.com',  # Duplicate email
                username='testuser2',
                password='testpass123'
            )

    def test_user_string_representation(self) -> None:
        """Test user __str__ method."""
        user = CustomUser.objects.create_user(**self.user_data)
        expected = "test@example.com (Test User)"
        self.assertEqual(str(user), expected)

    def test_full_name_property(self) -> None:
        """Test full_name property."""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, "Test User")
        
        # Test with only username
        user_no_name = CustomUser.objects.create_user(
            email='noname@example.com',
            username='noname',
            password='testpass123'
        )
        self.assertEqual(user_no_name.full_name, "noname")

    def test_phone_number_validation(self) -> None:
        """Test phone number validation."""
        # Valid phone numbers
        valid_numbers = ['+1234567890', '1234567890', '+123456789012345']
        
        for number in valid_numbers:
            user_data = self.user_data.copy()
            user_data['phone_number'] = number
            user_data['email'] = f'test{number[-4:]}@example.com'
            user_data['username'] = f'user{number[-4:]}'
            
            user = CustomUser(**user_data)
            user.full_clean()  # This will raise ValidationError if invalid


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_create_profile(self) -> None:
        """Test creating a user profile."""
        profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            location='Test City',
            marketing_emails=False
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.location, 'Test City')
        self.assertFalse(profile.marketing_emails)
        self.assertFalse(profile.sms_notifications)

    def test_profile_string_representation(self) -> None:
        """Test profile __str__ method."""
        profile = UserProfile.objects.create(user=self.user)
        expected = "Profile of test@example.com"
        self.assertEqual(str(profile), expected)

    def test_one_to_one_relationship(self) -> None:
        """Test one-to-one relationship with user."""
        profile = UserProfile.objects.create(user=self.user)
        
        # Access profile from user
        self.assertEqual(self.user.profile, profile)
        
        # Cannot create another profile for the same user
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user)


class AddressModelTest(TestCase):
    """Test cases for Address model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.address_data = {
            'user': self.user,
            'type': 'shipping',
            'first_name': 'John',
            'last_name': 'Doe',
            'address_line_1': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'postal_code': '12345',
            'country': 'United States'
        }

    def test_create_address(self) -> None:
        """Test creating an address."""
        address = Address.objects.create(**self.address_data)
        
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.type, 'shipping')
        self.assertEqual(address.first_name, 'John')
        self.assertEqual(address.city, 'Anytown')
        self.assertFalse(address.is_default)

    def test_address_string_representation(self) -> None:
        """Test address __str__ method."""
        address = Address.objects.create(**self.address_data)
        expected = "John Doe - Anytown, CA"
        self.assertEqual(str(address), expected)

    def test_full_address_property(self) -> None:
        """Test full_address property."""
        address_data = self.address_data.copy()
        address_data['company'] = 'Test Company'
        address_data['address_line_2'] = 'Apt 4B'
        
        address = Address.objects.create(**address_data)
        
        expected_lines = [
            "John Doe",
            "Test Company",
            "123 Main St",
            "Apt 4B",
            "Anytown, CA 12345",
            "United States"
        ]
        expected = '\n'.join(expected_lines)
        
        self.assertEqual(address.full_address, expected)

    def test_multiple_addresses_same_user(self) -> None:
        """Test user can have multiple addresses."""
        # Create shipping address
        shipping_address = Address.objects.create(**self.address_data)
        
        # Create billing address
        billing_data = self.address_data.copy()
        billing_data['type'] = 'billing'
        billing_data['city'] = 'Other City'
        billing_address = Address.objects.create(**billing_data)
        
        self.assertEqual(self.user.addresses.count(), 2)
        self.assertIn(shipping_address, self.user.addresses.all())
        self.assertIn(billing_address, self.user.addresses.all())

    def test_default_address_constraint(self) -> None:
        """Test that only one default address per type per user is allowed."""
        # Create first default shipping address
        Address.objects.create(**self.address_data, is_default=True)
        
        # Try to create another default shipping address for same user
        second_address_data = self.address_data.copy()
        second_address_data['city'] = 'Different City'
        
        with self.assertRaises(IntegrityError):
            Address.objects.create(**second_address_data, is_default=True)