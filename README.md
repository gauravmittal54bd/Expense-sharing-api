# Expense Splitter API

## 1. Overview

The Expense Sharing Application is designed to facilitate expense management and sharing among users. Users can add expenses, split them among different people, and keep track of balances.

## 2. Architecture Flow

#### API Flow:
Requests flow from views to controllers, where business logic is processed, then to serializers for data conversion, and finally to utility functions for additional processing.
#### Simplify Expenses Algorithm:
The simplify_expenses API uses the calculate_min_cash_flow algorithm to minimize transactions, updating user owe amounts without changing existing balances (User.owe).


## 3. API Endpoints

| HTTP Verb | Endpoint                               | Action                           |
| --------- | ---------------------------------------| -------------------------------- |
| POST      | /api/v1/users                          | Create a new user                |
| GET       | /api/v1/users/all                      | Get all users                    |
| DELETE    | /api/v1/users/<str:userid>             | Delete a user                    |
| PUT       | /api/v1/users/<str:userid>             | Update user information          |
| POST      | /api/v1/expenses                       | Add a new expense                |
| PUT       | /api/v1/expenses/<str:userid>/split    | Split an expense among users     |
| GET       | /api/v1/expenses/<str:userid>/balances | Get balances for a user          |
| PATCH     | /api/v1/expenses/simplify              | Simplify expenses                |
| GET       | /api/v1/users/<str:userid>             | Get user details by user ID      |
| GET       | /api/v1/passbook/<str:userid>          | View passbook for a user         |

## 4. Database Schema
### User Table
| Field         | Type         | Description                                           |
| ------------- | ------------ | ------------------------------------------------------|
| userid        | UUID         | Unique identifier for the user                        |
| name          | CharField    | User's name                                           |
| email         | EmailField   | User's email                                          |
| mobileNumber  | CharField    | User's mobile number                                  |
| balance       | CharField    | User's balance                                        |
| owe           | CharField    | User's owed amount                                    |
| to            | CharField    | User to whom the amount is owed                       |
| timestamp     | DateTime     | Timestamp of when the user record was created/updated |

### Expense Table
| Field             | Type         | Description                                              |
| ----------------- | ------------ | -------------------------------------------------------- |
| id                | UUID         | Unique identifier for the expense                        |
| payer_id          | CharField    | ID of the user who paid for the expense                  |
| amount            | DecimalField | Total amount of the expense                              |
| type              | CharField    | Type of expense (EQUAL, EXACT, PERCENT)                  |
| share             | TextField    | Share details (for EXACT and PERCENT types)              |
| participants_ids  | TextField    | IDs of participants in the expense                       |
| timestamp         | DateTime     | Timestamp of when the expense record was created/ipdated |



## 5. Views Structure

### CreateUserView
- **Endpoint:** `/api/v1/users`
- **Methods:**
  - `POST`: Create a new user
- **Controller:** `create_user_controller`

### GetAllUsersView
- **Endpoint:** `/api/v1/users/all`
- **Methods:**
  - `GET`: Get all users
- **Controller:** `get_all_users_controller`

### GetUserByIdView
- **Endpoint:** `/api/v1/users/{userid}`
- **Methods:**
  - `GET`: Get user details by ID
- **Controller:** `get_user_by_id_controller`

### DeleteUserView
- **Endpoint:** `/api/v1/delete_user/{userid}`
- **Methods:**
  - `DELETE`: Delete a user
- **Controller:** `delete_user_controller`

### UpdateUserView
- **Endpoint:** `/api/v1/update_user/{userid}`
- **Methods:**
  - `PUT`: Update user details
- **Controller:** `update_user_controller`

### AddExpenseView
- **Endpoint:** `/api/v1/expenses`
- **Methods:**
  - `POST`: Add a new expense
- **Controller:** `add_expense_controller`

### SplitExpenseView
- **Endpoint:** `/api/v1/expenses/{userid}/split`
- **Methods:**
  - `PUT`: Split expense among participants
  - `GET`: Get owe details for a user
- **Controller:** `split_expense_controller`

### SimplifyExpensesView
- **Endpoint:** `/api/v1/expenses/simplify`
- **Methods:**
  - `PATCH`: Simplify existing expenses
- **Controller:** `simplify_expenses_controller`

### PassbookView
- **Endpoint:** `/api/v1/passbook/{userid}`
- **Methods:**
  - `GET`: Get passbook details for a user
- **Controller:** `passbook_controller`

## 6. Postman Test Results
See [screenshots.md](https://github.com/gauravmittal54/Expense-splitter-API/blob/main/screenshots.md) for Postman test results.



