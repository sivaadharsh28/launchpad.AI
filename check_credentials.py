#!/usr/bin/env python3
"""
AWS Credentials Checker for LaunchPad.AI
"""

import boto3
import json
from botocore.exceptions import NoCredentialsError, ClientError
import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded .env file")
    else:
        print("⚠️  No .env file found")

def check_credentials():
    """Check if AWS credentials are properly configured"""
    print("🔍 Checking AWS credentials...")
    
    try:
        # Try to create a session and get caller identity
        session = boto3.Session()
        sts_client = session.client('sts')
        
        # This call requires valid credentials
        response = sts_client.get_caller_identity()
        
        print("✅ AWS credentials are valid!")
        print(f"   Account ID: {response['Account']}")
        print(f"   User ARN: {response['Arn']}")
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found!")
        print("\n🔧 How to fix:")
        print("1. Run 'aws configure' to set up credentials")
        print("2. Or set environment variables in .env file")
        print("3. Or export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
        
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_bedrock_access():
    """Check Bedrock model access"""
    print("\n🧠 Checking Bedrock access...")
    
    try:
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        
        # List available models
        response = bedrock_client.list_foundation_models()
        claude_models = [m for m in response['modelSummaries'] if 'claude' in m['modelId'].lower()]
        
        if claude_models:
            print("✅ Bedrock access confirmed!")
            print(f"   Found {len(claude_models)} Claude models")
            return True
        else:
            print("⚠️  No Claude models found - may need to request access")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print("❌ Bedrock access denied!")
            print("🔧 Go to AWS Console → Bedrock → Model access to request access")
        else:
            print(f"❌ Bedrock error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Bedrock check failed: {e}")
        return False

def check_service_permissions():
    """Check permissions for required services"""
    print("\n🔐 Checking service permissions...")
    
    services_to_check = [
        ('DynamoDB', 'dynamodb', 'list_tables'),
        ('S3', 's3', 'list_buckets'),
        ('IAM', 'iam', 'list_users')
    ]
    
    results = {}
    
    for service_name, service_code, test_operation in services_to_check:
        try:
            client = boto3.client(service_code)
            
            if test_operation == 'list_tables':
                client.list_tables()
            elif test_operation == 'list_buckets':
                client.list_buckets()
            elif test_operation == 'list_users':
                client.list_users(MaxItems=1)
            
            print(f"   ✅ {service_name}: Access OK")
            results[service_name] = True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                print(f"   ❌ {service_name}: Access denied")
            else:
                print(f"   ⚠️  {service_name}: {error_code}")
            results[service_name] = False
            
        except Exception as e:
            print(f"   ❌ {service_name}: {e}")
            results[service_name] = False
    
    return results

def show_credential_sources():
    """Show where credentials might be coming from"""
    print("\n📍 Credential sources:")
    
    # Check environment variables
    if os.getenv('AWS_ACCESS_KEY_ID'):
        print("   ✅ AWS_ACCESS_KEY_ID found in environment")
    else:
        print("   ❌ AWS_ACCESS_KEY_ID not in environment")
    
    if os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("   ✅ AWS_SECRET_ACCESS_KEY found in environment")
    else:
        print("   ❌ AWS_SECRET_ACCESS_KEY not in environment")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("   ✅ .env file exists")
        with open(env_file) as f:
            content = f.read()
            if 'AWS_ACCESS_KEY_ID' in content:
                print("   ✅ AWS_ACCESS_KEY_ID found in .env")
            if 'AWS_SECRET_ACCESS_KEY' in content:
                print("   ✅ AWS_SECRET_ACCESS_KEY found in .env")
    else:
        print("   ❌ .env file not found")
    
    # Check AWS credentials file
    aws_creds = Path.home() / '.aws' / 'credentials'
    if aws_creds.exists():
        print("   ✅ AWS credentials file exists (~/.aws/credentials)")
    else:
        print("   ❌ AWS credentials file not found")

def main():
    """Main function"""
    print("🚀 LaunchPad.AI AWS Credentials Checker")
    print("=" * 50)
    
    # Load .env file if it exists
    load_env_file()
    
    # Show credential sources
    show_credential_sources()
    
    # Check basic credentials
    if not check_credentials():
        print("\n❌ Credential check failed!")
        print("\n🔧 Quick setup:")
        print("1. Create AWS account at https://aws.amazon.com/")
        print("2. Go to IAM → Users → Create User")
        print("3. Attach AdministratorAccess policy (for development)")
        print("4. Download CSV with credentials")
        print("5. Run 'aws configure' or update .env file")
        return False
    
    # Check Bedrock access
    bedrock_ok = check_bedrock_access()
    
    # Check service permissions
    permissions = check_service_permissions()
    
    # Summary
    print("\n" + "=" * 50)
    all_good = all(permissions.values()) and bedrock_ok
    
    if all_good:
        print("🎉 All checks passed! You're ready to deploy.")
        print("\nNext steps:")
        print("1. Run: python deploy.py")
        print("2. Run: python run.py")
    else:
        print("⚠️  Some issues found. Please fix them before deploying.")
        
        if not bedrock_ok:
            print("\n🧠 Bedrock Setup:")
            print("   Go to AWS Console → Amazon Bedrock → Model access")
            print("   Request access to Claude 3 models")
        
        failed_services = [k for k, v in permissions.items() if not v]
        if failed_services:
            print(f"\n🔐 Missing permissions for: {', '.join(failed_services)}")
            print("   Consider attaching AdministratorAccess policy for development")

if __name__ == "__main__":
    main()
