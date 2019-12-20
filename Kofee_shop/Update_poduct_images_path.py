# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 10:51:55 2019

@author: Pups
"""

import xlrd
from xlutils.copy import copy
import os

PROJECT_DIR = os.getcwd() + '\\Kofee_shop'
STATIC_FILE_DIR = os.getcwd() + '\\static\media\\products_images\\'
book = xlrd.open_workbook("Price.xls")   # открывает файл
first_sheet = book.sheet_by_index(0)    # загружаем в переменную первую книгу из xl файла    
wb = copy(book)               # копия рабочей книги для записи
copy_book = wb.get_sheet(0)    # создание книги для работы
num_of_rows = first_sheet.nrows


def load_path_images():
    """
    Append list of path_images for each item
    """
    path_dict = {}
    path_dict['kofe'] = '\products_images\\kofe\\kofe.jpg'
    path_dict['tea'] =  '\products_images\\tea\\tea.jpg'
    
    for folder_name in os.listdir(STATIC_FILE_DIR):
        slug = folder_name.split()[0]
        folder_vs_image = os.listdir(STATIC_FILE_DIR + folder_name)

        list_of_images = []
        for images in folder_vs_image:     
            path = '\products_images\\' + folder_name + '\\'+ os.path.relpath(images)                 
            list_of_images.append(path)
        path_dict[slug] = list_of_images
        
    for row_index in range(1,num_of_rows):
        row = first_sheet.row_values(row_index)
        if str(int(row[0])) in path_dict:
            copy_book.write(row_index, 7, ';'.join(path_dict[str(int(row[0]))]))
        elif 'кофе' in row[1].lower():
            copy_book.write(row_index, 7, path_dict['kofe'])
        elif 'чай' in row[1].lower():
            copy_book.write(row_index, 7, path_dict['tea']) 
        else:
            copy_book.write(row_index, 7, path_dict['tea']) 
    wb.save('Price.xls')
    
load_path_images()