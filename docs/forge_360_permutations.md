# Weaver Forge 360 Permutation Generator

## Overview

The Forge 360 Permutation Generator creates 360 unique semantic convention permutations for comprehensive testing of DSLModel across multiple dimensions. This tool ensures thorough coverage of different span types, attribute combinations, metric types, languages, and frameworks.

## Features

- **360 Unique Permutations**: Systematically generated using a matrix approach
- **Multi-Language Support**: Python, Rust, TypeScript, Go, and Java
- **Framework Coverage**: Multiple frameworks per language (Pydantic, Serde, Zod, etc.)
- **Comprehensive Attributes**: Minimal, standard, extended, and custom attribute sets
- **Metric Types**: Counters, gauges, histograms, and more
- **Validation Suite**: Automated validation for all generated permutations

## Architecture

### Matrix Dimensions

1. **Span Types** (10 types)
   - http, database, messaging, rpc, faas
   - graphql, grpc, websocket, batch, stream

2. **Attribute Sets** (4 levels)
   - minimal: Only required attributes
   - standard: Required + recommended
   - extended: All attributes including optional
   - custom: Domain-specific attributes

3. **Metric Types** (8 types)
   - counter, gauge, histogram, summary
   - exponential_histogram, observable_counter
   - observable_gauge, observable_up_down_counter

4. **Languages** (5 languages)
   - Python, Rust, TypeScript, Go, Java

5. **Frameworks** (Multiple per language)
   - Python: pydantic, dataclass, attrs, msgspec
   - Rust: serde, prost, bincode
   - TypeScript: class, interface, zod, io-ts
   - Go: struct, protobuf
   - Java: pojo, record, lombok

## Usage

### CLI Commands

```bash
# Generate all 360 permutations
dslmodel forge permutations generate

# Generate with validation suite
dslmodel forge permutations generate --validate

# Check status
dslmodel forge permutations status --matrix --coverage

# Inspect specific permutation
dslmodel forge permutations inspect http_minimal_counter_python_pydantic

# Validate generated outputs
dslmodel forge permutations validate --language python
```

### Programmatic Usage

```python
from dslmodel.integrations.otel.forge_360_permutations import Forge360PermutationGenerator

# Initialize generator
generator = Forge360PermutationGenerator()

# Generate all permutations
permutations = generator.generate_all_permutations()

# Write to disk
generator.write_permutations_to_disk()

# Generate forge commands
commands = generator.generate_forge_commands()

# Create validation suite
generator.create_validation_suite()
```

## Generated Structure

```
semconv_360_permutations/
├── permutations_index.yaml       # Master index with metadata
├── run_all_permutations.sh       # Batch execution script
├── python/                       # Python permutations
│   ├── permutation_000_*.yaml
│   ├── permutation_001_*.yaml
│   └── ...
├── rust/                         # Rust permutations
├── typescript/                   # TypeScript permutations
├── go/                          # Go permutations
├── java/                        # Java permutations
└── validation/                  # Validation suite
    ├── validation_matrix.yaml
    └── coverage_report.md
```

## Permutation Example

Each permutation generates a semantic convention like:

```yaml
metadata:
  generated_at: '2024-01-20T10:30:00'
  generator_version: '1.0.0'
  permutation_index: 42

configuration:
  span_type: http
  attribute_set: standard
  metric_type: histogram
  language: python
  framework: pydantic
  template_config:
    base_class: pydantic.BaseModel
    imports: ['from pydantic import BaseModel, Field']

semconv:
  groups:
    - id: dslmodel.http
      type: span
      prefix: dslmodel.http
      brief: DSLModel http span attributes
      attributes:
        - id: http.method
          type: string
          requirement_level: required
          brief: The http method
        - id: http.status_code
          type: int
          requirement_level: recommended
          brief: The http response status code
        - id: http.duration_ms
          type: int
          requirement_level: recommended
          brief: Duration of http operation in milliseconds
```

## Integration with Weaver Forge

The generated permutations integrate seamlessly with OpenTelemetry Weaver:

1. **Generation Phase**: Creates 360 YAML semantic convention files
2. **Forge Phase**: Uses Weaver to generate code for each permutation
3. **Validation Phase**: Validates all generated code

## Performance Considerations

- Generation: ~5 seconds for all 360 permutations
- Disk Usage: ~10MB for all YAML files
- Forge Execution: ~30-60 minutes for all permutations (can be parallelized)

## Testing Coverage

The 360 permutations ensure:

- **100% span type coverage**: All 10 span types tested
- **100% attribute set coverage**: All 4 attribute levels tested
- **100% language coverage**: All 5 languages tested
- **Balanced framework coverage**: 2+ frameworks per language
- **Comprehensive metric coverage**: 3+ metric types tested

## Future Enhancements

1. **Cloud Integration**: Deploy permutations to cloud forge services
2. **Performance Benchmarks**: Measure generation performance per permutation
3. **Custom Matrices**: Allow user-defined matrix dimensions
4. **Incremental Generation**: Only regenerate changed permutations
5. **Visual Dashboard**: Web UI for exploring permutations

## Troubleshooting

### Common Issues

1. **Weaver Not Found**
   ```bash
   # Install weaver
   brew install opentelemetry-weaver
   ```

2. **Permission Denied**
   ```bash
   # Make script executable
   chmod +x semconv_360_permutations/run_all_permutations.sh
   ```

3. **Out of Memory**
   ```bash
   # Run in batches
   dslmodel forge permutations run --batch-size 50
   ```

## Contributing

To add new dimensions to the matrix:

1. Update `SPAN_TYPES`, `ATTRIBUTE_SETS`, etc. in `forge_360_permutations.py`
2. Implement corresponding generation logic in `_generate_semconv()`
3. Update template configurations in `_generate_template_config()`
4. Add tests for new dimensions

## License

Part of DSLModel project - see main LICENSE file.