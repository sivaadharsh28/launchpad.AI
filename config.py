import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # AWS Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'eu-west-3')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
    BEDROCK_NOVA_MODEL_ID = os.getenv('BEDROCK_NOVA_MODEL_ID', 'amazon.nova-micro-v1:0')
    
    # DynamoDB Tables
    USER_PROFILES_TABLE = os.getenv('USER_PROFILES_TABLE', 'launchpad-user-profiles')
    CAREER_PLANS_TABLE = os.getenv('CAREER_PLANS_TABLE', 'launchpad-career-plans')
    JOB_APPLICATIONS_TABLE = os.getenv('JOB_APPLICATIONS_TABLE', 'launchpad-job-applications')
    
    # S3 Configuration
    S3_BUCKET = os.getenv('S3_BUCKET', 'launchpad-ai-documents')
    
    # Application Settings
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Gradio Settings
    GRADIO_SERVER_NAME = os.getenv('GRADIO_SERVER_NAME', '0.0.0.0')
    GRADIO_SERVER_PORT = int(os.getenv('GRADIO_SERVER_PORT', '7860'))
    GRADIO_SHARE = os.getenv('GRADIO_SHARE', 'False').lower() == 'true'
    
    @classmethod
    def get_aws_config(cls) -> Dict[str, Any]:
        """Get AWS configuration"""
        config = {'region_name': cls.AWS_REGION}
        
        if cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY:
            config.update({
                'aws_access_key_id': cls.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': cls.AWS_SECRET_ACCESS_KEY
            })
        
        return config
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration"""
        required_vars = ['AWS_REGION']
        
        for var in required_vars:
            if not getattr(cls, var):
                print(f"Warning: {var} not configured")
                return False
        
        return True

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True
    GRADIO_SHARE = True

class ProductionConfig(Config):
    DEBUG = False
    GRADIO_SHARE = False

# Select configuration based on environment
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': Config
}

def get_config(env: str = None) -> Config:
    """Get configuration for environment"""
    env = env or os.getenv('ENVIRONMENT', 'default')
    return config_map.get(env, Config)
