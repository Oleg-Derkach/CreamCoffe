# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 10:51:55 2019

@author: Pups
"""

import xlrd
import os, sys

NACENKA = 50
PROJECT_DIR = os.getcwd() + '\\Kofee_shop'
STATIC_FILE_DIR = os.getcwd() + '\\static\media\\products_images\\'

sys.path.append(PROJECT_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'

import django

django.setup()

from Page_1.models import ProductImage, Item, Category


book = xlrd.open_workbook("Price.xls")   # открывает файл
first_sheet = book.sheet_by_index(0)    # загружаем в переменную первую книгу из xl файла    
num_of_rows = first_sheet.nrows


def add_new_product_to_DB():
    for row_index in range(1,num_of_rows):   
        row = first_sheet.row_values(row_index)
        cat_list = []
        
        for category in Category.objects.all():
            cat_list.append(category.category_name)
        if row[1] not in cat_list:
            cat = Category() 
            cat.category_name = row[1]
            cat.save()  
    
        item = Item()    
        item.slug = int(row[0])         
        item.title = row[2]
        item.price = row[3] + NACENKA 
        item.description = row[6]
        category = Category.objects.filter(category_name = row[1])[0]
        item.category = category
        item.save() 
        
        folder = row[7].split(';')
        for image_path in folder:
            product_image = ProductImage()
            product_image.product = item
            if image_path == folder[0]:
                product_image.is_main = True
            product_image.image = image_path
            product_image.save()

add_new_product_to_DB() 