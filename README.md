# DamnPlay Gaming Platform API

![DamnPlay](https://img.shields.io/badge/DamnPlay-Gaming%20Platform-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-2.2.5-red)
![Firebase](https://img.shields.io/badge/Firebase-Realtime%20Database-orange)

## Overview
DamnPlay is a comprehensive gaming platform API built with Flask and Firebase Realtime Database. It provides a complete backend solution for managing users, games, contests, leaderboards, and digital wallets in a gaming ecosystem. The platform is designed with scalability, security, and modern API practices in mind.

## 🚀 Features

### 🔐 **User Management**
- **Secure Authentication:** JWT-based authentication with bcrypt password hashing
- **User Registration & Login:** Complete user lifecycle management with rate limiting
- **Profile Management:** Update user profiles with validation
- **Admin Controls:** Admin-only endpoints for user management
- **Role-Based Access Control:** Support for admin and regular user roles

### 🎮 **Game Management**
- **Game Catalog:** Comprehensive game metadata management
- **Advanced Filtering:** Filter games by category, popularity, rating
- **Pagination Support:** Efficient data retrieval with pagination
- **Game Creation:** Add new games with complete metadata
- **Search Functionality:** Query games by various attributes

### 🏆 **Contest Management**
- **Contest Creation:** Create contests with entry fees and prize pools
- **Join Contests:** User participation with automatic wallet deduction
- **Active Contests:** Real-time listing of ongoing contests
- **Contest Validation:** Prevent overlapping contests for the same game
- **Contest Cancellation:** Admin controls for contest management

### 📊 **Leaderboard System**
- **Real-time Leaderboards:** Live contest rankings
- **Score Updates:** Dynamic score tracking during contests
- **Historical Data:** Archive completed contest results
- **Contest Completion:** Automated leaderboard archiving

### 💰 **Wallet System**
- **Digital Wallet:** Secure fund management for users
- **Add/Deduct Funds:** Complete transaction handling
- **Transaction History:** Detailed transaction logs with date filtering
- **Balance Inquiry:** Real-time wallet balance retrieval
- **Contest Integration:** Automatic entry fee processing

### 🛡️ **Security & Reliability**
- **Rate Limiting:** API protection against abuse
- **CORS Support:** Cross-origin resource sharing enabled
- **Comprehensive Logging:** Detailed application logs
- **Error Handling:** Global exception handling with proper responses
- **Input Validation:** Robust data validation across all endpoints

---

## 🏗️ Project Structure

```
DamnPlay/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── swagger.yaml          # API documentation
├── logging_utils.py      # Logging configuration
├── middleware.py         # Custom middleware
├── utils.py             # Utility functions
├── firebase.json        # Firebase configuration
├── database.rules.json  # Firebase security rules
│
├── contest/             # Contest management module
│   ├── controllers.py   # Contest business logic
│   ├── models.py       # Contest data models
│   ├── routes.py       # Contest API endpoints
│   └── services.py     # Contest services
│
├── game/               # Game management module
│   ├── controllers.py  # Game business logic
│   ├── models.py      # Game data models
│   ├── routes.py      # Game API endpoints
│   └── services.py    # Game services
│
├── leaderboard/        # Leaderboard module
│   ├── controllers.py  # Leaderboard logic
│   ├── models.py      # Leaderboard models
│   ├── routes.py      # Leaderboard endpoints
│   └── services.py    # Leaderboard services
│
├── user/              # User management module
│   ├── controllers.py  # User business logic
│   ├── models.py      # User models & auth
│   ├── routes.py      # User API endpoints
│   ├── services.py    # User services
│   └── firebase_credentials.json # Firebase config
│
├── wallet/            # Wallet management module
│   ├── controller.py  # Wallet business logic
│   ├── models.py     # Wallet data models
│   ├── routes.py     # Wallet API endpoints
│   └── services.py   # Wallet services
│
└── tests/            # Test suite
    ├── test_auth.py      # Authentication tests
    ├── test_contest.py   # Contest tests
    ├── test_game.py      # Game tests
    ├── test_leaderboard.py # Leaderboard tests
    └── test_wallet.py    # Wallet tests
```

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.8+**
- **Firebase Account** with Realtime Database enabled
- **Firebase Admin SDK** credentials

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/damnplay.git
   cd damnplay
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Firebase:**
   - Place your Firebase credentials JSON file in `user/firebase_credentials.json`
   - Update the database URL in `user/models.py`

5. **Run the application:**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

### 📚 API Documentation
Access the Swagger UI documentation at: `http://localhost:5000/damnplay/api-docs`

---

## 🔌 API Endpoints

### Authentication Header
Most endpoints require authentication via the `access-token` header:
```
Headers:
  access-token: <your-jwt-token>
  Content-Type: application/json
```

### 👤 User Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/damnplay/user/register` | POST | Register new user | No |
| `/damnplay/user/login` | POST | User login (rate limited) | No |
| `/damnplay/user/logout` | POST | User logout | Yes |
| `/damnplay/user/profile/update` | PUT | Update user profile | Yes |
| `/damnplay/user/admin/users` | GET | List all users (admin only) | Yes |

### 🎮 Game Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/damnplay/game/games` | GET | List games with filters & pagination | No |
| `/damnplay/game/games` | POST | Create new game | No |

### 🏆 Contest Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/damnplay/contest/create` | POST | Create contest (admin only) | Yes |
| `/damnplay/contest/join` | POST | Join contest | Yes |
| `/damnplay/contest/active` | GET | List active contests | No |
| `/damnplay/contest/cancel` | POST | Cancel contest (admin only) | Yes |

### 📊 Leaderboard Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/damnplay/leaderboard/leaderboard/{contest_id}` | GET | Get contest leaderboard | No |
| `/damnplay/leaderboard/update_leaderboard` | POST | Update user score | No |
| `/damnplay/leaderboard/leaderboard/history/{contest_id}` | GET | Get historical leaderboard | No |
| `/damnplay/leaderboard/leaderboard/complete` | POST | Complete contest | No |

### 💰 Wallet Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/damnplay/wallet/add-funds` | POST | Add funds to wallet | Yes |
| `/damnplay/wallet/deduct-funds` | POST | Deduct funds from wallet | Yes |
| `/damnplay/wallet/balance` | GET | Get wallet balance | Yes |
| `/damnplay/wallet/transactions` | GET | Get transaction history | Yes |

### 🏥 Health Check
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/damnplay/health` | GET | API health status | No |

---

## 🗄️ Data Models

### User Model (Firebase)
```json
{
  "username": "string",
  "email": "string",
  "password": "string (hashed)",
  "role": "string (user/admin)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Game Model (Firebase)
```json
{
  "title": "string",
  "category": "string",
  "description": "string",
  "thumbnail": "string (URL)",
  "release_year": "integer",
  "popularity": "number",
  "average_rating": "number"
}
```

### Contest Model (Firebase)
```json
{
  "game_id": "string",
  "title": "string",
  "description": "string",
  "start_time": "string (ISO datetime)",
  "end_time": "string (ISO datetime)",
  "entry_fee": "number",
  "prize": "number",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Wallet Model (Firebase)
```json
{
  "balance": "number",
  "transactions": {
    "transaction_id": {
      "amount": "number",
      "type": "string (credit/debit)",
      "description": "string",
      "timestamp": "timestamp"
    }
  }
}
```

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest tests/ --cov=.
```

### Manual API Testing
Use the provided Swagger UI or tools like Postman/cURL:

```bash
# Register a user
curl -X POST http://localhost:5000/damnplay/user/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:5000/damnplay/user/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Get active contests
curl -X GET http://localhost:5000/damnplay/contest/active
```

---

## 🔧 Configuration

### Environment Variables
The application uses the following configuration:
- `SECRET_KEY`: 'Raghav' (should be environment variable in production)
- `DEBUG`: True (disable in production)
- Firebase Database URL: Set in `user/models.py`

### Firebase Setup
1. Create a Firebase project
2. Enable Realtime Database
3. Generate Admin SDK credentials
4. Place credentials in `user/firebase_credentials.json`
5. Configure database rules in `database.rules.json`

---

## 📝 Dependencies

- **Flask 2.2.5**: Web framework
- **firebase-admin 6.0.1**: Firebase integration
- **bcrypt 4.0.1**: Password hashing
- **PyJWT 2.7.0**: JWT token handling
- **flask-limiter**: Rate limiting
- **flask-swagger-ui**: API documentation
- **flask-cors**: Cross-origin support

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation as needed
- Use meaningful commit messages

---

## 👥 Team

- **Raghav Arora** - Lead Developer
- **Megh Sankhla** - Developer

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/damnplay/api-docs`
- Review the test files for usage examples

---

*Built with ❤️ for the gaming community*

