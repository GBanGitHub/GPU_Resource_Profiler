"""GPU Resource Profiler - A tool for monitoring and analyzing GPU usage."""

import warnings
# Suppress pynvml deprecation warning globally
warnings.filterwarnings('ignore', message='.*pynvml.*deprecated.*')

__version__ = "1.0.0"
__author__ = "GPU Profiler Team"
__description__ = "A Python-based tool for monitoring and analyzing GPU resources"
