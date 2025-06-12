# Quick Start Guide

Get your face recognition system running in under 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv

# One-command setup (2-3 minutes)
make install

# Verify installation
make status
```

## First Usage

### Register a User
```bash
# Start user registration
make register

# Follow the prompts:
# 1. Enter your name
# 2. Camera opens
# 3. Press 's' to capture 5 photos
# 4. Press 'q' when done
```

### Start Recognition
```bash
# Begin face recognition
make recognize

# Camera opens and automatically detects faces
# Your name appears when recognized
```

### Web Interface
```bash
# Start the web server
uvicorn api.main:app --reload

# Open browser: http://localhost:8000
# Use the modern dashboard interface
```

## Essential Commands

| What you want to do | Command |
|---------------------|---------|
| Add a user | `make register` |
| Start recognition | `make recognize` |
| List users | `make list` |
| Check system | `make status` |
| Delete a user | `make delete` |
| Run tests | `make test` |

## Quick Reference

### Key Controls
- **'s'** → Capture photo (during registration)
- **'q'** → Quit/Exit

### Docker Alternative
```bash
# Quick Docker setup
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest
docker run -p 8000:8000 -v face_data:/app/data ghcr.io/ahmertsengol/face-auth-opencv:latest
```

## Troubleshooting

```bash
# If something goes wrong
make status      # Check system health
make test        # Run diagnostics
make help        # Show all commands
```

## What's Next?

1. **Add more users**: Run `make register` again
2. **Web dashboard**: Visit `http://localhost:8000`
3. **Performance check**: Run `make benchmark`
4. **Read full docs**: Check [INSTALLATION.md](INSTALLATION.md)

---

**🎉 That's it! Your face recognition system is ready to use.** 