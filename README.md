# ApplyAI 🎯

AI-Powered Job Application Assistant that helps optimize your job applications using Claude AI.

## Features

- 🔍 **Smart Job Fit Analysis**: AI analysis of job requirements against your resume
- ✨ **Resume Optimization**: Get tailored suggestions to improve your resume
- 💡 **Strategic Insights**: Receive detailed application strategy feedback
- 📝 **Custom Questions**: Help with application-specific questions
- 📊 **History Tracking**: Keep track of all your job application analyses

## Setup

### Local Development
1. Clone the repository
2. Create a `.streamlit/secrets.toml` file with:
```toml
ANTHROPIC_API_KEY = "your-api-key"
USERNAME = "admin"
PASSWORD = "your-password"
```

### Deployment
1. Push to GitHub (public or private repository)
2. Deploy on Streamlit Cloud:
   - Connect your GitHub repository
   - Add the required secrets in Streamlit Cloud dashboard
   - Deploy!

## Usage

1. Log in to the application
2. Upload your resume(s)
3. Paste a job posting to analyze
4. Get AI-powered insights and recommendations

## Technology Stack

- Streamlit for web interface
- Claude AI (Anthropic) for analysis
- SQLite for data storage
- Python 3.9+

## Support

For issues and feature requests, please create a GitHub issue.

## License

Private repository - All rights reserved