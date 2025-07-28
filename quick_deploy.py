#!/usr/bin/env python3

import requests
import json

# API tokens
RENDER_TOKEN = "rnd_p0Kk032YnqPg9tSjmWzEEoXiY7dL"

def find_render_service():
    """Find our Render service"""
    try:
        headers = {
            'Authorization': f'Bearer {RENDER_TOKEN}',
            'Accept': 'application/json'
        }
        
        response = requests.get('https://api.render.com/v1/services', headers=headers)
        
        if response.status_code == 200:
            services = response.json()
            print(f"Found {len(services)} services:")
            
            for service in services:
                print(f"  - {service.get('name', 'Unknown')}: {service.get('id', 'No ID')}")
                print(f"    URL: {service.get('serviceDetails', {}).get('url', 'No URL')}")
                print(f"    Status: {service.get('status', 'Unknown')}")
                print()
                
                # Check if this is our backend service
                if 'ai-coding' in service.get('name', '').lower():
                    return service['id']
        else:
            print(f"❌ Failed to get services: {response.status_code}")
            print(response.text)
            
        return None
        
    except Exception as e:
        print(f"❌ Error finding services: {e}")
        return None

def trigger_deploy(service_id):
    """Trigger deployment for a service"""
    try:
        headers = {
            'Authorization': f'Bearer {RENDER_TOKEN}',
            'Accept': 'application/json'
        }
        
        deploy_url = f'https://api.render.com/v1/services/{service_id}/deploys'
        response = requests.post(deploy_url, headers=headers)
        
        if response.status_code == 201:
            deploy_data = response.json()
            print("✅ Successfully triggered deployment!")
            print(f"   Deploy ID: {deploy_data.get('id')}")
            print(f"   Status: {deploy_data.get('status')}")
            return True
        else:
            print(f"❌ Failed to trigger deploy: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error triggering deploy: {e}")
        return False

def get_deploy_logs(service_id, deploy_id=None):
    """Get deployment logs"""
    try:
        headers = {
            'Authorization': f'Bearer {RENDER_TOKEN}',
            'Accept': 'application/json'
        }
        
        if deploy_id:
            logs_url = f'https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}/logs'
        else:
            logs_url = f'https://api.render.com/v1/services/{service_id}/logs'
        
        response = requests.get(logs_url, headers=headers)
        
        if response.status_code == 200:
            logs = response.json()
            print("📋 Recent logs:")
            for log in logs[-10:]:  # Show last 10 log entries
                print(f"   {log.get('timestamp', '')}: {log.get('message', '')}")
            return True
        else:
            print(f"❌ Failed to get logs: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return False

def main():
    print("🔍 Finding Render services...\n")
    
    service_id = find_render_service()
    
    if service_id:
        print(f"🎯 Found backend service ID: {service_id}")
        print("\n🚀 Triggering deployment...")
        
        if trigger_deploy(service_id):
            print("\n📋 Getting recent logs...")
            get_deploy_logs(service_id)
        else:
            print("❌ Deployment failed")
    else:
        print("❌ Could not find backend service")

if __name__ == "__main__":
    main()