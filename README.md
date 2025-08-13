# Trello MCP Server

A Model Context Protocol (MCP) server for creating Trello cards and lists.

## Features

- **`create_trello_card`**: Create a card in a specific Trello board
- **`create_trello_list`**: Create a new list in a specific Trello board
- **`boards://all`**: Resource to list all available boards
- **`lists://{board_name}`**: Resource to list all lists in a specific board

## Setup

### 1. Get Trello Credentials

1. Visit [Trello Developer Portal](https://developer.atlassian.com/cloud/trello/)
2. Create a new application
3. Get your API Key and Token

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit the `.env` file with your credentials:

```bash
# Trello API Credentials
TRELLO_API_KEY=your_api_key_here
TRELLO_TOKEN=your_token_here
```

Alternatively, you can set environment variables directly:

```bash
export TRELLO_API_KEY="your_api_key_here"
export TRELLO_TOKEN="your_token_here"
```

### 3. Install and Setup Enviroment

Install uv: `brew install uv`
Create (venv) enviroment: `uv venv`
Activate enviroment: `source .venv/bin/activate`
Install Dependencies: `uv sync`

## Usage

### Run the MCP Server
```bash
uv run mcp dev server.py
```

Inspector will open in a browser tab. you can connect and test the tools and resources available.

### Integrate with MCP Client (Claude Desktop)
```bash
uv run mcp install --with-editable server.py -f .env
```


## Claude Desktop Examples

Once integrated with Claude Desktop, you can use natural language to interact with your Trello boards:

### List Boards and Lists

**"Show me all my Trello boards"**
- Claude will use the `boards://all` resource to list all available boards

**"What lists are in my 'Project Alpha' board?"**
- Claude will use the `lists://Project Alpha` resource to show all lists in that board

**"Show me the structure of my 'Work Tasks' board"**
- Claude will fetch both board information and its lists

### Create Lists

**"Create a new list called 'In Progress' in my 'Project Alpha' board"**
- Claude will use `create_trello_list` with board_name="Project Alpha" and list_name="In Progress"

**"Add an 'Urgent' list at the top of my 'Work Tasks' board"**
- Claude will use `create_trello_list` with position="top"

**"Create a 'Review' list in my 'Personal Projects' board"**
- Claude will create the list in the default position (bottom)

### Create Cards

**"Add a new task called 'Fix login bug' to my 'Project Alpha' board"**
- Claude will use `create_trello_card` with the card name and board

**"Create a card titled 'Implement user authentication' with description 'Add JWT token system and user registration' in the 'To Do' list of my 'Work Tasks' board"**
- Claude will create a detailed card with description and specific list

**"Add a bug report card to my 'Issues' list in the 'Project Beta' board"**
- Claude will create a card in the specified list

**"Create a task called 'Update documentation' in my 'Project Alpha' board with description 'Update API docs and README files'"**
- Claude will create a card with both title and description

### Complex Workflows

**"Set up a new project board structure for 'Website Redesign' with lists: 'Backlog', 'In Progress', 'Review', and 'Done'"**
- Claude will create multiple lists in sequence

**"Add these tasks to my 'Work Tasks' board: 'Design homepage', 'Implement navigation', 'Add contact form'"**
- Claude will create multiple cards in the specified board

**"Create a sprint planning board with lists for 'This Sprint', 'Next Sprint', and 'Backlog', then add some initial tasks"**
- Claude will create the board structure and populate it with tasks

### Examples

#### Create a Trello List

```python
# Create a simple list
create_trello_list(
    board_name="My Project",
    list_name="In Progress"
)

# Create a list at the top
create_trello_list(
    board_name="My Project",
    list_name="Urgent",
    position="top"
)
```

#### Create a Trello Card

```python
# Create a simple card
create_trello_card(
    board_name="My Project",
    card_name="New task"
)

# Create a card with description
create_trello_card(
    board_name="My Project",
    card_name="Implement login",
    description="Create JWT authentication system"
)

# Create a card in a specific list
create_trello_card(
    board_name="My Project",
    card_name="Bug fix",
    description="Fix validation error",
    list_name="In Progress"
)
```

## Parameters

### create_trello_list
- `board_name` (required): Trello board name
- `list_name` (required): Name of the list to create
- `position` (optional): Position ('top', 'bottom', or number)

### create_trello_card
- `board_name` (required): Trello board name
- `card_name` (required): Card title
- `description` (optional): Card description
- `list_name` (optional): List name (defaults to first list)

## Response Format

### Success
```json
{
    "success": true,
    "card_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "card_name": "New task",
    "card_url": "https://trello.com/c/64f8a1b2c3d4e5f6a7b8c9d0",
    "board_name": "My Project",
    "list_name": "To Do"
}
```

### Error
```json
{
    "success": false,
    "error": "Board 'My Project' not found"
}
```

## Tips for Claude Desktop Usage

### Best Practices

1. **Be Specific**: Mention the exact board name when creating cards or lists
2. **Use Descriptive Names**: Give cards meaningful titles and descriptions
3. **Specify Lists**: When creating cards, mention which list they should go in
4. **Batch Operations**: Ask Claude to create multiple related items at once

### Common Patterns

**Project Setup:**
- "Create a new project board structure for [project name]"
- "Set up a Kanban board with standard lists"

**Task Management:**
- "Add these tasks to my [board name] board"
- "Create a bug report in my [board name] board"
- "Move tasks to the 'In Progress' list"

**Sprint Planning:**
- "Create a sprint planning board for [sprint name]"
- "Add user stories to the backlog"

### Troubleshooting

- If Claude doesn't find your board, check the exact spelling
- If a list doesn't exist, ask Claude to create it first
- For complex workflows, break them into smaller requests

## Error Handling

The server includes robust error handling for:
- Boards not found
- Lists not found
- Duplicate lists
- API connectivity issues
- Invalid credentials
