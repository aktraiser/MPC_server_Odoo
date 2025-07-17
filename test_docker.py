#!/usr/bin/env python3
"""
Test Docker deployment for Odoo MCP Server
"""
import subprocess
import sys
import time
import requests
import os

def run_command(cmd, capture_output=True):
    """Run a shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_docker_build():
    """Test Docker image build"""
    print("🧪 Testing Docker build...")
    
    success, stdout, stderr = run_command("docker build -t odoo-mcp-server .")
    
    if success:
        print("✅ Docker build successful")
        return True
    else:
        print(f"❌ Docker build failed: {stderr}")
        return False

def test_docker_run():
    """Test Docker container run"""
    print("\n🧪 Testing Docker run...")
    
    # Stop any existing container
    run_command("docker stop odoo-mcp-test 2>/dev/null", capture_output=False)
    run_command("docker rm odoo-mcp-test 2>/dev/null", capture_output=False)
    
    # Run container in background
    cmd = """docker run -d --name odoo-mcp-test \
        -e ODOO_URL=https://demo.odoo.com \
        -e ODOO_DATABASE=demo \
        -e ODOO_USERNAME=admin \
        -e ODOO_PASSWORD=admin \
        -p 8001:8000 \
        odoo-mcp-server"""
    
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Docker container started")
        return True
    else:
        print(f"❌ Docker run failed: {stderr}")
        return False

def test_container_health():
    """Test container health"""
    print("\n🧪 Testing container health...")
    
    # Wait for container to start
    print("⏳ Waiting for container to start...")
    time.sleep(10)
    
    # Check if container is running
    success, stdout, stderr = run_command("docker ps | grep odoo-mcp-test")
    
    if success:
        print("✅ Container is running")
        
        # Check logs
        success, logs, _ = run_command("docker logs odoo-mcp-test")
        if "error" not in logs.lower() and "exception" not in logs.lower():
            print("✅ No errors in container logs")
            return True
        else:
            print(f"⚠️  Container logs show potential issues:\n{logs}")
            return False
    else:
        print("❌ Container is not running")
        return False

def cleanup():
    """Cleanup test containers"""
    print("\n🧹 Cleaning up...")
    run_command("docker stop odoo-mcp-test 2>/dev/null", capture_output=False)
    run_command("docker rm odoo-mcp-test 2>/dev/null", capture_output=False)
    print("✅ Cleanup completed")

def test_docker_compose():
    """Test docker-compose configuration"""
    print("\n🧪 Testing docker-compose...")
    
    # Check if docker-compose.yml is valid
    success, stdout, stderr = run_command("docker-compose config")
    
    if success:
        print("✅ docker-compose.yml is valid")
        return True
    else:
        print(f"❌ docker-compose.yml validation failed: {stderr}")
        return False

def main():
    """Run all Docker tests"""
    print("🚀 Starting Docker Tests for Odoo MCP Server\n")
    
    # Check if Docker is available
    success, _, _ = run_command("docker --version")
    if not success:
        print("❌ Docker is not available. Please install Docker first.")
        return 1
    
    tests = [
        ("Docker Build", test_docker_build),
        ("Docker Run", test_docker_run),
        ("Container Health", test_container_health),
        ("Docker Compose", test_docker_compose)
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            print(f"\n{'='*50}")
            print(f"Running: {test_name}")
            print('='*50)
            
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
    
    finally:
        cleanup()
    
    print(f"\n{'='*50}")
    print("📊 DOCKER TEST RESULTS")
    print('='*50)
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All Docker tests passed!")
        print("✅ The Docker configuration is ready for Render deployment!")
        print("\n📋 Render Deployment Steps:")
        print("1. Push your code to GitHub")
        print("2. Connect repository to Render")
        print("3. Render will automatically detect Dockerfile")
        print("4. Set environment variables in Render dashboard")
        print("5. Deploy!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} Docker test(s) failed.")
        print("Please fix the issues before deploying to Render.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)