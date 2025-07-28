#!/usr/bin/env python3

import requests
import json
import base64
import subprocess
import sys
import os

# API Keys
GITHUB_TOKEN = "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"
RENDER_TOKEN = "rnd_p0Kk032YnqPg9tSjmWzEEoXiY7dL"
NETLIFY_TOKEN = "nfp_JFEj2Lm5vu14dpatfWzKcZRtduEarCbpd6b5"

def get_repo_info():
    """Get GitHub repository info"""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                               capture_output=True, text=True, cwd='/app')
        
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            
            # Parse different URL formats
            if 'github.com' in remote_url:
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
        print(f"Error getting repo info: {e}")
        return None, None

def commit_and_push_changes():
    """Commit and push all changes to GitHub"""
    try:
        os.chdir('/app')
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit changes
        commit_message = "Fix: Resolve OpenAI model and CORS issues - ChatDev Web repairs"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push changes
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✅ Successfully pushed changes to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in git operations: {e}")
        return False

def trigger_render_redeploy():
    """Force trigger Render redeploy"""
    try:
        # First, get all services
        headers = {
            'Authorization': f'Bearer {RENDER_TOKEN}',
            'Accept': 'application/json'
        }
        
        response = requests.get('https://api.render.com/v1/services', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get Render services: {response.status_code}")
            return False
        
        services = response.json()
        backend_service = None
        
        for service in services:
            if 'ai-coding' in service.get('name', '').lower():
                backend_service = service
                break
        
        if not backend_service:
            print("❌ Could not find backend service on Render")
            return False
        
        service_id = backend_service['id']
        print(f"🎯 Found backend service: {backend_service['name']} ({service_id})")
        
        # Trigger redeploy
        deploy_url = f'https://api.render.com/v1/services/{service_id}/deploys'
        response = requests.post(deploy_url, headers=headers)
        
        if response.status_code == 201:
            deploy_info = response.json()
            print(f"✅ Triggered Render redeploy: {deploy_info.get('id')}")
            return True
        else:
            print(f"❌ Failed to trigger Render redeploy: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering Render redeploy: {e}")
        return False

def trigger_netlify_redeploy():
    """Force trigger Netlify redeploy"""
    try:
        # Get all sites
        headers = {
            'Authorization': f'Bearer {NETLIFY_TOKEN}',
            'Accept': 'application/json'
        }
        
        response = requests.get('https://api.netlify.com/api/v1/sites', headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get Netlify sites: {response.status_code}")
            return False
        
        sites = response.json()
        frontend_site = None
        
        for site in sites:
            if 'kodix' in site.get('name', '').lower():
                frontend_site = site
                break
        
        if not frontend_site:
            print("❌ Could not find frontend site on Netlify")
            return False
        
        site_id = frontend_site['id']
        print(f"🎯 Found frontend site: {frontend_site['name']} ({site_id})")
        
        # Trigger redeploy
        deploy_url = f'https://api.netlify.com/api/v1/sites/{site_id}/deploys'
        response = requests.post(deploy_url, headers=headers)
        
        if response.status_code == 201:
            deploy_info = response.json()
            print(f"✅ Triggered Netlify redeploy: {deploy_info.get('id')}")
            return True
        else:
            print(f"❌ Failed to trigger Netlify redeploy: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering Netlify redeploy: {e}")
        return False

def main():
    print("🚀 Starting force deployment process...\n")
    
    # Get repository info
    owner, repo = get_repo_info()
    if owner and repo:
        print(f"📁 Repository: {owner}/{repo}")
    else:
        print("⚠️  Could not determine repository info")
    
    # Step 1: Commit and push changes
    print("\n📤 Committing and pushing changes to GitHub...")
    if not commit_and_push_changes():
        print("❌ Failed to push changes to GitHub")
        return 1
    
    # Step 2: Trigger Render redeploy
    print("\n🚀 Triggering Render backend redeploy...")
    if not trigger_render_redeploy():
        print("❌ Failed to trigger Render redeploy")
        return 1
    
    # Step 3: Trigger Netlify redeploy
    print("\n🚀 Triggering Netlify frontend redeploy...")
    if not trigger_netlify_redeploy():
        print("❌ Failed to trigger Netlify redeploy")
        return 1
    
    print("\n🎉 All deployments triggered successfully!")
    print("\n⏳ Deployment process initiated. Please wait 2-3 minutes for:")
    print("   - Render backend: https://ai-coding-51ss.onrender.com")
    print("   - Netlify frontend: https://kodix.netlify.app")
    print("\nAfter deployment, test the application again.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())