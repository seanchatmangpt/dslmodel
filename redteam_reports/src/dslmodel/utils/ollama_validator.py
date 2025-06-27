#!/usr/bin/env python3
"""
Ollama Validation and Configuration Utility

Provides comprehensive validation, error handling, and configuration
management for Ollama model usage throughout DSLModel.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuration for Ollama connection and models"""
    base_url: str = "http://localhost:11434"
    default_model: str = "qwen3:latest"
    timeout: int = 30
    max_retries: int = 3
    api_key: Optional[str] = None


class OllamaValidator:
    """Comprehensive Ollama validation and configuration manager"""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or self._load_config()
        self._session = requests.Session()
        self._session.timeout = self.config.timeout
        
    def _load_config(self) -> OllamaConfig:
        """Load Ollama configuration from environment variables and defaults"""
        return OllamaConfig(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            default_model=os.getenv("OLLAMA_DEFAULT_MODEL", "qwen3:latest"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "30")),
            max_retries=int(os.getenv("OLLAMA_MAX_RETRIES", "3")),
            api_key=os.getenv("OLLAMA_API_KEY")
        )
    
    def validate_url(self, url: str) -> bool:
        """Validate Ollama URL format"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False
    
    def check_server_availability(self) -> Tuple[bool, str]:
        """Check if Ollama server is available and responsive"""
        try:
            response = self._session.get(f"{self.config.base_url}/api/version")
            if response.status_code == 200:
                version_info = response.json()
                return True, f"Ollama server available (version: {version_info.get('version', 'unknown')})"
            else:
                return False, f"Ollama server responded with status {response.status_code}"
        except requests.ConnectionError:
            return False, f"Cannot connect to Ollama server at {self.config.base_url}"
        except requests.Timeout:
            return False, f"Timeout connecting to Ollama server (>{self.config.timeout}s)"
        except Exception as e:
            return False, f"Ollama server check failed: {str(e)}"
    
    def get_available_models(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Get list of available Ollama models"""
        try:
            response = self._session.get(f"{self.config.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return True, models
            else:
                return False, []
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
            return False, []
    
    def validate_model_availability(self, model_name: str) -> Tuple[bool, str]:
        """Check if a specific model is available"""
        success, models = self.get_available_models()
        if not success:
            return False, "Could not retrieve model list from Ollama"
        
        # Handle both "model:tag" and "ollama/model" formats
        clean_model = model_name.replace("ollama/", "")
        if ":" not in clean_model:
            clean_model += ":latest"
        
        available_names = [model["name"] for model in models]
        if clean_model in available_names:
            return True, f"Model {clean_model} is available"
        else:
            return False, f"Model {clean_model} not found. Available: {', '.join(available_names)}"
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Comprehensive configuration validation"""
        results = {
            "url_valid": False,
            "server_available": False,
            "models_accessible": False,
            "default_model_available": False,
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Validate URL format
        if self.validate_url(self.config.base_url):
            results["url_valid"] = True
            results["info"].append(f"✅ URL format valid: {self.config.base_url}")
        else:
            results["errors"].append(f"❌ Invalid URL format: {self.config.base_url}")
            return results
        
        # Check server availability
        server_ok, server_msg = self.check_server_availability()
        results["server_available"] = server_ok
        if server_ok:
            results["info"].append(f"✅ {server_msg}")
        else:
            results["errors"].append(f"❌ {server_msg}")
            return results
        
        # Check model access
        models_ok, models = self.get_available_models()
        results["models_accessible"] = models_ok
        if models_ok:
            results["info"].append(f"✅ Found {len(models)} available models")
            
            # Check default model
            default_ok, default_msg = self.validate_model_availability(self.config.default_model)
            results["default_model_available"] = default_ok
            if default_ok:
                results["info"].append(f"✅ {default_msg}")
            else:
                results["warnings"].append(f"⚠️ {default_msg}")
        else:
            results["errors"].append("❌ Could not access Ollama models")
        
        return results
    
    def get_recommended_models(self) -> List[str]:
        """Get list of recommended models for DSLModel usage"""
        success, models = self.get_available_models()
        if not success:
            return []
        
        recommended = []
        model_names = [model["name"] for model in models]
        
        # Check for common DSLModel-compatible models
        priority_models = [
            "qwen3:latest", "qwen2.5:latest", "phi4:latest", 
            "llama2:latest", "llama3:latest", "codellama:latest"
        ]
        
        for model in priority_models:
            if model in model_names:
                recommended.append(model)
        
        # Add any other available models
        for model in model_names:
            if model not in recommended:
                recommended.append(model)
        
        return recommended
    
    def suggest_fixes(self, validation_results: Dict[str, Any]) -> List[str]:
        """Suggest fixes for validation issues"""
        suggestions = []
        
        if not validation_results["server_available"]:
            suggestions.extend([
                "🔧 Start Ollama server: `ollama serve`",
                "🔧 Check if Ollama is installed: `ollama --version`",
                "🔧 Install Ollama from: https://ollama.com/download",
                f"🔧 Verify server URL: {self.config.base_url}"
            ])
        
        if not validation_results["default_model_available"]:
            recommended = self.get_recommended_models()
            if recommended:
                suggestions.append(f"🔧 Available models: {', '.join(recommended[:3])}")
            suggestions.extend([
                f"🔧 Pull default model: `ollama pull {self.config.default_model.replace('ollama/', '')}`",
                "🔧 Or set different default with OLLAMA_DEFAULT_MODEL env var"
            ])
        
        return suggestions
    
    def create_env_template(self, output_path: Path = None) -> str:
        """Create environment variable template for Ollama configuration"""
        template = f"""# Ollama Configuration for DSLModel
# Copy to your .env file or export these variables

# Ollama server URL (default: http://localhost:11434)
export OLLAMA_BASE_URL="{self.config.base_url}"

# Default Ollama model (default: qwen3:latest)
export OLLAMA_DEFAULT_MODEL="{self.config.default_model}"

# Connection timeout in seconds (default: 30)
export OLLAMA_TIMEOUT="{self.config.timeout}"

# Maximum retry attempts (default: 3)  
export OLLAMA_MAX_RETRIES="{self.config.max_retries}"

# Optional API key (if required)
# export OLLAMA_API_KEY="your-api-key-here"
"""
        
        if output_path:
            output_path.write_text(template)
            return f"Environment template saved to: {output_path}"
        
        return template


def validate_ollama_globally() -> Dict[str, Any]:
    """Global validation function for use throughout DSLModel"""
    validator = OllamaValidator()
    return validator.validate_configuration()


def safe_init_ollama(model: str = None, experimental: bool = True, adapter = None, **kwargs) -> Tuple[bool, Optional[Any], str]:
    """Safely initialize Ollama with validation and error handling"""
    validator = OllamaValidator()
    
    # Use provided model or default
    target_model = model or validator.config.default_model
    
    # Validate before attempting initialization
    validation = validator.validate_configuration()
    if not validation["server_available"]:
        return False, None, "Ollama server not available"
    
    model_ok, model_msg = validator.validate_model_availability(target_model)
    if not model_ok:
        return False, None, model_msg
    
    try:
        import dspy
        
        # Clean model name for DSPy (add ollama/ prefix if needed)
        if not target_model.startswith("ollama/"):
            dspy_model = f"ollama/{target_model}"
        else:
            dspy_model = target_model
        
        # Default configuration with 'model' parameter
        default_config = {
            "model": dspy_model,
            "api_key": None,
            "api_base": None,
            "temperature": 0.0,
            "max_tokens": 1000,
            "cache": True,
            "model_type": "chat",
            "stop": None,
        }

        # Update default config with user-provided kwargs
        lm_config = {**default_config, **kwargs}

        # Remove None values to use default settings from dspy.LM
        lm_config = {k: v for k, v in lm_config.items() if v is not None}
        lm = dspy.LM(**lm_config)

        # Configure the LM with DSPy settings
        dspy.settings.configure(lm=lm, adapter=adapter, experimental=experimental)
        
        return True, lm, f"Successfully initialized {dspy_model}"
        
    except Exception as e:
        return False, None, f"Failed to initialize Ollama model: {str(e)}"


def main():
    """CLI interface for Ollama validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Ollama configuration for DSLModel")
    parser.add_argument("--model", help="Specific model to validate")
    parser.add_argument("--create-env", action="store_true", help="Create environment template")
    parser.add_argument("--output", help="Output file for environment template")
    
    args = parser.parse_args()
    
    validator = OllamaValidator()
    
    if args.create_env:
        output_path = Path(args.output) if args.output else None
        result = validator.create_env_template(output_path)
        print(result)
        return
    
    print("🔍 Validating Ollama Configuration...")
    print("=" * 50)
    
    validation = validator.validate_configuration()
    
    # Print results
    for info in validation["info"]:
        print(info)
    
    for warning in validation["warnings"]:
        print(warning)
    
    for error in validation["errors"]:
        print(error)
    
    # Test specific model if provided
    if args.model:
        print(f"\n🎯 Testing specific model: {args.model}")
        model_ok, msg = validator.validate_model_availability(args.model)
        print(f"{'✅' if model_ok else '❌'} {msg}")
    
    # Show suggestions if there are issues
    if validation["errors"] or validation["warnings"]:
        print("\n💡 Suggested fixes:")
        suggestions = validator.suggest_fixes(validation)
        for suggestion in suggestions:
            print(f"  {suggestion}")
    
    # Show recommended models
    recommended = validator.get_recommended_models()
    if recommended:
        print(f"\n🎯 Available models: {', '.join(recommended[:5])}")
        if len(recommended) > 5:
            print(f"   ... and {len(recommended) - 5} more")


if __name__ == "__main__":
    main()