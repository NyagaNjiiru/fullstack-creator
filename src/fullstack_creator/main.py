#!/usr/bin/env python3
import os
import subprocess
import inquirer
import platform
import sys
import shutil

def run_cmd(cmd, cwd=None):
    print(f"[RUNNING] {cmd}")
    try:
        process = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"[ERROR] Command failed: {stderr.decode()}")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Failed to run command: {e}")
        return False

def check_dependencies():
    required = {'git': 'git --version', 'node': 'node --version', 'npm': 'npm --version'}
    missing = []
    for tool, check_cmd in required.items():
        try:
            subprocess.run(check_cmd.split(), capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
    
    if missing:
        print(f"[ERROR] Missing required dependencies: {', '.join(missing)}")
        sys.exit(1)

def open_project_folder(path):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", path])
        elif system == "Windows":
            subprocess.run(["start", path], shell=True)
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        print(f"[ERROR] Could not open folder: {e}")
        print(f"Project created at: {path}")

def setup_python_venv(backend_path, packages):
    python_cmd = "python3" if shutil.which("python3") else "python"
    run_cmd(f"{python_cmd} -m venv venv", cwd=backend_path)
    
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = f"{activate_cmd} && pip install {' '.join(packages)}"
    else:
        activate_cmd = "venv/bin/activate"
        pip_cmd = f"source {activate_cmd} && pip install {' '.join(packages)}"
    
    run_cmd(pip_cmd, cwd=backend_path)
    
    with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
        f.write("\n".join(packages))

def setup_npm_project(path, packages):
    run_cmd("npm init -y", cwd=path)
    if packages:
        run_cmd(f"npm install {' '.join(packages)}", cwd=path)

def setup_vite_project(project_path, template, folder_name="frontend"):
    if run_cmd(f"npm create vite@latest {folder_name} -- --template {template}", cwd=project_path):
        run_cmd("npm install", cwd=os.path.join(project_path, folder_name))

def create_rust_project(project_path, dependencies=None):
    run_cmd("cargo new backend --bin", cwd=project_path)
    if dependencies:
        backend_path = os.path.join(project_path, "backend")
        with open(os.path.join(backend_path, "Cargo.toml"), "a") as f:
            f.write(f'\n[dependencies]\n{dependencies}')

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def get_structure_choices(language):
    return ["Backend only"] if language in ["Rust", "Go", "C#"] else ["Fullstack", "Frontend only", "Backend only"]

def get_frontend_choices(language):
    return ["None"] if language != "JavaScript" else ["Vite + React", "Vue", "Angular", "Svelte", "None"]

def get_backend_choices(language):
    choices = {
        "JavaScript": ["Express", "None"],
        "Python": ["Flask", "Django", "FastAPI", "None"],
        "Rust": ["Rocket", "Actix", "None"],
        "Go": ["Basic HTTP Server", "None"],
        "C#": ["ASP.NET Core WebAPI", "None"]
    }
    return choices.get(language, ["None"])

def check_language_dependencies(language, backend):
    if backend == "None":
        return True
    
    tools = {
        "Python": ["python3", "python"],
        "Rust": ["cargo"],
        "Go": ["go"],
        "C#": ["dotnet"]
    }
    
    if language in tools:
        if not any(shutil.which(tool) for tool in tools[language]):
            print(f"[ERROR] {language} tools required for {backend} backend")
            return False
    return True

def create_gitignore(project_path, frontend, backend, language):
    content = ["# Dependencies", "node_modules/", "*.log", "", "# Environment", ".env", ".env.local", "", "# Build outputs", "dist/", "build/", ""]
    
    lang_ignores = {
        "Python": ["# Python", "__pycache__/", "*.pyc", "venv/", ".venv/", ""],
        "Rust": ["# Rust", "target/", "Cargo.lock", ""],
        "Go": ["# Go", "*.exe", "*.exe~", "*.dll", "*.so", "*.dylib", ""],
        "C#": ["# .NET", "bin/", "obj/", "*.user", ""]
    }
    
    if language in lang_ignores:
        content.extend(lang_ignores[language])
    
    if frontend == "Angular":
        content.extend(["# Angular", ".angular/", ""])
    
    write_file(os.path.join(project_path, ".gitignore"), "\n".join(content))

def create_readme(project_path, project_name, frontend, backend, language):
    content = f"# {project_name}\n\n## Project Structure\n\n"
    
    if frontend != "None" and backend != "None":
        content += f"- **Frontend**: {frontend}\n- **Backend**: {backend}\n"
    elif frontend != "None":
        content += f"- **Frontend**: {frontend}\n"
    elif backend != "None":
        content += f"- **Backend**: {backend}\n"
    
    content += "\n## Getting Started\n\n### Prerequisites\n- Node.js and npm (for frontend)"
    
    prereqs = {
        "Python": "\n- Python 3.x (for backend)",
        "Rust": "\n- Rust and Cargo (for backend)",
        "Go": "\n- Go (for backend)",
        "C#": "\n- .NET SDK (for backend)"
    }
    
    if language in prereqs:
        content += prereqs[language]
    
    content += '\n\n### Installation\n\n1. Clone the repository\n2. Run the start script: `./start.sh`\n\n### Manual Setup\n'
    
    if frontend != "None":
        content += '\n#### Frontend\n```bash\ncd frontend\nnpm install\nnpm run dev\n```\n'
    
    if backend != "None":
        backend_docs = {
            "Express": '\n#### Backend (Express)\n```bash\ncd backend\nnpm install\nnode server.js\n```\n',
            "Flask": '\n#### Backend (Flask)\n```bash\ncd backend\npython3 -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\npython app.py\n```\n',
            "Django": '\n#### Backend (Django)\n```bash\ncd backend\npython3 -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\npython manage.py runserver\n```\n',
            "FastAPI": '\n#### Backend (FastAPI)\n```bash\ncd backend\npython3 -m venv venv\nsource venv/bin/activate\npip install -r requirements.txt\nuvicorn main:app --reload\n```\n',
            "Rocket": '\n#### Backend (Rocket)\n```bash\ncd backend\ncargo run\n```\n',
            "Actix": '\n#### Backend (Actix)\n```bash\ncd backend\ncargo run\n```\n',
            "Basic HTTP Server": '\n#### Backend (Go)\n```bash\ncd backend\ngo run main.go\n```\n',
            "ASP.NET Core WebAPI": '\n#### Backend (ASP.NET Core)\n```bash\ncd backend\ndotnet run\n```\n'
        }
        content += backend_docs.get(backend, "")
    
    write_file(os.path.join(project_path, "README.md"), content)

def setup_frontend(project_path, frontend):
    if frontend == "Vite + React":
        setup_vite_project(project_path, "react")
    elif frontend == "Vue":
        setup_vite_project(project_path, "vue")
    elif frontend == "Angular":
        run_cmd("npx -p @angular/cli ng new frontend --skip-git --routing --style=css", cwd=project_path)
    elif frontend == "Svelte":
        setup_vite_project(project_path, "svelte")

def setup_backend(project_path, backend):
    backend_path = os.path.join(project_path, "backend")
    
    if backend == "Express":
        os.makedirs(backend_path, exist_ok=True)
        setup_npm_project(backend_path, ["express", "cors", "dotenv"])
        write_file(os.path.join(backend_path, "server.js"), """const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Express backend running!' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
""")
    
    elif backend == "FastAPI":
        os.makedirs(backend_path, exist_ok=True)
        setup_python_venv(backend_path, ["fastapi", "uvicorn[standard]"])
        write_file(os.path.join(backend_path, "main.py"), """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI backend running!"}
""")
    
    elif backend == "Flask":
        os.makedirs(backend_path, exist_ok=True)
        setup_python_venv(backend_path, ["flask", "flask-cors"])
        write_file(os.path.join(backend_path, "app.py"), """from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Flask backend running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
""")
    
    elif backend == "Django":
        os.makedirs(backend_path, exist_ok=True)
        setup_python_venv(backend_path, ["django", "djangorestframework", "django-cors-headers"])
        activate_cmd = "venv\\Scripts\\activate" if platform.system() == "Windows" else "source venv/bin/activate"
        django_cmd = f"{activate_cmd} && django-admin startproject backend_app ."
        run_cmd(django_cmd, cwd=backend_path)
    
    elif backend == "Rocket":
        create_rust_project(project_path, 'rocket = "0.5"')
        write_file(os.path.join(project_path, "backend", "src", "main.rs"), """#[macro_use] extern crate rocket;

#[get("/")]
fn index() -> &'static str {
    "Rocket backend running!"
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/", routes![index])
}
""")
    
    elif backend == "Actix":
        create_rust_project(project_path, 'actix-web = "4"')
        write_file(os.path.join(project_path, "backend", "src", "main.rs"), """use actix_web::{web, App, HttpResponse, HttpServer, Result};

async fn index() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json("Actix backend running!"))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(index))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
""")
    
    elif backend == "Basic HTTP Server":
        os.makedirs(backend_path, exist_ok=True)
        write_file(os.path.join(backend_path, "main.go"), """package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Access-Control-Allow-Origin", "*")
    fmt.Fprintln(w, "Go backend running!")
}

func main() {
    http.HandleFunc("/", handler)
    fmt.Println("Server running on http://localhost:8080")
    http.ListenAndServe(":8080", nil)
}
""")
    
    elif backend == "ASP.NET Core WebAPI":
        run_cmd("dotnet new webapi -n backend", cwd=project_path)

def create_start_script(project_path, frontend, backend):
    is_windows = platform.system() == "Windows"
    script_name = "start.bat" if is_windows else "start.sh"
    script_path = os.path.join(project_path, script_name)
    
    commands = []
    
    if is_windows:
        commands.append("@echo off")
        if frontend != "None":
            commands.append('start cmd /k "cd frontend && npm run dev"')
        
        backend_cmds = {
            "Express": 'start cmd /k "cd backend && node server.js"',
            "FastAPI": 'start cmd /k "cd backend && venv\\Scripts\\activate && uvicorn main:app --reload"',
            "Flask": 'start cmd /k "cd backend && venv\\Scripts\\activate && python app.py"',
            "Django": 'start cmd /k "cd backend && venv\\Scripts\\activate && python manage.py runserver"',
            "Rocket": 'start cmd /k "cd backend && cargo run"',
            "Actix": 'start cmd /k "cd backend && cargo run"',
            "Basic HTTP Server": 'start cmd /k "cd backend && go run main.go"',
            "ASP.NET Core WebAPI": 'start cmd /k "cd backend && dotnet run"'
        }
    else:
        commands.append("#!/bin/bash\n")
        if frontend != "None":
            commands.append("(cd frontend && npm run dev) &")
        
        backend_cmds = {
            "Express": "(cd backend && node server.js) &",
            "FastAPI": "(cd backend && source venv/bin/activate && uvicorn main:app --reload) &",
            "Flask": "(cd backend && source venv/bin/activate && python app.py) &",
            "Django": "(cd backend && source venv/bin/activate && python manage.py runserver) &",
            "Rocket": "(cd backend && cargo run) &",
            "Actix": "(cd backend && cargo run) &",
            "Basic HTTP Server": "(cd backend && go run main.go) &",
            "ASP.NET Core WebAPI": "(cd backend && dotnet run) &"
        }
    
    if backend in backend_cmds:
        commands.append(backend_cmds[backend])
    
    if not is_windows and len([cmd for cmd in commands if "&" in cmd]) > 0:
        commands.extend(["\necho \"All services started. Press Ctrl+C to stop all services.\"", "wait"])
    
    write_file(script_path, "\n".join(commands))
    
    if not is_windows:
        os.chmod(script_path, 0o755)

def main():
    print("Create Fullstack Project")
    print("=" * 25)
    
    check_dependencies()
    
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("[ERROR] Project name cannot be empty")
        sys.exit(1)
    
    save_path = input("Enter directory to save project (default: current dir): ").strip() or os.getcwd()
    project_path = os.path.join(save_path, project_name)
    
    if os.path.exists(project_path):
        overwrite = inquirer.list_input(f"Directory {project_path} already exists. Overwrite?", choices=["Yes", "No"])
        if overwrite == "No":
            sys.exit(0)
        shutil.rmtree(project_path)
    
    os.makedirs(project_path, exist_ok=True)

    language = inquirer.list_input("Choose primary language", choices=["JavaScript", "Python", "Rust", "Go", "C#"])
    structure = inquirer.list_input("Project type", choices=get_structure_choices(language))

    frontend = backend = "None"
    
    if structure in ["Fullstack", "Frontend only"]:
        frontend = inquirer.list_input("Choose frontend framework", choices=get_frontend_choices(language))
    
    if structure in ["Fullstack", "Backend only"]:
        backend = inquirer.list_input("Choose backend framework", choices=get_backend_choices(language))

    if not check_language_dependencies(language, backend):
        sys.exit(1)

    gh_available = shutil.which("gh") is not None
    if gh_available:
        visibility = inquirer.list_input("GitHub repository visibility", choices=["Public", "Private", "Skip"])
    else:
        print("[INFO] GitHub CLI not found. Skipping repository creation.")
        visibility = "Skip"

    print(f"[INFO] Creating {structure} project at {project_path}")

    run_cmd("git init", cwd=project_path)
    
    if frontend != "None":
        setup_frontend(project_path, frontend)
    
    if backend != "None":
        setup_backend(project_path, backend)

    create_start_script(project_path, frontend, backend)
    create_gitignore(project_path, frontend, backend, language)
    create_readme(project_path, project_name, frontend, backend, language)

    if visibility != "Skip":
        print("[INFO] Creating GitHub repository...")
        visibility_flag = "--public" if visibility == "Public" else "--private"
        success = run_cmd(f"gh repo create {project_name} {visibility_flag} --source . --remote=origin --push", cwd=project_path)
        if not success:
            print("[WARNING] Failed to create GitHub repository. You can create it manually later.")

    open_answer = inquirer.list_input("Open project folder now?", choices=["Yes", "No"])
    if open_answer == "Yes":
        open_project_folder(project_path)

    script_ext = ".bat" if platform.system() == "Windows" else ".sh"
    print(f"[DONE] Project {project_name} setup complete at {project_path}")
    print(f"Run .{os.sep}start{script_ext} to start your project")

if __name__ == "__main__":
    main()
    