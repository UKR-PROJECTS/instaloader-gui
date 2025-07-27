# Contributing to insta-downloader-gui

Thank you for your interest in contributing to insta-downloader-gui! We welcome contributions from everyone and appreciate your help in making this PyQt6-based media downloader better for the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [ujjwalkrai@gmail.com](mailto:ujjwalkrai@gmail.com).

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:
- A GitHub account
- Git installed on your local machine
- Python 3.8 or higher
- Basic knowledge of PyQt6 and GUI application development
- Understanding of Instagram's structure and media handling

### First Time Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/insta-downloader-gui.git
   cd insta-downloader-gui
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/uikraft-hub/insta-downloader-gui.git
   ```
4. Install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Core Functionality**: Enhance media downloading capabilities and features.
- **UI/UX Improvements**: Improve the PyQt6 interface and user experience.
- **Performance Optimization**: Optimize download speed, memory usage, and concurrency.
- **Error Handling**: Improve error handling and user feedback mechanisms.
- **Testing**: Add comprehensive tests for downloading and UI functionality.
- **Documentation**: Improve guides, API documentation, and usage examples.
- **Bug Reports**: Help us identify and fix downloading or UI issues.
- **Feature Requests**: Suggest new Instagram media sources or download options.
- **Platform Support**: Add support for new Instagram URL formats or media types.

### Before You Start

1. Check existing [issues](https://github.com/uikraft-hub/insta-downloader-gui/issues) and [pull requests](https://github.com/uikraft-hub/insta-downloader-gui/pulls) to avoid duplicates.
2. For major changes or new features, please open an issue first to discuss your proposed changes.
3. Make sure your contribution aligns with the project's goal of providing a reliable Instagram media downloader.
4. Test your changes with various Instagram URLs.

## Development Setup

### Local Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a new branch for your feature or improvement:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Running the Application

1. Start the application:
   ```bash
   python src/main.py
   ```

2. Test with various Instagram URLs.

## Coding Standards

### General Guidelines

- Write clean, readable, and well-documented Python code.
- Follow PEP 8 style guidelines.
- Use type hints for function parameters and return values.
- Handle errors gracefully with proper exception handling.
- Log important events and errors for debugging.
- Respect Instagram's robots.txt and rate limiting.

### Python Standards

#### Code Style
- Use a consistent code style.
- Use meaningful variable and function names.
- Add docstrings for all public functions and classes.
- Follow PEP 8 naming conventions.

#### Architecture Guidelines
- Separate concerns: UI logic in the `ui` package, download logic in the `core` package.
- Use utility functions in the `utils` package for common operations.
- Keep the main application entry point clean in `main.py`.
- Implement proper error handling and user feedback.

### Scraping Ethics and Guidelines

- **Respect Rate Limits**: Implement appropriate delays between requests.
- **User-Agent Headers**: Use appropriate user-agent strings.
- **Error Handling**: Handle HTTP errors, network timeouts, and parsing errors.
- **Content Validation**: Verify downloaded content integrity.
- **Legal Compliance**: Ensure scraping practices comply with terms of service.

### PyQt6 UI Guidelines

- **Responsive Design**: Ensure UI works on different screen sizes.
- **Progress Feedback**: Show progress for long-running operations.
- **Error Messages**: Display clear, actionable error messages.
- **Input Validation**: Validate Instagram URLs before processing.

## Testing Guidelines

### Test Structure

Tests are located in the `tests/` directory.

### Running Tests

```bash
# Run all tests
pytest
```

### Test Guidelines

- Write tests for all new functionality.
- Test both success and failure scenarios.
- Mock external API calls and network requests.
- Test with various Instagram URL formats.
- Include edge cases and error conditions.

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

### Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Examples

```
feat(downloader): add support for Instagram story downloads
fix(ui): resolve progress bar not updating during batch downloads
perf(downloader): optimize concurrent download processing
docs: update usage examples with new Instagram URL formats
test(downloader): add comprehensive URL validation tests
```

## Pull Request Process

### Before Submitting

1. Ensure your branch is up to date with the main branch:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Run the full test suite:
   ```bash
   pytest
   ```

3. Test the application manually with various Instagram URLs.

4. Update documentation if necessary.

### Submitting Your Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a pull request from your fork to the main repository.

3. Fill out the pull request template completely.

4. Include testing information and sample Instagram URLs used for testing.

## Issue Guidelines

### Before Creating an Issue

1. Search existing issues to avoid duplicates.
2. Test with the latest version of the application.
3. Gather relevant information (URLs, error messages, screenshots).
4. Try to reproduce the issue consistently.

### Bug Reports

When reporting a bug, please include:

- **Bug Description**: Clear and concise description of the issue.
- **Instagram URL**: The specific Instagram URL that's causing issues.
- **Steps to Reproduce**: Detailed steps to reproduce the issue.
- **Expected Behavior**: What should happen.
- **Actual Behavior**: What actually happens.
- **Error Messages**: Any error messages or logs.
- **Environment**: Operating system, Python version.
- **Screenshots**: UI screenshots showing the issue.

### Feature Requests

When requesting a new feature, please include:

- **Feature Description**: Clear description of the proposed feature.
- **Use Case**: Why is this feature needed? What problem does it solve?
- **Instagram Context**: Which Instagram features or URL types this relates to.
- **Proposed Implementation**: Your ideas for how this could be implemented.

## Community

### Getting Help

If you need help or have questions:

- Open an issue with the "question" label.
- Email us at [ujjwalkrai@gmail.com](mailto:ujjwalkrai@gmail.com).
- Check existing documentation in the `docs/` folder.
- Review the [USAGE.md](USAGE.md) for detailed usage instructions.

Thank you for contributing to insta-downloader-gui!
