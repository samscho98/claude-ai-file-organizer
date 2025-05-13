# Example of Structure Visualization

```json
{
  "name": "sample-project",
  "type": "directory",
  "children": [
    {
      "name": "src",
      "type": "directory",
      "children": [
        {
          "name": "main.py",
          "type": "file",
          "content": "# Main entry point\ndef main():\n    print(\"Hello, world!\")\n\nif __name__ == \"__main__\":\n    main()\n"
        },
        {
          "name": "utils.py",
          "type": "file",
          "content": "# Utility functions\ndef add(a, b):\n    return a + b\n"
        }
      ]
    },
    {
      "name": "README.md",
      "type": "file",
      "content": "# Sample Project\n\nThis is a sample project to demonstrate the Claude AI File Organizer.\n"
    },
    {
      "name": "config.ini",
      "type": "file",
      "content": "[settings]\npath=./sample-project\noutput_dir=output\n"
    }
  ]
}
```

This structure shows a sample project with its files and directories. The Claude AI File Organizer generates this type of structure for your project, including the content of selected files.

Key features of the structure:
- Preserves directory hierarchy
- Includes file content for important files
- JSON format for easy parsing

You can use this structure with Claude AI to get a comprehensive overview of your project.