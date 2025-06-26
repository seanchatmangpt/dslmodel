module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'domain',
        message: 'Semantic convention domain (e.g., analytics, security)',
        validate: (value) => value.length > 0 || 'Domain is required'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Domain description',
        default: 'Semantic conventions for telemetry attributes'
      },
      {
        type: 'input',
        name: 'prefix',
        message: 'Attribute prefix',
        default: (answers) => answers.domain.toLowerCase()
      },
      {
        type: 'input',
        name: 'version',
        message: 'Convention version',
        default: '1.0.0'
      },
      {
        type: 'input',
        name: 'attributes',
        message: 'Comma-separated list of base attributes',
        default: 'operation,status,duration,user_id',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'confirm',
        name: 'has_metrics',
        message: 'Include metric conventions?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_events',
        message: 'Include event conventions?',
        default: true
      },
      {
        type: 'confirm',
        name: 'generate_models',
        message: 'Generate Pydantic models?',
        default: true
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        // Generate metric names
        const metrics = [
          `${answers.prefix}.requests.total`,
          `${answers.prefix}.duration.histogram`,
          `${answers.prefix}.errors.total`,
          `${answers.prefix}.active.gauge`
        ];

        // Generate event names
        const events = [
          `${answers.prefix}.operation.started`,
          `${answers.prefix}.operation.completed`,
          `${answers.prefix}.error.occurred`,
          `${answers.prefix}.state.changed`
        ];

        return {
          ...answers,
          fileName: `${answers.domain.toLowerCase()}_semconv`,
          registryFileName: `${answers.domain.toLowerCase()}.yaml`,
          modelFileName: `${answers.domain.toLowerCase()}_models`,
          metrics: metrics,
          events: events
        };
      });
  }
};