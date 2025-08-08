# Project Documentation

## Overview
This repository implements a multi-functional system for user authentication, contest management, and game management. Built with Flask and Firebase RTB, the system is designed for scalability and easy integration with frontends.

---

## Features

### **1. User Authentication**
- **Secure Registration and Login:**
  - Password hashing using bcrypt.
  - JWT-based session management.
- **Password Management:**
  - Password reset requests and secure updates.
- **Admin Controls:**
  - Admin endpoint to retrieve user lists.

### **2. Contest Management**
- **Create Contests:**
  - API to create contests with datetime validation.
  - Firebase integration for storing contest data.
- **Join Contests:**
  - Enables users to join contests.
- **List Active Contests:**
  - Fetches all currently active contests.

### **3. Game Management**
- **Game CRUD Operations:**
  - Create, read, update, and delete games.
- **Game Search:**
  - Query games by category or other attributes.
- **Favorites and Ratings:**
  - Users can rate and mark games as favorites.

---

## Setup and Installation

### Prerequisites
- **Python 3.8+**
- **Flask**

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python setup_db.py
   ```
5. Run the application:
   ```bash
   flask run
   ```

---

## API Endpoints

### **User Authentication**
| Endpoint               | Method | Description                |
|------------------------|--------|----------------------------|
| `/register`            | POST   | Register a new user.       |
| `/login`               | POST   | Login and obtain a JWT.    |
| `/reset-password`      | POST   | Initiate a password reset. |
| `/reset-password/confirm` | POST | Confirm and update password. |
| `/admin/users`         | GET    | List all users (admin only). |

### **Contest Management**
| Endpoint           | Method | Description             |
|--------------------|--------|-------------------------|
| `/create_contest`  | POST   | Create a new contest with fields like `game`, `prize_pool`, `start_time`, and `end_time`. Validates input and stores data in Firebase. |
| `/join_contest`    | POST   | Join an existing contest. |
| `/active_contests` | GET    | List active contests.   |

### **Game Management**
| Endpoint               | Method | Description              |
|------------------------|--------|--------------------------|
| `/games`               | GET    | List all games.          |
| `/games/search`        | GET    | Search games by category.|
| `/games/<game_id>/rate`| POST   | Rate a specific game.    |
| `/games/<game_id>/favorite` | POST | Mark game as favorite.  |
| `/games/favorites`     | GET    | List favorite games.     |

---

## Database Models

### **1. User Model**
| Field      | Type    | Description             |
|------------|---------|-------------------------|
| `id`       | Integer | Unique user ID.         |
| `username` | String  | User's username.        |
| `password` | String  | Hashed password.        |
| `email`    | String  | User's email address.   |

### **2. Game Model**
| Field     | Type    | Description            |
|-----------|---------|------------------------|
| `id`      | Integer | Unique game ID.        |
| `title`   | String  | Game title.            |
| `category`| String  | Game category.         |
| `rating`  | Float   | User rating.           |

### **3. Contest Model**
| Field       | Type    | Description            |
|-------------|---------|------------------------|
| `id`        | Integer | Unique contest ID.     |
| `name`      | String  | Contest name.          |
| `start_time`| DateTime| Contest start time.    |
| `end_time`  | DateTime| Contest end time.      |

---

## Firebase Integration
The `contest.py` file integrates with Firebase Realtime Database to manage contests. Firebase nodes:
- **`contests`**: Stores contest details.
- **`user_contest_mapping`**: Maps users to contests they have joined.

---

## Testing

### Manual Testing
- Use tools like **Postman** or **cURL** to test API endpoints.
- Example cURL command:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"game": "chess", "prize_pool": 1000, "start_time": "2025-01-01 10:00:00", "end_time": "2025-01-01 12:00:00"}' http://localhost:5000/create_contest
  ```

### Automated Testing
- Use Python's `unittest` module for automated tests:
  ```python
  import unittest
  from app import app

  class TestAPI(unittest.TestCase):
      def setUp(self):
          self.client = app.test_client()

      def test_register(self):
          response = self.client.post('/register', json={"username": "test_user", "password": "password123"})
          self.assertEqual(response.status_code, 200)

  if __name__ == "__main__":
      unittest.main()
  ```

---

## Contributors
- **Raghav Arora**
- **Megh Sankhla**

---

## License
This project is licensed under the [MIT License](LICENSE).

