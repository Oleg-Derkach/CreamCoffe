from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.views.generic import View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout, authenticate, login
from .models import Item, OrderItem, Order, ProductImage, Category, Address
from .forms import CheckoutForm
from .telegram_bot import send_telegram_notification, send_email_notification
from django.contrib.auth.models import User



def _filter(request, cat_status):

    product_card = ProductImage.objects.filter(is_main = True).filter(product__available=True)
    counter = 0
    
    for cat_id in cat_status:
        if cat_status[cat_id] == 'off':
            product_card = product_card.exclude(product__category__id=int(cat_id))
            counter += 1
    if counter == len(cat_status):
        return ProductImage.objects.filter(is_main = True).filter(product__available=True)
    return product_card
            

def authenticate_anonymous_user(request):
    if request.session.session_key:    
        ses_key = request.session.session_key
    else:         
        request.session.cycle_key()
        ses_key = request.session.session_key
        User.objects.create_user(username = ses_key, password=ses_key)
    if not request.user.is_authenticated:
        user = authenticate(request, username=ses_key, password=ses_key)
        if user is not None:
            login(request, user) 
            

def home_view(request):
        
    all_category = [cat for cat in Category.objects.all()]
    main_filter = {'check_box':{}, 'search_filt':'', 'cat_on':[]}
    off_status_of_check_box = 0
    page = request.GET.get('page', request.COOKIES.get('page'))
    alone_category = request.GET.get('alone_category')  
    
    if request.method == 'GET':
        for cat in all_category:
            if request.COOKIES.get(str(cat.id)) == 'on':
                main_filter['check_box'][str(cat.id)] = 'on'
                main_filter['cat_on'].append(int(cat.id))
            else:
                main_filter['check_box'][str(cat.id)] = 'off'
            if request.GET.get('search') == 'reset':
                main_filter['cat_on'] = []
                main_filter['check_box'][str(cat.id)] = 'off'
        if alone_category:
            main_filter['cat_on'].append(int(alone_category))
            main_filter['check_box'][str(alone_category)] = 'on'
   
    elif request.method == 'POST':
        page = 1
        for cat in all_category:
            if str(cat.id) in request.POST:
                main_filter['check_box'][str(cat.id)] = 'on'
                main_filter['cat_on'].append(int(cat.id))
            else:
                main_filter['check_box'][str(cat.id)] = 'off'
                off_status_of_check_box += 1 
                                 
    main_filter['search_filt'] = request.GET.get('search_filt')
    if main_filter['search_filt'] == None:
        main_filter['search_filt'] = request.COOKIES.get('search_filt')
        if main_filter['search_filt'] == None:
            main_filter['search_filt'] = 'title'
    else:
        page = 1
                
    if off_status_of_check_box ==  len(all_category):
        product_card = ProductImage.objects.filter(is_main = True).filter(product__available=True)
    else:
        product_card = _filter(request, main_filter['check_box']) 
    
    if request.GET.get('search') == 'reset': 
        main_filter['search_filt'] = 'title'
        
    
    serched_slug =  request.GET.get('product__title')  
    if serched_slug != None:
        product_card = product_card.filter(product__title_lower__contains=serched_slug.lower())
      
    product_card = product_card.order_by("product__" + main_filter['search_filt'])
    

    if request.user.is_authenticated:
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            order = Order.objects.create(user=request.user, ordered=False, ordered_date=timezone.now())
    else:
        authenticate_anonymous_user(request)
        order = Order.objects.create(user=request.user, ordered=False, ordered_date=timezone.now())
         
    paginator = Paginator(product_card, 20)    # 20 Items per page

    if page == None:
        page = 1
    if request.GET.get('page') != None:
        page = request.GET.get('page')

    queryset = paginator.get_page(page)
    is_paginated = queryset.has_other_pages()

    response = render(request, 'main_page.html', 
        {'category': all_category,       'cat_on':main_filter['cat_on'],
        'order':order,                   'search_filt':main_filter['search_filt'],
        'query_products':queryset,       'is_paginated':is_paginated,
        'items_count':len(product_card)
        }) 
    
    for item in main_filter['check_box']:   
        response.set_cookie(str(item), main_filter['check_box'][item]) 
    response.set_cookie('search_filt', main_filter['search_filt'])
    response.set_cookie('page', page)
        
    return response 

  
def product_view(request, slug):

    product_images = ProductImage.objects.filter(product__slug=slug)
    product_item = Item.objects.filter(slug=slug)[0]
    category = Category.objects.all()
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            order = Order.objects.create(user=request.user, ordered=False, ordered_date=timezone.now())
    else:
        order = None
    return render(request, "card_page.html", locals())

class CheckoutView(View):
    
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        return render(self.request, "checkout_new.html", context={'form' : form})
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False) 

            if form.is_valid():
                address = Address(
                      user =              self.request.user,
                      first_name =        form.cleaned_data.get('first_name'),
                      last_name =         form.cleaned_data.get('last_name'),
                      city_region =       form.cleaned_data.get('city_region'),
                      delivery_address =  form.cleaned_data.get('delivery_address'),
                      phone =             form.cleaned_data.get('phone'),
                      comments =          form.cleaned_data.get('comments'))
                print('form valid---------------')
                
                address.save()
                order.address = address
                order.ordered = True
                order.save()
                messages.info(self.request, "Спасибо за заказ!")
                txt = ' user: {}\n first_name: {}\n last_name: {}\n city_region: {}\n delivery_address: {}\n\
                phone: {}\n Order: {}\n Ttl/price: {}\n comments: {}\n'.format(address.user, \
                address.first_name, address.last_name, \
                address.city_region, address.delivery_address, address.phone, \
                '\n'.join(order.ordered_items()), order.get_total() ,address.comments)
                # send massage to manager, to confirm the order  
                try:
                    send_email_notification(txt)
                except:
                    print('some problem with send_email_notification')
                send_telegram_notification(txt)   
                return redirect("/")
            messages.warning(self.request, "Заполните недостающие поля.") 
            return redirect('page_1:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "Добавьте товар в корзину.")
            return redirect('page_1:order_summary')          
            
  

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            all_category = [cat for cat in Category.objects.all()]
            context = {'order':order, 'category': all_category}
            
            return render(self.request, 'order_summary.html', context)
        
        except ObjectDoesNotExist:
            messages.warning(self.request, "Добавьте товар в корзину.")
            return redirect("/")
        
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)         # берем продукт по slug
    order_item, created = OrderItem.objects.get_or_create(product_item=item,
        user=request.user,
        ordered=False)              # создаем обьект заказа с продуктом item
    order_qs = Order.objects.filter(user = request.user, ordered=False)  # создаем очередь обьектов заказа
#    с фильтром по идентификатору user и флажком незаконченый заказ(ordered=False)
    if order_qs.exists():
        order = order_qs[0]                                  # берем первый заказ из списка заказов
        if order.items.filter(product_item__slug=item.slug).exists():  # если товар уже есть в заказе
            order_item.quantity += 1                # прибавить одну единицу            
            order_item.save()
            messages.info(request, "Корзина изменена.")
            return redirect("page_1:order_summary") 
        else:
            order.items.add(order_item)
            messages.info(request, "Товар добавлен.")
            return redirect("page_1:order_summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Товар добавлен.")

    return redirect("page_1:order_summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user = request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]                                  
        if order.items.filter(product_item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(product_item=item,
                                            user=request.user,
                                            ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "Корзина изменена.")
            return redirect("page_1:order_summary") 
        else:
            messages.info(request, "Этого товара нет в корзине")
            return redirect("page_1:product_view", slug=slug)            
    else:
        messages.info(request, "Добавьте товар в корзину.")
    return redirect("page_1:product_view", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user = request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product_item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                product_item=item,
                user=request.user,
                ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "Корзина изменена.")
            return redirect("page_1:order_summary")
        else:
            messages.info(request, "Этого товара нет в корзине")
            return redirect("page_1:product_view", slug=slug)
    else:
        messages.info(request, "Добавьте товар в корзину.")
        return redirect("page_1:product_view", slug=slug)


def logout_view(request):
    logout(request)
    return redirect("/")
    
    
    
    
    
    
    
    
    
    
