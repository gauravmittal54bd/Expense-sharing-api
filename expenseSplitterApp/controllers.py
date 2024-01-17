import decimal
from rest_framework import status
from django.http.response import JsonResponse
from django.utils import timezone
from rest_framework.parsers import JSONParser
from expenseSplitterApp.models import User
from expenseSplitterApp.serializers import UserSerializer
import uuid,json
from decimal import Decimal,ROUND_HALF_UP
import ast
from ast import literal_eval
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from expenseSplitterApp.models import User, Expense
from expenseSplitterApp.serializers import UserSerializer, ExpenseSerializer

from .utils import (
    calculate_expense_share,
    convert_participants,
    adjacency_list_to_matrix,
    validate_expense_data,
    calculate_min_cash_flow,
)

def create_user_controller(user_data):
    existing_user = User.objects.filter(email=user_data.get('email')).first()
    if existing_user:
        return {'status': False, 'error': 'User with this email already exists.'}, status.HTTP_400_BAD_REQUEST

    user_data['userid'] = str(uuid.uuid4())
    user_data.setdefault('balance', 0.0)
    user_data.setdefault('owe', 0.0)

    user_serializer = UserSerializer(data=user_data)

    if user_serializer.is_valid():
        user_serializer.save()
        return {'status': True, 'data': user_serializer.data}, status.HTTP_201_CREATED
    return {'status': False, 'errors': user_serializer.errors}, status.HTTP_400_BAD_REQUEST



def add_expense_controller(expense_data):
    payer_id = expense_data.get('payer_id')
    participants_data = expense_data.get('participant_ids', [])

    for participant_id in participants_data:
        if not User.objects.filter(userid=participant_id):
            return {'success': False, 'error': f'Invalid  participant userid : "{participant_id}"advised.'}, status.HTTP_400_BAD_REQUEST

    # Validate expense data
    validation_result = validate_expense_data(expense_data, participants_data, payer_id)
    if not validation_result['success']:
        return validation_result, status.HTTP_400_BAD_REQUEST

    # Serialize the expense data
    expense_serializer = ExpenseSerializer(data=expense_data)
    if expense_serializer.is_valid():
        expense_instance = expense_serializer.save()
        expense_instance.participants_ids = json.dumps(participants_data)
        expense_instance.save()
        return expense_serializer.data, status.HTTP_201_CREATED
    return expense_serializer.errors, status.HTTP_400_BAD_REQUEST

def split_expense_controller(userid):
    user = get_object_or_404(User, userid=userid)
    user_id_db_format = str(user.userid).replace('-', '')
    expenses = Expense.objects.filter(payer_id=user_id_db_format)

    if not expenses:
        return {'success': False, 'message': 'No expenses created for this user.'},  status.HTTP_400_BAD_REQUEST

    expense_share_list = []
    balances = [] 
    creditors = []
    total_amount = 0

    creditors.append(str(user_id_db_format))
    expense_serializer = ExpenseSerializer(expenses, many=True)

    for expense in expense_serializer.data:
        expense_share_list = ast.literal_eval(expense['share'])

    participants_ids_list = [
        convert_participants(expense['participants_ids']) for expense in expense_serializer.data
    ]
    types_list = [expense['type'] for expense in expense_serializer.data]
    amounts_list = [expense['amount'] for expense in expense_serializer.data]

    # Update the format of the "expenses" array
    formatted_expenses = [{"userid": str(participant_id).replace('-', '')} for participants_ids in participants_ids_list for participant_id in participants_ids]

    for expense, participants_ids in zip(expense_serializer.data, participants_ids_list):
        expense_type = expense['type']
        amount = expense['amount']
        expense_share = calculate_expense_share(expense_type, amount, len(participants_ids), expense_share_list)
        
        for participant_id, share_value in zip(participants_ids, expense_share):
            try:
                participant_id = str(participant_id).replace('-', '')
                participant = User.objects.get(userid=participant_id)

                if participant.to:
                    existing_creditors = eval(participant.to)
                    existing_creditors.extend(creditors)
                    existing_creditors = list(set(existing_creditors))
                    participant.to = str(existing_creditors)
                else:
                    participant.to = str(creditors)

                result = Decimal(participant.owe) + Decimal(share_value)
                participant.owe = result
                total_amount += result
                participant.save()

                userobj = User.objects.get(userid=participant_id)
                userobj.balance = Decimal(userobj.balance) + Decimal(share_value)
                userobj.save()

                balances.append({participant_id: result})
            except User.DoesNotExist:
                pass

    userobj = User.objects.get(userid=user_id_db_format)
    userobj.balance = Decimal(userobj.balance) - total_amount
    userobj.save()

    return {
        'success': True,
        'message': f'Successfully split amount between {len(expense_share)} participants',
        'type': types_list[0],
        'amount': amounts_list[0],
        'participants': formatted_expenses,
        'owe': balances
    }, status.HTTP_200_OK


def simplify_expenses_controller():
    # Fetch all users and expenses
    expenses = Expense.objects.all()
    expense_serializer = ExpenseSerializer(expenses, many=True)

    payer_and_participant_ids_set = set()

    for expense_data in expense_serializer.data:
        participants_ids = eval(expense_data['participants_ids'])
        payer_and_participant_ids_set.add(expense_data['payer_id'])
        payer_and_participant_ids_set.update(participants_ids)

    payer_and_participant_ids_list = list(payer_and_participant_ids_set)  # Convert the set to a list
    dependencies_list = [[] for _ in payer_and_participant_ids_list]    # Create a list of lists to represent dependencies

    for expense_data in expense_serializer.data:   # Iterate over expenses again to populate dependencies_list
        payer_id = expense_data['payer_id']
        participants_ids = eval(expense_data['participants_ids'])
        for participant_id in participants_ids:
            index = payer_and_participant_ids_list.index(participant_id)
            try:
                participant = User.objects.get(userid=participant_id)
                owe_value = (participant.owe)
                print(owe_value)
                to_list = literal_eval(participant.to) if participant.to else []

                if expense_data['type'] == 'EQUAL':
                    to_list_length = len(to_list)
                    if to_list_length > 0:
                        valid_elements = [element for element in to_list if element in payer_and_participant_ids_list]
                        if valid_elements:
                            owe_value = str(decimal.Decimal(owe_value) / to_list_length)
                else:
                    owe_value = 0

            except User.DoesNotExist:
                owe_value = 0  # Default to 0 if the user is not found
            owe_value = float(owe_value)
            # Append the pair (payer_id, owe) to the list
            dependencies_list[index].append((payer_and_participant_ids_list.index(payer_id), owe_value))

    graph = adjacency_list_to_matrix(dependencies_list)
    dependecy_details = []
    calculate_min_cash_flow(graph, payer_and_participant_ids_list, dependecy_details)

    return {
        'success': True,
        'message': 'Expenses simplified successfully.',
        'details': dependecy_details,
        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }, status.HTTP_200_OK


def update_user_controller(request, userid):
    # Find the user by userid or return 404 if not found
    user = get_object_or_404(User, userid=userid)
    if request.method == 'PUT':
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(user, data=user_data)

        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def delete_user_controller(request, userid):
    user = get_object_or_404(User, userid=userid)

    if request.method == 'DELETE':
        user.delete()
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        response_data = {'message': 'User deleted successfully.', 'timestamp': timestamp}
        return JsonResponse(response_data, status=204)
    
def get_all_users_controller(request):
    if request.method == 'GET':
        users = User.objects.all()
        if not users:
            return Response({'status': False, 'message': 'No users found in the database. Consider creating users.'}, status=status.HTTP_404_NOT_FOUND)
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data)
    
def get_user_by_id_controller(request, userid):
    try:
        # Find the user by userid or return 404 if not found
        user = get_object_or_404(User, userid=userid)

        # Serialize the user data
        user_serializer = UserSerializer(user)

        return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


def passbook_controller(userid):
    try:
        user = User.objects.get(userid=userid)
    except User.DoesNotExist:
        return {'error': 'User not found.'}, status.HTTP_404_NOT_FOUND

    user_serializer = UserSerializer(user)
    user_data = user_serializer.data

    # Fetch expenses related to the user
    expenses = Expense.objects.filter(participants_ids__contains=userid)
    expense_serializer = ExpenseSerializer(expenses, many=True)
    expenses_data = expense_serializer.data

    print(expenses_data,user.userid,userid,"uuu")

    # Combine user data and expenses data to form passbook
    passbook_data = {
        'user': user_data,
        'transactions': expenses_data,
        'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return passbook_data, status.HTTP_200_OK