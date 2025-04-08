# Swarm Prompt Validation System

A sophisticated AI system for processing and analyzing PDF documents using a Swarm architecture. This system employs multiple specialized AI agents working together in a coordinated workflow to enhance user prompts, process document content, validate responses, and deliver high-quality answers.

## Core Architecture

The system is built using a **Swarm AI architecture** with specialized nodes that communicate through transfer functions, creating a flexible and robust processing pipeline.

### Key Components

- **Orchestrator**: Central coordinator that initializes nodes, creates agents, defines transfer functions, and manages the overall flow
- **Nodes**: Specialized components with specific responsibilities in the processing pipeline
- **Agents**: AI agents with specific instructions and functions for each node
- **Transfer Functions**: Communication pathways that allow agents to pass context between nodes

## Node Flow Architecture

The system follows a defined node flow pattern:

1. **Manager Node** ➡️ **Enhancement Node** ➡️ **Processing Node** ➡️ **Validation Node** ➡️ **Completion Node**
   
   or
   
2. **Manager Node** ➡️ **Enhancement Node** ➡️ **Processing Node** ➡️ **Validation Node** ➡️ **Review Node** ➡️ **Manager Node**

### Detailed Node Responsibilities

#### Manager Node
- **Primary Role**: Entry point and workflow coordinator
- **Responsibilities**:
  - Receives initial PDF content and user prompt
  - Performs initial validation and preprocessing
  - Manages the flow between different processing stages
  - Handles error conditions and rerouting
  - Tracks node history and system state
- **Output**: Structured context with summary and metadata

#### Enhancement Node
- **Primary Role**: Improves and structures user prompts
- **Responsibilities**:
  - Analyzes the user's original prompt and PDF content
  - Creates enhanced, detailed prompts with specific requirements
  - Defines content structure with sections and formatting guidelines
  - Clarifies ambiguous aspects of the original prompt
  - Specifies required information and citation formats
- **Output**: Enhanced prompt and structured content outline

#### Processing Node
- **Primary Role**: Analyzes documents and extracts information
- **Responsibilities**:
  - Processes PDF content based on enhanced prompts
  - Extracts key information and relevant quotes
  - Organizes content into structured sections
  - Creates draft outlines for the response
  - Identifies important topics and themes
- **Output**: Structured content with extracted information and draft outline

#### Validation Node
- **Primary Role**: Ensures accuracy and quality
- **Responsibilities**:
  - Validates extracted information against source PDF
  - Identifies factual errors or inconsistencies
  - Scores responses based on accuracy and completeness
  - Makes routing decisions based on validation results
  - Provides detailed feedback for improvements
- **Output**: Validation result with score, feedback, and issues
- **Routing Logic**:
  - Score ≥ 70: Routes to Completion Node
  - Score < 70: Routes to Review Node

#### Review Node
- **Primary Role**: Improves failed responses
- **Responsibilities**:
  - Reviews validation feedback and identified issues
  - Corrects errors, adds missing information
  - Ensures alignment with original prompt and PDF content
  - Improves structure and clarity
  - Sends corrected content back for revalidation
- **Output**: Revised content with corrections

#### Completion Node
- **Primary Role**: Finalizes and formats the response
- **Responsibilities**:
  - Creates polished, final response from validated content
  - Formats according to specified structure
  - Ensures all requirements are met
  - Adds processing summary and metadata
  - Delivers the final answer
- **Output**: Final, formatted response ready for user consumption

## Orchestrator

The orchestrator is the central control system that coordinates all nodes and their interactions. Key responsibilities include:

1. **Initialization**: Creates all node instances in proper dependency order
2. **Connection Management**: 
   - Creates an available nodes dictionary for all nodes to access each other
   - Defines transfer functions for inter-node communication
   - Creates agents for each node with appropriate functions
3. **Flow Control**: 
   - Tracks node history and processing flow
   - Logs all transfers between nodes
   - Maintains context throughout the processing chain
4. **Error Handling**: 
   - Captures and processes errors from any node
   - Ensures graceful failure and appropriate error messages
5. **Process Execution**:
   - Initiates the processing flow with the manager node
   - Collects and returns final results with metadata

## How the System Works

1. **Initialization**:
   - Orchestrator creates all nodes
   - Transfer functions are defined for node communication
   - Agents are created for each node

2. **Processing Flow**:
   - User provides PDF content and prompt
   - Manager node receives input and validates
   - Enhancement node improves the prompt
   - Processing node extracts relevant information
   - Validation node checks for accuracy
   - Based on validation:
     - If passed: Completion node finalizes response
     - If failed: Review node corrects issues, then back to validation

3. **Output**:
   - Final, validated response
   - Processing metadata (node history, timing, etc.)
   - Structured content that addresses the user's prompt

## Technical Implementation

The system is built using:
- Python for core functionality
- Swarm AI framework for agent architecture
- Structured logging for debugging and monitoring
- JSON-based context passing between nodes
- Environment-based configuration

## Setup and Usage

### Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Running the System

Basic usage:
```bash
python main.py
```

The system will:
1. Ask for a PDF file path (or use default sample)
2. Ask for a user prompt (or use default)
3. Process the PDF through the node pipeline
4. Display the result and save to a JSON file

## Extending the System

### Adding a New Node

1. Create a new node class inheriting from `NodeBase`
2. Implement the required methods and properties
3. Add the node to the Orchestrator's initialization process
4. Define transfer functions to and from the new node
5. Update the agent creation logic

### Customizing Processing Logic

Each node can be customized by modifying:
- The instructions provided to the agent
- The functions available to the agent
- The validation and processing logic
- The context structure and requirements

## Debugging and Monitoring

The system includes extensive logging throughout the pipeline:
- Node initialization and status
- Transfer between nodes with context details
- Processing results and metadata
- Error conditions and handling

Logs are saved to both console and file for easy debugging.

## Use Cases

This system is ideal for:
- Document analysis and information extraction
- Generating comprehensive answers from technical documents
- Validating AI-generated content against source material
- Creating structured responses to user queries about document content

## License

This project is licensed under the MIT License. See the LICENSE file for details.

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

## Acknowledgments

- Swarm AI framework
- AWS Lambda
- Python community 