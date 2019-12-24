import django_filters
from .models import ProductImage
from django import forms

class ItemFilters(django_filters.FilterSet):
    
    product__title = django_filters.CharFilter(lookup_expr='icontains', 
                                               label = '', 
                                               widget=forms.TextInput(attrs={
                                    'placeholder': 'Поиск', 
                                    'class': 'form-control search__input'}))
    class Meta:
        model = ProductImage
        fields = ['product__title']
        
        
        
  