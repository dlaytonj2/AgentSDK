"""Model settings for configuring AI model behavior."""
from typing import Any, Dict, Optional


class ModelSettings:
    """Settings for configuring AI model behavior."""
    
    def __init__(
        self,
        temperature: float = 0.7,
        top_p: float = 1.0,
        tool_choice: Optional[str] = None,
        **kwargs
    ):
        self.temperature = temperature
        self.top_p = top_p
        self.tool_choice = tool_choice
        self.additional_settings = kwargs
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to a dictionary for API consumption."""
        settings = {
            "temperature": self.temperature,
            "top_p": self.top_p,
        }
        
        if self.tool_choice:
            settings["tool_choice"] = self.tool_choice
            
        settings.update(self.additional_settings)
        return settings 