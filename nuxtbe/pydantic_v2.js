import { python, PyClass } from 'pythonia'

python.setFastMode(true) // for improved performance

const pydantic = await python('pydantic')

// Define the User model in JavaScript using PyClass
class User extends PyClass {
  constructor(name, age, hobbies = []) {
    super(pydantic.BaseModel) // Extend Pydantic’s BaseModel
    this.name = name
    this.age = age
    this.hobbies = hobbies
  }

  // Define validation using Pydantic fields in the init function
  async init() {
    this.name = await pydantic.Field$({ type: 'str', description: 'The name of the user' })
    this.age = await pydantic.Field$({ type: 'int', ge: 0, description: 'The age of the user' })
    this.hobbies = await pydantic.Field$({ default: [], description: 'List of user hobbies' })
  }

  // A method in the User model, similar to a method in Pydantic
  async greet() {
    return `Hello, ${this.name}!`
  }
}

// Create an instance of the User model
const user = await User.init('Alice', 30, ['Reading', 'Cycling'])

// Validate data on the model
try {
  // Access validated fields
  console.log('Name:', user.name)
  console.log('Age:', user.age)
  console.log('Hobbies:', user.hobbies)

  // Call the greet method
  const greeting = await user.greet()
  console.log(greeting) // "Hello, Alice!"
} catch (error) {
  console.error('Validation failed:', error)
}

// Clean up Python environment
python.exit()
