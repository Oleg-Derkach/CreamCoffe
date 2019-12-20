from django.contrib import admin
from .models import UserProfile, Item, Category, OrderItem, Order, ProductImage, Address

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Item._meta.fields]
    inlines = [ProductImageInline]
    

    class Meta:
        model = Item
admin.site.register(Item, ItemAdmin)


class ProductImageAdmin (admin.ModelAdmin):
    list_display = [field.name for field in ProductImage._meta.fields]

    class Meta:
        model = ProductImage

admin.site.register(ProductImage, ProductImageAdmin)

class CategoryAdmin (admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]

    class Meta:
        model = Category

admin.site.register(Category, CategoryAdmin)

class UserProfileAdmin (admin.ModelAdmin):
    list_display = [field.name for field in UserProfile._meta.fields]

    class Meta:
        model = UserProfile
admin.site.register(UserProfile, UserProfileAdmin)


class OrderItemAdmin (admin.ModelAdmin):
    list_display = [field.name for field in OrderItem._meta.fields]
    class Meta:
        model = OrderItem
admin.site.register(OrderItem, OrderItemAdmin)


class OrderAdmin (admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]   

    
#    def get_ordered_items(self):
#        return ",".join([str(p) for p in self.items.all()])

#    list_display = ('user', 'ref_code', 'ordered_items')  
             
    class Meta:
        model = Order

admin.site.register(Order, OrderAdmin)

class AddressAdmin (admin.ModelAdmin):
    list_display = [field.name for field in Address._meta.fields]   
    class Meta:
        model = Address

admin.site.register(Address, AddressAdmin)



#def make_refund_accepted(modeladmin, request, queryset):
#    queryset.update(refund_requested=False, refund_granted=True)
#
#
#make_refund_accepted.short_description = 'Update orders to refund granted'
#
#
#class OrderAdmin(admin.ModelAdmin):
#    list_display = ['user',
#                    'ordered',
#                    'being_delivered',
#                    'received',
#                    'refund_requested',
#                    'refund_granted',
##                    'shipping_address',
##                    'billing_address',
##                    'payment',
##                    'coupon'
#                    ]
#    list_display_links = [
#        'user',
##        'shipping_address',
##        'billing_address',
##        'payment',
##        'coupon'
#    ]
#    list_filter = ['ordered',
#                   'being_delivered',
#                   'received',
#                   'refund_requested',
#                   'refund_granted']
#    search_fields = [
#        'user__username',
#        'ref_code'
#    ]
#    actions = [make_refund_accepted]
#
#
#class AddressAdmin(admin.ModelAdmin):
#    list_display = [
#        'user',
#        'street_address',
#        'apartment_address',
#        'country',
#        'zip',
#        'address_type',
#        'default'
#    ]
#    list_filter = ['default', 'address_type', 'country']
#    search_fields = ['user', 'street_address', 'apartment_address', 'zip']
#
#
#admin.site.register(Item)
#admin.site.register(OrderItem)
#admin.site.register(Order, OrderAdmin)
##admin.site.register(Payment)
##admin.site.register(Coupon)
##admin.site.register(Refund)
##admin.site.register(Address, AddressAdmin)
#admin.site.register(UserProfile)
