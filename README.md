# Create Fullstack Project Generator

A cross-platform Python script to quickly scaffold fullstack, frontend, or backend projects with popular frameworks.

## Features

- **Cross-platform support**: Works on Linux, macOS, and Windows
- **Multiple languages**: JavaScript, Python, Rust, Go, C#
- **Frontend frameworks**: React (Vite), Vue, Angular, Svelte
- **Backend frameworks**: Express, Flask, Django, FastAPI, Rocket, Actix, Go HTTP Server, ASP.NET Core
- **Automatic setup**: Dependencies installation, git initialization, starter files
- **GitHub integration**: Optional repository creation (requires GitHub CLI)
- **Smart start scripts**: Platform-specific scripts to run your services

## Prerequisites

### Required
- Python 3.6+
- Git
- Node.js and npm (for frontend frameworks)

### Optional (based on chosen backend)
- Python 3.x (for Flask/Django/FastAPI)
- Rust and Cargo (for Rocket/Actix)
- Go (for Go HTTP Server)
- .NET SDK (for ASP.NET Core)
- GitHub CLI (`gh`) for repository creation

## Installation

1. Make the script executable:
   ```bash
   chmod +x create-fullstack
   ```

2. Optionally, move it to your PATH:
   ```bash
   sudo cp create-fullstack /usr/local/bin/
   ```

## Usage

Run the script:
```bash
./create-fullstack
```

The script will prompt you for:
1. **Project name**
2. **Directory** (default: current directory)
3. **Primary language** (JavaScript, Python, Rust, Go, C#)
4. **Project type** (Fullstack, Frontend only, Backend only)
5. **Frontend framework** (if applicable)
6. **Backend framework** (if applicable)
7. **GitHub repository visibility** (Public, Private, or Skip)
8. **Open project folder** after creation

## Generated Project Structure

### Fullstack Project
```
my-project/
├── frontend/          # Frontend application
├── backend/           # Backend application
├── start.sh          # Start script (Linux/macOS)
├── start.bat         # Start script (Windows)
├── README.md         # Project documentation
├── .gitignore        # Git ignore rules
└── .git/             # Git repository
```

### Frontend Only
```
my-project/
├── frontend/         # Frontend application
├── start.sh/.bat     # Start script
├── README.md         # Project documentation
├── .gitignore        # Git ignore rules
└── .git/             # Git repository
```

### Backend Only
```
my-project/
├── backend/          # Backend application (or root level for some frameworks)
├── start.sh/.bat     # Start script
├── README.md         # Project documentation
├── .gitignore        # Git ignore rules
└── .git/             # Git repository
```

## Start Scripts

After project creation, use the generated start script to run your services:

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

The script will automatically start all configured services (frontend and/or backend) in the background.

## Supported Frameworks

### Frontend (JavaScript only)
- **Vite + React**: Modern React setup with Vite
- **Vue**: Vue 3 with Vite
- **Angular**: Angular CLI project
- **Svelte**: Svelte with Vite

### Backend
- **JavaScript**: Express.js
- **Python**: Flask, Django, FastAPI
- **Rust**: Rocket, Actix Web
- **Go**: Basic HTTP Server
- **C#**: ASP.NET Core WebAPI

## Examples

### Create a React + Express fullstack app:
1. Run `./create-fullstack`
2. Choose JavaScript as language
3. Select Fullstack
4. Pick Vite + React for frontend
5. Pick Express for backend

### Create a Python FastAPI backend:
1. Run `./create-fullstack`
2. Choose Python as language
3. Select Backend only
4. Pick FastAPI

### Create a Vue frontend:
1. Run `./create-fullstack`
2. Choose JavaScript as language
3. Select Frontend only
4. Pick Vue

## Default Ports

- **Frontend**: Usually 3000 (React), 5173 (Vite), 4200 (Angular)
- **Backend**: 5000 (Express/Flask/Django), 8000 (FastAPI), 8080 (Go/Rust)

## Troubleshooting

### Missing Dependencies
The script checks for required dependencies and will notify you if any are missing. Install them before running the script.

### GitHub CLI Not Found
If you don't have GitHub CLI installed, the script will skip repository creation. You can create the repository manually later.

### Permission Errors
On Unix systems, make sure the script is executable:
```bash
chmod +x create-fullstack
```

### Python Virtual Environments
For Python backends, the script automatically creates and activates virtual environments. If you encounter issues, manually activate:

**Linux/macOS:**
```bash
cd backend && source venv/bin/activate
```

**Windows:**
```bash
cd backend && venv\Scripts\activate
```

## Contributing

Feel free to submit issues and enhancement requests. The script is designed to be easily extensible for additional frameworks and languages.