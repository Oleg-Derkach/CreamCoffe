# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 10:43:46 2019

@author: Pups
"""
from django.conf.urls import url, include
from django.urls import path,  re_path
from .views import (home_view, 
                    logout_view,
                    product_view,
                    add_to_cart,
                    remove_from_cart,
                    OrderSummaryView,
                    remove_single_item_from_cart,
                    CheckoutView,
                    cookies_demo,
                    
                    )

app_name = 'page_1'

urlpatterns = [
        path('', home_view, name='home_view'),
        path('cookies_demo/', cookies_demo, name='cookies_demo'),
        path('logout/', logout_view, name='logout'),
        path('order_summary/', OrderSummaryView.as_view(), name='order_summary'),
        path('product/<slug>/', product_view, name='product_view'),
        path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
        path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
        path('remove_item_from_cart/<slug>/', 
             remove_single_item_from_cart, name='remove_single_item_from_cart'),
        path('checkout/', CheckoutView.as_view(), name='checkout'),     
               
               ]





















