# Context7 MCP Integration Guide

Context7 MCP (Model Context Protocol) provides up-to-date, version-specific documentation and code examples directly within AI-assisted coding workflows.

## Overview

Context7 MCP supercharges AI prompts with real-time documentation, eliminating hallucinated APIs and outdated examples by injecting live data into LLM interactions.

### Key Features
- **Real-Time Documentation**: Get the most recent official docs delivered directly into prompts
- **Version-Specific Examples**: Accurate examples for the exact library version you're using
- **Universal Compatibility**: Works with Claude Code, Cursor, VS Code, and other MCP clients
- **Productivity Boost**: Eliminates manual searches and reduces debugging time

## Prerequisites

- **Node.js**: v18.0.0 or higher (verified: v22.17.0 ✓)
- **NPX**: Available with Node.js installation
- **MCP-Compatible Client**: Claude Code, Cursor, VS Code, etc.

## Installation Methods

### 1. Project-Level Installation (Recommended)

The project includes a pre-configured MCP setup:

```bash
# Configuration file: .context7/mcp.json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "description": "Context7 MCP Server - Provides up-to-date code documentation",
      "transport": "stdio"
    }
  }
}
```

### 2. Direct Installation

```bash
# Test installation and help
npx -y @upstash/context7-mcp --help

# Run MCP server
npx -y @upstash/context7-mcp@latest
```

### 3. Claude Code Integration

```bash
# Add to Claude Code MCP configuration
claude mcp add context7 -- npx -y @upstash/context7-mcp --api-key YOUR_API
```

### 4. Alternative Runtime Support

#### For Bun users:
```json
{
  "mcpServers": {
    "context7": {
      "command": "bunx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

#### For Deno users:
```json
{
  "mcpServers": {
    "context7": {
      "command": "deno",
      "args": ["run", "--allow-net", "npm:@upstash/context7-mcp"]
    }
  }
}
```

## Configuration Options

### Transport Modes
- **stdio**: Standard input/output communication (default)
- **http**: HTTP-based communication on specified port

### Server Options
```bash
npx @upstash/context7-mcp [options]

Options:
  --transport <stdio|http>  transport type (default: "stdio")
  --port <number>           port for HTTP transport (default: "3000")
  --api-key <key>           API key for authentication and higher rate limits
  -h, --help                display help for command
```

## Usage

### Basic Usage
Add `use context7` to any prompt to access real-time documentation:

```
How do I use the latest Python asyncio features? use context7
```

```
What's the correct syntax for React Server Components? use context7
```

### In String-Multitool Development Context
```
How should I implement async transformations in Python 3.13? use context7
```

```
What's the recommended way to handle type hints with Protocol classes? use context7
```

## Benefits for String-Multitool Development

### 1. **Modern Python Features**
- Get up-to-date Python 3.13 documentation
- Latest asyncio, typing, and dataclass features
- Current best practices for type annotations

### 2. **Library-Specific Documentation**
- Fresh PyInstaller packaging methods
- Latest pytest testing patterns
- Current SQLAlchemy ORM approaches

### 3. **Cross-Platform Compatibility**
- Windows-specific Python development tips
- Cross-platform file handling best practices
- Unicode handling recommendations

## Troubleshooting

### Common Issues

#### Node.js Version
Ensure Node.js v18.0.0+ is installed:
```bash
node --version  # Should show v18.0.0 or higher
```

#### Network Issues
Context7 requires internet access to fetch real-time documentation.

#### Rate Limits
Consider using an API key for higher rate limits:
```bash
npx @upstash/context7-mcp --api-key YOUR_UPSTASH_API_KEY
```

### Testing Installation
```bash
# Test MCP server startup
npx -y @upstash/context7-mcp@latest --transport stdio
# Should output: "Context7 Documentation MCP Server running on stdio"
```

## Integration Status

- ✅ **Installed**: Context7 MCP v2025
- ✅ **Configured**: Project-level MCP configuration
- ✅ **Tested**: Server startup successful
- ✅ **Documented**: Usage guidelines established

## Next Steps

1. **Use in Prompts**: Start adding `use context7` to development questions
2. **API Key Setup**: Consider getting Upstash API key for higher rate limits
3. **Team Integration**: Share configuration with team members
4. **Client Configuration**: Set up in preferred IDE (Cursor, VS Code, etc.)

## Related Resources

- [Context7 GitHub Repository](https://github.com/upstash/context7)
- [Upstash Context7 Blog](https://upstash.com/blog/context7-mcp)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

---

*Last updated: 2025-09-11*