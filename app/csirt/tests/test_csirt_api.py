from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Csirt
from csirt.serializers import (CsirtSerializer, CsirtDetailSerializer)

import tempfile
import os
from PIL import Image

CSIRTS_URL = reverse('csirt:csirt-list')

def detail_url(csirt_id):
    """Create and return a csirt detail URL"""
    return reverse('csirt:csirt-detail', args=[csirt_id])


def image_upload_url(csirt_id):
    """Create and return an image upload URL."""
    return reverse('csirt:csirt-upload-image', args=[csirt_id])


def create_csirt(user, **params):
    """Create and return a sample csirt"""

    defaults = {
        'name':'Sample csirt name',
        'location':{
            'longitude':"6.122334",
             'latitude':"0.122334",
        },
        'contact':'csirt@email.com',
        'description':'Sample description',
        'website' : 'http://example.com'        
    }

    defaults.update(params)

    csirt = Csirt.objects.create(user=user, **defaults)
    return csirt



def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PubliccsirtAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res =self.client.get(CSIRTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivatecsirtApiTests(TestCase):
    """Test authentication API request"""

    def setUp(self):
        self.client=APIClient()
        self.user = create_user(email='user@example.com', password="test123")
       
        self.client.force_authenticate(self.user)

    def test_retrive_csirts(self):
        """Test retriving a list of csirts"""

        create_csirt(user=self.user)
        create_csirt(user=self.user)
        res =self.client.get(CSIRTS_URL)
        csirts = Csirt.objects.all().order_by('-id')
        serializer = CsirtSerializer(csirts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    
    def test_csirt_list_limited_to_user(self):
        """Test list of csirts is limited to authenticated user"""
        other_user = create_user(
           email= 'other@gmail.com',
        password='test123'
        )

        create_csirt(user=other_user)
        create_csirt(user=self.user)
        res = self.client.get(CSIRTS_URL)
        csirts = Csirt.objects.filter(user=self.user)
        serializer = CsirtSerializer(csirts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_csirt_detail(self):
        """Test get csirt detail."""
        csirt = create_csirt(user=self.user)

        url = detail_url(csirt.id)
        res = self.client.get(url)

        serializer = CsirtDetailSerializer(csirt)
        self.assertEqual(res.data, serializer.data)


    
    def test_create_csirt(self):
        """Test creating a csirt"""
        payload={
            'name':'Sample csirt',
        'location':{
            'longitude':"6.122334",
             'latitude':"0.122334",
        },
        'contact':'csirt@email.com',
        'description':'Sample description',
        'website' : 'http://example.com'        
        }
        res = self.client.post(CSIRTS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        csirt = Csirt.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(csirt, k), v)
        self.assertEqual(csirt.user, self.user)


    def test_partial_update(self):
        """Test partial update of a csirt"""
        original_website = 'http://example.com'
        csirt= create_csirt(
            user= self.user, name='Sample csirt name',
            website=original_website
        )
        payload = {'name':'New csirt name'}
        url = detail_url(csirt.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        csirt.refresh_from_db()
        self.assertEqual(csirt.name, payload['name'])
        self.assertEqual(csirt.website, original_website)
        self.assertEqual(csirt.user, self.user)

    def test_update_user_returns_error(self):
        """ Test changing the csirt user results in an error """
        new_user = create_user(email='user2@example.com', password='test123')
        csirt = create_csirt(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(csirt.id)
        self.client.patch(url, payload)
        csirt.refresh_from_db()
        self.assertEqual(csirt.user, self.user)

    def test_delete_csirt(self):
        """Test deleting a csirt successfull."""
        csirt = create_csirt(user=self.user)
        url = detail_url(csirt.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Csirt.objects.filter(id=csirt.id).exists())


class ImageUploadTests(TestCase):
    
    """Test for the image upload API"""


    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )

        self.client.force_authenticate(self.user)
        self.csirt = create_csirt(user=self.user)

    def tearDown(self):
        self.csirt.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a csirt"""
        url = image_upload_url(self.csirt.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image':image_file}
            res = self.client.post(url, payload, format ='multipart')
        self.csirt.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.csirt.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.csirt.id)
        payload = {'image': 'notanimage'}
        res=self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    