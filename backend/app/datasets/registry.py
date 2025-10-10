"""Dataset registry management."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()


class DatasetRegistry:
    """Manages dataset configurations from YAML registry."""
    
    def __init__(self, config_path: str = None):
        """Initialize dataset registry.
        
        Args:
            config_path: Path to datasets.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Default path: config/datasets.yaml from project root
            backend_dir = Path(__file__).parent.parent.parent
            config_path = backend_dir.parent / "config" / "datasets.yaml"
        
        self.config_path = Path(config_path)
        self.datasets = self._load_registry()
        logger.info("Dataset registry loaded", 
                   count=len(self.datasets), 
                   path=str(self.config_path))
    
    def _load_registry(self) -> Dict[str, Dict]:
        """Load dataset registry from YAML file.
        
        Returns:
            Dictionary mapping dataset IDs to their configurations.
        """
        try:
            if not self.config_path.exists():
                logger.warning("Dataset registry file not found", 
                             path=str(self.config_path))
                return {}
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config or 'datasets' not in config:
                logger.warning("No datasets found in registry")
                return {}
            
            # Convert list to dict keyed by dataset ID
            datasets = {}
            for dataset in config.get('datasets', []):
                if 'id' in dataset:
                    datasets[dataset['id']] = dataset
                else:
                    logger.warning("Dataset missing 'id' field", dataset=dataset)
            
            logger.info("Dataset registry loaded successfully", count=len(datasets))
            return datasets
            
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML", error=str(e))
            return {}
        except Exception as e:
            logger.error("Failed to load dataset registry", error=str(e))
            return {}
    
    def get_dataset_config(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset configuration by ID.
        
        Args:
            dataset_id: Dataset identifier.
            
        Returns:
            Dataset configuration dictionary or None if not found.
        """
        config = self.datasets.get(dataset_id)
        if config:
            logger.debug("Retrieved dataset config", dataset_id=dataset_id)
        else:
            logger.warning("Dataset not found in registry", dataset_id=dataset_id)
        return config
    
    def list_datasets(self, active_only: bool = True) -> List[Dict]:
        """List all datasets in registry.
        
        Args:
            active_only: If True, only return active datasets.
            
        Returns:
            List of dataset configuration dictionaries.
        """
        datasets = list(self.datasets.values())
        
        if active_only:
            datasets = [d for d in datasets if d.get('is_active', True)]
        
        logger.debug("Listed datasets", count=len(datasets), active_only=active_only)
        return datasets
    
    def get_dataset_ids(self, active_only: bool = True) -> List[str]:
        """Get list of dataset IDs.
        
        Args:
            active_only: If True, only return active dataset IDs.
            
        Returns:
            List of dataset IDs.
        """
        datasets = self.list_datasets(active_only=active_only)
        return [d['id'] for d in datasets]
    
    def add_dataset(self, dataset_config: Dict) -> bool:
        """Add new dataset to registry.
        
        Args:
            dataset_config: Dataset configuration dictionary.
            
        Returns:
            True if successful, False otherwise.
        """
        if 'id' not in dataset_config:
            logger.error("Cannot add dataset without 'id' field")
            return False
        
        dataset_id = dataset_config['id']
        
        if dataset_id in self.datasets:
            logger.warning("Dataset already exists", dataset_id=dataset_id)
            return False
        
        self.datasets[dataset_id] = dataset_config
        
        # Save to file
        if self._save_registry():
            logger.info("Dataset added to registry", dataset_id=dataset_id)
            return True
        else:
            # Rollback
            del self.datasets[dataset_id]
            return False
    
    def update_dataset(self, dataset_id: str, updates: Dict) -> bool:
        """Update dataset configuration.
        
        Args:
            dataset_id: Dataset identifier.
            updates: Dictionary of fields to update.
            
        Returns:
            True if successful, False otherwise.
        """
        if dataset_id not in self.datasets:
            logger.error("Dataset not found", dataset_id=dataset_id)
            return False
        
        # Backup current config
        backup = self.datasets[dataset_id].copy()
        
        # Apply updates
        self.datasets[dataset_id].update(updates)
        
        # Save to file
        if self._save_registry():
            logger.info("Dataset updated", dataset_id=dataset_id)
            return True
        else:
            # Rollback
            self.datasets[dataset_id] = backup
            return False
    
    def remove_dataset(self, dataset_id: str) -> bool:
        """Remove dataset from registry.
        
        Args:
            dataset_id: Dataset identifier.
            
        Returns:
            True if successful, False otherwise.
        """
        if dataset_id not in self.datasets:
            logger.error("Dataset not found", dataset_id=dataset_id)
            return False
        
        # Backup
        backup = self.datasets[dataset_id]
        
        # Remove
        del self.datasets[dataset_id]
        
        # Save to file
        if self._save_registry():
            logger.info("Dataset removed from registry", dataset_id=dataset_id)
            return True
        else:
            # Rollback
            self.datasets[dataset_id] = backup
            return False
    
    def _save_registry(self) -> bool:
        """Save registry to YAML file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            config = {'datasets': list(self.datasets.values())}
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            logger.info("Dataset registry saved", path=str(self.config_path))
            return True
            
        except Exception as e:
            logger.error("Failed to save dataset registry", error=str(e))
            return False
    
    def reload(self):
        """Reload registry from file."""
        self.datasets = self._load_registry()
        logger.info("Dataset registry reloaded", count=len(self.datasets))


# Singleton instance
_registry: Optional[DatasetRegistry] = None


def get_dataset_registry() -> DatasetRegistry:
    """Get dataset registry singleton.
    
    Returns:
        DatasetRegistry instance.
    """
    global _registry
    if _registry is None:
        _registry = DatasetRegistry()
    return _registry
