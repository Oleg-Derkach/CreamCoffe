from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from .models import Item, OrderItem, Order, ProductImage, Category, Address
from .forms import CheckoutForm
from .filters import ItemFilters
from .telegram_bot import send_telegram_notification, send_email_notification


def is_valid_queryparam(param):
    return param != '' and param is not None

def cookies_demo(request):

    all_category = [cat for cat in Category.objects.all()]
    all_cat_id = [str(cat.id) for cat in Category.objects.all()]
    
    '''
    {'get':   {'color_set': '#000000', '66': 'Зеленый элитный  чай', '67': 'Кофе'}, 
    'cookies': {'filt': 'title', 'page': '1', '68': 'off', '66': 'on', '67': 'on'}}
    '''
    get_categories = {str(k):v for k, v in request.GET.items() if k in all_cat_id}
    cookies_categories = {str(k):v for k, v in request.COOKIES.items() if k in all_cat_id}
    cat_status = {} 
    cat_on = []
    get_flag = False
    
    for item in all_cat_id:
        if str(item) in get_categories:
            get_flag = True

    if not get_flag:
        for item in all_cat_id:
            if str(item) in cookies_categories:
                cat_status[item] = cookies_categories[item]
            else:
                cookies_categories[item] = 'off'
                cat_status[str(item)] = 'off'
    else:
        for item in all_cat_id:
            if item in get_categories:
                cat_status[item] = 'on'
                cookies_categories[item] = 'on'   
            else:
                cat_status[item] = 'off'
                cookies_categories[item] = 'off'
    
    for item in cat_status:
        if cat_status[item] == 'on':
            cat_on.append(int(item))           
         
    product_card = ProductImage.objects.filter(is_main = True).order_by("product__title")
    queryset = ItemFilters(request.GET, queryset=product_card)
    response = render(request, 'cookies.html', {'category': all_category,
                                                'cat_on':cat_on,
                                                'query_products':queryset,})
    for item in cat_status:
        response.set_cookie(str(item), cat_status[item])
 
    return response 

def filter(request, cat_status):

    product_card = ProductImage.objects.filter(is_main = True)
    counter = 0
    
    for cat_id in cat_status:
        if cat_status[cat_id] == 'off':
            product_card = product_card.exclude(product__category__id=int(cat_id))
            counter += 1
    if counter == len(cat_status):
        return ProductImage.objects.filter(is_main = True)
    return product_card
            

def home_view(request):
    
    all_category = [cat for cat in Category.objects.all()]
    main_filter = {'check_box':{}, 'search_filt':'', 'cat_on':[]}
    off_status_of_check_box = 0
    
    if request.method == 'GET':
        for cat in all_category:
            if request.COOKIES.get(str(cat.id)) == 'on':
                main_filter['check_box'][str(cat.id)] = 'on'
                main_filter['cat_on'].append(int(cat.id))
            else:
                main_filter['check_box'][str(cat.id)] = 'off'
                
    elif request.method == 'POST':
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

                   
    if off_status_of_check_box ==  len(all_category):
        product_card = ProductImage.objects.filter(is_main = True)
    else:
        product_card = filter(request, main_filter['check_box']) 

    product_card = product_card.order_by("product__" + main_filter['search_filt'])
    search_bar = ItemFilters(request.GET, queryset=product_card)
    
    

    if request.user.is_authenticated:
        try:
            order = Order.objects.get(user=request.user, ordered=False)
        except ObjectDoesNotExist:
            order = Order.objects.create(user=request.user, ordered=False, ordered_date=timezone.now())
    else:
        order = None
         
    paginator = Paginator(search_bar.qs, 20)
    page = request.GET.get('page', request.COOKIES.get('page'))

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
        'search_bar':search_bar
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
                      first_last_name =   form.cleaned_data.get('first_last_name'),
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
                txt = ' user: {}\n first_last_name: {}\n city_region: {}\n delivery_address: {}\n\
                phone: {}\n Order: {}\n Ttl/price: {}\n comments: {}\n'.format(address.user, address.first_last_name, \
                address.city_region, address.delivery_address, address.phone, \
                order.ordered_items(), order.get_total() ,address.comments)
                # send massage to manager, to confirm the order  
                try:
                    send_email_notification(txt)
                except:
                    print('some problem with send_email_notification')
                send_telegram_notification(txt)   
                return redirect("/")
            messages.warning(self.request, "Failed checkout") 
            return redirect('page_1:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect('page_1:order_summary')          
            
  

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = { 'object': order }
            
            return render(self.request, 'order_summary.html', context)
        
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")
        
'''
from django.views.generic import ListView, DetailView, View
c помощью импортированых классов ListView, DetailView, View можно сконструировать
вьюшки
  
#сортировки Query Set   

----------------------------------------------------------------
запись в одну строчку сортировки
#list_product = sorted(list_product, key=lambda product: product.status_available == 'not_available')
-------------------------------------------------------
   Кастомный фильтр QuerySet , может быть любым - просто добавить этот метод в класс
    и описать как нужно сортировать QuerySet
    def get_queryset(self):
        return ProductImage.objects.order_by('-product__price')
----------------------------------------------------------------------

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        return ProductImage.objects.filter(product__slug=self.kwargs['slug'])
        
    этот метод перезаписывает классический метод получения списка. Он нужен
    для того чтобы можно было фильтровать список по ключу переданному в патче
    URL. Так этот ключ заносится в self.kwargs (это соварь), к которому
    можно обратится по ключу и получить значение, например для фильтра
----------------------------------------------------------------------------
#    is_authenticated - если пользователь авторизирован)
#    is_anonymous - если пользователь анонимный)
----------------------------------------------------------------------------
'''
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
            messages.info(request, "This item quantity was updated.")
            return redirect("page_1:order_summary") 
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("page_1:order_summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")

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

            messages.info(request, "This item was removed from your cart.")
            return redirect("page_1:order_summary") 
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("page_1:product_view", slug=slug)            
    else:
        messages.info(request, "You do not have an active order")
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

            messages.info(request, "This item quantity was updated.")
            return redirect("page_1:order_summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("page_1:product_view", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("page_1:product_view", slug=slug)


def logout_view(request):
    logout(request)
    return redirect("/")
    
    
    
    
    
    
    
    
    
    
