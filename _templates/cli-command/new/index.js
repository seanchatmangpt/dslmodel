module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'name',
        message: 'Command name (e.g., analyze, report)',
        validate: (value) => value.length > 0 || 'Name is required'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Command description',
        default: 'Execute SwarmAgent coordination task'
      },
      {
        type: 'input',
        name: 'parent_command',
        message: 'Parent command group (e.g., swarm, otel)',
        default: 'swarm'
      },
      {
        type: 'confirm',
        name: 'has_subcommands',
        message: 'Will this command have subcommands?',
        default: false
      },
      {
        type: 'input',
        name: 'arguments',
        message: 'Comma-separated list of positional arguments',
        default: '',
        filter: (value) => value ? value.split(',').map(s => s.trim()) : []
      },
      {
        type: 'input',
        name: 'options',
        message: 'Comma-separated list of options (e.g., output-format,verbose)',
        default: 'format,verbose',
        filter: (value) => value ? value.split(',').map(s => s.trim()) : []
      },
      {
        type: 'confirm',
        name: 'uses_rich',
        message: 'Use Rich for formatted output?',
        default: true
      },
      {
        type: 'confirm',
        name: 'async_command',
        message: 'Is this an async command?',
        default: false
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        // Generate function names
        const functionName = answers.has_subcommands ? 
          `${answers.name}_group` : 
          `${answers.name}_command`;
          
        return {
          ...answers,
          functionName: functionName,
          fileName: `${answers.parent_command}_${answers.name}_command`,
          moduleName: `${answers.parent_command}_commands`
        };
      });
  }
};