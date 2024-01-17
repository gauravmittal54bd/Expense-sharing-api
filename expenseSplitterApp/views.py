
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.decorators import api_view

from .controllers import (
    create_user_controller,
    add_expense_controller,
    split_expense_controller,
    simplify_expenses_controller,
    update_user_controller,
    delete_user_controller,
    get_all_users_controller,
    get_user_by_id_controller,
    passbook_controller   
)



@csrf_exempt
@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        result, http_status = create_user_controller(user_data)
        return JsonResponse(result, status=http_status)

@csrf_exempt
@api_view(['GET'])
def get_all_users(request):
    return get_all_users_controller(request)  

@csrf_exempt
@api_view(['GET'])
def get_user_by_id(request,userid):
    return get_user_by_id_controller(request,userid)  


@csrf_exempt    
@api_view(['DELETE'])
def delete_user(request, userid):
    return delete_user_controller(request, userid)

@csrf_exempt
@api_view(['PUT'])
def update_user(request, userid):
    return update_user_controller(request, userid)
    
@csrf_exempt
@api_view(['POST'])
def add_expense(request):
    if request.method == 'POST':
        expense_data = JSONParser().parse(request)
        result, http_status = add_expense_controller(expense_data)
        return JsonResponse(result, status=http_status)

@csrf_exempt
@api_view(['PUT', 'GET'])
def split_expense(request, userid):
    if request.method == 'PUT' or request.method == 'GET':
        result, http_status = split_expense_controller(userid)
        if request.method == 'GET':
            result = {
                "owe": result.get("owe", [])
            }
        return JsonResponse(result, status=http_status)
    
@csrf_exempt
@api_view(['PATCH'])
def simplify_expenses(request):
    if request.method == 'PATCH':
        result, http_status = simplify_expenses_controller()
        return JsonResponse(result, status=http_status)
    

@api_view(['GET'])
def passbook(request, userid):
    result, http_status = passbook_controller(userid)
    return JsonResponse(result, status=http_status)
        
   