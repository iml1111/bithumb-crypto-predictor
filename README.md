# Bithumb Crytpo Predictor

## Get Started

### Install Dependencies
```bash
$ pip install -r requirements.txt
```

### Set Environment Variables
Create `.env` file in source root directory and, set environment variables.
```bash
# .env
OPENAI_API_KEY={API_KEY}
``` 

### Run Job
```bash
$ python main.py run Job:Predictor KRW-{Crypto} iteration={iteration}
# python main.py run Job:Predictor KRW-WLD 5
```

# References
- https://github.com/youtube-jocoding/gpt-bitcoin
