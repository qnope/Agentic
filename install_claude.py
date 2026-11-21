#!/usr/bin/env python3
"""Install parts of this repository into a project for Claude Code: ./install_claude.py <kind>/<name> [--project <folder>].

<kind> is skill, agent, hook, workflow or mcp-server. Run it without argument to list the parts. See install_lib.py.
"""
import sys

import install_lib

sys.exit(install_lib.main("claude"))
