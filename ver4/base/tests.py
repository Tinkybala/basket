from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Room, Topic
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from base.tokens import account_activation_token  # Import activation token generator

User = get_user_model()

class RoomAppTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user.is_active = True
        self.user.save()
        
        # Creating a topic
        self.topic = Topic.objects.create(name='basketball')

        # Room setup
        self.room = Room.objects.create(
            host=self.user,
            topic=self.topic,
            name="Test Room",
            location="Test Location",
            date=timezone.now() + timedelta(days=1),
            start_time="10:00",
            end_time="12:00",
            pax_required=10,
            description="Test Room Description"
        )

    def test_login_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser', 
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))


    def test_register_user_with_activation(self):
        # Attempt to register a new user with the required fields
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'name': 'New User',  # Add the required name field
            'password1': 'newuserpassword',
            'password2': 'newuserpassword',
            'email': 'newuser@example.com'
        })
        
        # Verify if the user is created and inactive
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user, "User registration failed, user was not created.")
        self.assertFalse(user.is_active, "User should be inactive until email is verified.")
        
        # Activation process
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_url = reverse('activate', args=[uid, token])
        response = self.client.get(activation_url)

        user.refresh_from_db()  # Reload the user to check activation
        self.assertTrue(user.is_active, "User should be active after clicking the activation link.")
        self.assertRedirects(response, reverse('login'))

    # def test_register_user(self):
    #     response = self.client.post(reverse('register'), {
    #         'username': 'newuser',
    #         'password1': 'newuserpassword',
    #         'password2': 'newuserpassword',
    #         'email': 'newuser@example.com'
    #     })
    #     user = User.objects.filter(username='newuser').first()
    #     self.assertIsNotNone(user, "User registration failed, user was not created.")
    #     self.assertFalse(user.is_active)

    def test_activate_user(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        response = self.client.get(reverse('activate', args=[uid, token]))
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertRedirects(response, reverse('login'))

    def test_join_event(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('mainJoinEvent', args=[self.room.pk]), HTTP_REFERER=reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, self.room.participants.all())

    def test_quit_event(self):
        self.room.participants.add(self.user)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('quitEvent', args=[self.room.pk]), HTTP_REFERER=reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user, self.room.participants.all())

    def test_home_view_with_filters(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('home'), {
            'location': 'Test Location',
            'date': (timezone.now() + timedelta(days=1)).date(),
            'time': '11:00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Room")

    def test_create_room(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('create-room'), {
            'name': 'New Room',
            'location': 'New Location',
            'date': (timezone.now() + timedelta(days=2)).date(),
            'start_time': '10:00',
            'end_time': '12:00',
            'pax_required': 15,
            'description': 'New Room Description',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(name='New Room').exists())

    def test_update_room(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('update-room', args=[self.room.pk]), {
            'name': 'Updated Room Name',
            'location': 'Updated Location',
            'date': (timezone.now() + timedelta(days=3)).date(),
            'start_time': '11:00',
            'end_time': '13:00',
            'pax_required': 20,
            'description': 'Updated Description',
        })
        self.room.refresh_from_db()
        self.assertEqual(self.room.name, 'Updated Room Name')
        self.assertEqual(response.status_code, 302)

    def test_delete_room(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('delete-room', args=[self.room.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Room.objects.filter(id=self.room.pk).exists())

    def test_update_user_profile(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('update-user'), {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'bio': 'This is the updated bio.'  # Add the required bio field
        })

        # Reload user data after form submission
        self.user.refresh_from_db()  # Reload user data from the database
        self.assertEqual(self.user.username, 'updateduser', "User profile update failed")
        self.assertEqual(response.status_code, 302)