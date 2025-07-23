# YouTube Downloader Anti-Detection Configuration
# Modify these settings to adjust stealth behavior

# Rate Limiting Settings
CLOUD_MIN_DELAY = 5.0      # Minimum delay between requests in cloud (seconds)
CLOUD_MAX_DELAY = 12.0     # Maximum delay between requests in cloud (seconds)
LOCAL_MIN_DELAY = 1.0      # Minimum delay between requests locally (seconds)
LOCAL_MAX_DELAY = 3.0      # Maximum delay between requests locally (seconds)

# Session Management
MAX_CONSECUTIVE_FAILURES = 3    # Switch strategies after this many failures
IP_ROTATION_COOLDOWN = 3600     # Don't reuse IP for this many seconds (1 hour)
SESSION_FINGERPRINT_LENGTH = 16 # Length of session fingerprints

# Quality Fallback Strategy
PRIMARY_MAX_QUALITY = "1080"     # Primary attempt max quality
FALLBACK_MAX_QUALITY = "720"     # Fallback attempt max quality  
EMERGENCY_MAX_QUALITY = "480"    # Emergency fallback max quality
MINIMAL_MAX_QUALITY = "360"      # Minimal fallback max quality

# User Agent Rotation
ROTATE_USER_AGENTS = True        # Enable user agent rotation
FAVOR_SUCCESSFUL_PROFILES = True # Prefer profiles that worked before

# Advanced Stealth Features
ENABLE_ISP_SIMULATION = True     # Simulate realistic ISP ranges
ENABLE_BROWSER_ENTROPY = True    # Add realistic browser fingerprints
ENABLE_TIMING_JITTER = True      # Add human-like timing variations
ENABLE_HEADER_RANDOMIZATION = True # Randomize HTTP headers

# Emergency Mode (when detection is very aggressive)
EMERGENCY_MODE_DELAY_MIN = 20.0  # Minimum delay in emergency mode
EMERGENCY_MODE_DELAY_MAX = 45.0  # Maximum delay in emergency mode
EMERGENCY_MODE_RETRIES = 1       # Number of retries in emergency mode

# Debugging
VERBOSE_LOGGING = True           # Enable detailed logging
LOG_SUCCESSFUL_PROFILES = True   # Log which profiles work
LOG_FAILED_ATTEMPTS = True       # Log failed attempts for analysis
