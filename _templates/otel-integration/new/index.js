module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'name',
        message: 'Integration name (e.g., Metrics, Traces, Logs)',
        validate: (value) => value.length > 0 || 'Name is required'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Integration description',
        default: 'OpenTelemetry integration for observability'
      },
      {
        type: 'list',
        name: 'signal_type',
        message: 'Primary telemetry signal type',
        choices: ['traces', 'metrics', 'logs', 'all'],
        default: 'traces'
      },
      {
        type: 'input',
        name: 'service_name',
        message: 'Service name for telemetry',
        default: (answers) => `swarmsh.${answers.name.toLowerCase()}`
      },
      {
        type: 'confirm',
        name: 'has_exporter',
        message: 'Include custom exporter?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_processor',
        message: 'Include custom processor?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_semantic_conventions',
        message: 'Define semantic conventions?',
        default: true
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        return {
          ...answers,
          className: `${answers.name}Telemetry`,
          fileName: `${answers.name.toLowerCase()}_telemetry`,
          exporterName: `${answers.name}SpanExporter`,
          processorName: `${answers.name}SpanProcessor`
        };
      });
  }
};