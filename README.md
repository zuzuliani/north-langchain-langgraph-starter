# LangChain LangGraph Starter

A comprehensive starter template for building powerful applications with LangChain and LangGraph.

![image](https://github.com/user-attachments/assets/56410349-803d-46fb-b81d-4c1e9528a2d9)

## 📚 Introduction

This repository provides a structured foundation for developing applications that leverage the power of Large Language Models (LLMs) through LangChain, with advanced workflow orchestration using LangGraph.

### What is LangGraph?

LangGraph is an extension of LangChain that enables the creation of stateful, multi-actor applications using a graph-based framework. It allows you to:

- Build complex, cyclic workflows with multiple LLM agents
- Maintain state across interactions
- Create conditional logic and branching in your LLM applications
- Implement feedback loops and recursive improvement

## 🚀 Features

- Integration with LangChain for LLM operations
- Graph-based workflow management with LangGraph
- Easy-to-follow project structure
- Pre-configured environment setup
- Example workflows for common use cases
- Testing framework

## 📋 Prerequisites

- Python 3.9+
- pip or poetry for dependency management
- API key for LLM provider (OpenAI, Groq, etc.)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/rahulsamant37/langchain-langgraph-starter.git
cd langchain-langgraph-starter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GROQ_API_KEY=your_api_key_here
```

## 🏗️ Project Structure

```
langchain-langgraph-starter/
├── Tutorial_XX/
│   ├── chains/
│   └── Tutorial_XX_XX/
├── tests/
├── examples/
└── README.md
```

## 🔍 Understanding LangGraph

### Core Concepts

1. **Nodes**: 
   - Individual components in your workflow
   - Can be LLM calls, tools, or utility functions
   - Process inputs and produce outputs

2. **Edges**: 
   - Connections between nodes
   - Define the flow of data and execution
   - Can include conditional logic

3. **State**: 
   - Persistent information across the graph execution
   - Modifiable by nodes during execution
   - Allows for context preservation and decision-making

4. **Graph**: 
   - The complete workflow definition
   - Orchestrates execution of nodes based on the defined edges
   - Manages state transitions

### Basic LangGraph Example

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Define the state schema
class GraphState(TypedDict):
    input: str
    response: str

# Create nodes (functions)
def generate_response(state: GraphState) -> GraphState:
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt = ChatPromptTemplate.from_template("Answer this question: {input}")
    chain = prompt | llm
    response = chain.invoke({"input": state["input"]})
    return {"response": response.content}

# Create the graph
graph = StateGraph(GraphState)

# Add nodes
graph.add_node("generate_response", generate_response)

# Add edges
graph.set_entry_point("generate_response")
graph.add_edge("generate_response", END)

# Compile the graph
chain = graph.compile()

# Execute the graph
result = chain.invoke({"input": "What is LangGraph?"})
print(result["response"])
```

## 🔄 Advanced Patterns with LangGraph

### Multi-Agent Systems

LangGraph excels at coordinating multiple LLM agents to work together:

```python
from langgraph.graph import StateGraph

# Define multiple agent nodes
def researcher(state):
    # Research information
    return {"research_results": "..."}

def writer(state):
    # Write content based on research
    return {"draft": "..."}

def editor(state):
    # Edit and improve the draft
    return {"final_document": "..."}

# Define conditional routing
def should_continue_research(state):
    # Logic to determine if more research is needed
    if "enough_information" in state:
        return "writer"
    return "researcher"

# Create the graph
graph = StateGraph()
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)
graph.add_node("editor", editor)

# Add conditional edges
graph.add_conditional_edges("researcher", should_continue_research)
graph.add_edge("writer", "editor")
graph.add_edge("editor", END)

# Compile and run
chain = graph.compile()
```

### Feedback Loops

LangGraph supports recursive improvement through feedback loops:

```python
def evaluate_quality(state):
    # Assess the quality of current output
    quality_score = calculate_score(state["output"])
    return {"quality_score": quality_score}

def route_based_on_quality(state):
    if state["quality_score"] > 0.8:
        return "finalize"
    else:
        return "improve"

def improve(state):
    # Make improvements to the output
    return {"output": enhanced_version(state["output"])}

def finalize(state):
    # Finalize the output
    return {"final_result": state["output"]}

graph = StateGraph()
graph.add_node("evaluate", evaluate_quality)
graph.add_node("improve", improve)
graph.add_node("finalize", finalize)

graph.add_conditional_edges("evaluate", route_based_on_quality)
graph.add_edge("improve", "evaluate")
graph.add_edge("finalize", END)
```

## 📝 Example Use Cases

### 1. Conversational Agents

Build chatbots that can maintain context, ask follow-up questions, and provide coherent responses across multiple turns.

### 2. Research Assistants

Create systems that can search for information, synthesize findings, and generate comprehensive reports on complex topics.

### 3. Content Generation Pipelines

Develop workflows that brainstorm ideas, create drafts, edit content, and produce polished final outputs.

### 4. Decision Support Systems

Build applications that can analyze problems, evaluate options, and recommend solutions based on specified criteria.

## 🧪 Testing LangGraph Applications

```python
from langchain_core.messages import HumanMessage
from your_project.graphs import conversation_graph

def test_conversation_flow():
    graph = conversation_graph.compile()
    state = {"messages": [HumanMessage(content="Tell me about quantum computing")]}
    result = graph.invoke(state)
    
    # Assert expected behavior
    assert "response" in result
    assert len(result["messages"]) > 1
```

## 🔗 Integration with Other Tools

LangGraph works seamlessly with:

- **Vector Databases** (Chroma, Pinecone, etc.) for retrieval-augmented generation
- **Tool Calling** to interact with external APIs and services
- **Human-in-the-loop** workflows for expert oversight and intervention
- **Persistent Storage** for maintaining state across sessions

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph GitHub Repository](https://github.com/langchain-ai/langgraph)
- [LangSmith](https://smith.langchain.com/) for tracing and debugging

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## 🙏 Acknowledgements

- LangChain team for creating these powerful tools
- The open-source AI community
