export const backgroundChoices = [
  {text: "White", src: null, isSolid: true, color: "#ffffff"},
  {text: "Black", src: null, isSolid: true, color: "#000000"},
  {text: "Red", src: null, isSolid: true, color: "#ff0000"},
  {text: "Green", src: null, isSolid: true, color: "#00ff00"},
  {text: "Blue", src: null, isSolid: true, color: "#0000ff"},
  {text: "Office", src: "office.jpg", isSolid: false, color: null},
  {text: "Stars", src: "stars.jpg", isSolid: false, color: null},
]

// Add ID to each choice
backgroundChoices.forEach((choice, index) => {
  choice.id = index;
})

export const subjectChoices = [
    'A person',
    'A dog',
    'A cat',
    'A bird',
    'A fish',
    'A car',
    'An onion',
    'A banana',
    'A donkey',
    'Shrek',
    'A tree',
    'A house',
    'James Cameron',
]
