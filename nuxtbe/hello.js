// Import the pythonia bridge
import { python } from 'pythonia'; // Removed PyClass as it's unused in this simple example

(async () => {
  try {
    // Initialize the Python bridge with the hello.py script
    const helloModule = await python('./hello.py')

    // Access the greet function from the Python module
    let greet = helloModule.greet

    // Create plain JavaScript objects that match the GreetingModel fields
    const greetingInstance = {
      name: 'Alice',
      greeting: 'Hi'
    }

    // Call the greet function with the plain object
    const message = await greet(greetingInstance)

    console.log(message) // Output: Hi, Alice!

    // Example with default greeting
    const defaultGreetingInstance = {
      name: 'Bob'
      // 'greeting' is optional and defaults to "Hello"
    }

    greet = helloModule.greet

    const defaultMessage = await greet(defaultGreetingInstance)
    console.log(defaultMessage) // Output: Hello, Bob!

    // Example with missing required field to trigger validation
    const invalidGreetingInstance = {
      greeting: 'Hey'
      // 'name' is missing
    }

    greet = helloModule.greet

    const invalidMessage = await greet(invalidGreetingInstance)
    console.log(invalidMessage) // Output: Validation Error: ...

    // Exit the Python bridge
    python.exit()
  } catch (error) {
    console.error('Error:', error)
    python.exit()
  }
})()
