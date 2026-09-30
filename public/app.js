const questions = [
  {
    topic: 'THE BASICS',
    overline: 'START WITH THE BIG IDEA',
    prompt: 'What do we mean when we say a machine is using artificial intelligence?',
    answers: ['It follows a fixed list of instructions, no matter what.', 'It performs tasks that usually call for human-like reasoning or perception.', 'It has a physical body and can move through the world.', 'It is connected to the internet and can search for information.'],
    correct: 1,
    explanation: 'AI describes systems built to perform tasks associated with human intelligence, such as recognizing patterns, understanding language, or making predictions.'
  },
  {
    topic: 'LANGUAGE MODELS',
    overline: 'THREE LETTERS, ONE BIG IDEA',
    prompt: 'What does “LLM” stand for?',
    answers: ['Logical Learning Machine', 'Large Language Model', 'Linked Language Memory', 'Long-form Logic Module'],
    correct: 1,
    explanation: 'A Large Language Model learns statistical patterns in text and uses them to interpret and generate language.'
  },
  {
    topic: 'HOW IT LEARNS',
    overline: 'BEFORE THE ANSWER COMES THE PRACTICE',
    prompt: 'What happens during the training of a machine-learning model?',
    answers: ['It practices on data and adjusts internal parameters to improve at a task.', 'It memorizes every possible answer a person might ask for.', 'It receives a set of permanent rules that cannot change.', 'It checks the internet every time it needs to make a prediction.'],
    correct: 0,
    explanation: 'Training uses examples to adjust a model’s internal parameters. The model can then apply the patterns it learned to new inputs.'
  },
  {
    topic: 'GENERATIVE AI',
    overline: 'MAKING SOMETHING NEW',
    prompt: 'What is generative AI primarily designed to do?',
    answers: ['Guarantee that information is true and up to date.', 'Sort existing files into folders.', 'Create new content, such as text, images, audio, or code.', 'Replace the data it was trained on with live facts.'],
    correct: 2,
    explanation: 'Generative systems produce new outputs based on patterns learned from their training data. New does not automatically mean accurate.'
  },
  {
    topic: 'MODEL LIMITS',
    overline: 'SOUNDS SURE. IS IT?',
    prompt: 'In AI, what is a “hallucination”?',
    answers: ['A model refusing to answer a question.', 'A made-up or incorrect response presented as if it were true.', 'An image that contains an optical illusion.', 'A temporary loss of internet connection.'],
    correct: 1,
    explanation: 'A hallucination is plausible-sounding content that is false, unsupported, or invented. Important claims still need checking.'
  },
  {
    topic: 'EVERYDAY AI',
    overline: 'PATTERNS IN THE SMALL THINGS',
    prompt: 'Which of these is a common example of narrow AI?',
    answers: ['A universal mind that can learn any human skill.', 'A recommendation system suggesting what to watch next.', 'A computer that understands every topic exactly as a person does.', 'A robot that has emotions and personal goals.'],
    correct: 1,
    explanation: 'Narrow AI is designed for a limited task. Recommendations, spam filters, translation tools, and voice assistants are familiar examples.'
  },
  {
    topic: 'AI LANGUAGE',
    overline: 'THE MODEL’S BUILDING BLOCK',
    prompt: 'What is a “token” in the context of a language model?',
    answers: ['A unit of text, such as a word or part of a word, processed by the model.', 'A digital coin used to pay for internet access.', 'A password that unlocks the model’s source code.', 'A single complete sentence.'],
    correct: 0,
    explanation: 'Models split text into tokens before processing it. A token can be a whole word, a piece of one, punctuation, or other text units.'
  },
  {
    topic: 'SAFER PROMPTS',
    overline: 'WHEN INSTRUCTIONS COLLIDE',
    prompt: 'What is a prompt injection attempt?',
    answers: ['A request to make an AI answer in a shorter format.', 'An instruction hidden in input that tries to override the system’s intended rules.', 'A technique that improves a model by adding more training data.', 'A prompt that asks the model to explain its answer.'],
    correct: 1,
    explanation: 'Prompt injection tries to manipulate a model into ignoring its intended instructions, often by hiding conflicting directions in user-provided content.'
  },
  {
    topic: 'AI & PEOPLE',
    overline: 'TOOLS STILL NEED JUDGMENT',
    prompt: 'Why should people review AI-generated information before relying on it?',
    answers: ['AI can only produce information after a human approves each word.', 'A review makes the model learn the answer permanently.', 'Outputs can contain errors, bias, or missing context.', 'AI systems do not use data to generate responses.'],
    correct: 2,
    explanation: 'AI outputs can be wrong, biased, or incomplete. Human review adds context and accountability, especially in high-stakes decisions.'
  },
  {
    topic: 'A QUICK REALITY CHECK',
    overline: 'THE MOST HUMAN SKILL OF ALL',
    prompt: 'You get a confident answer from an AI tool. What is the smartest next move?',
    answers: ['Assume the confident tone means it is correct.', 'Check important claims against reliable sources.', 'Ask the same tool to repeat the answer more firmly.', 'Share it immediately so others can verify it later.'],
    correct: 1,
    explanation: 'Confidence in the wording is not proof. Verify important claims with trustworthy sources and use human judgment.'
  }
];

const bestScoreKey = 'machine-mind-best-score';
let currentQuestion = 0;
let selectedAnswers = Array(questions.length).fill(null);
let finished = false;

const $ = (selector) => document.querySelector(selector);
const quizScreen = $('#quiz-screen');
const resultsScreen = $('#results-screen');

function readBestScore() {
  try {
    return Number(localStorage.getItem(bestScoreKey)) || 0;
  } catch {
    return 0;
  }
}

function setBestScore(score) {
  try {
    localStorage.setItem(bestScoreKey, String(score));
  } catch {
    // The quiz remains playable if browser storage is unavailable.
  }
}

function getScore() {
  return selectedAnswers.reduce((score, answer, index) => score + (answer === questions[index].correct ? 1 : 0), 0);
}

function renderMap() {
  $('#question-map').innerHTML = questions.map((question, index) => {
    const answered = selectedAnswers[index] !== null;
    const correct = answered && selectedAnswers[index] === question.correct;
    const classes = [index === currentQuestion ? 'current' : '', answered ? 'answered' : '', correct ? 'correct' : answered ? 'incorrect' : ''].filter(Boolean).join(' ');
    return `<button class="map-item ${classes}" type="button" data-question="${index}" aria-label="Go to question ${index + 1}${answered ? correct ? ', correct' : ', incorrect' : ''}" aria-current="${index === currentQuestion ? 'step' : 'false'}">${String(index + 1).padStart(2, '0')}</button>`;
  }).join('');
}

function renderQuestion() {
  if (finished) {
    renderResults();
    return;
  }

  const question = questions[currentQuestion];
  const selected = selectedAnswers[currentQuestion];
  const answered = selected !== null;
  const score = getScore();
  $('#topic-tag').textContent = question.topic;
  $('#question-overline').textContent = question.overline;
  $('#question-text').textContent = question.prompt;
  $('#question-number').textContent = `QUESTION ${String(currentQuestion + 1).padStart(2, '0')}`;
  $('#rail-current').textContent = String(currentQuestion + 1).padStart(2, '0');
  $('#rail-fill').style.width = `${((currentQuestion + 1) / questions.length) * 100}%`;
  $('#best-score').textContent = readBestScore() ? `${readBestScore()}/10` : '—';
  $('#answer-list').innerHTML = question.answers.map((answer, index) => {
    let stateClass = '';
    if (answered && index === question.correct) stateClass = ' correct';
    else if (answered && index === selected) stateClass = ' incorrect';
    else if (answered) stateClass = ' subdued';
    return `<button class="answer-option${stateClass}" type="button" data-answer="${index}" aria-pressed="${selected === index}" ${answered ? 'disabled' : ''}><span class="answer-letter">${String.fromCharCode(65 + index)}</span><span class="answer-copy">${answer}</span><span class="answer-mark" aria-hidden="true"></span></button>`;
  }).join('');
  const feedback = $('#feedback');
  feedback.hidden = !answered;
  if (answered) {
    const isCorrect = selected === question.correct;
    feedback.className = `feedback ${isCorrect ? 'feedback-correct' : 'feedback-incorrect'}`;
    feedback.innerHTML = `<span class="feedback-label">${isCorrect ? 'THAT’S RIGHT' : 'NOT QUITE'}</span><p>${question.explanation}</p>`;
  }
  $('#back-button').disabled = currentQuestion === 0;
  $('#next-button').disabled = !answered;
  $('#next-button').innerHTML = currentQuestion === questions.length - 1 ? 'SEE RESULTS <span aria-hidden="true">↗</span>' : 'NEXT <span aria-hidden="true">→</span>';
  renderMap();
}

function renderResults() {
  const score = getScore();
  const percent = Math.round((score / questions.length) * 100);
  quizScreen.hidden = true;
  resultsScreen.hidden = false;
  $('#final-score').textContent = score;
  $('#score-ring').style.setProperty('--score', `${percent}%`);
  $('#score-caption').textContent = score === 10 ? 'A perfect run. Nicely reasoned.' : score >= 7 ? 'A strong grasp of the essentials.' : score >= 4 ? 'A solid start. Keep asking questions.' : 'Every good question is a first step.';
  $('#results-message').textContent = score >= 7
    ? 'You know your way around the ideas behind AI. Keep your curiosity switched on.'
    : 'You just met some of the ideas behind AI. Take a look at the answer notes, then give it another go.';
  $('#review-summary').textContent = `${score} RIGHT · ${questions.length - score} TO REVISIT`;
  $('#review-list').innerHTML = questions.map((question, index) => {
    const isCorrect = selectedAnswers[index] === question.correct;
    return `<article class="review-item ${isCorrect ? 'review-correct' : 'review-incorrect'}"><span class="review-number">${String(index + 1).padStart(2, '0')}</span><div><h3>${question.prompt}</h3><p>${question.answers[question.correct]}</p></div><span class="review-mark" aria-label="${isCorrect ? 'Correct' : 'Review'}">${isCorrect ? '✓' : '↗'}</span></article>`;
  }).join('');
  const best = readBestScore();
  if (score > best) setBestScore(score);
  $('#best-score').textContent = `${Math.max(score, best)}/10`;
}

function restartQuiz() {
  currentQuestion = 0;
  selectedAnswers = Array(questions.length).fill(null);
  finished = false;
  quizScreen.hidden = false;
  resultsScreen.hidden = true;
  renderQuestion();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

$('#answer-list').addEventListener('click', (event) => {
  const answerButton = event.target.closest('[data-answer]');
  if (!answerButton || selectedAnswers[currentQuestion] !== null) return;
  selectedAnswers[currentQuestion] = Number(answerButton.dataset.answer);
  renderQuestion();
});

$('#question-map').addEventListener('click', (event) => {
  const mapButton = event.target.closest('[data-question]');
  if (!mapButton) return;
  currentQuestion = Number(mapButton.dataset.question);
  renderQuestion();
});

$('#back-button').addEventListener('click', () => {
  if (currentQuestion > 0) {
    currentQuestion -= 1;
    renderQuestion();
  }
});

$('#next-button').addEventListener('click', () => {
  if (selectedAnswers[currentQuestion] === null) return;
  if (currentQuestion === questions.length - 1) {
    finished = true;
    renderResults();
  } else {
    currentQuestion += 1;
    renderQuestion();
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

$('#restart-top').addEventListener('click', restartQuiz);
$('#replay-button').addEventListener('click', restartQuiz);
renderQuestion();