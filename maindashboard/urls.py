from django.urls import path

from . import viewss
from .views.warehouse import delivery_party
from .views.warehouse import marking
from .views.warehouse import items
from .views.warehouse import verify
from .views.stuffing import containers

urlpatterns = [
    path('',
         viewss.home, name='home'),
    path('dashboard',
         viewss.dashboard, name='dashboard'),

    path('warehouse/delivery_party',
         delivery_party.delivery_party, name='delivery_party'),
    path('warehouse/delivery_party/new',
         delivery_party.delivery_party_new, name='delivery_party_new'),
    path('warehouse/delivery_party/edit/<int:party_id>',
         delivery_party.delivery_party_edit, name='delivery_party_edit'),

    path('warehouse/marking',
         marking.marking, name='marking'),
    path('warehouse/marking/new',
         marking.marking_new, name='marking_new'),
    path('warehouse/marking/edit/<int:marking_id>',
         marking.marking_edit, name='marking_edit'),


    path('warehouse/items',
         items.warehouse_items, name='warehouse_items'),
    path('warehouse/items/new',
         items.warehouse_items_new, name='warehouse_items_new'),
    path('warehouse/items/edit/<int:item_id>',
         items.warehouse_items_edit, name="warehouse_items_edit"),

    path('warehouse/verify',
         verify.verify, name='verify'),
    path('warehouse/verify/item/<int:item_id>',
         verify.verify_item, name="verify_item"),
    path('warehouse/verify/edit/<int:item_id>',
         verify.verify_edit, name="verify_edit"),

    path('stuffing/containers',
         containers.containers, name='containers'),
    path('stuffing/containers/view/<int:container_id>',
         containers.containers_view, name='containers_view'),
    path('stuffing/containers/edit/<int:container_id>/details',
         containers.container_edit_details, name='containers_edit_details'),
    path('stuffing/containers/edit/<int:container_id>/item/<int:item_id>',
         containers.container_edit_item, name='containers_edit_item'),

]
