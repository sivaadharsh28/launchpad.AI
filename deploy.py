#!/usr/bin/env python3
"""
LaunchPad.AI Deployment Script

This script helps deploy the necessary AWS infrastructure for LaunchPad.AI.
"""

import boto3
import json
import logging
from typing import Dict, Any
from config import get_config

logger = logging.getLogger(__name__)

class AWSDeployer:
    def __init__(self):
        self.config = get_config()
        self.aws_config = self.config.get_aws_config()
        
        self.dynamodb = boto3.client('dynamodb', **self.aws_config)
        self.s3 = boto3.client('s3', **self.aws_config)
        self.iam = boto3.client('iam', **self.aws_config)
    
    def create_dynamodb_tables(self) -> bool:
        """Create required DynamoDB tables"""
        tables = [
            {
                'TableName': self.config.USER_PROFILES_TABLE,
                'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                'AttributeDefinitions': [{'AttributeName': 'user_id', 'AttributeType': 'S'}],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'TableName': self.config.CAREER_PLANS_TABLE,
                'KeySchema': [{'AttributeName': 'plan_id', 'KeyType': 'HASH'}],
                'AttributeDefinitions': [
                    {'AttributeName': 'plan_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [{
                    'IndexName': 'user-id-index',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'}
                }],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'TableName': self.config.JOB_APPLICATIONS_TABLE,
                'KeySchema': [{'AttributeName': 'application_id', 'KeyType': 'HASH'}],
                'AttributeDefinitions': [
                    {'AttributeName': 'application_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [{
                    'IndexName': 'user-id-index',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'}
                }],
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ]
        
        for table_config in tables:
            try:
                response = self.dynamodb.create_table(**table_config)
                logger.info(f"Created table: {table_config['TableName']}")
            except self.dynamodb.exceptions.ResourceInUseException:
                logger.info(f"Table already exists: {table_config['TableName']}")
            except Exception as e:
                logger.error(f"Failed to create table {table_config['TableName']}: {e}")
                return False
        
        return True
    
    def create_s3_bucket(self) -> bool:
        """Create S3 bucket for document storage"""
        try:
            # Check if bucket exists
            self.s3.head_bucket(Bucket=self.config.S3_BUCKET)
            logger.info(f"S3 bucket already exists: {self.config.S3_BUCKET}")
            return True
        except:
            pass
        
        try:
            if self.config.AWS_REGION == 'us-east-1':
                self.s3.create_bucket(Bucket=self.config.S3_BUCKET)
            else:
                self.s3.create_bucket(
                    Bucket=self.config.S3_BUCKET,
                    CreateBucketConfiguration={'LocationConstraint': self.config.AWS_REGION}
                )
            
            # Set bucket policy for security
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "DenyPublicAccess",
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{self.config.S3_BUCKET}/*",
                        "Condition": {
                            "Bool": {
                                "aws:SecureTransport": "false"
                            }
                        }
                    }
                ]
            }
            
            self.s3.put_bucket_policy(
                Bucket=self.config.S3_BUCKET,
                Policy=json.dumps(bucket_policy)
            )
            
            logger.info(f"Created S3 bucket: {self.config.S3_BUCKET}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create S3 bucket: {e}")
            return False
    
    def setup_iam_role(self) -> bool:
        """Setup IAM role for the application"""
        role_name = "LaunchPadAI-ExecutionRole"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for LaunchPad.AI application"
            )
            logger.info(f"Created IAM role: {role_name}")
        except self.iam.exceptions.EntityAlreadyExistsException:
            logger.info(f"IAM role already exists: {role_name}")
        except Exception as e:
            logger.error(f"Failed to create IAM role: {e}")
            return False
        
        # Attach policies
        policies = [
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3FullAccess",
            "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
        ]
        
        for policy_arn in policies:
            try:
                self.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                logger.info(f"Attached policy: {policy_arn}")
            except Exception as e:
                logger.warning(f"Failed to attach policy {policy_arn}: {e}")
        
        return True
    
    def deploy_all(self) -> bool:
        """Deploy all AWS resources"""
        logger.info("Starting AWS infrastructure deployment...")
        
        success = True
        
        # Create DynamoDB tables
        if not self.create_dynamodb_tables():
            logger.error("Failed to create DynamoDB tables")
            success = False
        
        # Create S3 bucket
        if not self.create_s3_bucket():
            logger.error("Failed to create S3 bucket")
            success = False
        
        # Setup IAM role
        if not self.setup_iam_role():
            logger.error("Failed to setup IAM role")
            success = False
        
        if success:
            logger.info("✅ AWS infrastructure deployment completed successfully!")
        else:
            logger.error("❌ AWS infrastructure deployment failed!")
        
        return success

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy LaunchPad.AI AWS infrastructure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deployed without actually deploying")
    args = parser.parse_args()
    
    if args.dry_run:
        print("Dry run mode - would deploy:")
        print("- DynamoDB tables for user profiles, career plans, and job applications")
        print("- S3 bucket for document storage")
        print("- IAM roles and policies")
        return
    
    deployer = AWSDeployer()
    success = deployer.deploy_all()
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
