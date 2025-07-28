#!/usr/bin/env python3

import requests
import time
import json

RENDER_TOKEN = "rnd_p0Kk032YnqPg9tSjmWzEEoXiY7dL"
NETLIFY_TOKEN = "nfp_JFEj2Lm5vu14dpatfWzKcZRtduEarCbpd6b5"
OPENAI_API_KEY = "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"

def monitor_render_deployment():
    """Monitor Render deployment status"""
    try:
        headers = {
            'Authorization': f'Bearer {RENDER_TOKEN}',
            'Accept': 'application/json'
        }
        
        # Get services
        response = requests.get('https://api.render.com/v1/services', headers=headers)
        
        if response.status_code != 200:
            return False, "Could not get services"
        
        services = response.json()
        backend_service = None
        
        for service in services:
            if 'ai-coding' in service.get('name', '').lower():
                backend_service = service
                break
        
        if not backend_service:
            return False, "Backend service not found"
        
        service_id = backend_service['id']
        
        # Get recent deploys
        deploys_url = f'https://api.render.com/v1/services/{service_id}/deploys'
        response = requests.get(deploys_url, headers=headers, params={'limit': 5})
        
        if response.status_code == 200:
            deploys = response.json()
            if deploys:
                latest_deploy = deploys[0]
                status = latest_deploy.get('status', 'unknown')
                created_at = latest_deploy.get('createdAt', 'unknown')
                
                return True, f"Status: {status}, Created: {created_at}"
        
        return False, "Could not get deploy info"
        
    except Exception as e:
        return False, str(e)

def monitor_netlify_deployment():
    """Monitor Netlify deployment status"""
    try:
        headers = {
            'Authorization': f'Bearer {NETLIFY_TOKEN}',
            'Accept': 'application/json'
        }
        
        # Get sites
        response = requests.get('https://api.netlify.com/api/v1/sites', headers=headers)
        
        if response.status_code != 200:
            return False, "Could not get sites"
        
        sites = response.json()
        frontend_site = None
        
        for site in sites:
            if 'kodix' in site.get('name', '').lower():
                frontend_site = site
                break
        
        if not frontend_site:
            return False, "Frontend site not found"
        
        site_id = frontend_site['id']
        
        # Get recent deploys
        deploys_url = f'https://api.netlify.com/api/v1/sites/{site_id}/deploys'
        response = requests.get(deploys_url, headers=headers, params={'per_page': 5})
        
        if response.status_code == 200:
            deploys = response.json()
            if deploys:
                latest_deploy = deploys[0]
                state = latest_deploy.get('state', 'unknown')
                created_at = latest_deploy.get('created_at', 'unknown')
                
                return True, f"State: {state}, Created: {created_at}"
        
        return False, "Could not get deploy info"
        
    except Exception as e:
        return False, str(e)

def test_full_functionality():
    """Test full functionality end-to-end"""
    try:
        print("\n🔄 Testing full functionality...")
        
        # Step 1: Backend health
        response = requests.get("https://ai-coding-51ss.onrender.com/api/health", timeout=10)
        if response.status_code != 200:
            return False, "Backend health check failed"
        
        health_data = response.json()
        print(f"   Backend version: {health_data.get('version', 'unknown')}")
        
        # Step 2: Create session
        session_payload = {
            "task": "Создай простую веб-страницу с заголовком Hello World",
            "project_name": "TestHelloWorld",
            "model_type": "gpt-3.5-turbo",
            "api_key": OPENAI_API_KEY,
            "provider": "openai"
        }
        
        response = requests.post(
            "https://ai-coding-51ss.onrender.com/api/sessions",
            json=session_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            session_data = response.json()
            return True, f"Session created successfully: {session_data.get('session_id')}"
        else:
            return False, f"Session creation failed: {response.status_code} - {response.text}"
        
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 Monitoring deployment status...\n")
    
    max_checks = 20  # Max 10 minutes of monitoring
    check_interval = 30  # 30 seconds between checks
    
    for i in range(max_checks):
        print(f"Check {i+1}/{max_checks}:")
        
        # Check Render deployment
        render_success, render_status = monitor_render_deployment()
        if render_success:
            print(f"   🔧 Render: {render_status}")
        else:
            print(f"   ❌ Render: {render_status}")
        
        # Check Netlify deployment
        netlify_success, netlify_status = monitor_netlify_deployment()
        if netlify_success:
            print(f"   🌐 Netlify: {netlify_status}")
        else:
            print(f"   ❌ Netlify: {netlify_status}")
        
        # Test functionality
        func_success, func_status = test_full_functionality()
        if func_success:
            print(f"   ✅ Functionality: {func_status}")
            print("\n🎉 Deployment successful and fully functional!")
            return 0
        else:
            print(f"   ❌ Functionality: {func_status}")
        
        if i < max_checks - 1:
            print(f"   ⏳ Waiting {check_interval} seconds before next check...\n")
            time.sleep(check_interval)
    
    print("\n⚠️  Deployment monitoring completed. Manual check may be needed.")
    return 1

if __name__ == "__main__":
    main()