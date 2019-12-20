# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 07:56:12 2019

@author: Pups
"""

from django.core.management.base import BaseCommand, CommandError
from Page_1.models import ProductCategory

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        category = ProductCategory.objects.all()
        print(category)
        
