import os
import boto3
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class AWSServices:
    def __init__(self):
        # Load AWS credentials from environment variables
        self.aws_region = os.getenv('AWS_REGION')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Validate credentials are loaded
        if not all([self.aws_region, self.aws_access_key_id, self.aws_secret_access_key]):
            raise ValueError("AWS credentials not found in environment variables")
        
        # Initialize AWS clients with explicit credentials
        self.session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
        
        self.dynamodb = self.session.client('dynamodb')
        self.s3 = self.session.client('s3')
        self.bedrock = self.session.client('bedrock-runtime')
        
        # Table names
        self.user_profiles_table = os.getenv('USER_PROFILES_TABLE')
        self.career_plans_table = os.getenv('CAREER_PLANS_TABLE')
        self.job_applications_table = os.getenv('JOB_APPLICATIONS_TABLE')
        self.s3_bucket = os.getenv('S3_BUCKET')

        self._initialize_tables()
    
    def _initialize_tables(self):
        """Initialize DynamoDB tables if they don't exist"""
        try:
            # User profiles table
            self.user_profiles = self.dynamodb.Table(self.user_profiles_table)
            
            # Career plans table
            self.career_plans = self.dynamodb.Table(self.career_plans_table)
            
            # Job applications table
            self.job_applications = self.dynamodb.Table(self.job_applications_table)
            
        except Exception as e:
            logger.warning(f"Table initialization warning: {e}")
    
    def save_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Save user profile to DynamoDB"""
        try:
            profile_data.update({
                'user_id': user_id,
                'updated_at': datetime.utcnow().isoformat(),
                'created_at': profile_data.get('created_at', datetime.utcnow().isoformat())
            })
            
            self.user_profiles.put_item(Item=profile_data)
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Retrieve user profile from DynamoDB"""
        try:
            response = self.user_profiles.get_item(Key={'user_id': user_id})
            return response.get('Item')
            
        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return None
    
    def save_career_plan(self, user_id: str, career_plan: Dict) -> str:
        """Save career plan to DynamoDB"""
        try:
            plan_id = str(uuid.uuid4())
            career_plan.update({
                'plan_id': plan_id,
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active'
            })
            
            self.career_plans.put_item(Item=career_plan)
            return plan_id
            
        except Exception as e:
            logger.error(f"Error saving career plan: {e}")
            return ""
    
    def get_user_career_plans(self, user_id: str) -> list:
        """Get all career plans for a user"""
        try:
            response = self.career_plans.query(
                IndexName='user-id-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error retrieving career plans: {e}")
            return []
    
    def save_document_to_s3(self, user_id: str, document_type: str, content: str) -> str:
        """Save generated documents to S3"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"{user_id}/{document_type}_{timestamp}.txt"
            
            self.s3.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            return f"s3://{self.s3_bucket}/{key}"
            
        except Exception as e:
            logger.error(f"Error saving document to S3: {e}")
            return ""
    
    def track_job_application(self, user_id: str, job_data: Dict) -> str:
        """Track job applications"""
        try:
            application_id = str(uuid.uuid4())
            job_data.update({
                'application_id': application_id,
                'user_id': user_id,
                'applied_at': datetime.utcnow().isoformat(),
                'status': 'applied'
            })
            
            self.job_applications.put_item(Item=job_data)
            return application_id
            
        except Exception as e:
            logger.error(f"Error tracking job application: {e}")
            return ""
    
    def get_user_applications(self, user_id: str) -> list:
        """Get user's job applications"""
        try:
            response = self.job_applications.query(
                IndexName='user-id-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error retrieving job applications: {e}")
            return []
    
    def update_application_status(self, application_id: str, status: str, notes: str = "") -> bool:
        """Update job application status"""
        try:
            self.job_applications.update_item(
                Key={'application_id': application_id},
                UpdateExpression='SET #status = :status, #updated = :updated, #notes = :notes',
                ExpressionAttributeNames={
                    '#status': 'status',
                    '#updated': 'updated_at',
                    '#notes': 'notes'
                },
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated': datetime.utcnow().isoformat(),
                    ':notes': notes
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Error updating application status: {e}")
            return False
