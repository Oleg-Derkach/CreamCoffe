from django import forms


class CheckoutForm(forms.Form):

    first_name = forms.CharField(widget=forms.TextInput(attrs=
                            {'placeholder':'Имя'}),
                            label="Имя")
    
    last_name = forms.CharField(widget=forms.TextInput(attrs=
                            {'placeholder':'Фамилия'}),
                            label="Фамилия")
    
    city_region = forms.CharField(widget=forms.TextInput(attrs=
                            {'placeholder':'Львов, Львовская обл.'}),
                            label="Город, Область")
    
    delivery_address = forms.CharField(widget=forms.TextInput(attrs=
                            {'placeholder':'Новая Почта № 1'}),
                            label="Адрес доставки")
    
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Тел.'}),
                            label="Телефон")
    
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs=
                            {'placeholder':'Комментарии к заказу'}),
                            label="Комментарии")
    
    
    