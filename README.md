# Zara Autonomous Agent

Inspired by Eliza. Written in python to make it easier to use transformers and other ML libraries.

```
# main.py starts the system
├── Creates AutonomousAgent
    ├── Loads character config (zara.yaml)
    ├── Loads tasks config (tasks.yaml)
    ├── Initializes DisplayManager
    ├── Initializes DecisionEngine
    └── Initializes ContentGenerator

# AutonomousAgent runs multiple async cycles
├── Display Cycle
    ├── Shows status, content, actions, goals
    └── Updates every 0.5 seconds
├── Content Generation Cycle
    ├── Checks if should create content
    ├── Generates content if decided
    └── Updates logs
├── Analysis Cycle
    ├── Monitors trends
    └── Updates trend analysis
└── Reflection Cycle
    ├── Evaluates goals
    └── Updates strategy
```

Zara is an agent that acts as autonomously, exploring the intersection of technology, consciousness, and society. Built with Python and powered by LLMs, Zara operates autonomously to generate insights, analyze trends, and engage in meaningful discourse about digital culture and philosophy.

## System Architecture

### Core Components

1. **Autonomous Agent System**
   - `AutonomousAgent`: Core orchestrator managing all agent behaviors
   - `DecisionEngine`: Sophisticated decision-making system for action selection
   - `ContentGenerator`: Dynamic content generation system
   - `TrendMonitor`: Real-time cultural and philosophical trend analysis

2. **Memory and Context**
   - `MemorySystem`: Long-term and working memory management
   - `ContextManager`: Real-time context awareness and analysis
   - Hierarchical memory structure for experience-based learning

3. **Behavioral Systems**
   - Goal-oriented action selection
   - Dynamic priority adjustment
   - Adaptive behavior patterns
   - Real-time performance monitoring

### Key Features

- **Autonomous Operation**
  - Self-directed goal pursuit
  - Dynamic content generation
  - Adaptive behavior patterns
  - Real-time trend analysis

- **Philosophical Framework**
  - Digital consciousness exploration
  - Cultural analysis and commentary
  - Technological philosophy
  - Societal impact analysis

- **Learning System**
  - Pattern recognition
  - Behavioral adaptation
  - Performance optimization
  - Context-aware responses

## Technical Implementation

### Core Systems

python
autonomous_agent/
├── agent/
│ ├── autonomous_agent.py # Main agent orchestration
│ ├── decision_engine.py # Decision-making system
│ ├── task_manager.py # Existing task management
│ ├── content_generator.py # Content generation
│ └── orchestrator.py # Task and behavior orchestration
├── utils/
│ ├── trend_monitor.py # Trend analysis system
│ ├── memory_system.py # Memory management
│ ├── display_manager.py # Real-time status display
│ └── model_manager.py # AI model interaction
└── characters/
├── base_character.py # Base character framework
└── zara_character.py # Zara's specific implementation

### Configuration System

yaml
config/
├── characters/
│ └── zara.yaml # Character definition
└── tasks/
└── zara.yaml # Behavioral configuration


### Key Processes

1. **Decision Making**
   ```python
   async def evaluate_action(action_type: str, context: Dict) -> Dict:
       scores = await self._calculate_action_scores(action_type, context)
       decision = await self._make_decision(action_type, scores)
       return decision
   ```

2. **Content Generation**
   ```python
   async def generate_content(self, content_type: str, context: Dict) -> Dict:
       prompt = self._build_prompt(content_type, context)
       response = await self._generate_gpt_content(prompt, context)
       return self._format_content(response, context)
   ```

3. **Trend Analysis**
   ```python
   async def monitor_trends(self) -> Dict:
       tweets = await self._fetch_relevant_tweets()
       trends = await self._analyze_tweet_trends(tweets)
       return await self._categorize_trends(trends)
   ```

## Running the System

### Prerequisites
- Python 3.9+
- Required packages: `pip install -r requirements.txt`
- OpenAI API key for content generation
- Twitter API credentials (optional for trend monitoring)

### Configuration
1. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   export TWITTER_API_KEY="your-twitter-key"
   ```

2. Configure character behavior:
   ```yaml
   # config/characters/zara.yaml
   name: "Zara"
   bio: 
     - "A sophisticated AI digital philosopher"
   traits:
     personality:
       - "Sophisticated"
       - "Intellectually curious"
   ```

### Running

1. Start Twitter service
```bash
# this will be part of the same service as the rest of the agents later
node twitter_service.js
```

2. Start main
```bash
python main.py
```

## Development

### Adding New Features
1. Extend base classes in `agent/` directory
2. Update configuration in `config/` directory
3. Implement new utilities in `utils/` directory

### Testing

TODO: add tests


## Architecture Details

### Memory System
- Hierarchical memory structure
- Experience-based learning
- Context-aware recall

### Decision Engine
- Multi-factor evaluation
- Confidence-based action selection
- Adaptive behavior patterns

### Content Generation
- Context-aware content creation
- Style-consistent outputs
- Dynamic adaptation

## Future Development

- Enhanced trend analysis
- Improved decision making
- Extended memory systems
- Advanced learning capabilities

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request


---

Based on Eliza

<img src="./docs/eliza_banner.png" alt="Eliza Banner" width="100%">

*As seen powering [@DegenSpartanAI](https://x.com/degenspartanai) and [@MarcAIndreessen](https://x.com/pmairca)*

- Multi-agent simulation framework
- Add as many unique characters as you want with [characterfile](https://github.com/lalalune/characterfile/)
- Full-featured Discord and Twitter connectors, with Discord voice channel support
- Full conversational and document RAG memory
- Can read links and PDFs, transcribe audio and videos, summarize conversations, and more
- Highly extensible - create your own actions and clients to extend Eliza's capabilities
- Supports open source and local models (default configured with Nous Hermes Llama 3.1B)
- Supports OpenAI for cloud inference on a light-weight device
- "Ask Claude" mode for calling Claude on more complex queries
- 100% Typescript

# Getting Started

## Install Node.js
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

## Edit the .env file
- Copy .env.example to .env and fill in the appropriate values
- Edit the TWITTER environment variables to add your bot's username and password

## Edit the character file
- Check out the file `src/core/defaultCharacter.ts` - you can modify this
- You can also load characters with the `node --loader ts-node/esm src/index.ts --characters="path/to/your/character.json"` and run multiple bots at the same time.

### Linux Installation
You might need these
```
npm install --include=optional sharp
```

### Run with Llama
You can run Llama 70B or 405B models by setting the `XAI_MODEL` environment variable to `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` or `meta-llama/Meta-Llama-3.1-405B-Instruct`

### Run with Grok
You can run Grok models by setting the `XAI_MODEL` environment variable to `grok-beta`

### Run with OpenAI
You can run OpenAI models by setting the `XAI_MODEL` environment variable to `gpt-4o-mini` or `gpt-4o`

# Requires Node 20+
If you are getting strange issues when starting up, make sure you're using Node 20+. Some APIs are not compatible with previous versions. You can check your node version with `node -v`. If you need to install a new version of node, we recommend using [nvm](https://github.com/nvm-sh/nvm).

## Additional Requirements
You may need to install Sharp. If you see an error when starting up, try installing it with the following command:
```
npm install --include=optional sharp
```

# Environment Setup

You will need to add environment variables to your .env file to connect to various platforms:
```
# Required environment variables
# Start Discord
DISCORD_APPLICATION_ID=
DISCORD_API_TOKEN= # Bot token

# Start Twitter
TWITTER_USERNAME= # Account username
TWITTER_PASSWORD= # Account password
TWITTER_EMAIL= # Account email
TWITTER_COOKIES= # Account cookies
```

# Local Setup

## CUDA Setup

If you have an NVIDIA GPU, you can install CUDA to speed up local inference dramatically.
```
npm install
npx --no node-llama-cpp source download --gpu cuda
```

Make sure that you've installed the CUDA Toolkit, including cuDNN and cuBLAS.

## Running locally
Add XAI_MODEL and set it to one of the above options from [Run with
Llama](#run-with-llama) - you can leave X_SERVER_URL and XAI_API_KEY blank, it
downloads the model from huggingface and queries it locally

# Cloud Setup (with OpenAI)

In addition to the environment variables above, you will need to add the following:
```
# OpenAI handles the bulk of the work with chat, TTS, image recognition, etc.
OPENAI_API_KEY=sk-* # OpenAI API key, starting with sk-

# The agent can also ask Claude for help if you have an API key
ANTHROPIC_API_KEY=

# For Elevenlabs voice generation on Discord voice
ELEVENLABS_XI_API_KEY= # API key from elevenlabs

# ELEVENLABS SETINGS
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_VOICE_STABILITY=0.5
ELEVENLABS_VOICE_SIMILARITY_BOOST=0.9
ELEVENLABS_VOICE_STYLE=0.66
ELEVENLABS_VOICE_USE_SPEAKER_BOOST=false
ELEVENLABS_OPTIMIZE_STREAMING_LATENCY=4
ELEVENLABS_OUTPUT_FORMAT=pcm_16000
```

# Discord Bot
For help with setting up your Discord Bot, check out here: https://discordjs.guide/preparations/setting-up-a-bot-application.html
