# Swarm Prompt Validation System

A specialized system for processing PDF documents and user prompts using a Swarm AI architecture. This system analyzes PDF content, enhances user prompts, and generates comprehensive responses through a multi-node processing pipeline.

## Features

- PDF text processing and analysis
- User prompt enhancement
- Multi-stage validation pipeline
- Error handling and logging
- AWS Lambda integration ready

## Architecture

The system is built using a Swarm AI architecture with the following components:

- **ManagerNode**: Entry point for processing, validates inputs
- **EnhancementNode**: Enhances user prompts with PDF context
- **ProcessingNode**: Generates responses based on enhanced prompts
- **ValidationNode**: Validates generated responses
- **ReviewNode**: Reviews and improves responses when needed
- **CompletionNode**: Finalizes and formats responses

## Directory Structure

```
swarm_prompt_validation/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── base_node.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── pdf_context.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── manager_node.py
│   │   ├── enhancement_node.py
│   │   ├── processing_node.py
│   │   ├── validation_node.py
│   │   ├── review_node.py
│   │   └── completion_node.py
│   └── orchestrator.py
├── utils/
│   ├── __init__.py
│   └── logging_config.py
├── main.py
├── requirements.txt
├── prompt.json
└── compost_tutorial.json
```

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Local Testing

Run the system with test documents:
```bash
python main.py
```

### AWS Lambda Deployment

The system is designed to be deployed as an AWS Lambda function. The `lambda_handler` function in `main.py` serves as the entry point.

Example Lambda event:
```json
{
    "pdf_text": "Your PDF content here",
    "user_prompt": "Your question here",
    "additional_context": {
        "source": "document_source",
        "timestamp": "2024-03-20T12:00:00Z"
    }
}
```

## Development

### Adding New Nodes

1. Create a new node class in `app/nodes/`
2. Implement required methods from `NodeBase`
3. Update `Orchestrator` to include the new node

### Testing

Run tests:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Swarm AI framework
- AWS Lambda
- Python community 