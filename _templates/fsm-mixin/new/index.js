module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'name',
        message: 'Mixin name (e.g., Workflow, Approval)',
        validate: (value) => value.length > 0 || 'Name is required'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Mixin description',
        default: 'State machine mixin for coordinated behavior'
      },
      {
        type: 'input',
        name: 'states',
        message: 'Comma-separated list of states',
        default: 'INIT,PENDING,ACTIVE,COMPLETE,ERROR',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'confirm',
        name: 'has_timeout',
        message: 'Include timeout handling?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_retry',
        message: 'Include retry logic?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_callbacks',
        message: 'Include state transition callbacks?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_persistence',
        message: 'Include state persistence?',
        default: false
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        // Generate transition triggers
        const triggers = [];
        const states = answers.states;
        
        // Common triggers
        triggers.push('initialize', 'reset', 'error');
        
        // State-based triggers
        states.forEach((state, index) => {
          if (index < states.length - 1) {
            triggers.push(`to_${state.toLowerCase()}`);
          }
        });
        
        return {
          ...answers,
          className: `${answers.name}FSMMixin`,
          fileName: `${answers.name.toLowerCase()}_fsm_mixin`,
          triggers: triggers,
          initialState: states[0]
        };
      });
  }
};