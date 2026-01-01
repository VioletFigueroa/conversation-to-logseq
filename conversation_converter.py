#!/usr/bin/env python3
"""
Conversation to Logseq Note Converter

Converts Perplexity conversations and VS Code chat exports to Logseq-compatible 
notes with automatic domain classification, schema compliance, and duplicate detection.

Author: Violet Figueroa
License: MIT
"""

import argparse
import re
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import json


class ConversationConverter:
    """Convert conversation markdown files to Logseq notes with schema compliance."""
    
    # Domain classification keywords
    DOMAIN_KEYWORDS = {
        'grc': ['risk', 'compliance', 'governance', 'audit', 'nist', 'iso', 
                'regulatory', 'framework', 'control', 'policy'],
        'risk-management': ['risk assessment', 'risk analysis', 'vulnerability', 
                           'threat', 'cvss', 'rmf', 'mitigation'],
        'threat-intelligence': ['mitre', 'att&ck', 'threat', 'apt', 'threat actor',
                               'threat landscape', 'ioc', 'indicators'],
        'security-operations': ['siem', 'soc', 'log', 'monitoring', 'incident',
                               'detection', 'response', 'forensics'],
        'network-security': ['firewall', 'vpn', 'network', 'wireshark', 'nmap',
                            'packet', 'tcp', 'ids', 'ips'],
        'cryptography': ['encryption', 'cryptography', 'cipher', 'hash', 'ssl',
                        'tls', 'certificate', 'pki', 'rsa', 'aes'],
        'application-security': ['owasp', 'xss', 'sql injection', 'web security',
                                'secure coding', 'sast', 'dast'],
        'cloud-security': ['aws', 'azure', 'cloud', 'kubernetes', 'docker',
                          'container', 'serverless'],
        'iam': ['authentication', 'authorization', 'access control', 'identity',
               'rbac', 'mfa', 'sso', 'ldap'],
        'career': ['resume', 'interview', 'job', 'career', 'certification',
                  'learning', 'portfolio', 'skills']
    }
    
    # Activity type keywords
    ACTIVITY_KEYWORDS = {
        'learning': ['how to', 'what is', 'explain', 'tutorial', 'guide',
                    'learn', 'understanding'],
        'research': ['research', 'investigate', 'analyze', 'compare',
                    'review', 'study'],
        'problem-solving': ['error', 'fix', 'debug', 'troubleshoot', 'issue',
                           'problem', 'solution'],
        'planning': ['plan', 'strategy', 'roadmap', 'goals', 'project',
                    'organize', 'structure'],
        'reference': ['list', 'reference', 'documentation', 'guide',
                     'cheat sheet', 'quick reference']
    }
    
    def __init__(self, output_dir: Path):
        """Initialize converter and build index of existing files."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.converted = []
        self.skipped = []
        self.failed = []
        self.duplicates = []
        
        # Build hash index of existing files for deduplication
        self.existing_hashes: Dict[str, Path] = {}
        self.build_existing_index()
    
    def build_existing_index(self):
        """Build index of existing converted files by content hash."""
        if not self.output_dir.exists():
            return
        
        for md_file in self.output_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                # Hash the conversation section only (skip frontmatter)
                conv_match = re.search(r'## Conversation\n\n(.+?)(?:\n---|\Z)', 
                                      content, re.DOTALL)
                if conv_match:
                    content_hash = self.hash_content(conv_match.group(1))
                    self.existing_hashes[content_hash] = md_file
            except:
                pass
    
    def hash_content(self, content: str) -> str:
        """Generate SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def detect_source_type(self, content: str) -> str:
        """Detect if conversation is from Perplexity, VS Code, or other."""
        if 'perplexity' in content.lower()[:500]:
            return 'perplexity'
        elif 'github copilot' in content.lower()[:500]:
            return 'vscode_copilot'
        elif '```json' in content and 'conversation' in content.lower():
            return 'vscode_export'
        else:
            return 'general'
    
    def extract_title(self, content: str) -> str:
        """Extract or infer title from conversation."""
        lines = content.split('\n')
        
        # Look for first heading
        for line in lines[:20]:
            if line.startswith('# '):
                title = line[2:].strip()
                if title.lower() not in ['chat session', 'conversation', 'untitled']:
                    return title
            elif line.startswith('## '):
                title = line[3:].strip()
                if title.lower() not in ['chat session', 'conversation', 'untitled']:
                    return title
        
        # Look for question patterns (first substantial user question)
        user_questions = []
        for match in re.finditer(r'^(?:User|Q|Question):\s*(.+?)(?:\n|$)', 
                                content, re.MULTILINE | re.IGNORECASE):
            question = match.group(1).strip()
            # Skip meta questions
            if len(question) > 20 and not any(skip in question.lower() 
                                             for skip in ['how are you', 'hello', 'hi ', 'test']):
                user_questions.append(question)
                if len(user_questions) >= 1:
                    break
        
        if user_questions:
            title = user_questions[0]
            # Clean up and truncate
            title = re.sub(r'[*_`]', '', title)  # Remove markdown
            return title[:80] + ('...' if len(title) > 80 else '')
        
        # Use first substantial line
        for line in lines[:30]:
            line = line.strip()
            if (len(line) > 20 and 
                not line.startswith(('---', '```', '>', '#', 'Date:', 'Source:')) and
                line.lower() not in ['chat session', 'conversation']):
                return line[:80] + ('...' if len(line) > 80 else '')
        
        return "Conversation"
    
    def extract_date(self, filepath: Path, content: str) -> str:
        """Extract conversation date from content or filename."""
        # Try to find date in content
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content[:500])
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse and normalize
                    if '-' in date_str:
                        return date_str
                except:
                    pass
        
        # Try filename
        filename_date = re.search(r'(\d{4}-\d{2}-\d{2})', filepath.name)
        if filename_date:
            return filename_date.group(1)
        
        # Use file modification time
        mtime = filepath.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    
    def classify_domains(self, content: str) -> List[str]:
        """Classify conversation into relevant domains."""
        content_lower = content.lower()
        matched_domains = []
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    matched_domains.append(domain)
                    break
        
        return matched_domains if matched_domains else ['general']
    
    def classify_activity(self, content: str) -> str:
        """Classify the type of activity/conversation."""
        content_lower = content.lower()
        
        for activity, keywords in self.ACTIVITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return activity
        
        return 'reference'
    
    def extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics/concepts from conversation."""
        topics = []
        content_lower = content.lower()
        
        # Check for specific frameworks/tools
        if 'nist' in content_lower:
            if 'rmf' in content_lower:
                topics.append('NIST-RMF')
            if '800-53' in content_lower:
                topics.append('NIST-800-53')
            if 'csf' in content_lower or 'cybersecurity framework' in content_lower:
                topics.append('NIST-CSF')
        
        if 'mitre' in content_lower or 'att&ck' in content_lower:
            topics.append('MITRE ATT&CK')
        
        if 'cvss' in content_lower:
            topics.append('CVSS')
        
        if 'iso 27001' in content_lower or 'iso27001' in content_lower:
            topics.append('ISO 27001')
        
        # Check for tools
        tools = ['wireshark', 'nmap', 'splunk', 'metasploit', 'burp suite',
                'snort', 'suricata', 'zeek', 'elk', 'siem']
        for tool in tools:
            if tool in content_lower:
                topics.append(tool.title())
        
        return topics
    
    def generate_tags(self, domains: List[str], activity: str, 
                     source_type: str) -> List[str]:
        """Generate hierarchical tags for the note."""
        tags = ['conversation', source_type]
        
        # Add activity tag
        tags.append(f'activity/{activity}')
        
        # Add domain tags
        for domain in domains:
            tags.append(domain)
        
        # Add source tag
        tags.append(f'source/{source_type}')
        
        return sorted(list(set(tags)))
    
    def create_related_links(self, domains: List[str], topics: List[str]) -> str:
        """Generate links to related domain pages and topics."""
        links = []
        
        # Link to domain pages
        domain_map = {
            'grc': '[[Governance, Risk, and Compliance]]',
            'risk-management': '[[Risk Management]]',
            'threat-intelligence': '[[Threat Intelligence and Hunting]]',
            'security-operations': '[[Security Operations]]',
            'network-security': '[[Network Security]]',
            'cryptography': '[[Cryptography]]',
            'application-security': '[[Application Security]]',
            'cloud-security': '[[Cloud Security]]',
            'iam': '[[Identity and Access Management (IAM)]]',
            'career': '[[Career Development]]'
        }
        
        for domain in domains:
            if domain in domain_map:
                links.append(domain_map[domain])
        
        # Link to specific topics
        for topic in topics:
            links.append(f'[[{topic}]]')
        
        return links
    
    def clean_content(self, content: str) -> str:
        """Clean and format conversation content."""
        # Remove multiple blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Clean up conversation markers
        content = re.sub(r'^(User|Assistant|Q|A):\s*', r'**\1**: ', 
                        content, flags=re.MULTILINE)
        
        # Preserve code blocks
        # (already in markdown format, no changes needed)
        
        return content.strip()
    
    def generate_frontmatter(self, title: str, date: str, domains: List[str],
                            tags: List[str], source_type: str,
                            source_file: str) -> str:
        """Generate YAML frontmatter."""
        primary_domain = domains[0] if domains else 'general'
        
        frontmatter = f"""---
title: "{title}"
domain: "conversations/{primary_domain}"
type: "conversation"
source: "{source_type}"
source_file: "{source_file}"
created: "{date}"
tags:
"""
        for tag in tags:
            frontmatter += f"  - {tag}\n"
        
        frontmatter += 'status: "converted"\n---\n'
        return frontmatter
    
    def convert_file(self, filepath: Path, dry_run: bool = False, 
                    skip_existing: bool = True, force: bool = False) -> bool:
        """Convert a single conversation file."""
        print(f"\n📄 Processing: {filepath.name}")
        
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            self.failed.append(str(filepath))
            return False
        
        # Check for duplicate content
        conv_match = re.search(r'## Conversation\n\n(.+?)(?:\n---|\Z)', 
                              content, re.DOTALL)
        if conv_match:
            content_hash = self.hash_content(conv_match.group(1))
        else:
            content_hash = self.hash_content(content)
        
        if content_hash in self.existing_hashes and not force:
            existing_file = self.existing_hashes[content_hash]
            print(f"   ⏭️  Duplicate content exists: {existing_file.name}")
            self.duplicates.append((str(filepath), str(existing_file)))
            return False
        
        # Detect source type
        source_type = self.detect_source_type(content)
        print(f"   🔍 Source: {source_type}")
        
        # Extract metadata
        title = self.extract_title(content)
        date = self.extract_date(filepath, content)
        domains = self.classify_domains(content)
        activity = self.classify_activity(content)
        topics = self.extract_key_topics(content)
        tags = self.generate_tags(domains, activity, source_type)
        
        print(f"   📝 Title: {title}")
        print(f"   📅 Date: {date}")
        print(f"   🏷️  Domains: {', '.join(domains)}")
        print(f"   🎯 Activity: {activity}")
        if topics:
            print(f"   📚 Topics: {', '.join(topics)}")
        
        # Generate output
        frontmatter = self.generate_frontmatter(
            title, date, domains, tags, source_type, filepath.name
        )
        
        # Clean content
        clean_content = self.clean_content(content)
        
        # Add heading and metadata section
        output = frontmatter + '\n'
        output += f"# {title}\n\n"
        output += f"**Date**: {date}  \n"
        output += f"**Source**: {source_type.replace('_', ' ').title()}  \n\n"
        output += "---\n\n"
        output += "## Conversation\n\n"
        output += clean_content + "\n\n"
        output += "---\n\n"
        output += "## Related Topics\n\n"
        
        # Add related links
        related_links = self.create_related_links(domains, topics)
        for link in related_links:
            output += f"- {link}\n"
        
        output += "\n---\n"
        output += "*Part of [[Core Cybersecurity Domains]] > [[Knowledge Base]]*\n"
        
        # Determine output filename with unique hash to avoid conflicts
        safe_title = re.sub(r'[^\w\s-]', '', title.lower())
        safe_title = re.sub(r'[-\s]+', '_', safe_title)[:50]
        
        # Add short hash of source filename for uniqueness
        source_hash = hashlib.md5(filepath.name.encode()).hexdigest()[:8]
        output_filename = f"{date}_{safe_title}_{source_hash}.md"
        
        # Keep all conversations in single directory (use tags for organization)
        output_path = self.output_dir / output_filename
        
        # Check if file already exists
        if output_path.exists() and skip_existing and not force:
            print(f"   ⏭️  File already exists: {output_path.name}")
            self.skipped.append(str(output_path))
            return False
        
        if dry_run:
            print(f"   🔍 [DRY RUN] Would create: {output_path}")
            return True
        
        # Write file
        try:
            output_path.write_text(output, encoding='utf-8')
            print(f"   ✅ Created: {output_path}")
            self.converted.append(str(output_path))
            # Add to hash index
            self.existing_hashes[content_hash] = output_path
            return True
        except Exception as e:
            print(f"   ❌ Error writing file: {e}")
            self.failed.append(str(filepath))
            return False
    
    def convert_directory(self, input_dir: Path, pattern: str = "*.md",
                         recursive: bool = True, dry_run: bool = False,
                         skip_existing: bool = True, force: bool = False):
        """Convert all matching files in directory."""
        print(f"\n🔍 Scanning: {input_dir}")
        
        # Find files
        if recursive:
            files = list(input_dir.rglob(pattern))
        else:
            files = list(input_dir.glob(pattern))
        
        print(f"📊 Found {len(files)} files matching '{pattern}'")
        
        if not files:
            print("⚠️  No files found to convert")
            return
        
        if not dry_run:
            print(f"📂 Existing files indexed: {len(self.existing_hashes)}")
            if skip_existing:
                print("⏭️  Will skip existing files and duplicates")
        
        # Convert each file
        for filepath in files:
            self.convert_file(filepath, dry_run=dry_run, 
                            skip_existing=skip_existing, force=force)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 Conversion Summary")
        print("="*60)
        print(f"✅ Successfully converted: {len(self.converted)}")
        print(f"⏭️  Skipped (existing): {len(self.skipped)}")
        print(f"🔁 Skipped (duplicate): {len(self.duplicates)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"📁 Output directory: {self.output_dir}")
        
        if self.converted:
            print(f"\n✨ Created {len(self.converted)} notes in {self.output_dir.name}/")
            # Group by domain tags
            by_domain = {}
            for path in self.converted:
                # Read frontmatter to get domain tags
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        # Extract domain from tags
                        for domain in ['grc', 'risk-management', 'threat-intelligence', 
                                     'security-operations', 'network-security', 'cryptography',
                                     'application-security', 'cloud-security', 'iam', 'career', 'general']:
                            if f'- {domain}\n' in content:
                                by_domain[domain] = by_domain.get(domain, 0) + 1
                except:
                    pass
            
            if by_domain:
                print("\nBy domain (via tags):")
                for domain, count in sorted(by_domain.items()):
                    print(f"   • {domain}: {count} notes")
        
        if self.duplicates:
            print(f"\n🔁 Duplicate content found:")
            for orig, existing in self.duplicates[:5]:
                print(f"   • {Path(orig).name} → {Path(existing).name}")
            if len(self.duplicates) > 5:
                print(f"   ... and {len(self.duplicates) - 5} more")


def main():
    parser = argparse.ArgumentParser(
        description="Convert conversation files to Logseq-compatible notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all .md files from Perplexity exports
  python conversation_converter.py --input-dir ~/Downloads/perplexity_export \\
                                    --output-dir Notes/pages/Conversations
  
  # Dry run to preview conversion
  python conversation_converter.py --input-dir ~/conversations \\
                                    --output-dir Notes/pages/Conversations \\
                                    --dry-run
  
  # Convert single file
  python conversation_converter.py --input-file conversation.md \\
                                    --output-dir Notes/pages/Conversations
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--input-dir',
        type=Path,
        help='Input directory containing conversation files'
    )
    group.add_argument(
        '--input-file',
        type=Path,
        help='Single conversation file to convert'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Output directory for converted notes'
    )
    parser.add_argument(
        '--pattern',
        default='*.md',
        help='File pattern to match (default: *.md)'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        default=True,
        help='Recursively search input directory (default: True)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview conversion without creating files'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing files and ignore duplicates'
    )
    parser.add_argument(
        '--no-skip',
        dest='skip_existing',
        action='store_false',
        default=True,
        help='Do not skip existing files (by default, existing files are skipped)'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if args.input_dir:
        if not args.input_dir.exists():
            print(f"❌ Input directory not found: {args.input_dir}")
            sys.exit(1)
    
    if args.input_file:
        if not args.input_file.exists():
            print(f"❌ Input file not found: {args.input_file}")
            sys.exit(1)
    
    # Create converter
    converter = ConversationConverter(args.output_dir)
    
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       CONVERSATION TO LOGSEQ NOTE CONVERTER               ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    # Convert
    if args.input_file:
        converter.convert_file(args.input_file, dry_run=args.dry_run,
                             skip_existing=args.skip_existing, force=args.force)
    else:
        converter.convert_directory(
            args.input_dir,
            pattern=args.pattern,
            recursive=args.recursive,
            dry_run=args.dry_run,
            skip_existing=args.skip_existing,
            force=args.force
        )


if __name__ == '__main__':
    main()
