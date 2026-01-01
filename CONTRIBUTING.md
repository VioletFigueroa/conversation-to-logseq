# Contributing to conversation-to-logseq

Thank you for your interest in contributing! This guide explains how to contribute to the project.

## Code of Conduct

Be respectful, inclusive, and professional.

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### Local Setup

```bash
git clone https://github.com/VioletFigueroa/conversation-to-logseq.git
cd conversation-to-logseq
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Testing Your Changes

```bash
python3 conversation_converter.py --input-dir ./test-data --output-dir ./test-output
```

## Making Changes

### Code Style

- Follow PEP 8 Python standards
- Use meaningful variable names
- Add docstrings for functions
- Include comments for complex logic

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type: short description

Longer explanation if needed
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat: add domain classification`
- `fix: handle duplicate detection correctly`
- `docs: update quickstart`

### Testing

- Test your changes with sample data
- Verify output format is correct
- Check YAML frontmatter generation
- Test with various conversation sizes

## Submitting Changes

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test thoroughly
5. Commit with descriptive messages
6. Push to your fork
7. Open a Pull Request with:
   - Clear title
   - Description of changes
   - Why the change is needed
   - Link to related issues if any

### PR Checklist

- [x] Code follows PEP 8
- [x] Changes are tested
- [x] Documentation updated (if needed)
- [x] Commit messages are clear
- [x] No breaking changes (or documented)

## Areas for Contribution

### Code

- [ ] Performance improvements
- [ ] New domain categories
- [ ] Better duplicate detection
- [ ] Error handling improvements
- [ ] Support for more input formats

### Documentation

- [ ] Clarify existing docs
- [ ] Add more examples
- [ ] Fix typos
- [ ] Improve troubleshooting

### Community

- [ ] Help answer issues
- [ ] Share use cases
- [ ] Provide feedback
- [ ] Report bugs

## Reporting Issues

Include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS
- Error messages/stack traces

## Questions?

- Check [docs/](./docs/) for documentation
- Read [EXAMPLES.md](./docs/EXAMPLES.md) for usage
- Open an issue for help

## License

By contributing, you agree your contributions are licensed under MIT License.

## Recognition

Contributors will be:
- Added to acknowledgments in README
- Mentioned in release notes
- Credited in git history

Thank you! 🎉
