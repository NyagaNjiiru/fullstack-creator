#!/usr/bin/env python3

import inquirer
import os
import subprocess

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        exit(1)
        
def main():
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("Project name cannot be empty!")
        return
    
    save_path = input("Enter directory to save project (default: current dir): ").strip()
    if not save_path:
        save_path = os.getcwd()
    project_path = os.path.join(save_path, project_name)
    
    questions = [
        inquirer.List(
            "language",
            message="Choose primary language",
            choices=["JavaScript", "Python", "Rust", "Go", "C#"]
        ),
        inquirer.List(
            "structure",
            message="Project type",
            choices=["Fullstack", "Frontend only", "Backend only"]
        ),
        inquirer.List(
            "frontend",
            message="Choose frontend framework",
            choices=["Vite + React", "Vue", "Angular", "Svelte", "None"]
        ),
        inquirer.List(
            "backend",
            message="Choose backend framework",
            choices=["Express (Node.js)", "Django", "Flask", "FastAPI", "None"]
        )
    ]
    answers = inquirer.prompt(questions)
    
    print(f"Creating {answers['structure']} project at {project_path}...")
    
    # Create project directory
    os.makedirs(project_path, exist_ok=True)
    
    # Create subdirectories based on project structure
    if answers["structure"] in ["Fullstack", "Frontend only"]:
        os.makedirs(os.path.join(project_path, "frontend"), exist_ok=True)
    if answers["structure"] in ["Fullstack", "Backend only"]:
        os.makedirs(os.path.join(project_path, "backend"), exist_ok=True)
    
    print("Initializing Git...")
    run_cmd("git init", cwd=project_path)
    
    # Frontend setup
    if answers["frontend"] == "Vite + React":
        run_cmd("npm create vite@latest frontend -- --template react", cwd=project_path)
        frontend_path = os.path.join(project_path, "frontend")
        run_cmd("npm install", cwd=frontend_path)
        run_cmd("npm install -D tailwindcss postcss autoprefixer", cwd=frontend_path)
        run_cmd("npx tailwindcss init -p", cwd=frontend_path)
        
    elif answers["frontend"] == "Vue":
        run_cmd("npm create vite@latest frontend -- --template vue", cwd=project_path)
        run_cmd("npm install", cwd=os.path.join(project_path, "frontend"))
        
    elif answers["frontend"] == "Angular":
        run_cmd("npx -p @angular/cli ng new frontend --skip-git --routing --style=css", cwd=project_path)
        
    elif answers["frontend"] == "Svelte":
        run_cmd("npm create vite@latest frontend -- --template svelte", cwd=project_path)
        run_cmd("npm install", cwd=os.path.join(project_path, "frontend"))
    
    # Backend setup
    if answers["backend"] == "Express (Node.js)":
        backend_path = os.path.join(project_path, "backend")
        run_cmd("npm init -y", cwd=backend_path)
        run_cmd("npm install express cors dotenv", cwd=backend_path)
        run_cmd("npm install -D nodemon", cwd=backend_path)
        
        # Create basic Express server
        with open(os.path.join(backend_path, "server.js"), "w") as f:
            f.write("""const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Backend server is running!' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
""")
        
        # Update package.json scripts
        import json
        package_json_path = os.path.join(backend_path, "package.json")
        with open(package_json_path, "r") as f:
            package_data = json.load(f)
        package_data["scripts"]["start"] = "node server.js"
        package_data["scripts"]["dev"] = "nodemon server.js"
        with open(package_json_path, "w") as f:
            json.dump(package_data, f, indent=2)
    
    elif answers["backend"] == "FastAPI":
        backend_path = os.path.join(project_path, "backend")
        
        # Create virtual environment
        run_cmd("python3 -m venv venv", cwd=backend_path)
        
        # Determine the correct pip path based on OS
        pip_path = "./venv/bin/pip" if os.name != 'nt' else ".\\venv\\Scripts\\pip"
        python_path = "./venv/bin/python" if os.name != 'nt' else ".\\venv\\Scripts\\python"
        
        # Install dependencies in venv
        run_cmd(f"{pip_path} install fastapi uvicorn python-dotenv", cwd=backend_path)
        
        # Create requirements.txt
        with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
            f.write("fastapi\nuvicorn[standard]\npython-dotenv\n")
        
        # Create main.py
        with open(os.path.join(backend_path, "main.py"), "w") as f:
            f.write("""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")
        
        # Create .env file
        with open(os.path.join(backend_path, ".env"), "w") as f:
            f.write("# Environment variables\nPORT=8000\n")
    
    elif answers["backend"] == "Django":
        backend_path = os.path.join(project_path, "backend")
        
        # Create virtual environment
        run_cmd("python3 -m venv venv", cwd=backend_path)
        
        pip_path = "./venv/bin/pip" if os.name != 'nt' else ".\\venv\\Scripts\\pip"
        python_path = "./venv/bin/python" if os.name != 'nt' else ".\\venv\\Scripts\\python"
        
        # Install Django
        run_cmd(f"{pip_path} install django djangorestframework django-cors-headers", cwd=backend_path)
        
        # Create Django project
        run_cmd(f"{python_path} -m django startproject backend_app .", cwd=backend_path)
        
        # Create requirements.txt
        with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
            f.write("django\ndjangorestframework\ndjango-cors-headers\n")
    
    elif answers["backend"] == "Flask":
        backend_path = os.path.join(project_path, "backend")
        
        # Create virtual environment
        run_cmd("python3 -m venv venv", cwd=backend_path)
        
        pip_path = "./venv/bin/pip" if os.name != 'nt' else ".\\venv\\Scripts\\pip"
        
        # Install Flask
        run_cmd(f"{pip_path} install flask flask-cors python-dotenv", cwd=backend_path)
        
        # Create requirements.txt
        with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
            f.write("flask\nflask-cors\npython-dotenv\n")
        
        # Create app.py
        with open(os.path.join(backend_path, "app.py"), "w") as f:
            f.write("""from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Flask backend is running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
""")
    
    # Create main README.md
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, "w") as f:
        f.write(f"# {project_name}\n\n")
        f.write(f"**Language:** {answers['language']}\n")
        f.write(f"**Frontend:** {answers['frontend']}\n")
        f.write(f"**Backend:** {answers['backend']}\n\n")
        
        if answers["structure"] in ["Fullstack", "Frontend only"] and answers["frontend"] != "None":
            f.write("## Frontend Setup\n")
            f.write("```bash\ncd frontend\nnpm install\nnpm run dev\n```\n\n")
        
        if answers["structure"] in ["Fullstack", "Backend only"] and answers["backend"] != "None":
            f.write("## Backend Setup\n")
            if answers["backend"] in ["FastAPI", "Django", "Flask"]:
                f.write("```bash\ncd backend\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\npip install -r requirements.txt\n")
                if answers["backend"] == "FastAPI":
                    f.write("uvicorn main:app --reload\n```\n\n")
                elif answers["backend"] == "Flask":
                    f.write("python app.py\n```\n\n")
                elif answers["backend"] == "Django":
                    f.write("python manage.py runserver\n```\n\n")
            else:
                f.write("```bash\ncd backend\nnpm install\nnpm run dev\n```\n\n")
        
        f.write("## Development\n")
        f.write("This project was generated using a fullstack project creator.\n")
        
    # Create .gitignore
    gitignore_path = os.path.join(project_path, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write("""# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.log
""")
        
    run_cmd("git add .", cwd=project_path)
    run_cmd("git commit -m 'Initial commit'", cwd=project_path)
    
    print("Creating GitHub repository...")
    run_cmd(f"gh repo create {project_name} --public --source . --remote=origin --push", cwd=project_path)
    
    print(f"\n✅ Done! Your project '{project_name}' is ready and live on GitHub.")
    print(f"📂 Project location: {project_path}")
    if answers["structure"] in ["Fullstack", "Frontend only"] and answers["frontend"] != "None":
        print(f"🎨 Frontend: cd {project_name}/frontend && npm run dev")
    if answers["structure"] in ["Fullstack", "Backend only"] and answers["backend"] != "None":
        if answers["backend"] in ["FastAPI", "Django", "Flask"]:
            print(f"🔧 Backend: cd {project_name}/backend && source venv/bin/activate")
        else:
            print(f"🔧 Backend: cd {project_name}/backend && npm run dev")
    
if __name__ == "__main__":
    main()