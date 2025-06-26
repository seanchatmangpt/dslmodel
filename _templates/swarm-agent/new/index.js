module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'name',
        message: 'Agent name (e.g., Monitoring, Analytics)',
        validate: (value) => value.length > 0 || 'Name is required'
      },
      {
        type: 'input',
        name: 'purpose',
        message: 'Agent purpose/description',
        default: 'Process telemetry spans and coordinate actions'
      },
      {
        type: 'input',
        name: 'states',
        message: 'Comma-separated list of states',
        default: 'IDLE,ACTIVE,PROCESSING,COMPLETE',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'input',
        name: 'triggers',
        message: 'Comma-separated list of triggers',
        default: 'start,process,analyze,complete',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'input',
        name: 'listen_filter',
        message: 'Span name filter (e.g., swarmsh.monitoring)',
        default: (answers) => `swarmsh.${answers.name.toLowerCase()}`
      },
      {
        type: 'confirm',
        name: 'has_next_command',
        message: 'Does this agent trigger other agents?',
        default: true
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        // Generate state machine configuration
        const transitions = [];
        const states = answers.states;
        
        // Create basic transitions between sequential states
        for (let i = 0; i < states.length - 1; i++) {
          transitions.push({
            trigger: answers.triggers[i] || `to_${states[i+1].toLowerCase()}`,
            source: states[i],
            dest: states[i+1]
          });
        }

        return {
          ...answers,
          className: `${answers.name}Agent`,
          fileName: `${answers.name.toLowerCase()}_agent`,
          transitions: transitions,
          initialState: states[0]
        };
      });
  }
};