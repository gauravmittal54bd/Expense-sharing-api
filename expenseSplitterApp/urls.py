from django.urls import path
from .views import (
    create_user, 
    get_all_users, 
    delete_user, 
    update_user, 
    add_expense, 
    split_expense, 
    simplify_expenses, 
    get_user_by_id,
    passbook
)

urlpatterns = [
    path('users/', create_user, name='create_user'),
    path('users/all/', get_all_users, name='get_all_users'),
    path('delete_user/<str:userid>/', delete_user, name='delete_user'),
    path('update_user/<str:userid>/', update_user, name='update_user'),
    path('expenses/', add_expense, name='add_expense'),
    path('expenses/<str:userid>/split/', split_expense, name='split_expense'),
    path('expenses/<str:userid>/balances/', split_expense, name='split_expense'),
    path('expenses/simplify/', simplify_expenses, name='simplify_expenses'),
    path('users/<str:userid>/', get_user_by_id, name='get_user_by_id'),
    path('passbook/<str:userid>/', passbook, name='passbook')
]
