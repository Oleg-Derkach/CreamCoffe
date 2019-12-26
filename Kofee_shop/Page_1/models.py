from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.conf import settings
from django.db.models import Sum



class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Item(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    price = models.FloatField()
    min_req = models.FloatField()
    pcs_or_kg = models.CharField(max_length=10)
    category = models.ForeignKey(Category, default=None, on_delete=models.CASCADE)   
    available = models.BooleanField(default=True)
    description = models.TextField()
    

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        '''
        возвращает абсолютный путь к обьекту (товару)
        где  'core' - папка , а 'product' название url пути в URLS.PY
        так в HTML документе можно указать {{ item.get_absolute_url }}
        который при загрузке возьмет self.slug и вставит его в URLS.PY
        в path('product/<slug>/', ItemDetailView.as_view(), name='product'),
        таким образом получится путь 'product/shirt-1/' , который сгенерирует
        ItemDetailView.as_view(), то есть страницу товара
        ''' 
        return reverse("page_1:product_view", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        '''
        Аналогично с get_absolute_url, метод возвращает
        path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
        котрый вызывает метод add_to_cart
        '''
        return reverse("page_1:add_to_cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        '''
        Аналогично с get_absolute_url, метод возвращает
        path('remove-from-cart/<slug>/', remove-from-cart, name='remove-from-cart'),
        котрый вызывает метод get_remove-from-cart
        '''
        return reverse("page_1:remove_from_cart", kwargs={'slug': self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Item, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products_images/')
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "%s" % self.id

    class Meta:
        verbose_name = 'Product_Photo'
        verbose_name_plural = 'Product_Photos'
        ordering = ['product__title']


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product_item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    

    def __str__(self):
        return "{} of {}".format(self.quantity, self.product_item.title)

    def get_total_quantity(self):
        return self.product_item.min_req * self.quantity

    def get_one_kg_price(self):
        if self.product_item.pcs_or_kg == 'KG':
            return self.product_item.price
        if self.product_item.pcs_or_kg == 'PCS':
            return self.product_item.price / self.product_item.min_req          

    def get_final_price(self):
        return self.get_total_quantity() * self.get_one_kg_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    address = models.ForeignKey('Address', related_name='shipping_address', 
        on_delete=models.SET_NULL, blank=True, null=True)
 
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()

        return total
    
    def ordered_items(self):
        list_of_items = []
        for items in self.items.filter(user=self.user):
            list_of_items.append(str(items.product_item.title +'\n'+ ' qtty= ' + 
                                     str(items.quantity)+'\n'+ ' price/per item= ' +
                                     str(items.product_item.price)+'\n'+ ' price/per cat= '+ 
                                     str(items.get_final_price())+'\n'+'------------------')) 
        return list_of_items
    
    
class Address(models.Model): 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    first_last_name = models.CharField(max_length=50, verbose_name="Заказчик", null=True)
    city_region = models.CharField(max_length=255, blank=True)
    delivery_address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, default=None, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа", null=True)
    comments = models.TextField(blank=True)
    
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'
        
        

        


