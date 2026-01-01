# Conversation to Logseq

> Convert Perplexity and VS Code conversations into Logseq-compatible notes with automatic domain classification and duplicate detection.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/VioletFigueroa/conversation-to-logseq.git
cd conversation-to-logseq
pip install -r requirements.txt

# Convert conversations
python conversation_converter.py \
  --input-dir ~/path/to/conversations \
  --output-dir ./notes/conversations

# Preview first (dry run)
python conversation_converter.py \
  --input-dir ~/path/to/conversations \
  --output-dir ./notes/conversations \
  --dry-run
```

## Features

- 🤖 **Multi-Source Support**: Perplexity, VS Code Copilot, and generic conversations
- 🏷️ **Auto-Classification**: Cybersecurity domains (GRC, Risk, Threat Intel, SOC, etc.)
- 📋 **Logseq Ready**: YAML frontmatter, hierarchical tags, schema-compliant
- 🔍 **Smart Deduplication**: SHA256 hashing detects identical content
- 💾 **Resume Safe**: Safely rerun without recreating existing files
- 🎯 **Batch Processing**: Convert 1000+ conversations in seconds
- 📝 **Intelligent Titles**: Extracts meaningful titles from conversations

## Domain Classification

Automatically categorizes into 10+ cybersecurity domains:
- **GRC** - Governance, Risk, Compliance
- **Risk Management** - Assessment, analysis, vulnerability
- **Threat Intelligence** - MITRE ATT&CK, threat actors
- **Security Operations** - SIEM, SOC, incident response
- **Network Security** - Firewalls, IDS/IPS, Wireshark
- **Cryptography** - Encryption, certificates, PKI
- **Application Security** - OWASP, secure coding
- **Cloud Security** - AWS, Azure, containers
- **IAM** - Authentication, access control
- **Career** - Interviews, certifications, learning

## Output

All conversations in single flat directory with unique filenames:
```
output/
├── 2025-11-23_nist_rmf_implementation_abc12345.md
├── 2025-11-24_incident_response_planning_def67890.md
└── ... (1000+ notes with domains preserved in tags)
```

Domains stored as YAML tags for Logseq filtering:
```yaml
tags:
  - conversation
  - perplexity
  - activity/learning
  - grc
  - risk-management
  - NIST-RMF
```

## Performance

- Processing: 50-100 files/second
- Memory: ~50MB for 1,200+ conversations
- 1,200 Perplexity conversations: ~20-30 seconds

## Requirements

- Python 3.8+
- pip

## Installation

```bash
git clone https://github.com/VioletFigueroa/conversation-to-logseq.git
cd conversation-to-logseq
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Dry Run (Preview)
```bash
python conversation_converter.py \
  --input-dir ~/perplexity_exports \
  --output-dir ./notes \
  --dry-run
```

### Convert Directory
```bash
python conversation_converter.py \
  --input-dir ~/perplexity_exports \
  --output-dir ./notes
```

### Convert Single File
```bash
python conversation_converter.py \
  --input-file conversation.md \
  --output-dir ./notes
```

### Force Overwrite
```bash
python conversation_converter.py \
  --input-dir ~/chats \
  --output-dir ./notes \
  --force
```

## Documentation

For detailed usage, examples, and troubleshooting, see [README.md](README.md).

## License

MIT License - See [LICENSE](LICENSE) for details

## Author

Created by [Violet Figueroa](https://github.com/VioletFigueroa)

## Contributing

Pull requests welcome! Please maintain the existing code style and add tests for new features.
