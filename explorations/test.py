import os

#Troubleshooting: Uncomment to see the environment variables
for key in sorted(os.environ.keys()):
    value = os.environ[key]
# Optionally mask sensitive values
if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
    value = '***REDACTED***'
print(f"{key}={value}")