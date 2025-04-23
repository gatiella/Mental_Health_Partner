# Mental Health Partner

A compassionate AI-powered Django application designed to provide mental health conversations and support through an intuitive web interface.

![Mental Health Partner](https://github.com/gatiella/Mental_Health_Partner/raw/main/static/images/logo.png)

## Overview

Mental Health Partner connects users with an empathetic AI assistant powered by DeepseekAI via OpenRouter, offering a safe space for emotional support and mental wellness discussions. The application focuses on providing accessible mental health support while encouraging professional help when needed.

## Features

- **AI-Powered Conversations**: Real-time supportive conversations with an empathetic mental health assistant
- **User Management**: Secure authentication and personalized user profiles
- **Conversation History**: Access to previous conversations and support sessions
- **Feedback System**: Collect user feedback to improve the quality of support
- **Crisis Detection**: Identification of potential crisis situations with appropriate resource recommendations
- **Topic Organization**: Conversations organized by relevant mental health topics
- **Analytics Dashboard**: Track usage patterns and effectiveness (admin only)

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL
- **AI Integration**: DeepseekAI via OpenRouter API
- **Frontend**: Bootstrap 5, JavaScript
- **Deployment**: Compatible with Render, Heroku, or similar platforms

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/gatiella/Mental_Health_Partner.git
   cd Mental_Health_Partner
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to include your PostgreSQL credentials and DeepseekAI API key

6. Set up the PostgreSQL database
   - Create a database named in your `.env` file
   - Ensure the user has proper permissions

7. Run migrations
   ```bash
   python manage.py migrate
   ```

8. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```

9. Run the server
   ```bash
   python manage.py runserver
   ```

10. Access the application at `http://localhost:8000`

## Project Structure

The project consists of three main apps:

- **`conversation`**: Core conversation functionality and AI integration
  - Manages message exchanges between users and the AI assistant
  - Handles the DeepseekAI API integration
  - Implements content moderation and safety features

- **`users`**: User management and profiles
  - Authentication and authorization
  - User preferences and settings
  - Profile management

- **`analytics`**: Usage tracking and insights (optional)
  - Conversation metrics and statistics
  - Effectiveness reporting
  - Usage patterns and trends

## Configuration

The application requires the following environment variables:

- Database configuration:
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  
- Django settings:
  - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
  
- DeepseekAI integration:
  - `DEEPSEEK_API_KEY`, `DEEPSEEK_API_URL`, `SITE_URL`

## Contributing

Contributions to improve Mental Health Partner are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is not a substitute for professional mental health treatment or crisis intervention. If you or someone you know is experiencing a mental health emergency, please contact your local emergency services or a mental health crisis hotline immediately.
