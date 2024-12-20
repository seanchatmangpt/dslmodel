import fs from 'fs'
import path from 'path'
import { python } from 'pythonia'

// Factory function to create and validate a Pydantic model
async function createPydanticModel(modelName, fields) {
  // Generate Python code for the Pydantic model
  const fieldDefs = Object.entries(fields)
    .map(([name, type]) => `    ${name}: ${type}`)
    .join('\n')

  const pythonCode = `
from pydantic import BaseModel, ValidationError
from typing import List

class ${modelName}(BaseModel):
${fieldDefs}

    def greet(self):
        return f"Hello, {self.name}!"
`

  // Write the Python code to a temporary file
  const modelFilePath = path.join(process.cwd(), `${modelName.toLowerCase()}_model.py`)
  fs.writeFileSync(modelFilePath, pythonCode)

  // Load the Python model from the file
  const modelModule = await python(modelFilePath)
  const ModelClass = await modelModule[modelName]

  // Define a validation and instantiation function
  async function validateAndInstantiate(data) {
    try {
      // Validate the JavaScript object with model_validate
      const validatedData = await ModelClass.model_validate$(data)
      console.log(`Validated ${modelName}:`, validatedData)

      // Optionally create an instance if needed
      const modelInstance = await ModelClass.$(validatedData)
      return modelInstance
    } catch (error) {
      console.error(`Validation failed for ${modelName}:`, error)
      throw error
    }
  }

  // Clean up temporary Python file (optional)
  // fs.unlinkSync(modelFilePath)

  return validateAndInstantiate
}

// Define fields for the User model
const userFields = {
  name: 'str',
  age: 'int',
  hobbies: 'List[str]'
};

(async () => {
  // Create a validation function for the User model
  const validateUser = await createPydanticModel('User', userFields)

  // JavaScript object to validate
  const userData = {
    name: 'Alice',
    age: 30,
    hobbies: ['Reading', 'Cycling']
  }

  // Validate and create a User instance
  try {
    const userInstance = await validateUser(userData)

    // Call methods on the validated instance
    console.log(await userInstance.greet()) // Output: "Hello, Alice!"
    console.log('User Hobbies:', await userInstance.hobbies)
  } catch (error) {
    console.error('User validation failed:', error)
  }

  // Clean up Python environment
  python.exit()
})()
