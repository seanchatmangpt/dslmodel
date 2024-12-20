import { python } from 'pythonia'

// Initialize DSLModel and required classes from Python
const DSLModel = await python('dslmodel')

// Create participants using Python's DSLModel Participant class
const participants = []
for (let i = 0; i < 5; i++) {
  const participant = await DSLModel.Participant()
  await participant.set('name', `Participant ${i + 1}`)
  await participant.set('role', 'Member')
  participants.push(participant)
}

// Define meeting details and create a meeting instance
const meetingTemplate = `
Project Planning Meeting for Q4 Initiatives
Participants:
{% for participant in participants %}
- {{ participant.name }} ({{ participant.role }})
{% endfor %}
`

const meetingInstance = await DSLModel.Meeting({
  name: 'Q4 Project Planning',
  meeting_date: '2024-10-10',
  location: 'Main Conference Room',
  chairperson: participants[0],
  secretary: participants[1],
  participants: participants,
  agenda: ['Introduction', 'Review of Previous Quarter', 'Planning Next Steps'],
  minutes: [],
  rules_of_order: ['Robert\'s Rules of Order']
})

// Generate data from the meeting template (using template with participant names)
await meetingInstance.from_prompt(meetingTemplate, { participants })

// Print the meeting instance in YAML format
console.log(await meetingInstance.to_yaml())

// Clean up Python environment
python.exit()
