#!/usr/bin/fish

# Base directory
set base_dir "docs"

# Function to create directories and files
function create_docs_structure
    # Create the base docs directory
    mkdir -p $base_dir

    # Create README
    touch "$base_dir/README.md"

    # getting_started section
    mkdir -p "$base_dir/getting_started"
    touch "$base_dir/getting_started/installation.md"
    touch "$base_dir/getting_started/quick_start.md"
    touch "$base_dir/getting_started/concepts.md"
    touch "$base_dir/getting_started/faq.md"

    # core_components section
    mkdir -p "$base_dir/core_components"
    touch "$base_dir/core_components/Workflow.md"
    touch "$base_dir/core_components/Job.md"
    touch "$base_dir/core_components/Action.md"
    touch "$base_dir/core_components/Condition.md"
    touch "$base_dir/core_components/Trigger.md"
    touch "$base_dir/core_components/Loop.md"
    touch "$base_dir/core_components/Scheduler.md"
    touch "$base_dir/core_components/StateMachine.md"
    touch "$base_dir/core_components/context_management.md"

    # dslmodel_components section
    mkdir -p "$base_dir/dslmodel_components/generators"
    mkdir -p "$base_dir/dslmodel_components/mixins"
    mkdir -p "$base_dir/dslmodel_components/template"
    mkdir -p "$base_dir/dslmodel_components/utils"
    touch "$base_dir/dslmodel_components/DSLModel.md"
    touch "$base_dir/dslmodel_components/generators/DSLClassGenerator.md"
    touch "$base_dir/dslmodel_components/generators/IPythonNotebookGenerator.md"
    touch "$base_dir/dslmodel_components/generators/gen_ipynb_notebook.md"
    touch "$base_dir/dslmodel_components/mixins/ToolMixin.md"
    touch "$base_dir/dslmodel_components/mixins/FSMMixin.md"
    touch "$base_dir/dslmodel_components/mixins/JinjaMixin.md"
    touch "$base_dir/dslmodel_components/mixins/FileHandlerMixin.md"
    touch "$base_dir/dslmodel_components/template/JinjaTemplates.md"
    touch "$base_dir/dslmodel_components/template/functional.md"
    touch "$base_dir/dslmodel_components/template/custom_templates.md"
    touch "$base_dir/dslmodel_components/utils/DataReader.md"
    touch "$base_dir/dslmodel_components/utils/DataWriter.md"
    touch "$base_dir/dslmodel_components/utils/ContextGenerator.md"
    touch "$base_dir/dslmodel_components/utils/FilenameModel.md"

    # workflows section
    mkdir -p "$base_dir/workflows/examples"
    touch "$base_dir/workflows/examples/data_analysis_workflow.md"
    touch "$base_dir/workflows/examples/etl_workflow.md"
    touch "$base_dir/workflows/examples/notification_workflow.md"
    touch "$base_dir/workflows/compliance_workflow.md"
    touch "$base_dir/workflows/patterns.md"
    touch "$base_dir/workflows/scheduling_workflows.md"

    # api section
    mkdir -p "$base_dir/api/v1"
    mkdir -p "$base_dir/api/v2"
    touch "$base_dir/api/overview.md"
    touch "$base_dir/api/endpoints.md"
    touch "$base_dir/api/v1/endpoints.md"
    touch "$base_dir/api/v1/examples.md"
    touch "$base_dir/api/v2/endpoints.md"

    # ci_cd section
    mkdir -p "$base_dir/ci_cd"
    touch "$base_dir/ci_cd/pipeline_overview.md"
    touch "$base_dir/ci_cd/docs_automation.md"
    touch "$base_dir/ci_cd/quality_assurance.md"
    touch "$base_dir/ci_cd/deployment_pipeline.md"

    # testing section
    mkdir -p "$base_dir/testing"
    touch "$base_dir/testing/overview.md"
    touch "$base_dir/testing/unit_testing.md"
    touch "$base_dir/testing/integration_testing.md"
    touch "$base_dir/testing/doc_testing.md"
    touch "$base_dir/testing/debugging_guide.md"

    # compliance section
    mkdir -p "$base_dir/compliance"
    touch "$base_dir/compliance/EU_AI_Act.md"
    touch "$base_dir/compliance/documentation_standards.md"
    touch "$base_dir/compliance/audit_and_logging.md"

    # advanced section
    mkdir -p "$base_dir/advanced"
    touch "$base_dir/advanced/custom_triggers.md"
    touch "$base_dir/advanced/extending_mixins.md"
    touch "$base_dir/advanced/external_integrations.md"

    # best_practices section
    mkdir -p "$base_dir/best_practices"
    touch "$base_dir/best_practices/general.md"
    touch "$base_dir/best_practices/naming_conventions.md"
    touch "$base_dir/best_practices/docs_feedback_process.md"

    # auto_generated section
    mkdir -p "$base_dir/auto_generated/model_docs"
    mkdir -p "$base_dir/auto_generated/workflow_docs"
    mkdir -p "$base_dir/auto_generated/api_docs"
    mkdir -p "$base_dir/auto_generated/class_diagrams"

    # Root-level files
    touch "$base_dir/changelog.md"
    touch "$base_dir/glossary.md"
end

# Execute the function to create the structure
create_docs_structure
