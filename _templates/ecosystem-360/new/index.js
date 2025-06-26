module.exports = {
  prompt: ({ inquirer }) => {
    const questions = [
      {
        type: 'input',
        name: 'feature_name',
        message: 'Feature name for 360° ecosystem (e.g., SecurityMonitoring)',
        validate: (value) => value.length > 0 || 'Feature name is required'
      },
      {
        type: 'input',
        name: 'description',
        message: 'Feature description',
        default: 'Complete ecosystem feature with full integration'
      },
      {
        type: 'input',
        name: 'domain',
        message: 'Semantic convention domain',
        default: (answers) => answers.feature_name.toLowerCase().replace(/([A-Z])/g, '_$1').substring(1)
      },
      {
        type: 'input',
        name: 'agents',
        message: 'Comma-separated list of agents',
        default: 'detector,analyzer,responder',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'input',
        name: 'workflows',
        message: 'Comma-separated list of workflows',
        default: 'detection,analysis,response',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'input',
        name: 'states',
        message: 'Comma-separated list of common states',
        default: 'IDLE,MONITORING,PROCESSING,ALERTING,RESOLVED',
        filter: (value) => value.split(',').map(s => s.trim())
      },
      {
        type: 'confirm',
        name: 'include_cli',
        message: 'Include CLI commands?',
        default: true
      },
      {
        type: 'confirm',
        name: 'include_tests',
        message: 'Include comprehensive test suite?',
        default: true
      },
      {
        type: 'confirm',
        name: 'include_docs',
        message: 'Include documentation?',
        default: true
      },
      {
        type: 'confirm',
        name: 'include_e2e',
        message: 'Include E2E demonstration?',
        default: true
      }
    ];

    return inquirer
      .prompt(questions)
      .then(answers => {
        // Generate file names
        const prefix = answers.domain;
        const featureLower = answers.feature_name.toLowerCase();
        
        return {
          ...answers,
          prefix: prefix,
          featureLower: featureLower,
          featureClass: answers.feature_name.charAt(0).toUpperCase() + answers.feature_name.slice(1),
          fileName: `${featureLower}_ecosystem`,
          testFileName: `test_${featureLower}_ecosystem`,
          e2eFileName: `e2e_${featureLower}_demo`,
          docFileName: `${answers.feature_name}_ECOSYSTEM`
        };
      });
  }
};