# Contributing to Home Slice

Thank you for your interest in contributing to Home Slice! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/home-slice.git
   cd home-slice
   ```

2. Install dependencies:

   ```bash
   # Install pnpm if you haven\'\t already
   npm install -g pnpm

   # Install project dependencies
   pnpm install
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up Python environment:
   ```bash
   cd data-service
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Workflow

1. Create a new branch for your feature/fix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git commit -m "Description of your changes"
   ```

3. Push your branch and create a Pull Request

## Code Style

- Python: Follow PEP 8 guidelines
- JavaScript/TypeScript: Use ESLint and Prettier configurations
- Use meaningful commit messages
- Write tests for new features

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if needed
3. The PR will be merged once you have the sign-off of at least one other developer

## Questions?

Feel free to open an issue for any questions or concerns.
