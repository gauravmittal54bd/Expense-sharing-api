from ast import literal_eval
import json
from uuid import UUID
from expenseSplitterApp.models import User, Expense
from decimal import Decimal,ROUND_HALF_UP


def calculate_expense_share(type, amount, length, expense_share_list):
    if type == "EQUAL":
        share_value = Decimal(amount) / length
        share_value = share_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return [share_value for _ in range(length)]
    elif type == "PERCENTAGE":
        return [str((Decimal(amount) * Decimal(share) * Decimal('0.01')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) for share in expense_share_list]
    elif type == "EXACT":
        return [str(item) for item in expense_share_list]
    else:
        return []
    
def convert_participants(participants_str):
            participants_list = json.loads((participants_str.replace("'", "\"")).replace('-', ''))
            return [UUID(participant_id) for participant_id in participants_list]

def adjacency_list_to_matrix(adj_list):
    max_node_id = len(adj_list)
    matrix_size = max_node_id  # To account for 0-based indexing

    # Initialize the matrix with zeros
    adj_matrix = [[0] * matrix_size for _ in range(matrix_size)]

    # Populate the matrix using the adjacency list
    for i, sublist in enumerate(adj_list):
        for pair in sublist:
            node, owe = pair
            adj_matrix[i][node] = float(owe)

    return adj_matrix

def save_simplified_result(debitor_user_id, min_amount, creditor_user_id,list):
    debitor_list = []
    
    debitor = User.objects.get(userid=debitor_user_id)
    if debitor_user_id in list:
        debitor_list = literal_eval(debitor.to) if debitor.to else []
        debitor_list.append(debitor_user_id)
        debitor.to = str(debitor_list)
    else:
        debitor.to = str([])  
        debitor_list.append(creditor_user_id)
        debitor.to = str(debitor_list) 
         
    debitor.owe = str(min_amount)
    debitor.save()

def validate_expense_data(expense_data,participants_data,payer_id):
    type = expense_data.get('type', '')
    share_data = expense_data.get('share', [])

    try:
        payer = User.objects.get(userid=payer_id)
    except User.DoesNotExist:
        return {'success': False, 'error': 'Invalid payer_Id'}

    if Expense.objects.filter(payer_id=payer_id):
        return {'success': False, 'error': 'Expense entry for this payer_id already exists.'}

    if type not in ['EQUAL', 'PERCENTAGE', 'EXACT']:
        return {'success': False, 'error': f'Invalid type advised in request.'}

    if type in ['EXACT', 'PERCENTAGE'] and (not share_data or share_data == '[]'):
        return {'success': False, 'error': f'Share is required when expense type is {type}.'}

    if type in ['PERCENTAGE', 'EXACT']:
        try:
            share_list = json.loads(share_data)
            if len(participants_data) != len(share_list):
                return {'success': False, 'error': 'Participants and share lists should have the same length.'}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON format for share data.'}

    return {'success': True}

def calculate_min_cash_flow(graph, payer_and_participant_ids_list, dependecy_details):
    N = len(payer_and_participant_ids_list)

    def get_min(arr):
        min_ind = 0
        for i in range(1, N):
            if arr[i] < arr[min_ind]:
                min_ind = i
        return min_ind

    def get_max(arr):
        max_ind = 0
        for i in range(1, N):
            if arr[i] > arr[max_ind]:
                max_ind = i
        return max_ind

    def min_of_2(x, y):
        return x if x < y else y

    def min_cash_flow_rec(amount, user_list, dependency_details):
        mx_credit = get_max(amount)
        mx_debit = get_min(amount)
        if amount[mx_credit] == 0 and amount[mx_debit] == 0:
            return 0
        min_val = min_of_2(-amount[mx_debit], amount[mx_credit])
        amount[mx_credit] -= min_val
        amount[mx_debit] += min_val
        if int(min_val) <= 0:
            return
        min_val = round(min_val, 2)
        print("Person ", mx_debit, " pays ", min_val
              , " to ", "Person ", mx_credit)
        mx_debit_user_id = payer_and_participant_ids_list[mx_debit]
        mx_credit_user_id = payer_and_participant_ids_list[mx_credit]
        save_simplified_result(mx_debit_user_id, min_val, mx_credit_user_id,user_list)
        
        dependency_details.append({
            'text': f"User \"{mx_debit_user_id}\" owes {min_val} to \"{mx_credit_user_id}\"",
            'payer_id': mx_debit_user_id,
            'amount': min_val,
            'payee_id': mx_credit_user_id
        })
        user_list.append(mx_debit_user_id)
        min_cash_flow_rec(amount, user_list, dependency_details)

    def min_cash_flow(graph, dependency_details):
        amount = [0 for i in range(N)]
        for p in range(N):
            for i in range(N):
                amount[p] += (graph[i][p] - graph[p][i])
        user_list = []
        min_cash_flow_rec(amount, user_list, dependency_details)

    min_cash_flow(graph, dependecy_details)




    

