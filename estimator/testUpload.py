import os
import unittest
from urllib.request import Request

import app as app
import jsonify as jsonify
from django.http import request, HttpResponseRedirect
from django.urls import reverse
from six import StringIO

from estimator.models import GBOM, File
from estimator.views import file_create


class MyTestCase(unittest.TestCase):
    #def test_something(self):
     #   self.assertEqual(True, False)

    def setUpTestData(cls):
        File.title = 'GBOM'
        File.file = 'home/ivan/Downloads/Tong Hsing Weekly Data/20181105-1111'
        File.type = 5

    def test_GBOM(self):
        response = reverse('estimator:file-create')
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(GBOM.objects.count(), 0)



if __name__ == '__main__':
    unittest.main()
