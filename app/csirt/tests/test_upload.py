# Dans l'application où vous voulez ajouter les tests, par exemple `myapp/tests.py`

from django.test import TestCase
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class S3UploadTest(TestCase):
    def test_s3_upload(self):
        content = ContentFile('Test content')
        file_name = 'test_file.txt'
        file_path = default_storage.save(file_name, content)
        self.assertTrue(default_storage.exists(file_path))
        print(f"File uploaded to: {file_path}")
