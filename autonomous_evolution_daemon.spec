# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for autonomous evolution daemon
Generated for standalone distribution of the autonomous evolution system
"""

import os
from pathlib import Path

# Get the source directory
src_dir = Path('src')
project_root = Path('.')

a = Analysis(
    ['src/dslmodel/commands/autonomous_evolution_daemon.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include semantic conventions and generated models
        ('src/dslmodel/registry', 'dslmodel/registry'),
        ('src/dslmodel/generated', 'dslmodel/generated'),
        # Include evolution engine templates if they exist
        ('src/dslmodel/evolution_weaver', 'dslmodel/evolution_weaver'),
    ],
    hiddenimports=[
        # OpenTelemetry imports
        'opentelemetry.exporter.otlp.proto.grpc.trace_exporter',
        'opentelemetry.sdk.trace.export',
        'opentelemetry.sdk.trace.export.in_memory_span_exporter',
        'opentelemetry.semantic_conventions',
        
        # Core dependencies
        'loguru',
        'typer',
        'rich.console',
        'rich.panel',
        'rich.table',
        'rich.progress',
        
        # Pydantic and DSL model
        'pydantic',
        'dslmodel',
        
        # Async support
        'asyncio',
        'concurrent.futures',
        
        # System utilities
        'subprocess',
        'pathlib',
        'json',
        'time',
        'uuid',
        'random',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy development dependencies
        'pytest',
        'hypothesis',
        'jupyter',
        'ipython',
        'matplotlib',
        'pandas',
        'numpy',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='autonomous-evolution-daemon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)