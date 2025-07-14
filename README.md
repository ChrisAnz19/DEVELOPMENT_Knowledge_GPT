# knowledge_gpt

A natural language to behavioral data converter that transforms human prompts into Apollo API filters and simulates behavioral insights using AI.

## Overview

knowledge_gpt is an interim solution that bridges the gap between natural language queries and structured B2B data. It converts user prompts into precise Apollo API filters and uses AI to simulate behavioral data until the actual behavioral dataset is migrated.

### Key Features

- **Natural Language Processing**: Convert conversational prompts into structured API filters
- **Apollo API Integration**: Generate precise filters for Apollo's B2B data platform
- **Behavioral Data Simulation**: AI-powered insights based on generated filters
- **Error Handling**: Robust error handling and validation
- **CLI Interface**: User-friendly command-line interface

## Architecture

```
User Prompt → AI Processing → Apollo Filters → Behavioral Simulation → Results
```

1. **Prompt Processing**: Uses GPT-3.5-turbo to understand natural language
2. **Filter Generation**: Converts understanding into Apollo API parameters
3. **Data Simulation**: Generates realistic behavioral insights based on filters
4. **Output**: Structured JSON with filters and behavioral data

## Setup

### Prerequisites

- Python 3.7+
- OpenAI API key
- Apollo API key (optional for interim period)
- Bright Data API key (optional for interim period)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd knowledge_gpt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```bash
cp secrets_template.json secrets.json
# Edit secrets.json with your actual API keys
```

### API Keys Required

- **OpenAI API Key**: Required for natural language processing
- **Apollo API Key**: Required for B2B data queries (currently used for filter generation)
- **Bright Data API Key**: Optional for additional data enrichment

## Usage

### Command Line Interface

Run the main application:
```bash
python main.py
```

Example interaction:
```
🤖 knowledge_gpt - Natural Language to Behavioral Data
============================================================
This system converts your prompts into Apollo API filters and simulates behavioral insights.
Note: Behavioral data is AI-simulated until the actual dataset is migrated.

Enter your search prompt (or 'quit' to exit): Find CEOs at large software companies in San Francisco

🔍 Processing: 'Find CEOs at large software companies in San Francisco'
----------------------------------------
📊 Generating Apollo API filters...
✅ Filters generated successfully!

📋 Generated Filters:
{
  "organization_filters": {
    "organization_num_employees_ranges": ["1000,10000"],
    "organization_locations": ["San Francisco"]
  },
  "person_filters": {
    "person_titles": ["CEO"],
    "person_seniorities": ["c_suite"]
  },
  "reasoning": "Identified large companies by employee range and location, targeted CEO-level executives"
}

🧠 Simulating behavioral data...
✅ Behavioral data simulated successfully!

📈 Behavioral Insights:
{
  "engagement_patterns": {...},
  "technology_adoption": {...},
  "decision_making_behaviors": {...}
}
```

### Programmatic Usage

```python
from prompt_formatting import parse_prompt_to_apollo_filters, simulate_behavioral_data

# Generate filters from prompt
prompt = "Find marketing directors at companies using Salesforce"
filters = parse_prompt_to_apollo_filters(prompt)

# Simulate behavioral data
behavioral_data = simulate_behavioral_data(filters)

print(filters)
print(behavioral_data)
```

## API Filter Structure

### Organization Filters
- `organization_num_employees_ranges[]`: Employee count ranges
- `organization_locations[]`: Geographic locations
- `revenue_range[min/max]`: Revenue ranges
- `currently_using_any_of_technology_uids[]`: Technology stack
- `q_organization_keyword_tags[]`: Industry keywords

### Person Filters
- `person_titles[]`: Job titles
- `person_seniorities[]`: Seniority levels
- `person_locations[]`: Geographic locations
- `include_similar_titles`: Boolean for title variations

## Behavioral Data Simulation

The system simulates realistic behavioral insights including:
- **Engagement Patterns**: How companies/people interact with content
- **Technology Adoption**: Trends in technology usage
- **Decision Making**: Behavioral indicators for purchasing decisions
- **Market Dynamics**: Industry-specific behavioral patterns

## Future Roadmap

- [ ] Migration to actual behavioral dataset
- [ ] Real-time data integration
- [ ] Advanced analytics dashboard
- [ ] API endpoint for external integrations
- [ ] Machine learning model training on real data

## Error Handling

The system includes comprehensive error handling:
- Invalid prompts return empty filters with error reasoning
- API failures are gracefully handled
- JSON parsing errors are caught and reported
- Network timeouts are managed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For questions or issues, please open an issue in the repository. 