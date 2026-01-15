# CareConnect

A community-driven donation and request platform that connects donors with those in need, managed by community clubs across Singapore.

## 🌟 Overview

CareConnect is a full-stack web application that facilitates charitable donations and requests within local communities. The platform enables clients to donate items or request assistance, while community club managers oversee and coordinate these activities to ensure efficient resource allocation.

## Demo

https://youtu.be/QbCB52LaZBY?si=uuOlf7zNbOmczBUk

## Key Features

- **Multi-Authentication System**: Support for Google OAuth and traditional email/password authentication
- **Role-Based Access**: Separate interfaces for clients and community managers
- **Smart Matching**: Automated allocation system matching donations with requests
- **Real-Time Notifications**: Instant updates on donation status, request fulfillment, and community activities
- **Community Management**: Location-based community club oversight and coordination
- **Inventory Tracking**: Comprehensive item management with expiry date monitoring
- **Analytics Dashboard**: Fulfillment rate tracking and community performance metrics

## 🏗️ Architecture & Design

### Object-Oriented Design Principles

CareConnect demonstrates adherence to core OOP principles:

#### 1. **Encapsulation**
- **Data Hiding**: Private methods and attributes in authentication strategies
- **Interface Abstraction**: Clean public APIs hiding implementation complexity
- **Modular Design**: Each class has well-defined responsibilities and boundaries

#### 2. **Inheritance**
- **Base Classes**: Abstract `AuthenticationStrategy` and `DatabaseInterface` classes
- **Polymorphic Behavior**: Multiple concrete implementations sharing common interfaces
- **Code Reuse**: Shared functionality through inheritance hierarchies

#### 3. **Polymorphism**
- **Strategy Interchangeability**: Authentication strategies can be swapped at runtime
- **Database Abstraction**: PostgreSQL and SQLite implementations through common interface
- **Notification Delivery**: Multiple notification strategies with unified interface

#### 4. **Abstraction**
- **Abstract Base Classes**: Define contracts without implementation details
- **Interface Segregation**: Focused, single-purpose interfaces
- **Implementation Independence**: Clients depend on abstractions, not concrete classes

### Design Patterns Implementation

#### 1. **Strategy Pattern** - Authentication System
```python
# Abstract Strategy
class AuthenticationStrategy(ABC):
    @abstractmethod
    def authenticate(self, data): pass
    
    @abstractmethod
    def create_user(self, data): pass

# Concrete Strategies
class GoogleOAuthStrategy(AuthenticationStrategy):
    def authenticate(self, data):
        # Google OAuth implementation
        
class PasswordStrategy(AuthenticationStrategy):
    def authenticate(self, data):
        # Email/password implementation

# Context
class AuthenticationContext:
    def set_strategy(self, strategy: AuthenticationStrategy):
        self._strategy = strategy
```

#### 2. **Factory Pattern** - Database Abstraction
```python
class DatabaseFactory:
    @staticmethod
    def getDatabase(db_type: str):
        if db_type == "sqlite":
            return SQLiteDatabase()
        elif db_type == "postgres":
            return PostgresSQLDatabase()
        raise ValueError(f"Unsupported database type: {db_type}")
```

#### 3. **Observer Pattern** - Notification System
```python
class IObserver(ABC):
    @abstractmethod
    def update(self, cc: str) -> None: pass

class CCFulfilmentSubject(ISubject):
    def notify(self, cc: str) -> None:
        for obs in self._observers:
            if obs.is_interested_in(cc):
                obs.update(cc)
```

### Backend (Flask)
- **Layered Architecture**: Controllers → Services → Models → Database
- **Database Support**: PostgreSQL (production) and SQLite (development)
- **Authentication**: OAuth 2.0 (Google) and secure password-based authentication
- **Design Patterns**: Strategy, Factory, Observer patterns for maintainable code

### Frontend (React)
- **Modern React**: Functional components with hooks
- **Routing**: React Router for SPA navigation
- **HTTP Client**: Axios for API communication
- **Styling**: Custom CSS with responsive design
- **Build Tool**: Vite for fast development and optimized builds

## 📁 Project Structure

### Backend Architecture

```
backend/
├── controllers/          # Business logic layer
│   ├── auth_controller.py       # Authentication operations
│   ├── community_controller.py  # Community club operations
│   ├── donations_controller.py  # Donation management
│   ├── inventory_controller.py  # Inventory tracking and management
│   ├── jobs_controller.py       # Background job scheduling
│   ├── notification_controller.py # Notification management
│   ├── profile_controller.py    # User profile management
│   └── requests_controller.py   # Request handling
├── services/            # Domain logic layer
│   ├── auth_strategies.py       # Strategy pattern for authentication
│   ├── community_clubs.py       # Community club management
│   ├── find_user.py             # User lookup utilities
│   ├── image_upload.py          # Image upload handling
│   ├── jobs_service.py          # Background job scheduling
│   ├── metrics.py               # Analytics and metrics
│   ├── notification_service.py  # Notification management
│   ├── notification_strategies.py # Observer pattern for notifications
│   ├── password.py              # Secure password hashing
│   └── run_allocation.py        # Smart matching algorithm
├── database/            # Data access layer
│   ├── database_factory.py      # Factory pattern for DB selection
│   ├── database_interface.py    # Abstract database interface
│   ├── postgres_database.py     # PostgreSQL implementation
│   └── sqlite_database.py       # SQLite implementation
├── routes/              # API endpoint layer
│   ├── auth_routes.py           # Authentication endpoints
│   ├── community_routes.py      # Community club endpoints
│   ├── donations_routes.py      # Donation API routes
│   ├── inventory_routes.py      # Inventory management endpoints
│   ├── jobs_routes.py           # Background job endpoints
│   ├── notification_routes.py   # Notification endpoints
│   ├── profile_routes.py        # User profile endpoints
│   └── requests_routes.py       # Request API routes
├── models.py            # SQLAlchemy data models
├── config.py            # Application configuration
├── extensions.py        # Flask extensions setup
├── broadcast_observer.py # Observer pattern implementation
└── app.py              # Application factory
```

### Frontend Architecture

```
frontend/
├── src/
│   ├── assets/          # Static assets
│   │   └── logo.png            # Application logo
│   ├── Components/      # Reusable React components
│   │   ├── CommunityClubsMap.jsx # Interactive map component
│   │   ├── DonationCard.jsx     # Donation display card
│   │   └── TopNav.jsx           # Top navigation bar
│   ├── pages/           # Page-level components
│   │   ├── ClientUI/           # Client-specific pages
│   │   │   ├── ClientDashboard.jsx # Client analytics dashboard
│   │   │   ├── ClientHome.jsx      # Client main page
│   │   │   ├── DonationForm.jsx    # Create donation form
│   │   │   ├── DonationsList.jsx   # View donations list
│   │   │   ├── RegisterForm.jsx    # User registration form
│   │   │   ├── RequestForm.jsx     # Create request form
│   │   │   └── RequestsList.jsx    # View requests list
│   │   ├── MainUI/             # Shared UI components
│   │   │   ├── Login.jsx           # Authentication page
│   │   │   ├── Notifications.jsx   # Notifications center
│   │   │   ├── Profile.jsx         # User profile management
│   │   │   └── Subscriptions.jsx   # Community subscriptions
│   │   └── ManagerUI/          # Manager-specific pages
│   │       ├── CompleteRequest.jsx # Complete request workflow
│   │       ├── ManageDonations.jsx # Donation approval system
│   │       ├── ManagerAction.jsx   # Manager action center
│   │       ├── ManagerDashboard.jsx # Manager analytics dashboard
│   │       ├── ManageRegistrations.jsx # User registration approval
│   │       └── ManagerHome.jsx     # Manager main page
│   ├── styles/          # CSS styling
│   │   ├── ClientDashboard.css     # Client dashboard styles
│   │   ├── ClientHome.css          # Client home styles
│   │   ├── CommunityClubsMap.css   # Map component styles
│   │   ├── CompleteRequest.css     # Request completion styles
│   │   ├── DonationsList.css       # Donations list styles
│   │   ├── Login.css               # Login page styles
│   │   ├── ManageDonations.css     # Donation management styles
│   │   ├── ManagerAction.css       # Manager action styles
│   │   ├── ManagerDashboard.css    # Manager dashboard styles
│   │   ├── ManageRegistrations.css # Registration management styles
│   │   ├── ManagerHome.css         # Manager home styles
│   │   ├── Notifications.css       # Notifications styles
│   │   ├── Profile.css             # Profile page styles
│   │   ├── RegisterForm.css        # Registration form styles
│   │   ├── RequestsList.css        # Requests list styles
│   │   └── TopNav.css              # Navigation bar styles
│   ├── App.jsx          # Main application component
│   ├── httpClient.jsx   # Axios HTTP client configuration
│   └── main.jsx         # Application entry point
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite build configuration
└── index.html          # HTML template
```

### Key File Descriptions

#### **Backend Core Files**

- **`models.py`**: SQLAlchemy models defining database schema with proper relationships and constraints
- **`app.py`**: Flask application factory implementing dependency injection and configuration
- **`config.py`**: Environment-based configuration management with security best practices
- **`extensions.py`**: Centralized Flask extension initialization (SQLAlchemy, OAuth, CORS)

#### **Design Pattern Implementations**

- **`auth_strategies.py`**: Strategy pattern for authentication with Google OAuth and password strategies
- **`database_factory.py`**: Factory pattern enabling database-agnostic architecture
- **`broadcast_observer.py`**: Observer pattern for decoupled notification system
- **`notification_strategies.py`**: Strategy pattern for multiple notification delivery methods

#### **Business Logic Layer**

- **`controllers/`**: Clean separation of business logic from routing concerns
- **`services/`**: Domain-specific services implementing core business rules
- **`run_allocation.py`**: Smart matching algorithm connecting donations with requests
- **`jobs_service.py`**: Background job scheduling for automated tasks

#### **Data Layer**

- **`database/`**: Abstract database layer supporting multiple database backends
- **`models.py`**: Rich domain models with proper validation and relationships
- **Migration support**: Automatic schema creation and updates

#### **Security & Authentication**

- **`password.py`**: Argon2-based secure password hashing
- **OAuth integration**: Google OAuth 2.0 implementation
- **Session management**: Redis-backed secure session handling



### Complete File Descriptions

#### **Backend Controllers**

- **`auth_controller.py`**: Handles user authentication, registration, login, logout, and OAuth callbacks
- **`community_controller.py`**: Handles community club operations and manager functionalities
- **`donations_controller.py`**: Manages donation creation, approval, listing, and status updates
- **`inventory_controller.py`**: Manages inventory tracking, item status, and expiry monitoring
- **`jobs_controller.py`**: Controls background job scheduling and automated task execution
- **`notification_controller.py`**: Manages notification retrieval, marking as read, and user notifications
- **`profile_controller.py`**: Handles user profile management and account verification
- **`requests_controller.py`**: Controls request creation, matching, completion, and user-specific queries profile management and account verification

#### **Backend Services**

- **`auth_strategies.py`**: Implements Strategy pattern with GoogleOAuthStrategy and PasswordStrategy
- **`notification_strategies.py`**: Observer pattern implementation for notification delivery
- **`password.py`**: Secure password hashing using Argon2 algorithm
- **`run_allocation.py`**: Smart matching algorithm that connects donations with requests
- **`jobs_service.py`**: Background job scheduling for cleanup and allocation tasks
- **`notification_service.py`**: Core notification management and delivery service
- **`metrics.py`**: Analytics and performance metrics calculation
- **`image_upload.py`**: Image upload handling for donation photos
- **`find_user.py`**: User lookup and retrieval utilities
- **`community_clubs.py`**: Community club management and location services

#### **Backend Database Layer**

- **`database_factory.py`**: Factory pattern implementation for database type selection
- **`database_interface.py`**: Abstract interface defining database operations contract
- **`postgres_database.py`**: PostgreSQL-specific database implementation
- **`sqlite_database.py`**: SQLite database implementation for development

#### **Backend Routes**

- **`auth_routes.py`**: Authentication API endpoints (login, register, OAuth)
- **`community_routes.py`**: Community club management endpoints
- **`donations_routes.py`**: Donation management API endpoints
- **`inventory_routes.py`**: Inventory tracking and management endpoints
- **`jobs_routes.py`**: Background job control endpoints
- **`notification_routes.py`**: Notification system API endpoints
- **`profile_routes.py`**: User profile management endpoints
- **`requests_routes.py`**: Request handling API endpoints

#### **Backend Core Files**

- **`models.py`**: SQLAlchemy models (User, Client, Manager, Request, Donation, Item, Reservation, Notification)
- **`app.py`**: Flask application factory with dependency injection and configuration
- **`config.py`**: Environment-based configuration management
- **`extensions.py`**: Flask extensions initialization (SQLAlchemy, OAuth, CORS, Session)
- **`broadcast_observer.py`**: Observer pattern implementation for community notifications
- **`requirements.txt`**: Python dependencies with specific versions
- **`test-requirements.txt`**: Testing-specific dependencies



#### **Frontend Core Files**

- **`App.jsx`**: Main application component with routing and global state
- **`main.jsx`**: Application entry point and React DOM rendering
- **`httpClient.jsx`**: Axios configuration for API communication

#### **Frontend Components**

- **`CommunityClubsMap.jsx`**: Interactive map component for community club locations
- **`DonationCard.jsx`**: Reusable card component for displaying donation information
- **`TopNav.jsx`**: Top navigation bar with user authentication and menu options

#### **Frontend Client Pages**

- **`ClientDashboard.jsx`**: Analytics dashboard showing client donation and request statistics
- **`ClientHome.jsx`**: Main client interface with navigation to key features
- **`DonationForm.jsx`**: Form component for creating new donations
- **`DonationsList.jsx`**: List view of user's donations with status tracking
- **`RegisterForm.jsx`**: User registration form with validation
- **`RequestForm.jsx`**: Form component for creating new requests
- **`RequestsList.jsx`**: List view of user's requests with status tracking

#### **Frontend Shared Pages**

- **`Login.jsx`**: Authentication page supporting OAuth and password login
- **`Notifications.jsx`**: Notifications center for user alerts and updates
- **`Profile.jsx`**: User profile management and account settings
- **`Subscriptions.jsx`**: Community club subscription management

#### **Frontend Manager Pages**

- **`CompleteRequest.jsx`**: Workflow for managers to complete and close requests
- **`ManageDonations.jsx`**: Donation approval and management system for managers
- **`ManagerAction.jsx`**: Central action hub for manager operations
- **`ManagerDashboard.jsx`**: Analytics dashboard for community performance metrics
- **`ManageRegistrations.jsx`**: User registration approval and verification system
- **`ManagerHome.jsx`**: Main manager interface with administrative tools

#### **Frontend Styling**

- **Component-specific CSS**: Each major component has dedicated styling files
- **Responsive Design**: CSS files include mobile and desktop responsive layouts
- **Consistent Theming**: Unified color scheme and typography across all components

#### **Frontend Configuration**

- **`package.json`**: Dependencies, scripts, and project metadata
- **`vite.config.js`**: Vite build tool configuration
- **`index.html`**: HTML template with meta tags and root element
- **`.env`**: Environment variables for API endpoints and configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (for production) or SQLite (for development)
- Redis (for session management)

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Create virtual environment**
   ```bash
   cd backend
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the application**
   ```bash
   cd ..
   python -m backend.app
   ```

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm i
   ```

3. **Environment configuration**
   ```bash
   cp .env.example .env
   # Configure API endpoints
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

### Environment Variables

#### Backend (.env)
```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_RUN_PORT=5000

# Database
DATABASE_URL=postgresql://username:password@localhost/careconnect
# Or for SQLite: DATABASE_URL=sqlite:///careconnect.db

# Session Management
SESSION_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# OAuth (Google)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend
FRONTEND_ORIGIN=http://localhost:5173
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## 📊 Database Schema

### Core Models

- **User**: Base user model with role-based access (Manager/Client)
- **Client**: Extended user profile with income verification and account status
- **Manager**: Community club managers with location oversight
- **Request**: Items requested by clients with status tracking
- **Donation**: Items donated by clients with approval workflow
- **Item**: Individual units from donations for precise allocation
- **Reservation**: Links between requests and allocated items
- **Notification**: Real-time user notifications and updates

### Key Relationships

```
User (1) → (1) Client/Manager
Client (1) → (N) Requests
Client (1) → (N) Donations  
Donation (1) → (N) Items
Request (1) → (N) Reservations → (N) Items
User (1) → (N) Notifications
```

## 🔐 Authentication & Security

### Authentication Strategies

The application implements the Strategy pattern for flexible authentication:

- **Google OAuth Strategy**: Seamless Google account integration
- **Password Strategy**: Traditional email/password with secure hashing
- **Context Switching**: Runtime strategy selection based on user preference

### Security Features

- **Password Hashing**: Argon2 and bcrypt for secure password storage
- **Session Management**: Redis-backed secure sessions
- **Input Validation**: Comprehensive server-side validation
- **CORS Protection**: Configured cross-origin resource sharing

## 🎯 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/google` - Google OAuth initiation
- `GET /auth/google/callback` - OAuth callback handling
- `POST /auth/logout` - User logout

### Donations
- `GET /donations` - List all donations
- `POST /donations` - Create new donation
- `PUT /donations/<id>/approve` - Approve donation (managers)
- `DELETE /donations/<id>` - Delete donation

### Requests
- `GET /requests` - List all requests
- `POST /requests` - Create new request
- `GET /requests/my` - User's requests
- `PUT /requests/<id>/complete` - Mark request complete

### Notifications
- `GET /notifications` - Get user notifications
- `PUT /notifications/<id>/read` - Mark notification as read

## 🏃‍♂️ Development Workflow

### Code Quality Standards

- **Type Hints**: Comprehensive type annotations
- **Documentation**: Detailed docstrings for all modules/classes/methods
- **Error Handling**: Robust exception handling with proper rollbacks
- **Code Organization**: Clean separation of concerns across layers

### SOLID Principles Implementation

#### 1. **Single Responsibility Principle (SRP)**
- **AuthController**: Handles only authentication logic
- **NotificationService**: Manages only notification delivery
- **DatabaseFactory**: Responsible solely for database instance creation

#### 2. **Open/Closed Principle (OCP)**
- **Authentication Strategies**: Open for extension (new auth methods), closed for modification
- **Database Implementations**: New database types can be added without changing existing code
- **Notification Strategies**: Extensible notification delivery methods

#### 3. **Liskov Substitution Principle (LSP)**
- **Database Interfaces**: PostgreSQL and SQLite implementations are interchangeable
- **Authentication Strategies**: Google OAuth and Password strategies can substitute each other
- **Observer Implementations**: All observers can be used interchangeably

#### 4. **Interface Segregation Principle (ISP)**
- **Focused Interfaces**: `IObserver`, `DatabaseInterface`, `AuthenticationStrategy`
- **Minimal Dependencies**: Classes depend only on methods they actually use
- **Cohesive Contracts**: Each interface serves a specific, well-defined purpose

#### 5. **Dependency Inversion Principle (DIP)**
- **Abstract Dependencies**: Controllers depend on service interfaces, not implementations
- **Dependency Injection**: Strategies and implementations injected at runtime
- **Inversion of Control**: High-level modules don't depend on low-level modules

### Design Pattern Benefits

#### **Strategy Pattern Advantages**
- **Runtime Flexibility**: Switch authentication methods without code changes
- **Easy Testing**: Mock strategies for unit testing
- **Maintainability**: Add new authentication methods without modifying existing code

#### **Factory Pattern Advantages**
- **Database Agnostic**: Support multiple databases through unified interface
- **Configuration Driven**: Database selection through environment variables
- **Scalability**: Easy addition of new database implementations

#### **Observer Pattern Advantages**
- **Loose Coupling**: Notification system decoupled from business logic
- **Event-Driven Architecture**: Reactive system responding to state changes
- **Extensibility**: Add new notification channels without core system changes

#### **Facade Pattern Advantages**
- **Decouples Client from system**: Hides business logic from frontend

## 📈 Performance & Scalability

### Monitoring & Analytics

- **Fulfillment Rate Tracking**: Community performance metrics
- **Usage Analytics**: Donation and request pattern analysis
- **Error Tracking**: Comprehensive logging and error reporting

---

**CareConnect** - Connecting communities through technology and compassion 💝
