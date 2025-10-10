"""Dataset loaders module."""

from .base import BaseDatasetLoader
from .ieee_cis import IEEECISLoader
from .givemesomecredit import GiveMeSomeCreditLoader
from .german_credit import GermanCreditLoader

__all__ = [
    'BaseDatasetLoader',
    'IEEECISLoader', 
    'GiveMeSomeCreditLoader',
    'GermanCreditLoader',
    'get_loader'
]


def get_loader(dataset_id: str, config: dict) -> BaseDatasetLoader:
    """Get appropriate loader for dataset.
    
    Args:
        dataset_id: Dataset identifier
        config: Dataset configuration
        
    Returns:
        Dataset loader instance
    """
    loaders = {
        'ieee-cis-fraud': IEEECISLoader,
        'givemesomecredit': GiveMeSomeCreditLoader,
        'german-credit': GermanCreditLoader,
    }
    
    loader_class = loaders.get(dataset_id)
    if loader_class is None:
        raise ValueError(f"No loader found for dataset: {dataset_id}")
    
    return loader_class(dataset_id, config)
