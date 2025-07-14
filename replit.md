# Overview

This is a Telegram group protection bot written in Python that provides comprehensive moderation and security features for Telegram groups. The bot includes member verification, message filtering, spam detection, and administrative tools to help maintain safe and organized group environments.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The bot follows a modular architecture with clear separation of concerns:

- **Main Entry Point**: `main.py` handles bot initialization and deployment
- **Configuration Layer**: Centralized settings management in `config/`
- **Handler Layer**: Event-driven handlers for different bot functionalities in `bot/handlers/`
- **Service Layer**: Business logic services in `bot/services/`
- **Utility Layer**: Helper functions and database management in `bot/utils/`
- **Data Layer**: Static data files and SQLite database storage

## Key Components

### 1. Bot Framework
- **Technology**: Python-telegram-bot library
- **Deployment**: Supports both webhook and polling modes
- **Language**: Bilingual support (Arabic and English)

### 2. Handler System
- **Command Handlers**: General bot commands (`/start`, `/help`)
- **Verification Handlers**: New member verification with challenges
- **Moderation Handlers**: Message filtering and spam detection
- **Admin Handlers**: Administrative commands for group management

### 3. Service Layer
- **VerificationService**: Manages new member verification challenges
- **ModerationService**: Handles spam detection, warnings, and user muting
- **BadWordsService**: Filters inappropriate content using pattern matching

### 4. Database Layer
- **Technology**: SQLite with custom wrapper class
- **Purpose**: Stores user data, verification states, warnings, and moderation logs
- **Schema**: Tables for users, verification challenges, warnings, and audit logs

## Data Flow

1. **Message Reception**: Telegram sends updates to the bot
2. **Handler Routing**: Updates are routed to appropriate handlers based on type
3. **Service Processing**: Business logic is executed through service classes
4. **Database Operations**: Data is persisted or retrieved from SQLite
5. **Response Generation**: Bot sends responses back to Telegram

## External Dependencies

### Core Libraries
- `python-telegram-bot`: Main bot framework
- `sqlite3`: Database operations (built-in)
- `logging`: Application logging (built-in)

### Configuration Requirements
- `BOT_TOKEN`: Telegram bot token (required)
- `WEBHOOK_URL`: For webhook deployment (optional)
- `DATABASE_URL`: Database connection string (defaults to local SQLite)

### Data Sources
- `data/badwords.txt`: Static list of prohibited words in Arabic
- Environment variables for configuration

## Deployment Strategy

### Development Mode
- **Method**: Polling mode with local SQLite database
- **Configuration**: `DEBUG=True`, no webhook URL
- **Logging**: Console output with debug level

### Production Mode
- **Method**: Webhook mode for better performance
- **Configuration**: Webhook URL and port configuration
- **Logging**: File-based logging with rotation
- **Database**: SQLite (can be upgraded to PostgreSQL)

### Key Features
- **Member Verification**: Quiz-based challenges for new members
- **Enhanced Content Filtering**: Arabic bad words detection with automatic muting
- **Offensive Word Management**: Admin commands to add and manage offensive words
- **Spam Protection**: Message frequency and pattern analysis
- **Administrative Tools**: Ban, mute, warn, and kick commands
- **Audit Logging**: Comprehensive action tracking

### Security Considerations
- Admin privilege validation for sensitive operations
- Rate limiting and spam detection
- Automatic cleanup of verification challenges
- Secure token management through environment variables

## Recent Changes

### July 14, 2025 - Enhanced Offensive Word Detection
- **Added automatic muting feature**: Users who send offensive words are automatically muted for 5 minutes
- **New admin command `/addbad`**: Allows admins to add offensive words to the filter list
- **New admin command `/listbad`**: Displays current list of offensive words
- **Enhanced moderation**: All bot messages are now in Arabic only
- **Improved user experience**: Clear Arabic warnings when offensive content is detected

### Previous Updates
- Fixed bot startup issues and added proper error handling
- Added comprehensive logging and debugging
- Enhanced handler registration system

The architecture is designed to be scalable and maintainable, with clear separation between presentation (handlers), business logic (services), and data persistence (database utilities).