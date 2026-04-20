# Quick script to start mobile access tunnel
from pyngrok import ngrok

# Set your auth token
ngrok.set_auth_token("39buB6uCPdntFAwaDMQaH3a9lBP_6HinEnsnQhykcDAmTUNRP")

# Create tunnel to port 5001
public_url = ngrok.connect(5001, "http")

print("=" * 50)
print("YOUR PUBLIC URL:")
print("=" * 50)
print(public_url)
print("=" * 50)
print("\nOpen this URL on your mobile!")
print("Login: admin / admin123")
print("\nPress Ctrl+C to stop the tunnel")
print("=" * 50)

# Keep the tunnel open
input()

