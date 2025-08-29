#!/usr/bin/env python3
import os
import subprocess
import inquirer
import platform
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor
import threading

def run_cmd(cmd, cwd=None, capture_output=True, show_output=False):
    """Enhanced command runner with better output handling"""
    if show_output:
        print(f"[RUNNING] {cmd}")
    
    try:
        if show_output:
            # For commands we want to see output from
            process = subprocess.Popen(
                cmd, 
                cwd=cwd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Print output in real-time
            for line in iter(process.stdout.readline, ''):
                print(line.rstrip())
            
            process.wait()
            return process.returncode == 0
        else:
            # Silent execution for faster operations
            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Command timed out: {cmd}")
        return False
    except Exception as e:
        if show_output:
            print(f"[ERROR] Failed to run command: {e}")
        return False

def check_dependencies():
    """Quick dependency check with parallel execution"""
    required = {'git': 'git --version', 'node': 'node --version', 'npm': 'npm --version'}
    
    def check_tool(tool_cmd):
        tool, cmd = tool_cmd
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True, timeout=10)
            return tool, True
        except:
            return tool, False
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = dict(executor.map(check_tool, required.items()))
    
    missing = [tool for tool, available in results.items() if not available]
    
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
            # Try different Linux file managers
            file_managers = ["xdg-open", "nautilus", "dolphin", "thunar", "pcmanfm"]
            opened = False
            for fm in file_managers:
                if shutil.which(fm):
                    subprocess.run([fm, path])
                    opened = True
                    break
            if not opened:
                print(f"[INFO] No file manager found. Project created at: {path}")
    except Exception as e:
        print(f"[ERROR] Could not open folder: {e}")
        print(f"Project created at: {path}")

def setup_python_venv(backend_path, packages):
    """Optimized Python venv setup"""
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    print("[INFO] Creating Python virtual environment...")
    if not run_cmd(f"{python_cmd} -m venv venv", cwd=backend_path):
        return False
    
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\python -m pip install --upgrade pip"
        install_cmd = f"venv\\Scripts\\python -m pip install {' '.join(packages)}"
    else:
        pip_cmd = "venv/bin/python -m pip install --upgrade pip"
        install_cmd = f"venv/bin/python -m pip install {' '.join(packages)}"
    
    print("[INFO] Upgrading pip...")
    run_cmd(pip_cmd, cwd=backend_path)
    
    print("[INFO] Installing Python packages...")
    run_cmd(install_cmd, cwd=backend_path, show_output=True)
    
    # Create requirements.txt
    with open(os.path.join(backend_path, "requirements.txt"), "w") as f:
        f.write("\n".join(packages))
    
    return True

def setup_npm_project(path, packages, silent=True):
    """Optimized NPM setup"""
    print(f"[INFO] Initializing npm project in {os.path.basename(path)}...")
    
    # Use --silent flag and skip optional dependencies for speed
    init_cmd = "npm init -y"
    if not run_cmd(init_cmd, cwd=path, show_output=not silent):
        return False
    
    if packages:
        # Install packages with optimizations, but show output for debugging
        install_cmd = f"npm install {' '.join(packages)} --no-audit --no-fund"
        print(f"[INFO] Installing packages: {', '.join(packages)}")
        return run_cmd(install_cmd, cwd=path, show_output=True)
    
    return True

def setup_vite_project(project_path, template, folder_name="frontend"):
    """Optimized Vite project setup with Tailwind CSS"""
    print(f"[INFO] Creating Vite {template} project...")
    
    # Use --silent flag and skip git init
    vite_cmd = f"npm create vite@latest {folder_name} -- --template {template}"
    
    if run_cmd(vite_cmd, cwd=project_path, show_output=True):
        frontend_path = os.path.join(project_path, folder_name)
        
        # Ensure package.json exists before proceeding
        if not os.path.exists(os.path.join(frontend_path, "package.json")):
            print("[ERROR] Vite project creation failed - no package.json found")
            return False
            
        print("[INFO] Installing frontend dependencies...")
        
        # Install base dependencies (remove --silent to see any errors)
        install_cmd = "npm install --no-audit --no-fund --prefer-offline"
        if not run_cmd(install_cmd, cwd=frontend_path, show_output=True):
            print("[ERROR] Failed to install base dependencies")
            # Try without --prefer-offline as fallback
            print("[INFO] Retrying without --prefer-offline...")
            fallback_cmd = "npm install --no-audit --no-fund"
            if not run_cmd(fallback_cmd, cwd=frontend_path, show_output=True):
                print("[ERROR] Frontend dependency installation failed")
                return False
        
        # Install and configure Tailwind CSS
        print("[INFO] Installing Tailwind CSS...")
        tailwind_cmd = "npm install -D tailwindcss postcss autoprefixer --no-audit --no-fund"
        if not run_cmd(tailwind_cmd, cwd=frontend_path, show_output=True):
            print("[WARNING] Failed to install Tailwind CSS")
            return True  # Continue without Tailwind
        
        # Initialize Tailwind config
        print("[INFO] Configuring Tailwind CSS...")
        if not run_cmd("npx tailwindcss init -p", cwd=frontend_path, show_output=False):
            print("[WARNING] Failed to initialize Tailwind config, creating manually...")
            # Create config files manually as fallback
            write_file(os.path.join(frontend_path, "tailwind.config.js"), '''/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}''')
            write_file(os.path.join(frontend_path, "postcss.config.js"), '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''')
        
        # Configure Tailwind CSS for the specific template
        setup_tailwind_config(frontend_path, template)
        return True
    
    return False

def create_rust_project(project_path, dependencies=None):
    """Optimized Rust project creation"""
    print("[INFO] Creating Rust project...")
    
    if not run_cmd("cargo new backend --bin", cwd=project_path):
        return False
    
    if dependencies:
        backend_path = os.path.join(project_path, "backend")
        cargo_toml = os.path.join(backend_path, "Cargo.toml")
        
        with open(cargo_toml, "a") as f:
            f.write(f'\n[dependencies]\n{dependencies}')
    
    return True

def setup_tailwind_config(frontend_path, template):
    """Configure Tailwind CSS for different Vite templates"""
    
    # Update tailwind.config.js with proper content paths
    tailwind_config = {
        "react": '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}''',
        "vue": '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}''',
        "svelte": '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{svelte,js,ts}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}'''
    }
    
    # Write the appropriate tailwind config
    config = tailwind_config.get(template, tailwind_config["react"])
    write_file(os.path.join(frontend_path, "tailwind.config.js"), config)
    
    # Add Tailwind directives to CSS file
    tailwind_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;'''
    
    # Different CSS file locations for different templates
    css_paths = {
        "react": "src/index.css",
        "vue": "src/style.css",
        "svelte": "src/lib/index.css"  # Svelte might vary
    }
    
    css_path = css_paths.get(template, "src/index.css")
    full_css_path = os.path.join(frontend_path, css_path)
    
    # For Svelte, we might need to create the lib directory
    if template == "svelte":
        lib_dir = os.path.join(frontend_path, "src", "lib")
        os.makedirs(lib_dir, exist_ok=True)
        # Also update the main CSS import in App.svelte
        app_svelte_path = os.path.join(frontend_path, "src", "App.svelte")
        if os.path.exists(app_svelte_path):
            try:
                with open(app_svelte_path, "r") as f:
                    content = f.read()
                # Replace the default CSS import with Tailwind
                content = content.replace('./app.css', './lib/index.css')
                write_file(app_svelte_path, content)
            except:
                # If replacement fails, just create the CSS file
                pass
    
    # Write Tailwind CSS directives
    write_file(full_css_path, tailwind_css)
    
    # Add some example Tailwind classes to demonstrate it's working
    create_tailwind_example(frontend_path, template)

def create_tailwind_example(frontend_path, template):
    """Add example Tailwind classes to show it's working"""
    
    if template == "react":
        # Update App.jsx with Tailwind example
        app_jsx_path = os.path.join(frontend_path, "src", "App.jsx")
        if os.path.exists(app_jsx_path):
            app_content = '''import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './index.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
        <div className="flex justify-center space-x-4 mb-6">
          <a href="https://vitejs.dev" target="_blank" rel="noopener noreferrer">
            <img src={viteLogo} className="w-16 h-16 hover:drop-shadow-lg transition-all duration-300" alt="Vite logo" />
          </a>
          <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
            <img src={reactLogo} className="w-16 h-16 hover:drop-shadow-lg transition-all duration-300 animate-spin-slow" alt="React logo" />
          </a>
        </div>
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Vite + React + Tailwind</h1>
        <div className="mb-6">
          <button 
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 transform hover:scale-105"
            onClick={() => setCount((count) => count + 1)}
          >
            Count is {count}
          </button>
        </div>
        <p className="text-gray-600 mb-4">
          Edit <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">src/App.jsx</code> and save to test HMR
        </p>
        <p className="text-sm text-gray-500">
          Tailwind CSS is configured and ready to use! 🎨
        </p>
      </div>
    </div>
  )
}

export default App'''
            write_file(app_jsx_path, app_content)
    
    elif template == "vue":
        # Update App.vue with Tailwind example
        app_vue_path = os.path.join(frontend_path, "src", "App.vue")
        if os.path.exists(app_vue_path):
            app_content = '''<script setup>
import { ref } from 'vue'
import HelloWorld from './components/HelloWorld.vue'

const count = ref(0)
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
      <div class="flex justify-center space-x-4 mb-6">
        <a href="https://vitejs.dev" target="_blank" rel="noopener noreferrer">
          <img src="/vite.svg" class="w-16 h-16 hover:drop-shadow-lg transition-all duration-300" alt="Vite logo" />
        </a>
        <a href="https://vuejs.org/" target="_blank" rel="noopener noreferrer">
          <img src="./assets/vue.svg" class="w-16 h-16 hover:drop-shadow-lg transition-all duration-300" alt="Vue logo" />
        </a>
      </div>
      <h1 class="text-3xl font-bold text-gray-800 mb-6">Vite + Vue + Tailwind</h1>
      <div class="mb-6">
        <button 
          class="bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 transform hover:scale-105"
          @click="count++"
        >
          Count is {{ count }}
        </button>
      </div>
      <p class="text-gray-600 mb-4">
        Edit <code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">src/App.vue</code> and save to test HMR
      </p>
      <p class="text-sm text-gray-500">
        Tailwind CSS is configured and ready to use! 🎨
      </p>
    </div>
  </div>
</template>

<style scoped>
/* Component-specific styles can go here */
</style>'''
            write_file(app_vue_path, app_content)
    
    elif template == "svelte":
        # Update App.svelte with Tailwind example
        app_svelte_path = os.path.join(frontend_path, "src", "App.svelte")
        if os.path.exists(app_svelte_path):
            app_content = '''<script>
  import svelteLogo from './assets/svelte.svg'
  import Counter from './lib/Counter.svelte'
  let count = 0
</script>

<main class="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
  <div class="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
    <div class="flex justify-center space-x-4 mb-6">
      <a href="https://vitejs.dev" target="_blank" rel="noopener noreferrer">
        <img src="/vite.svg" class="w-16 h-16 hover:drop-shadow-lg transition-all duration-300" alt="Vite logo" />
      </a>
      <a href="https://svelte.dev" target="_blank" rel="noopener noreferrer">
        <img src={svelteLogo} class="w-16 h-16 hover:drop-shadow-lg transition-all duration-300" alt="Svelte Logo" />
      </a>
    </div>

    <h1 class="text-3xl font-bold text-gray-800 mb-6">Vite + Svelte + Tailwind</h1>

    <div class="mb-6">
      <button 
        class="bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 transform hover:scale-105"
        on:click={() => count += 1}
      >
        Count is {count}
      </button>
    </div>

    <p class="text-gray-600 mb-4">
      Edit <code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">src/App.svelte</code> and save to test HMR
    </p>
    
    <p class="text-sm text-gray-500">
      Tailwind CSS is configured and ready to use! 🎨
    </p>
  </div>
</main>'''
            write_file(app_svelte_path, app_content)

def write_file(path, content):
    """Write file with error handling"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write {path}: {e}")
        return False
    """Write file with error handling"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to write {path}: {e}")
        return False

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
        content += f"- **Frontend**: {frontend}"
        if frontend in ["Vite + React", "Vue", "Svelte"]:
            content += " (with Tailwind CSS v3)"
        content += f"\n- **Backend**: {backend}\n"
    elif frontend != "None":
        content += f"- **Frontend**: {frontend}"
        if frontend in ["Vite + React", "Vue", "Svelte"]:
            content += " (with Tailwind CSS v3)"
        content += "\n"
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
        if frontend in ["Vite + React", "Vue", "Svelte"]:
            content += '\n**Tailwind CSS is pre-configured!** You can start using Tailwind utility classes immediately.\n'
    
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
    """Setup frontend with optimizations"""
    if frontend == "Vite + React":
        return setup_vite_project(project_path, "react")
    elif frontend == "Vue":
        return setup_vite_project(project_path, "vue")
    elif frontend == "Angular":
        print("[INFO] Creating Angular project...")
        # Use --skip-install to speed up initial creation, then install separately
        cmd = "npx -p @angular/cli ng new frontend --skip-git --skip-install --routing --style=css --package-manager=npm"
        if run_cmd(cmd, cwd=project_path, show_output=True):
            frontend_path = os.path.join(project_path, "frontend")
            print("[INFO] Installing Angular dependencies...")
            return run_cmd("npm install --silent --no-audit --no-fund", cwd=frontend_path, show_output=True)
        return False
    elif frontend == "Svelte":
        return setup_vite_project(project_path, "svelte")
    return True

def setup_backend(project_path, backend):
    """Setup backend with optimizations"""
    backend_path = os.path.join(project_path, "backend")
    
    if backend == "Express":
        os.makedirs(backend_path, exist_ok=True)
        if not setup_npm_project(backend_path, ["express", "cors", "dotenv"]):
            return False
            
        server_content = """const express = require('express');
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
"""
        return write_file(os.path.join(backend_path, "server.js"), server_content)
    
    elif backend == "FastAPI":
        os.makedirs(backend_path, exist_ok=True)
        if not setup_python_venv(backend_path, ["fastapi", "uvicorn[standard]"]):
            return False
            
        main_content = """from fastapi import FastAPI
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
"""
        return write_file(os.path.join(backend_path, "main.py"), main_content)
    
    elif backend == "Flask":
        os.makedirs(backend_path, exist_ok=True)
        if not setup_python_venv(backend_path, ["flask", "flask-cors"]):
            return False
            
        app_content = """from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Flask backend running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"""
        return write_file(os.path.join(backend_path, "app.py"), app_content)
    
    elif backend == "Django":
        os.makedirs(backend_path, exist_ok=True)
        if not setup_python_venv(backend_path, ["django", "djangorestframework", "django-cors-headers"]):
            return False
            
        print("[INFO] Creating Django project...")
        activate_cmd = "venv\\Scripts\\python" if platform.system() == "Windows" else "venv/bin/python"
        django_cmd = f"{activate_cmd} -m django startproject backend_app ."
        return run_cmd(django_cmd, cwd=backend_path, show_output=True)
    
    elif backend == "Rocket":
        if not create_rust_project(project_path, 'rocket = "0.5"'):
            return False
            
        main_content = """#[macro_use] extern crate rocket;

#[get("/")]
fn index() -> &'static str {
    "Rocket backend running!"
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/", routes![index])
}
"""
        return write_file(os.path.join(project_path, "backend", "src", "main.rs"), main_content)
    
    elif backend == "Actix":
        if not create_rust_project(project_path, 'actix-web = "4"'):
            return False
            
        main_content = """use actix_web::{web, App, HttpResponse, HttpServer, Result};

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
"""
        return write_file(os.path.join(project_path, "backend", "src", "main.rs"), main_content)
    
    elif backend == "Basic HTTP Server":
        os.makedirs(backend_path, exist_ok=True)
        main_content = """package main

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
"""
        return write_file(os.path.join(backend_path, "main.go"), main_content)
    
    elif backend == "ASP.NET Core WebAPI":
        print("[INFO] Creating ASP.NET Core WebAPI project...")
        return run_cmd("dotnet new webapi -n backend", cwd=project_path, show_output=True)
    
    return True

def create_start_script(project_path, frontend, backend):
    is_windows = platform.system() == "Windows"
    script_name = "start.bat" if is_windows else "start.sh"
    script_path = os.path.join(project_path, script_name)
    
    commands = []
    
    if is_windows:
        commands.append("@echo off")
        commands.append("echo Starting development servers...")
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
        commands.append("echo \"Starting development servers...\"")
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
    
    # Quick dependency check
    check_dependencies()
    
    # Get project details
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("[ERROR] Project name cannot be empty")
        sys.exit(1)
    
    save_path = input("Enter directory to save project (default: current dir): ").strip() or os.getcwd()
    project_path = os.path.join(save_path, project_name)
    
    # Handle existing directory
    if os.path.exists(project_path):
        overwrite = inquirer.list_input(f"Directory {project_path} already exists. Overwrite?", choices=["Yes", "No"])
        if overwrite == "No":
            sys.exit(0)
        print("[INFO] Removing existing directory...")
        shutil.rmtree(project_path)
    
    # Create project directory
    os.makedirs(project_path, exist_ok=True)

    # Get user choices
    language = inquirer.list_input("Choose primary language", choices=["JavaScript", "Python", "Rust", "Go", "C#"])
    structure = inquirer.list_input("Project type", choices=get_structure_choices(language))

    frontend = backend = "None"
    
    if structure in ["Fullstack", "Frontend only"]:
        frontend = inquirer.list_input("Choose frontend framework", choices=get_frontend_choices(language))
    
    if structure in ["Fullstack", "Backend only"]:
        backend = inquirer.list_input("Choose backend framework", choices=get_backend_choices(language))

    # Check language dependencies
    if not check_language_dependencies(language, backend):
        sys.exit(1)

    # GitHub setup
    gh_available = shutil.which("gh") is not None
    if gh_available:
        visibility = inquirer.list_input("GitHub repository visibility", choices=["Public", "Private", "Skip"])
    else:
        print("[INFO] GitHub CLI not found. Skipping repository creation.")
        visibility = "Skip"

    print(f"\n[INFO] Creating {structure} project at {project_path}")
    print("[INFO] This may take a few minutes for package installations...")

    # Initialize git early and make initial commit
    print("[INFO] Initializing git repository...")
    run_cmd("git init", cwd=project_path)
    
    # Setup components with better error handling
    try:
        # Setup frontend and backend in parallel where possible
        tasks = []
        
        if frontend != "None":
            print(f"\n=== Setting up {frontend} frontend ===")
            if not setup_frontend(project_path, frontend):
                print(f"[WARNING] Frontend setup failed, continuing...")
        
        if backend != "None":
            print(f"\n=== Setting up {backend} backend ===")
            if not setup_backend(project_path, backend):
                print(f"[WARNING] Backend setup failed, continuing...")

        # Create project files
        print("\n=== Creating project files ===")
        create_start_script(project_path, frontend, backend)
        create_gitignore(project_path, frontend, backend, language)
        create_readme(project_path, project_name, frontend, backend, language)

        # Make initial git commit
        print("[INFO] Making initial commit...")
        run_cmd("git add .", cwd=project_path)
        run_cmd('git commit -m "Initial commit: Project scaffolding"', cwd=project_path)

        # GitHub repository creation
        if visibility != "Skip":
            print("\n=== Creating GitHub repository ===")
            visibility_flag = "--public" if visibility == "Public" else "--private"
            success = run_cmd(f"gh repo create {project_name} {visibility_flag} --source . --remote=origin --push", 
                            cwd=project_path, show_output=True)
            if not success:
                print("[WARNING] Failed to create GitHub repository. You can create it manually later.")

        # Final steps
        open_answer = inquirer.list_input("\nOpen project folder now?", choices=["Yes", "No"])
        if open_answer == "Yes":
            open_project_folder(project_path)

        script_ext = ".bat" if platform.system() == "Windows" else ".sh"
        print(f"\n[SUCCESS] Project {project_name} setup complete!")
        print(f"Location: {project_path}")
        print(f"To start your project, run: .{os.sep}start{script_ext}")
        
    except KeyboardInterrupt:
        print("\n[INFO] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()