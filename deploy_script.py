#!/usr/bin/env python3

import requests
import json
import base64
import os
import sys
from datetime import datetime

# API tokens from user
GITHUB_TOKEN = "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"
RENDER_TOKEN = "rnd_p0Kk032YnqPg9tSjmWzEEoXiY7dL"
NETLIFY_TOKEN = "nfp_JFEj2Lm5vu14dpatfWzKcZRtduEarCbpd6b5"

# Repository details (need to determine from current git setup)
GITHUB_OWNER = "your-username"  # Need to get this
GITHUB_REPO = "your-repo"  # Need to get this
RENDER_SERVICE_ID = "srv-your-service"  # Need to get this from Render
NETLIFY_SITE_ID = "your-site-id"  # Need to get this from Netlify

def get_git_info():
    """Get git repository information"""
    try:
        import subprocess
        
        # Get remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                               capture_output=True, text=True, cwd='/app')
        
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            print(f"Git remote URL: {remote_url}")
            
            # Parse GitHub URL
            if 'github.com' in remote_url:
                # Extract owner and repo from URL
                if remote_url.startswith('https://github.com/'):
                    parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
                elif remote_url.startswith('git@github.com:'):
                    parts = remote_url.replace('git@github.com:', '').replace('.git', '').split('/')
                else:
                    return None, None
                
                if len(parts) >= 2:
                    return parts[0], parts[1]
        
        return None, None
        
    except Exception as e:
        print(f"Error getting git info: {e}")
        return None, None

def push_file_to_github(owner, repo, file_path, content, commit_message):
    """Push a file to GitHub repository"""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get current file SHA if it exists (for updates)
        get_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
        get_response = requests.get(get_url, headers=headers)
        
        # Encode content to base64
        base64_content = base64.b64encode(content.encode()).decode()
        
        # Prepare request data
        data = {
            'message': commit_message,
            'content': base64_content,
            'branch': 'main'
        }
        
        # If file exists, include SHA for update
        if get_response.status_code == 200:
            data['sha'] = get_response.json()['sha']
        
        # Push the file
        response = requests.put(get_url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"✅ Successfully pushed {file_path} to GitHub")
            return True
        else:
            print(f"❌ Failed to push {file_path}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error pushing {file_path}: {e}")
        return False

def trigger_render_deploy(service_id=None):
    """Trigger a deployment on Render"""
    try:
        # If no service ID provided, try to find it
        if not service_id:
            # List services to find ours
            headers = {
                'Authorization': f'Bearer {RENDER_TOKEN}',
                'Accept': 'application/json'
            }
            
            response = requests.get('https://api.render.com/v1/services', headers=headers)
            
            if response.status_code == 200:
                services = response.json()
                for service in services:
                    if 'ai-coding' in service.get('name', ''):
                        service_id = service['id']
                        break
        
        if not service_id:
            print("❌ Could not find Render service ID")
            return False
        
        # Trigger deploy
        headers = {
            'Authorization': f'Bearer {RENDER_TOKEN}',
            'Accept': 'application/json'
        }
        
        deploy_url = f'https://api.render.com/v1/services/{service_id}/deploys'
        response = requests.post(deploy_url, headers=headers)
        
        if response.status_code == 201:
            print("✅ Successfully triggered Render deployment")
            return True
        else:
            print(f"❌ Failed to trigger Render deploy: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering Render deploy: {e}")
        return False

def trigger_netlify_deploy(site_id=None):
    """Trigger a deployment on Netlify"""
    try:
        # If no site ID provided, try to find it
        if not site_id:
            headers = {
                'Authorization': f'Bearer {NETLIFY_TOKEN}',
                'Accept': 'application/json'
            }
            
            response = requests.get('https://api.netlify.com/api/v1/sites', headers=headers)
            
            if response.status_code == 200:
                sites = response.json()
                for site in sites:
                    if 'kodix' in site.get('name', ''):
                        site_id = site['id']
                        break
        
        if not site_id:
            print("❌ Could not find Netlify site ID")
            return False
        
        # Trigger deploy
        headers = {
            'Authorization': f'Bearer {NETLIFY_TOKEN}',
            'Accept': 'application/json'
        }
        
        deploy_url = f'https://api.netlify.com/api/v1/sites/{site_id}/deploys'
        response = requests.post(deploy_url, headers=headers)
        
        if response.status_code == 201:
            print("✅ Successfully triggered Netlify deployment")
            return True
        else:
            print(f"❌ Failed to trigger Netlify deploy: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering Netlify deploy: {e}")
        return False

def main():
    print("🚀 Starting deployment process...\n")
    
    # Get git repository info
    owner, repo = get_git_info()
    if not owner or not repo:
        print("❌ Could not determine GitHub repository information")
        return 1
    
    print(f"📁 GitHub repository: {owner}/{repo}")
    
    # Read and push backend files
    print("\n📤 Pushing backend files to GitHub...")
    
    try:
        # Push server.py
        with open('/app/backend/server.py', 'r') as f:
            server_content = f.read()
        
        if not push_file_to_github(owner, repo, 'backend/server.py', server_content, 
                                  'Fix: Updated server.py with corrected model names and improved error handling'):
            return 1
        
        # Push requirements.txt
        with open('/app/backend/requirements.txt', 'r') as f:
            requirements_content = f.read()
        
        if not push_file_to_github(owner, repo, 'backend/requirements.txt', requirements_content, 
                                  'Update: Backend requirements'):
            return 1
        
        # Push frontend files
        print("\n📤 Pushing frontend files to GitHub...")
        
        # Push ChatInterface.jsx
        with open('/app/frontend/src/pages/ChatInterface.jsx', 'r') as f:
            chat_content = f.read()
        
        if not push_file_to_github(owner, repo, 'frontend/src/pages/ChatInterface.jsx', chat_content, 
                                  'Fix: Updated ChatInterface with improved model mapping'):
            return 1
        
        # Push api.js
        with open('/app/frontend/src/utils/api.js', 'r') as f:
            api_content = f.read()
        
        if not push_file_to_github(owner, repo, 'frontend/src/utils/api.js', api_content, 
                                  'Fix: Updated API utility with better error handling'):
            return 1
        
    except Exception as e:
        print(f"❌ Error reading files: {e}")
        return 1
    
    # Trigger deployments
    print("\n🚀 Triggering deployments...")
    
    # Trigger Render deployment
    if not trigger_render_deploy():
        print("⚠️  Render deployment failed, but continuing...")
    
    # Trigger Netlify deployment
    if not trigger_netlify_deploy():
        print("⚠️  Netlify deployment failed, but continuing...")
    
    print("\n🎉 Deployment process completed!")
    print("\n📝 Next steps:")
    print("1. Check Render logs: https://dashboard.render.com/")
    print("2. Check Netlify logs: https://app.netlify.com/")
    print("3. Test the application at: https://kodix.netlify.app/")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())