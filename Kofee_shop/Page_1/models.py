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
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True, default=None, on_delete=models.CASCADE)
    slug = models.SlugField()
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

    def get_total_item_price(self):
        return self.quantity * self.product_item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product_item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.product_item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


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


    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
#        if self.coupon:
#            total -= self.coupon.amount
        return total
    
    def ordered_items(self):
        list_of_items = []
        for items in self.items.filter(user=self.user):
            list_of_items.append(str(items.product_item.title + ' qtty= ' + 
                                     str(items.quantity) +  ' price/per item= ' +
                                     str(items.product_item.price) + ' price/per cat= '+ 
                                     str(items.get_final_price()))) 
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
        
        

        


