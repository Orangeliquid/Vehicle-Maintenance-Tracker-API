# Vehicle Maintenance Tracker API

Vehicle Maintenance Tracker API is a RESTful API that offers SQLAlchemy database persistence and Pydantic models for request validation and response serialization. It allows users to register and manage their accounts, add vehicles to their profile, log maintenance records for each vehicle, and set up service reminders based on mileage or time intervals. In addition, users can view helpful statistics such as the total cost of all maintenance and identify their most frequently maintained vehicle. The project emphasizes clean design, modular routing, and strong typing for reliability and scalability.


## Table of Contents

- [Installation](#installation)
- [Usage](#Usage-API-Overview)
- [API-Endpoints](#API-Endpoints)
  - [Users](#Users)
  - [Vehicles](#Vehicles)
  - [Maintenance](#Maintenance)
  - [Reminders](#Reminders)
  - [Statistics](#Statistics)
- [License](#license)

## Installation

To run Vehicle Maintenance Tracker API locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Orangeliquid/Vehicle-Maintenance-Tracker-API.git
   cd Vehicle-Maintenance-Tracker-API
   ```
   
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file in Crypto_Wallet_API
   ```bash
   echo -e "SECRET_KEY=your_secret_key_here\nALGORITHM=HS256\nACCESS_TOKEN_EXPIRE_MINUTES=30" > .env
   ```
   These variables are used for authentication and token generation:

   - SECRET_KEY: A secret string used to sign and verify JWT tokens. Change this to a secure, random value. Example: SECRET_KEY=aGsdg12A1sd32f2SD1vS0dseghhas2

   - ALGORITHM: The hashing algorithm used for encoding the JWT (default is HS256).
     Example: ALGORITHM=HS256

   - ACCESS_TOKEN_EXPIRE_MINUTES: Defines how long an access token remains valid (default is 30 minutes).
     Example: ACCESS_TOKEN_EXPIRE_MINUTES=30

   Adjust these values as needed for your security and expiration preferences.


## Usage API Overview

1. **Ensure all packages from `requirements.txt` are installed**  
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure .env is created and variables are set

3. Start the application:
   ```bash
   python main.py
   ```
   
4. Navigate to the interactive documentation
   - http://127.0.0.1:8000/docs

5. Register User
   - POST /users/

6. Login User
   - POST /sessions/

7. Register New Vehicle
   - POST /vehicles/

8. Create Maintenance Record
   - POST /maintenance_records/

9. Create Maintenance Reminder
   - POST /reminders/

 10. Get User Maintenance Statistics
     - GET /statistics/

11. **Additional endpoints for Users, Vehicles, Maintenance, and Reminders:**
    
   ### User Endpoints
   - POST /token/ - Login User OAUTH
   - PUT /users/{user_id} - Modify User Information
   - GET /users/ - Fetch All Users
   - GET /users/{username}/ - Fetch User By Username
   - GET /users/{user_id}/ - Fetch User by User Id
   - DELETE /users/{user_id} - Delete User

   ### Vehicle Endpoints
   - PUT /vehicles/{vehicle_id} - Update Vehicle
   - GET /vehicles/ - Fetch User Vehicles
   - GET /vehicles/filter/ - Fetch User Vehicles Filtered
   - DELETE /vehicles/{vehicle_id} - Delete Vehicle

   ### Maintenance Endpoints
   - PUT /maintenance_records/ - Update Maintenance Record
   - GET /maintenance_records/ - Fetch All Vehicle Maintenance Records
   - GET /maintenance_records/filtered/ Fetch All Vehicle Maintenance Records Filtered
   - DELETE /maintenance_records/ - Delete Maintenance Record

   ### Reminder Endpoints
   - PUT /reminder/ - Update Maintenance Reminder
   - GET /reminders/ - Fetch All Maintenance Reminders
   - GET /reminders/filtered/ Fetch All Maintenance Reminders Filtered
   - DELETE /reminder/ - Delete Maintenance Reminder

## API Endpoints

### Users

- **GET /users/**
- **Description**: Fetch all users in database.
- **Successful Response**:
  ```json
  [
    {
      "username": "string",
      "email": "string",
      "id": 0
    }
  ]
  ```
---

- **POST /users/**
- **Description**: Register a new user in the database.
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "username": "string",
    "email": "string",
    "id": 0
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **POST /token/**
- **Description**: Login user to access other routes via OAuth.
- **Request Body**:
  ```json
  {
    "grant_type": "string",
    "username": "string",
    "password": "string",
    "scope": "scope",
    "client_id": "string",
    "client_secret": "string"
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "access_token": "string",
    "token_type": "string"
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **POST /sessions/**
- **Description**: Login user to access other routes.
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "access_token": "string",
    "token_type": "string"
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **GET /users/{username}/**
- **Description**: Fetch user by username in database.
- **Parameters**:
  ```json
  {
    "username": "string",
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "username": "string",
    "email": "string",
    "id": 0
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **GET /users/{user_id}/**
- **Description**: Fetch user by User Id in database.
- **Parameters**:
  ```json
  {
    "user_id": "string",
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "username": "string",
    "email": "string",
    "id": 0
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **PUT /users/{user_id}/**
- **Description**: Modify user information in database.
- **Parameters**
  ```json
  {
    "user_id": "string",
  }
  ```
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "old_data": {
      "username": "string",
      "email": "string",
      "id": 0
    },
    "updated_data": {
      "username": "string",
      "email": "string",
      "id": 0
    },
    "changes": {
      "additionalProp1": {}
    },
    "update_message": "string"
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **DELETE /users/{user_id}/**
- **Description**: Delete user from database with User Id database.
- **Parameters**:
  ```json
  {
    "user_id": "string",
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "username": "string",
    "email": "string",
    "id": 0
  }
  ```
- **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

### Vehicles

- **GET /vehicles/ - Requires User Authentication**
- **Description**: Fetch all of the user's vehicles from database.
- **200 Successful Response**:
  ```json
  {
    "vehicles": [
      {
        "vehicle_type": "string",
        "make": "string",
        "model": "string",
        "color": "string",
        "year": 0,
        "mileage": 0,
        "vin": "string",
        "license_plate": "string",
        "registration_state": "string",
        "fuel_type": "string",
        "transmission_type": "string",
        "is_active": true,
        "nickname": "string",
        "id": 0,
        "created_at": "2025-05-08T09:20:16.501Z",
        "updated_at": "2025-05-08T09:20:16.501Z"
      }
    ]
  }
  ```
---

- **POST /vehicles/ - Requires User Authentication**
- **Description**: Register a new vehicle for current user in database.
- **Request Body**:
  ```json
  {
    "vehicle_type": "string",
    "make": "string",
    "model": "string",
    "color": "string",
    "year": 0,
    "mileage": 0,
    "vin": "string",
    "license_plate": "string",
    "registration_state": "string",
    "fuel_type": "string",
    "transmission_type": "string",
    "is_active": true,
    "nickname": "string"
  }
  ```
- **200 Successful Response**:
  ```json
  {
    "vehicle_type": "string",
    "make": "string",
    "model": "string",
    "color": "string",
    "year": 0,
    "mileage": 0,
    "vin": "string",
    "license_plate": "string",
    "registration_state": "string",
    "fuel_type": "string",
    "transmission_type": "string",
    "is_active": true,
    "nickname": "string",
    "id": 0,
    "created_at": "2025-05-08T09:22:20.191Z"
  }
  ```
  - **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

- **DELETE /vehicles/filtered/ - Requires User Authentication**
- **Description**: Fetch user vehicles with filter parameters.
- **Parameters**:
  ```json
  {
    "vehicle_type": "string",
    "make": "string",
    "model": "string",
    "color": "string",
    "year": 0,
    "mileage": 0,
    "vin": "string",
    "license_plate": "string",
    "registration_state": "string",
    "fuel_type": "string",
    "transmission_type": "string",
    "is_active": true,
    "nickname": "string"
  }
- **200 Successful Response**:
  ```json
  {
    "vehicles": [
      {
        "vehicle_type": "string",
        "make": "string",
        "model": "string",
        "color": "string",
        "year": 0,
        "mileage": 0,
        "vin": "string",
        "license_plate": "string",
        "registration_state": "string",
        "fuel_type": "string",
        "transmission_type": "string",
        "is_active": true,
        "nickname": "string",
        "id": 0,
        "created_at": "2025-05-08T09:28:15.427Z",
        "updated_at": "2025-05-08T09:28:15.427Z"
      }
    ]
  }
  ```
  - **422 Validation Error**:
  ```json
  {
    "detail": [
      {
        "loc": [
          "string",
          0
        ],
        "msg": "string",
        "type": "string"
      }
    ]
  }
  ```
---

  
