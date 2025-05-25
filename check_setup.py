"""
Utility script to check the setup and configuration of the Resume Analysis API
"""
import os
import sys
import importlib.metadata
import requests
import pkg_resources

def check_openai_api_key():
    """Validate OpenAI API key"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        print("❌ OpenAI API key not found or not set properly")
        print("   Please set a valid OPENAI_API_KEY in your .env file")
        return False
    
    print("✅ OpenAI API key found")
    
    # Test key validity with a simple request (optional)
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list(limit=1)
        print("✅ OpenAI API key is valid")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key might not be valid: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed and versions are compatible"""
    required_packages = {
        "fastapi": ">=0.103.1",
        "uvicorn": ">=0.23.2",
        "pydantic": ">=2.4.2",
        "langchain": ">=0.0.267",
        "langgraph": ">=0.0.20",  # Updated requirement
        "openai": ">=1.2.0"
    }
    
    all_ok = True
    
    for package, version_req in required_packages.items():
        try:
            installed_version = importlib.metadata.version(package)
            print(f"✅ {package} {installed_version} installed")
            
            # Check version compatibility
            try:
                requirement = pkg_resources.Requirement.parse(f"{package}{version_req}")
                if pkg_resources.parse_version(installed_version) not in requirement:
                    print(f"⚠️ Version mismatch: {package} {installed_version} does not meet requirement {version_req}")
                    all_ok = False
            except Exception as e:
                print(f"⚠️ Cannot check version compatibility for {package}: {e}")
            
        except importlib.metadata.PackageNotFoundError:
            print(f"❌ {package} not installed")
            all_ok = False
    
    return all_ok

def check_langgraph_compatibility():
    """Check specifically for langgraph compatibility"""
    try:
        import langgraph
        from langgraph.graph import StateGraph, END, START
        
        # Try creating a simple StateGraph
        try:
            from typing import TypedDict
            
            class TestState(TypedDict):
                value: str
            
            # Test if we can create a graph with schema
            graph = StateGraph(state_schema=TestState)
            
            # Test newer API
            graph.add_node("start", lambda x: x)
            graph.add_node("end", lambda x: x)
            
            # Test START and END connections
            graph.add_edge(START, "start")
            graph.add_edge("start", "end")
            graph.add_edge("end", END)
            
            # Try compiling
            compiled = graph.compile()
            
            print("✅ LangGraph version is compatible with our code")
            return True
        except TypeError as e:
            if "got an unexpected keyword argument" in str(e):
                print("❌ LangGraph version incompatible - unexpected keyword argument")
            elif "missing a required argument" in str(e):
                print("❌ LangGraph version incompatible - missing required argument")
            else:
                print(f"❌ LangGraph version incompatible: {e}")
            return False
        except AttributeError as e:
            if "has no attribute 'set_finish_node'" in str(e):
                print("❌ LangGraph version incompatible - API changed, use add_edge(node, END) instead of set_finish_node")
            else:
                print(f"❌ LangGraph version incompatible API: {e}")
            return False
        except ValueError as e:
            if "Graph must have an entrypoint" in str(e):
                print("❌ LangGraph version requires START connection - use workflow.add_edge(START, 'start_node')")
            else:
                print(f"❌ LangGraph configuration error: {e}")
            return False
    except ImportError:
        print("❌ LangGraph not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking LangGraph compatibility: {e}")
        return False

def check_folder_structure():
    """Check if all required folders and files exist"""
    required_paths = [
        "app/api/v1/endpoints.py",
        "app/core/config.py",
        "app/graph/builder.py",
        "app/models/resume.py",
        "app/models/response.py",
        "app/services/llm_utils.py",
        "app/main.py"
    ]
    
    all_ok = True
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✅ Found {path}")
        else:
            print(f"❌ Missing {path}")
            all_ok = False
    
    return all_ok

def check_api_connection():
    """Try to connect to the API if it's running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is running and health check passed")
            return True
        else:
            print(f"❌ API health check failed with status code {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Start it with: python -m app.main")
        return False
    except Exception as e:
        print(f"❌ Error checking API connection: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Resume Analysis API setup...")
    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n📊 Checking LangGraph compatibility...")
    langgraph_ok = check_langgraph_compatibility()
    
    print("\n📂 Checking folder structure...")
    structure_ok = check_folder_structure()
    
    print("\n🔑 Checking OpenAI API key...")
    key_ok = check_openai_api_key()
    
    print("\n🌐 Checking API connection...")
    try:
        api_ok = check_api_connection()
    except:
        print("❌ API connection check failed")
        api_ok = False
    
    print("\n📋 Summary:")
    if all([deps_ok, structure_ok, key_ok, api_ok, langgraph_ok]):
        print("✅ All checks passed! The setup appears to be working correctly.")
    else:
        print("⚠️ Some checks failed. Please address the issues mentioned above.")
