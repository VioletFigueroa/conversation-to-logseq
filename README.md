# Conversation to Logseq

A Python CLI tool that converts Perplexity and VS Code chat conversations into Logseq-compatible notes with automatic domain classification, schema compliance, and duplicate detection.

## Features

- **Multi-Source Support**: Converts conversations from Perplexity AI and VS Code Copilot
- **Automatic Classification**: Detects cybersecurity domains (GRC, Risk Management, Threat Intelligence, SOC, etc.)
- **Logseq Integration**: Generates notes with YAML frontmatter following Logseq schema standards
- **Duplicate Detection**: Uses SHA256 hashing to identify and skip duplicate content
- **Resume Capability**: Builds index of existing files; safely rerun without recreating files
- **Intelligent Title Extraction**: Extracts meaningful titles from conversations instead of generic labels
- **Hierarchical Tagging**: Generates domain, activity type, and source tags for advanced filtering
- **Batch Processing**: Process hundreds or thousands of conversations in one command
- **Dry Run Mode**: Preview conversions before committing changes to disk

## Sample Output

Before (Raw conversation):
```markdown
User: What is NIST RMF and how do you implement it?
Assistant: NIST RMF stands for...
```

After (Logseq-integrated note):
```markdown
---
title: "How to implement NIST RMF in a small organization?"
domain: "conversations/grc"
type: "conversation"
source: "perplexity"
created: "2025-11-23"
tags:
  - conversation
  - perplexity
  - activity/learning
  - grc
  - risk-management
  - NIST-RMF
status: "converted"
---

# How to implement NIST RMF in a small organization?

**Date**: 2025-11-23
**Source**: Perplexity

---

## Conversation

**User**: What is NIST RMF and how...
**Assistant**: NIST RMF stands for...

---

## Related Topics

- [[Governance, Risk, and Compliance]]
- [[Risk Management]]
- [[NIST-RMF]]
```

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/VioletFigueroa/conversation-to-logseq.git
cd conversation-to-logseq

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Commands

#### Convert all conversations from a directory
```bash
python conversation_converter.py \
  --input-dir /path/to/perplexity_exports \
  --output-dir ./notes/conversations
```

#### Convert with dry-run (preview first)
```bash
python conversation_converter.py \
  --input-dir /path/to/chats \
  --output-dir ./notes/conversations \
  --dry-run
```

#### Convert a single file
```bash
python conversation_converter.py \
  --input-file conversation.md \
  --output-dir ./notes/conversations
```

#### Force overwrite existing files
```bash
python conversation_converter.py \
  --input-dir /path/to/chats \
  --output-dir ./notes/conversations \
  --force
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `--input-dir DIR` | ✓ (or `--input-file`) | Directory with conversation files |
| `--input-file FILE` | ✓ (or `--input-dir`) | Single conversation file |
| `--output-dir DIR` | ✓ | Output directory for converted notes |
| `--pattern PATTERN` | | File glob pattern (default: `*.md`) |
| `--recursive` | | Search directories recursively (default: True) |
| `--dry-run` | | Preview conversions without writing |
| `--force` | | Overwrite existing files and duplicates |
| `--no-skip` | | Don't skip existing files (by default, existing files are skipped) |

## How It Works

### 1. Source Detection
Automatically identifies if conversation is from:
- **Perplexity AI** - Detects Perplexity branding/format
- **VS Code Copilot** - Detects GitHub Copilot markers
- **General** - Fallback for other formats

### 2. Metadata Extraction
- **Title**: Extracts first meaningful user question (skips "hello", "test")
- **Date**: Parses from content or file modification time
- **Topics**: Identifies frameworks (NIST, MITRE ATT&CK, ISO 27001)

### 3. Domain Classification
Automatically categorizes into cybersecurity domains:
- **GRC** - Governance, Risk, Compliance
- **Risk Management** - Risk assessment, vulnerability analysis
- **Threat Intelligence** - MITRE ATT&CK, threat actors, IOCs
- **Security Operations** - SIEM, SOC, incident response
- **Network Security** - Firewalls, IDS/IPS, network analysis
- **Cryptography** - Encryption, certificates, SSL/TLS
- **Application Security** - OWASP, secure coding
- **Cloud Security** - AWS, Azure, containers
- **IAM** - Authentication, access control
- **Career** - Resume, interviews, certifications

### 4. Activity Classification
Tags conversations by type:
- **learning** - Tutorials, explanations, "how to"
- **research** - Analysis, comparisons, investigations
- **problem-solving** - Debugging, troubleshooting
- **planning** - Strategy, roadmaps, organization
- **reference** - Lists, documentation

### 5. Duplicate Detection
- Computes SHA256 hash of conversation content
- Maintains index of existing notes
- Skips identical content (even with different filenames)
- Safely resume interrupted conversions

### 6. Output Organization
All files in a single flat directory with unique filenames:
```
output/
├── 2025-11-23_nist_rmf_implementation_abc12345.md
├── 2025-11-24_incident_response_planning_def67890.md
├── 2025-11-25_encryption_best_practices_ghi24680.md
└── ... (all 1000+ notes in one directory)
```

Domains are preserved as tags in YAML frontmatter for Logseq filtering.

## Output Format

Each converted note includes:

### YAML Frontmatter
```yaml
---
title: "[Title]"
domain: "conversations/[domain]"
type: "conversation"
source: "[perplexity|vscode_copilot|general]"
source_file: "[original_filename]"
created: "[YYYY-MM-DD]"
tags:
  - conversation
  - [domain tags]
  - activity/[activity_type]
  - source/[source_type]
status: "converted"
---
```

### Sections
1. **Title & Metadata** - Date and source
2. **Conversation** - Full chat with User/Assistant markers
3. **Related Topics** - Links to domain pages and concepts
4. **Navigation** - Links to knowledge base

## Statistics & Performance

### Benchmarks
- **Processing Speed**: ~50-100 files/second
- **Memory Usage**: ~50MB for 1,200 conversations
- **Deduplication**: Minimal overhead; single index pass

### Example Results
```
📊 Conversion Summary
============================================================
✅ Successfully converted: 1200
⏭️  Skipped (existing): 0
🔁 Skipped (duplicate): 0
❌ Failed: 0

✨ Created 1200 notes

By domain (via tags):
   • grc: 972 notes
   • security-operations: 1110 notes
   • threat-intelligence: 683 notes
   • network-security: 896 notes
   • cryptography: 710 notes
   • cloud-security: 633 notes
   • iam: 663 notes
   • application-security: 118 notes
   • risk-management: 422 notes
   • career: 678 notes
```

## Integration with Logseq

1. **Point Logseq to Output Directory**
   - In Logseq settings, add your output directory as a graph

2. **Filter by Domain**
   ```logseq
   Query: #grc
   Query: #security-operations
   Query: #activity/learning
   ```

3. **Cross-Link with Existing Notes**
   - Backlinks automatically created via `[[Domain Name]]` syntax
   - Links to domain index pages for easy navigation

4. **Full-Text Search**
   - Search conversations by topic, keyword, or concept
   - Example: `search: "NIST RMF"`

## Troubleshooting

### "File already exists" messages
- **Expected behavior**: Script skips existing files by default
- **To overwrite**: Use `--force` flag
- **To recreate**: Delete output directory first

### Poor title extraction (e.g., "Chat Session")
- **Cause**: Conversation doesn't start with clear question
- **Solution**: Script tries multiple fallback strategies
- **Manual fix**: Edit the generated file's title

### Wrong domain classification
- **Cause**: Content keywords match multiple domains
- **Solution**: Script uses primary domain; all others in tags
- **Manual fix**: Edit the generated file's domain in frontmatter

### Duplicate content warnings
- **Normal behavior**: Script detects identical conversations
- **Why**: Multiple exports of same conversation
- **Action**: Check paths shown in summary

## Project Status

- ✅ Converts Perplexity conversations
- ✅ Converts VS Code Copilot chats
- ✅ Duplicate detection and skipping
- ✅ Resume capability (safe reruns)
- ✅ Logseq schema compliance
- ✅ Batch processing (1000+ files)

### Future Enhancements
- [ ] Support for other AI chat platforms (ChatGPT, Claude, etc.)
- [ ] Configurable domain classification
- [ ] Export to other formats (Obsidian, OneNote)
- [ ] Web UI for batch conversion
- [ ] Incremental sync with Perplexity API

## Use Cases

### Personal Knowledge Management
Build a searchable archive of all your AI conversations organized by topic and domain.

### Security Team Knowledge Base
Share conversation insights with your team while maintaining domain classification.

### Learning & Research
Track your learning journey across different cybersecurity topics.

### Career Development
Reference past conversations about certifications, interviews, and career planning.

### Project Documentation
Extract technical discussions for project retrospectives and documentation.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## Author

Created by [Your Name] - Cybersecurity Analyst & Knowledge Management Enthusiast

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

## Related Projects

- [resume-automator](https://github.com/VioletFigueroa/resume-automator) - Automated resume generation
- [knowledge-pipeline-public](https://github.com/VioletFigueroa/knowledge-pipeline-public) - Knowledge base automation

---

**Made with ❤️ for cybersecurity professionals and lifelong learners**
