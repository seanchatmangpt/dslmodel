module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'name',
        message: 'Workflow name (e.g., deployment, analysis)',
        validate: (value) => value.length > 0 || 'Name is required'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Workflow description',
        default: 'Multi-agent coordination workflow'
      },
      {
        type: 'input',
        name: 'agents',
        message: 'Comma-separated list of participating agents',
        default: 'roberts,scrum,lean',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'input',
        name: 'steps',
        message: 'Number of workflow steps',
        default: '5',
        validate: (value) => !isNaN(parseInt(value)) || 'Must be a number',
        filter: (value) => parseInt(value)
      },
      {
        type: 'confirm',
        name: 'has_rollback',
        message: 'Include rollback capability?',
        default: true
      },
      {
        type: 'confirm',
        name: 'has_monitoring',
        message: 'Include monitoring spans?',
        default: true
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        // Generate workflow steps
        const workflowSteps = [];
        for (let i = 0; i < answers.steps; i++) {
          const agentIndex = i % answers.agents.length;
          workflowSteps.push({
            step: i + 1,
            agent: answers.agents[agentIndex],
            action: `step_${i + 1}`,
            span_name: `swarmsh.${answers.agents[agentIndex]}.${answers.name}_step_${i + 1}`
          });
        }

        return {
          ...answers,
          workflowSteps: workflowSteps,
          functionName: `run_${answers.name}_workflow`,
          fileName: `${answers.name}_workflow`
        };
      });
  }
};